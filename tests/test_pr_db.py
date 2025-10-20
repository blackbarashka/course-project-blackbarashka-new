import importlib

import pytest


def test_sqlalchemy_crud(tmp_path, monkeypatch):
    pytest.importorskip("sqlalchemy")

    monkeypatch.setenv("USE_SQL_DB", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    import sys

    sys.modules.pop("app.storage.orm", None)
    sys.modules.pop("app.storage.db", None)
    sys.modules.pop("app.database", None)

    dbmod = importlib.import_module("app.storage.db")
    orm_mod = importlib.import_module("app.storage.orm")

    try:
        orm_mod.Base.metadata.drop_all(bind=dbmod.engine)
    except Exception:
        pass

    # Попытка явно создать схему; в редких случаях sqlite может выбросить
    # OperationalError если индекс/таблица уже существует (например при
    # некорректных re-import). В этом тесте — игнорируем эту ошибку.
    try:
        orm_mod.Base.metadata.create_all(bind=dbmod.engine)
    except Exception as exc:
        # лениво проверяем текст ошибки — если это ошибка "index already exists",
        # считаем её не критичной
        import sqlalchemy

        if isinstance(exc, sqlalchemy.exc.OperationalError):
            msg = str(exc).lower()
            if "index" in msg and "already exists" in msg:
                pass
            else:
                raise
        else:
            raise

    database_mod = importlib.import_module("app.database")

    db = database_mod.db

    created = db.create_book(title="SQL Book", author="Author", description="Desc")
    assert created.id is not None
    assert created.title == "SQL Book"

    fetched = db.get_book_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "SQL Book"

    updated = db.update_book(created.id, title="Updated Title")
    assert updated is not None
    assert updated.title == "Updated Title"

    deleted = db.delete_book(created.id)
    assert deleted is True

    assert db.get_book_by_id(created.id) is None
