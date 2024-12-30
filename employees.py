import pandas as pd
from xmlrpc import client


def connect():
    common = client.ServerProxy("%s/xmlrpc/2/common" % options['url'])
    uid = common.authenticate(options['db'], options['user'], options['password'], {})
    if not uid:
        raise NameError
    return uid

def get_options():
    options={
                'url': 'localhost:8069',
            'user': 'admin',
            'password': 'admin',
            'db': 'testdb',
            'chunk_interval': 30,
            'inception': '2022-10-01 00:00:00'
    }
    return options

def get_emplyoee_data(api):
    fields = [
        'id',
        'name',
        'job_title',
        'work_email',
    ]
    domain = [
        ('active', 'in', [True, False])
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "hr.employee", "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period
    employees = pd.DataFrame(data)
    return employees

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    emplyoee_data = get_emplyoee_data(api)
    return emplyoee_data

options = get_options()
if not options:
    options = {
        'url': '"&Url&"',
        'db': '"&DatabaseName&"', 
        'user': '"&User&"',
        'password': '"&Password&"',
        'chunk_interval': '"&ChunkInterval&"', 
        'inception': '"&StartDate&"'
    }
uid = connect()
DimEmployees = get_data()
