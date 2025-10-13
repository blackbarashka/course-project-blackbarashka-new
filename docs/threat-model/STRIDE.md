# STRIDE — Угрозы и контрмеры (Reading List API)

| Поток/Элемент | Угроза (S/T/R/I/D/E) | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---|---|---|---|---|---|
| F1, F11, F13 | **S**poofing | Подмена клиента через отсутствие аутентификации | Rate limiting + IP блокировка при 100+ RPS | NFR-004 | tests/test_nfr_security.py |
| F1, F11, F13 | **T**ampering | Изменение данных книг в HTTP запросах | Pydantic валидация схем BookCreate/BookUpdate | NFR-005 | app/schemas/book.py |
| F1, F11, F13 | **I**nformation Disclosure | Утечка stack trace в ошибках API | Кастомные exception handlers | NFR-005 | tests/test_errors.py |
| F1, F11, F13 | **D**enial of Service | Flood запросов на создание книг | Rate limiting 10 POST/мин на endpoint | NFR-003 | tests/test_nfr_security.py |
| F3, F4 | **T**ampering | Инъекция через поля title/author | Sanitization строковых полей, валидация длины | NFR-005 | app/models/book.py |
| F5, F6 | **I**nformation Disclosure | Доступ ко всем книгам без ограничений | Пагинация GET запросов, лимиты выборки | NFR-006 | GET /api/v1/books |
| F5 | **T**ampering | Невалидируемое изменение статуса книги | Валидация переходов статусов (to_read→in_progress→completed) | NFR-005 | PATCH /api/v1/books/{id}/status |
| F10 | **R**epudiation | Отказ от операций с книгами | Логирование с correlation_id, timestamp | NFR-009 | app/database.py |
| F1, F11, F13 | **D**enial of Service | Атаки на доступность API через большие payloads | Лимит размера JSON (1MB) + timeout | NFR-004 | FastAPI конфигурация |
| F2, F8 | **T**ampering | Подмена внутренних API вызовов | Валидация данных между сервисами | NFR-005 | Internal API checks |
| F5, F6 | **I**nformation Disclosure | Утечка данных при дампе памяти | Очистка памяти при graceful shutdown | NFR-006 | app/database.py |
| F10 | **T**ampering | Изменение журналов аудита | Append-only логи, цифровые подписи | NFR-009 | Audit log protection |
| Все потоки | **I**nformation Disclosure | Утечка чувствительных данных в логах | Маскирование email/имен в логах | NFR-006 | Logging configuration |
| F1, F11, F13 | **D**enial of Service | Исчерпание памяти через множество книг | Мониторинг использования памяти, лимиты | NFR-004 | Memory monitoring |
| FastAPI App | **E**levation of Privilege | Доступ ко всем операциям без авторизации | Будущая реализация RBAC | NFR-002 | (planned) |

## Ключевые выводы по угрозам

### Критичные угрозы (требуют немедленного внимания):
1. **DoS через создание книг** - риск исчерпания памяти
2. **Инъекции в данные книг** - компрометация целостности данных
3. **Утечка stack trace** - раскрытие внутренней структуры

### Угрозы, покрытые текущими NFR:
- **NFR-005** защищает от Tampering и Information Disclosure
- **NFR-004** защищает от Denial of Service
- **NFR-006** защищает от утечки данных в логах
- **NFR-009** защищает от Repudiation

### Неприменимые угрозы для текущей архитектуры:
- **Spoofing через brute-force** (NFR-001) - нет аутентификации
- **Унификация auth ответов** (NFR-002) - нет аутентификации

## Рекомендации по верификации

### Существующие тесты:
- `tests/test_nfr_security.py` - проверка rate limiting
- `tests/test_errors.py` - проверка безопасных ошибок
- `tests/test_books.py` - проверка валидации данных

### Планируемые проверки:
- Нагрузочное тестирование для NFR-003, NFR-004
- Secret scanning для NFR-007
- SAST сканирование для NFR-008
