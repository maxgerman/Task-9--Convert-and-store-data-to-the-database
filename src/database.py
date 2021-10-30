"""
This module defines peewee ORM models for database and contains some utility functions.
"""

import os
import sys
import peewee

DATABASE = '../data/racing.db'
db = peewee.SqliteDatabase(DATABASE)


class BaseModel(peewee.Model):
    """Base model for app models (will have same db)"""

    class Meta:
        database = db


class Team(BaseModel):
    """Team table with team names"""
    name = peewee.CharField(unique=True)


class Driver(BaseModel):
    """Driver table with all info and foreign key to Team table"""
    name = peewee.CharField(unique=True)
    abbr = peewee.CharField(unique=True)
    team = peewee.ForeignKeyField(Team, backref='drivers')
    start_time = peewee.CharField()
    stop_time = peewee.CharField()
    best_lap = peewee.CharField()


def create_db_tables(filename: str = DATABASE, db: peewee.SqliteDatabase = db) -> None:
    """Create tables in db if db is not created yet"""
    if os.path.exists(filename):
        raise SystemExit('Error. Database file already exists. Use -r to rebuild database')
    with db:
        db.create_tables([Team, Driver])


def delete_old_db_file(verbose: bool = False) -> None:
    """Delete old db file if rebuilding db (on first start or by -r switch)"""
    if os.path.exists(db.database):
        if not input('Delete old version file: ' + os.path.abspath(db.database) + '\n(y/n)? \n') == 'y':
            print('Exiting')
            sys.exit(0)
        else:
            try:
                os.remove(db.database)
            except OSError as err:
                print('Error deleting old db file.', err)
                sys.exit(1)
            if verbose:
                print('Removed old db file:', os.path.abspath(db.database))
