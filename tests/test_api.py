import json
from xml.etree import ElementTree as ET


def test_report_status_code(build_report, client):
    r = client.get('/api/v1/report/')
    assert r.status_code == 200


def test_report_format_default_json(build_report, client):
    r = client.get('/api/v1/report/')
    assert r.content_type == "application/json"


def test_report_format_json(build_report, client):
    r = client.get('/api/v1/report/?format=json')
    assert r.content_type == "application/json"


def test_report_format_xml(build_report, client):
    r = client.get('/api/v1/report/?format=xml')
    assert r.content_type == "application/xml"


def test_report_data_json(build_report, client):
    r = client.get('/api/v1/report/')
    data_str = r.data.decode('utf-8')
    dic = json.loads(data_str)
    assert len(dic) == 1
    assert len(dic['report']) == 19
    for d in dic['report']:
        assert dic['report'][d]['name'] is not None
        assert dic['report'][d]['abbr'] is not None
        assert dic['report'][d]['team'] is not None
        assert dic['report'][d]['start_time'] is not None
        assert dic['report'][d]['stop_time'] is not None
        assert dic['report'][d]['best_lap_time'] is not None


def test_report_data_xml(build_report, client):
    r = client.get('/api/v1/report/?format=xml')
    data_str = r.data.decode('utf-8')
    xml_tree = ET.fromstring(data_str)
    assert xml_tree.tag == 'report'
    assert len(xml_tree.findall('./')) == 19
    for d in xml_tree.findall('./'):
        d.find('name').text is not None
        d.find('abbr').text is not None
        d.find('team').text is not None
        d.find('start_time').text is not None
        d.find('stop_time').text is not None
        d.find('best_lap_time').text is not None


def test_drivers_status_code(build_report, client):
    r = client.get('/api/v1/drivers/')
    assert r.status_code == 200


def test_drivers_list_data(build_report, client):
    r = client.get('/api/v1/drivers/')
    drivers_dic = json.loads(r.data.decode('utf-8'))
    assert len(drivers_dic['drivers']) == 19


def test_driver_search_success(build_report, client):
    r = client.get('/api/v1/drivers/ham/')
    assert r.status_code == 200
    driver_dic = json.loads(r.data.decode('utf-8'))
    assert driver_dic == {
        "driver": {
            "name": "Lewis Hamilton",
            "abbr": "LHM",
            "team": "MERCEDES",
            "start_time": "12:11:32.585",
            "stop_time": "12:18:20.125",
            "best_lap_time": "0:06:47.540"
        }
    }


def test_driver_search_not_found(build_report, client):
    r = client.get('/api/v1/drivers/unknown_driver/')
    assert r.status_code == 404
