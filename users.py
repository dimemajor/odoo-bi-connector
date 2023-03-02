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
    }
    return options

def get_user_data(api):
    fields = [
        'id',
        'display_name',
        'phone',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "res.users", "search_read", [], {"domain": [], "fields": fields}) # get all orders within specified period
    users = pd.DataFrame(data)
    return users

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    user_data = get_user_data(api)
    return user_data


options = get_options()
if not options:
    options = {
        'url': "&Url&",
        'db': "&Database Name&", 
        'user': "&User&",
        'password': "&Password&",
        'chunk_interval': "&Chunk Interval&", 
        'inception': "&Start Date&"
    }

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
DimUsers = get_data()
