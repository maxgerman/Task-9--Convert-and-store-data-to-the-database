import datetime as dt

from src.drivers import Driver
from .conftest import DATA_PATH


def test_drivers_from_abbr():
    """Test that driver objects are created from the abbr file, their count and properties"""
    drivers = Driver._drivers_from_abbr(data_path=DATA_PATH)
    assert len(drivers) == 19
    for d in drivers:
        assert isinstance(d, Driver)
        assert d.name is not None
        assert d.abbr is not None
        assert d.team is not None


def test_parse_logs():
    """Test that start and stop times (datetime objects) are added to driver objects"""
    drivers = Driver._drivers_from_abbr(data_path=DATA_PATH)
    drivers = Driver._parse_logs(drivers, data_path=DATA_PATH)
    for d in drivers:
        assert isinstance(d.start_time, dt.datetime)
        assert isinstance(d.stop_time, dt.datetime)


def test_build_report():
    """Ensure that test files have logs with start time > stop time.
    Test that these are replaced with each other after building report """
    drivers = Driver._drivers_from_abbr(data_path=DATA_PATH)
    drivers = Driver._parse_logs(drivers, data_path=DATA_PATH)

    swapped_times_detected = False
    for d in drivers:
        if d.start_time > d.stop_time:
            swapped_times_detected = True
            break
    assert swapped_times_detected

    drivers = Driver.build_report(data_path=DATA_PATH)
    for d in drivers:
        assert d.start_time < d.stop_time


def test_all():
    """Test that Driver.all() method returns the list of all drivers"""
    Driver.build_report(data_path=DATA_PATH)
    assert len(Driver.all()) == 19
    for d in Driver.all():
        assert isinstance(d, Driver)
        assert d.name is not None
        assert d.abbr is not None
        assert d.team is not None
        assert d.best_lap is not None
        assert d.best_lap is not None


def test_all_ascending():
    """Test that Driver.all() method returns list sorted ascending in alphabetical order"""
    Driver.build_report(data_path=DATA_PATH)
    prev = 'a'
    for d in Driver.all(asc=True):
        assert d.name[0].lower() >= prev
        prev = d.name[0].lower()


def test_all_descending():
    """Test that Driver.all(asc=False) method returns list sorted DESCENDING in alphabetical order"""
    Driver.build_report(data_path=DATA_PATH)
    prev = 'z'
    for d in Driver.all(asc=False):
        assert d.name[0].lower() <= prev
        prev = d.name[0].lower()


def test_get_by_id():
    """Test that method returns driver object by id or name or empty list returns"""
    Driver.build_report(data_path=DATA_PATH)
    assert Driver.get_by_id('unknown') == []
    assert Driver.get_by_id('KRF')[0].name == 'Kimi Räikkönen'
    assert Driver.get_by_id('fernan')[0].name == 'Fernando Alonso'
