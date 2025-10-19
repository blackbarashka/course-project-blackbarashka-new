import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ProblemDetailsException(HTTPException):
    """Исключение с деталями проблемы по RFC 7807"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        title: str = None,
        type: str = None,
        instance: str = None,
        headers: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.title = title
        self.type = type
        self.instance = instance
        self.headers = headers or {}


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок по RFC 7807"""

    async def dispatch(self, request: Request, call_next):
        try:
            # Генерируем correlation_id для запроса
            correlation_id = str(uuid.uuid4())
            request.state.correlation_id = correlation_id

            response = await call_next(request)
            return response

        except ProblemDetailsException as exc:
            return self._create_problem_response(request, exc)
        except HTTPException as exc:
            # ПЕРЕХВАТЫВАЕМ ВСЕ HTTPException и конвертируем в RFC 7807
            return self._create_problem_response(
                request,
                ProblemDetailsException(
                    status_code=exc.status_code,
                    detail=exc.detail,
                    title=self._get_title_for_status(exc.status_code),
                    type=self._get_type_for_status(exc.status_code),
                    instance=request.url.path,
                    headers=exc.headers,
                ),
            )
        except RequestValidationError:
            # Обработка ошибок валидации Pydantic
            return self._create_problem_response(
                request,
                ProblemDetailsException(
                    status_code=422,
                    detail="Validation error",
                    title="Validation Error",
                    type="https://api.readinglist.com/errors/validation-error",
                    instance=request.url.path,
                ),
            )
        except Exception:
            # В production не раскрываем детали внутренних ошибок
            return self._create_problem_response(
                request,
                ProblemDetailsException(
                    status_code=500,
                    detail="Internal Server Error",
                    title="Internal Server Error",
                    type="https://api.readinglist.com/errors/internal-error",
                    instance=request.url.path,
                ),
            )

    def _create_problem_response(
        self, request: Request, exc: ProblemDetailsException
    ) -> JSONResponse:
        """Создает ответ в формате RFC 7807"""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

        problem_details = {
            "type": exc.type or "https://api.readinglist.com/errors/generic-error",
            "title": exc.title or "An error occurred",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": exc.instance or request.url.path,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Логируем ошибку для аудита
        self._log_error(request, problem_details)

        return JSONResponse(
            status_code=exc.status_code, content=problem_details, headers=exc.headers
        )

    def _log_error(self, request: Request, problem_details: Dict):
        """Логирование ошибок для аудита"""
        log_data = {
            "correlation_id": problem_details["correlation_id"],
            "method": request.method,
            "url": str(request.url),
            "status_code": problem_details["status"],
            "error_type": problem_details["type"],
            "client_ip": request.client.host if request.client else "unknown",
        }
        logger = logging.getLogger("app.audit")
        logger.info("AUDIT_ERROR: %s", log_data)

    def _get_title_for_status(self, status_code: int) -> str:
        """Получить заголовок для HTTP статуса"""
        titles = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            422: "Validation Error",
            429: "Too Many Requests",
            500: "Internal Server Error",
        }
        return titles.get(status_code, "Error")

    def _get_type_for_status(self, status_code: int) -> str:
        """Получить тип ошибки для HTTP статуса"""
        types = {
            400: "https://api.readinglist.com/errors/bad-request",
            404: "https://api.readinglist.com/errors/not-found",
            422: "https://api.readinglist.com/errors/validation-error",
            500: "https://api.readinglist.com/errors/internal-error",
        }
        return types.get(
            status_code, "https://api.readinglist.com/errors/generic-error"
        )
