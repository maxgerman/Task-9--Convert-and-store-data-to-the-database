import pathlib
# import logging
import pytest
from contextlib import contextmanager
from flask import template_rendered
import peewee

from src.drivers import Driver
from src.app import app
import src.database as database

# test data files
DATA_PATH = 'test_data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'
TEST_DB = pathlib.Path(DATA_PATH) / 'test_racing.db'


# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


@pytest.fixture
def client():
    """Client used for testing"""
    app.testing = True
    return app.test_client()


@pytest.fixture
def build_report():
    """Build report for rendering pages and APIs before testing"""
    return Driver.build_report(data_path=DATA_PATH)


@contextmanager
def captured_templates(app):
    """Provides access to the rendered template name and context dict from the tests"""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def test_db_ctx():
    """Bind all models queries to test db (tests/test_racing.db) instead of the main one"""
    db = peewee.SqliteDatabase(TEST_DB)
    ctx = db.bind_ctx([database.Team, database.Driver])
    db.connect(reuse_if_open=True)
    yield ctx
    db.close()


@pytest.fixture
def empty_db():
    """Create in-memory db and bind existing models to it"""
    db = peewee.SqliteDatabase(':memory:')
    models = [database.Team, database.Driver]
    db.bind(models)
    db.create_tables(models)
    db.connect(reuse_if_open=True)
    yield db
    db.close()
