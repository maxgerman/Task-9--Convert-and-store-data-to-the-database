import os
import datetime as dt

DATA_PATH = '../data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'


class Driver:
    """
        A class to represent a driver.

        Attributes
        ----------

        _driver_list : list
            list of driver objects
        abbr : str
            name abbreviation as in abbreviation file
        name : str
            driver's name
        team : str
            driver's team
        start_time : datetime
            start time of the lap
        stop_time : datetime
            finish time of the lap
        best_lap : timedelta
            time of the best lap

        Methods
        -------
        statistics : str
            Return the pretty string with the driver's statistics
        build_report : list
            Build report from logs, return complete list of drivers with info

            _drivers_from_abbr : list
                Return the list of drivers from data files
            _parse_logs : list
                Return the list of drivers with updated times from parsing of log files

        print_report : str
            Return the statistics of all or one driver
        all : list
            Return the list of driver objects
        get_by_id : list
            Return the list of one driver object (by id or name)
        """

    _driver_list = []

    def __init__(self, abbr=None, name=None, team=None, start_time=None, stop_time=None,
                 best_lap=None):
        self.abbr = abbr
        self.name = name
        self.team = team
        self.start_time = start_time
        self.stop_time = stop_time
        self.best_lap = best_lap

    def __repr__(self):
        return f'Driver ({self.__dict__})'

    def statistics(self) -> str:
        return '{:<20} | {:<25} | {}'.format(self.name, self.team, str(self.best_lap)[:-3])

    @staticmethod
    def _drivers_from_abbr(data_path: str = DATA_PATH, abbr_file=ABBR_FILE) -> list:
        """
        Return the list of driver instances each with their name, abbreviation and team parsed from the
        data_path/ABBR_FILE
        """
        drivers = []
        with open(os.path.join(data_path, abbr_file), 'r', encoding='UTF-8') as f:
            for line in f:
                abbr, name, team = line.split('_')
                new_driver = Driver(abbr=abbr, name=name, team=team.rstrip())
                drivers.append(new_driver)
        return drivers

    @staticmethod
    def _parse_logs(drivers: list, data_path: str = DATA_PATH) -> list:
        """
        Return the copy of drivers list with updated start and finish times from the parsing of the logs
        in 'data_path'
        """
        result_drivers = drivers[:]
        with open(os.path.join(data_path, START_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = (line for line in f if line.strip())
            for line in lines:
                abbr, start_time = line[:3], line.split('_')[1].rstrip()
                for driver in result_drivers:
                    if driver.abbr == abbr:
                        driver.start_time = dt.datetime.strptime(start_time, "%H:%M:%S.%f")
                        break
        with open(os.path.join(data_path, END_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = (line for line in f if line.strip())
            for line in lines:
                abbr, stop_time = line[:3], line.split('_')[1].rstrip()
                for driver in result_drivers:
                    if driver.abbr == abbr:
                        driver.stop_time = dt.datetime.strptime(stop_time, "%H:%M:%S.%f")
                        break
        return result_drivers

    @staticmethod
    def build_report(data_path: str = DATA_PATH, abbr_file: str = ABBR_FILE) -> list:
        """
        Build the report based on files of name abbreviations and time logs in DATA_PATH. Calculate best lap time for
        each driver. Return the list of drivers.
        """
        drivers = Driver._drivers_from_abbr(data_path, abbr_file)
        drivers = Driver._parse_logs(drivers, data_path)
        for driver in drivers:
            if driver.start_time > driver.stop_time:
                driver.start_time, driver.stop_time = driver.stop_time, driver.start_time
            driver.best_lap = driver.stop_time - driver.start_time
        Driver._driver_list = drivers
        return drivers

    @staticmethod
    def print_report(asc: bool = True, driver_query: str = None) -> str:
        """
        Pretty print the report of drivers statistics.
        Sorted by best lap time.
        Optionally, search for only one driver by name or abbr.


        Parameters:
        drivers - list of drivers built by 'build_report' function.
        asc - ascending order if True
        driver_query - if set, print the report of this only driver
        """

        if not Driver._driver_list:
            return ''

        if driver_query:
            for d in Driver._driver_list:
                if driver_query.lower() in d.name.lower() or driver_query.lower() in d.abbr.lower():
                    return d.statistics()
            else:
                return 'Driver not found'
        else:
            sorted_drivers = sorted(Driver._driver_list, key=lambda dr: dr.best_lap)
            res_table = ['{:2d}. '.format(i + 1) + driver.statistics() for i, driver in enumerate(sorted_drivers)]
            if asc:
                res_table.insert(15, '-' * 60)
            else:
                res_table.reverse()
            report = '\n'.join(res_table)
            return report

    @staticmethod
    def all(asc=True) -> list:
        """Return the list of drivers in requested order"""
        Driver._driver_list.sort(key=lambda d: d.name, reverse=not asc)
        return Driver._driver_list

    @staticmethod
    def get_by_id(driver_id) -> list:
        """Return the list with driver object by id or name. Return empty list if not found"""
        for d in Driver._driver_list:
            if driver_id.lower() in d.name.lower() or driver_id.lower() in d.abbr.lower():
                return [d]
        else:
            return []

    def driver_info_dictionary(self):
        """Return the driver info as a dictionary. Used for api"""
        return {
            'name': self.name,
            'abbr': self.abbr,
            'team': self.team,
            'start_time': self.start_time.strftime('%H:%M:%S.%f')[:-3],
            'stop_time': self.stop_time.strftime('%H:%M:%S.%f')[:-3],
            'best_lap_time': str(self.best_lap)[:-3],
        }
