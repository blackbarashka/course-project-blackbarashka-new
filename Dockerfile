# Build stage
FROM python:3.11.9-slim AS build
WORKDIR /build

# Установка зависимостей для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Копируем только файлы зависимостей для оптимизации кэша слоев
COPY requirements.txt requirements-dev.txt ./

# Устанавливаем все зависимости (включая dev для тестов)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Копируем код приложения
COPY . .

# Запускаем тесты
RUN pytest -q

# Runtime stage
FROM python:3.11.9-slim AS runtime
WORKDIR /app

# Создаем non-root пользователя
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Копируем только production зависимости из build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Копируем только необходимые файлы приложения
COPY --chown=appuser:appuser app/ ./app/

# Устанавливаем рабочую директорию и пользователя
WORKDIR /app
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:$PATH"

# Открываем порт
EXPOSE 8000

# Healthcheck без curl (используем python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Явный ENTRYPOINT и CMD
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
