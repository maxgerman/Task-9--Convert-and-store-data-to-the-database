import datetime as dt

import database
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


def test_all(test_db_ctx):
    """Test that Driver.all() method returns the list of all drivers. Using test db file"""
    with test_db_ctx:
        assert len(Driver.all()) == 19
        for d in Driver.all():
            assert isinstance(d, Driver)
            assert d.name is not None
            assert d.abbr is not None
            assert d.team is not None
            assert d.best_lap is not None
            assert d.best_lap is not None


def test_all_ascending(test_db_ctx):
    """Test that Driver.all() method returns list sorted ascending in alphabetical order. Using test db file """
    with test_db_ctx:
        prev = 'a'
        for d in Driver.all(asc=True):
            assert d.name[0].lower() >= prev
            prev = d.name[0].lower()


def test_all_descending(test_db_ctx):
    """Test that Driver.all(asc=False) method returns list sorted DESCENDING in alphabetical order.
    Using test db file"""
    with test_db_ctx:
        prev = 'z'
        for d in Driver.all(asc=False):
            assert d.name[0].lower() <= prev
            prev = d.name[0].lower()


def test_get_by_id(test_db_ctx):
    """Test that method returns driver object by id or name or empty list returns. Using test db file"""
    with test_db_ctx:
        assert Driver.get_by_id('unknown') == []
        assert Driver.get_by_id('KRF')[0].name == 'Kimi Räikkönen'
        assert Driver.get_by_id('fernan')[0].name == 'Fernando Alonso'


def test_create_driver_from_queryset(empty_db):
    """Test that driver object is created from the db entry and all fields are filled by data.
    Requires a team in db"""
    empty_db.bind([database.Team, database.Driver])
    sample_team = database.Team.create(name='Team1')
    qs = database.Driver(
        name='Joe',
        abbr='abc',
        team=sample_team,
        start_time='12:00',
        stop_time='12:01',
        best_lap='01:00:00'
    )
    d = Driver.create_driver_from_queryset(qs)
    assert isinstance(d, Driver)
    assert all((d.name, d.abbr, d.team, d.start_time, d.stop_time, d.best_lap))


def test_save_teams_to_db(empty_db):
    """Test that teams (parsed from data files) are saved to db (into separate table)"""
    Driver.build_report(data_path=DATA_PATH)
    empty_db.bind([database.Team, database.Driver])
    Driver.save_teams_to_db(database.Team)
    assert database.Team.select().count() == 10
    sample_teams = ['SCUDERIA TORO ROSSO HONDA', 'MERCEDES', 'FERRARI']
    for team in sample_teams:
        assert team in [team.name for team in database.Team.select()]


def test_save_drivers_to_db(empty_db):
    """Test that drivers (parsed from data files) are saved to db. Includes saving teams table first"""
    Driver.build_report(data_path=DATA_PATH)
    empty_db.bind([database.Team, database.Driver])
    Driver.save_teams_to_db(database.Team)
    Driver.save_drivers_to_db(database.Driver, database.Team)
    for d in database.Driver.select():
        assert all((d.name, d.team, d.abbr, d.start_time, d.stop_time, d.best_lap))
    assert database.Driver.select().count() == 19
