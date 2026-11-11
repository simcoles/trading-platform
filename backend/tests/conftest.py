from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url
from sqlalchemy.orm import Session

from backend.auth import User, get_current_user
from backend.config import settings
from backend.db import get_session
from backend.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]

# Same server and credentials as the app, but a separate "<name>_test" database
_app_url = make_url(settings.database_url)
TEST_DATABASE_URL = _app_url.set(database=f"{_app_url.database}_test")

# Most tests are about trading, not login, so they run as a signed-in trader
TEST_TRADER = User(sub="test-trader", username="trader", roles=frozenset({"trader"}))


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    alembic_config = Config(BACKEND_DIR / "alembic.ini")
    alembic_url = TEST_DATABASE_URL.render_as_string(hide_password=False).replace(
        "%", "%%"
    )
    alembic_config.set_main_option("sqlalchemy.url", alembic_url)
    command.upgrade(alembic_config, "head")
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(engine: Engine) -> Iterator[Session]:
    with engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        yield session
        session.close()
        transaction.rollback()


@pytest.fixture()
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: TEST_TRADER
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
