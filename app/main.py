import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.endpoints import books
from app.middleware.error_handler import ErrorHandlerMiddleware

app = FastAPI(title="SecDev Course App", version="0.1.0")

# Настройка логгера по умолчанию для аудита
logging.basicConfig(level=logging.INFO)


app.add_middleware(ErrorHandlerMiddleware)

# используем встроенные exception handlers


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации в формате RFC 7807"""
    correlation_id = str(uuid.uuid4())

    problem_details = {
        "type": "https://api.readinglist.com/errors/validation-error",
        "title": "Validation Error",
        "status": 422,
        "detail": "Request validation failed",
        "instance": request.url.path,
        "correlation_id": correlation_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logging.getLogger("app.audit").info("AUDIT_ERROR: %s", problem_details)
    return JSONResponse(status_code=422, content=problem_details)


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    """Обработчик 404 ошибок в формате RFC 7807"""
    correlation_id = str(uuid.uuid4())

    problem_details = {
        "type": "https://api.readinglist.com/errors/not-found",
        "title": "Resource Not Found",
        "status": 404,
        "detail": "The requested resource was not found",
        "instance": request.url.path,
        "correlation_id": correlation_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logging.getLogger("app.audit").info("AUDIT_ERROR: %s", problem_details)
    return JSONResponse(status_code=404, content=problem_details)


@app.exception_handler(500)
async def internal_error_exception_handler(request: Request, exc: Exception):
    """Обработчик 500 ошибок в формате RFC 7807"""
    correlation_id = str(uuid.uuid4())

    problem_details = {
        "type": "https://api.readinglist.com/errors/internal-error",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An internal server error occurred",
        "instance": request.url.path,
        "correlation_id": correlation_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logging.getLogger("app.audit").info("AUDIT_ERROR: %s", problem_details)
    return JSONResponse(status_code=500, content=problem_details)


# Подключаем роутеры для книг
app.include_router(books.router)


@app.get("/health")
def health():
    return {"status": "ok"}


_DB = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        # Вызываем ошибку валидации
        raise RequestValidationError(errors=[])
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    # Вызываем 404 ошибку
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="item not found")
