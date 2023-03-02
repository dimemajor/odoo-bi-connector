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

def get_product_categories(api):
    fields = [
        'id',
        'display_name',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "product.category", "search_read", [], {"domain": [], "fields": fields}) # get all orders within specified period
    categories = pd.DataFrame(data)
    return categories

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    product_categories = get_product_categories(api)
    return product_categories

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
DimCategories = get_data()