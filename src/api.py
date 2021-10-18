from flask import make_response, request
from flask_restful import Resource, Api
from flask_restful.representations.json import output_json
import xml.etree.ElementTree as ET

from src.drivers import Driver


class CustomApi(Api):
    """
    Custom flask_restful Api class for:
        - providing additional representation (xml)
        - output function to convert data (dicts) to xml strings
    """

    @staticmethod
    def output_xml(data: dict, code, headers: dict = None) -> "Response":
        """Make a Flask response with xml body (output function for xml representation, which we added in __init__)"""

        def dict_to_tree_recursive(src_dict: dict, root: ET.Element = None) -> ET.Element:
            """Convert the data dict to the etree.Element object (including all children) recursively.
            src_dict (data) is always a dict with a single key at the top level -- this is used as the root tag"""
            if root is None:
                src_top_key = next(iter(src_dict.keys()))
                root = ET.Element(src_top_key)

            for key, value in src_dict.items():
                child = ET.SubElement(root, key)
                if isinstance(value, dict):
                    dict_to_tree_recursive(value, child)
                else:
                    child.text = value
            return root[0]

        tree = dict_to_tree_recursive(data)
        xml_string = ET.tostring(tree, xml_declaration=True, encoding="utf-8")
        resp = make_response(xml_string)
        resp.headers.extend(headers or {})
        return resp

    def __init__(self, *args, **kwargs):
        """Register representation for xml"""
        super().__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
            'application/xml': __class__.output_xml,
        }


class DriversListApi(Resource):
    def get(self) -> dict:
        """Return the drivers list API.
        This docstring also contains all definitions of the API for flasgger (accessible at /apidocs/)

        ---
        parameters:
         - in: query
           name: format
           type: string
           enum: ['json', 'xml']
           required: false
           description: Specify which format the response will be in

        definitions:
          Driver:
            type: object
            properties:
               name:
                 type: string
                 description: The name of the driver
                 example: Brendon Hartley
               abbr:
                 type: string
                 description: The abbreviation of the driver
                 example: BHS
               team:
                 type: string
                 description: The team name of the driver
                 example: SCUDERIA TORO ROSSO HONDA
               start_time:
                 type: datetime
                 description: The start time of the driver
                 example: "12:14:51.985"
               stop_time:
                 type: datetime
                 description: The finish time of the driver
                 example: "12:16:05.164"
               best_lap_time:
                 type: timedelta
                 description: The best lap time of the driver
                 example: "0:01:13.179"
          Drivers:
            type: object
            properties:
                Drivers:
                    type: array
                    items:
                        $ref: '#/definitions/Driver'
          Report:
            type: object
            properties:
                Report:
                    type: array
                    items:
                        $ref: '#/definitions/Driver'

        responses:
         200:
           description: All drivers
           schema:
             $ref: '#/definitions/Drivers'
            """

        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        drivers_dic = {'drivers': {}}
        for ind, d in enumerate(Driver.all()):
            drivers_dic['drivers'].update({f'driver{ind + 1}': d.driver_info_dictionary()})
        return drivers_dic


class DriverApi(Resource):
    def get(self, driver_id):
        """Return the info about one particular driver API.

         ---
        parameters:
         - in: path
           name: driver_id
           type: string
           required: false
           description: driver id, abbreviation or name (full or partly)
           example: ham
         - in: query
           name: format
           type: string
           enum: ['json', 'xml']
           required: false
           description: Specify which format the response will be in
        responses:
         200:
           description: Driver
           schema:
             $ref: '#/definitions/Driver'
         404:
            description: A driver with the specified ID/abbr/name was not found
        """

        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        try:
            d = Driver.get_by_id(driver_id)[0].driver_info_dictionary()
            result_dic = {'driver': d}
        except IndexError:
            return {'error': f'driver \'{driver_id}\' not found'}, 404
        return result_dic


class ReportApi(Resource):
    def get(self) -> dict:
        """Return the report about the race.

         ---
        parameters:
         - in: query
           name: format
           type: string
           enum: ['json', 'xml']
           required: false
           description: Specify which format the response will be in

        responses:
         200:
           description: Report
           schema:
             $ref: '#/definitions/Report'
        """
        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        asc_order = True
        report_dic = {'report': {}}
        drivers = Driver.all()
        drivers.sort(key=lambda d: d.best_lap)
        for ind, d in enumerate(drivers):
            report_dic['report'].update({f'place{ind + 1}': d.driver_info_dictionary()})
        return report_dic
