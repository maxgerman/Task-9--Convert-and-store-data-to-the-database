import pytest
from contextlib import contextmanager
from flask import template_rendered

from src.drivers import Driver
from src.app import app


# test data files
DATA_PATH = 'test_data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'


@pytest.fixture
def client():
    """Client used for testing"""
    app.testing = True
    return app.test_client()


@pytest.fixture
def build_report():
    """Build report for rendering pages and APIs before testing"""
    Driver.build_report(data_path=DATA_PATH)


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