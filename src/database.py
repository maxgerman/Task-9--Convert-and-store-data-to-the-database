import os
import sys
import peewee
from app import app

DATABASE = 'racing.db'

db = peewee.SqliteDatabase(DATABASE)




@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


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


def create_db(filename=DATABASE, db=db):
    if os.path.exists(filename):
        raise SystemExit('Error. Database file already exists. Use -r to rebuild database')
    with db:
        db.create_tables([Driver, Team])


def delete_old_db_file(filename=DATABASE, verbose=False):
    if os.path.exists(db.database):
        if not input('Delete old version file: ' + os.path.abspath(db.database) + '\n(y/n)? \n') == 'y':
            print('Exiting')
            sys.exit(1)
        else:
            try:
                os.remove(db.database)
            except OSError as err:
                print('Error deleting old db file.', err)
                sys.exit(1)
            if verbose:
                print('Removed old db file:', os.path.abspath(db.database))
