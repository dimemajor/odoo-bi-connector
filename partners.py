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

def get_partner_data(api, options):
    fields = [
        'id',
        'display_name',
        'phone',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "res.partner", "search_read", [], {"domain": [], "fields": fields}) # get all orders within specified period
    partners = pd.DataFrame(data)
    return partners

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    partner_data = get_partner_data(api)
    return partner_data

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
DimPartners = get_data()