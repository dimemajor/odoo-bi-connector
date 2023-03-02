import pandas as pd
from xmlrpc import client


def connect():
    common = client.ServerProxy("%s/xmlrpc/2/common" % options['url'])
    uid = common.authenticate(options['db'], options['user'], options['password'], {})
    if not uid:
        raise NameError
    return uid

def get_options():
    options={}
    return options

def get_company_data(api):
    fields = [
        'id',
        'display_name',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "res.company", "search_read", [], {"domain": [], "fields": fields}) # get all orders within specified period
    companies = pd.DataFrame(data)
    return companies

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    company_data = get_company_data(api)
    return company_data

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
DimCompanies = get_data()