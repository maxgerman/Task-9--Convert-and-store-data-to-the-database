import argparse
import os.path

from flask import Flask, render_template, request, redirect, url_for, session
from flasgger import Swagger
from wikipedia import wikipedia

from drivers import Driver
from utils import wiki
from api import CustomApi, DriverApi, DriversListApi, ReportApi
import database as database

app = Flask(__name__)
app.secret_key = 'dev'

api = CustomApi(app)
swagger = Swagger(app)


@app.route('/report', methods=['GET', 'POST'])
def common_report() -> "Response":
    """
    Show the report for all drivers.
    Sort and set the order switch based on url for the template. 
    """
    if request.args.get('order') == 'desc':
        asc_order = False
    else:
        asc_order = True
    session['report_desc_switch'] = not asc_order

    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['report_desc_switch'] = True
            return redirect(url_for('common_report', order='desc'))
        else:
            session['report_desc_switch'] = False
            return redirect(url_for('common_report'))

    lines = Driver.print_report(asc=asc_order).split('\n') if Driver.print_report() else []
    return render_template('report.html', lines=lines)


@app.route('/drivers', methods=['GET', 'POST'])
def list_drivers() -> "Response":
    """Show ordered driver list as 'name - abbreviation' """
    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['driver_desc_switch'] = True
            return redirect(url_for('list_drivers', order='desc'))
        else:
            session['driver_desc_switch'] = False
            return redirect(url_for('list_drivers'))

    driver_id = request.args.get('driver_id')
    driver_info = ''
    if driver_id:
        drivers = Driver.get_by_id(driver_id)
        try:
            driver_info = wiki(drivers[0].name)
        except (TypeError, IndexError, wikipedia.PageError):
            driver_info = None
    else:
        asc_order = False if request.args.get('order') == 'desc' else True
        session['driver_desc_switch'] = not asc_order
        drivers = Driver.all(asc=asc_order)
    return render_template('drivers.html', drivers=drivers, driver_info=driver_info)


@app.route('/')
def home() -> "Response":
    return redirect(url_for('common_report'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('base.html', error=404)


@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', context=500)


api.add_resource(DriversListApi, '/api/v1/drivers/')
api.add_resource(DriverApi, '/api/v1/drivers/<driver_id>/')
api.add_resource(ReportApi, '/api/v1/report/')

parser = argparse.ArgumentParser('Drivers statistics and reports')
parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuild drivers database from data files')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')

if __name__ == '__main__':
    args = parser.parse_args()
    if args.rebuild or not os.path.exists(database.db.database):
        Driver.build_report()
        database.delete_old_db_file(verbose=args.verbose)
        database.create_db()
        Driver.save_teams_to_db(db=database.db, team_table=database.Team, verbose=args.verbose)
        Driver.save_drivers_to_db(db=database.db, driver_table=database.Driver, team_table=database.Team, verbose=args.verbose)
    app.run()
