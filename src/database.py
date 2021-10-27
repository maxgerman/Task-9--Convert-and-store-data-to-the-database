import os
import sys
import peewee

DATABASE = 'racing.db'

db = peewee.SqliteDatabase(DATABASE)
print('imported db module!!')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Team(BaseModel):
    name = peewee.CharField(unique=True)


class Driver(BaseModel):
    name = peewee.CharField(unique=True)
    abbr = peewee.CharField(unique=True)
    team = peewee.ForeignKeyField(Team, backref='drivers')
    start_time = peewee.CharField()
    stop_time = peewee.CharField()
    best_lap = peewee.CharField()


def create_db_tables(filename=DATABASE, db=db):
    if os.path.exists(filename):
        raise SystemExit('Error. Database file already exists. Use -r to rebuild database')
    with db:
        db.create_tables([Team, Driver])


def delete_old_db_file(filename=DATABASE, verbose=False):
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
