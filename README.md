# Reading List API

Веб-приложение для управления списком чтения книг с REST API на FastAPI.

**Автор**: Мусаев Умахан Рашидович. БПИ234.

## Описание

Reading List API - это веб-приложение для управления списком книг к прочтению. Приложение предоставляет REST API для работы с книгами.

## Требования

- Python 3.11+
- Docker и Docker Compose (для контейнеризованного запуска)

## Быстрый старт

### Запуск через Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd course-project-blackbarashka
```

2. Запустите приложение:
```bash
docker compose up --build
```

3. Приложение будет доступно по адресу:
   - API: http://localhost:8000
   - Документация API: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Локальная установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

3. Запустите приложение:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker

Приложение контейнеризировано с использованием multi-stage build. Для запуска используйте:

```bash
docker compose up --build
```

Подробности о конфигурации Docker см. в `Dockerfile` и `compose.yaml`.

## API Документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Основные эндпоинты

- `GET /api/v1/books/` - Получить список всех книг
- `POST /api/v1/books/` - Создать новую книгу
- `GET /api/v1/books/{book_id}` - Получить книгу по ID
- `PUT /api/v1/books/{book_id}` - Обновить информацию о книге
- `PATCH /api/v1/books/{book_id}/status` - Изменить статус книги
- `DELETE /api/v1/books/{book_id}` - Удалить книгу
- `GET /api/v1/books/search?q={query}` - Поиск книг
- `GET /health` - Health check endpoint

## Тестирование

Запуск тестов:
```bash
pytest -q
```

## Структура проекта

```
course-project-blackbarashka/
├── app/                    # Основной код приложения
│   ├── api/               # API эндпоинты
│   ├── middleware/        # Middleware
│   ├── models/           # Модели данных
│   ├── schemas/          # Pydantic схемы
│   ├── storage/          # Хранилище данных
│   └── main.py           # Точка входа приложения
├── tests/                # Тесты
├── Dockerfile            # Docker образ
├── compose.yaml          # Docker Compose конфигурация
├── .dockerignore         # Исключения для Docker build
└── requirements.txt      # Зависимости
```

## Дополнительная документация

- `SECURITY.md` - Политика безопасности
- `.github/workflows/ci.yml` - CI/CD конфигурация
