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

def replace(cell, index=1):
    '''
    to replace many2one fields that
    return a list of the id and name
    with just the id of the related field  
    '''
    if cell:
        cell = list(cell)
        try:
            cell = cell[index]
        except:
            try:
                cell = cell[0]
            except:
                return None
    return cell

def get_products(api):
    domain = [
        ('active', 'in', [True, False]),
        ]
    fields = [
        'id',
        'display_name',
        'categ_id',
        'active',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "product.product", "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period
    products = pd.DataFrame(data)

    # modify many2one fields that return a list
    products['categ_id'] = products['categ_id'].apply(replace)
    products.rename(columns={
        'id': 'product_id',
        'categ_id': 'category'
        }, 
        inplace=True)
    return products

def get_data():
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    products = get_products(api)
    return products

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
DimProducts = get_data()