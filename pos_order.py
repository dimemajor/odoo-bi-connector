import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
from xmlrpc import client

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

def get_options():
    options={}
    return options

def chunks():
    chunk_interval = int(options['chunk_interval'])
    date = options['inception']

    next_date = dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    datediff = dt.datetime.today() - next_date
    df = pd.DataFrame()

    while datediff.days > chunk_interval:
        start_date = f'{next_date:%Y-%m-%d %H:%M:%S}'
        next_date = next_date+relativedelta(days=+chunk_interval)
        end_date = f'{next_date:%Y-%m-%d %H:%M:%S}'
        pos_order_lines = get_data(start_date, end_date)
        datediff = dt.datetime.today() - next_date
        df = pd.concat([df, pos_order_lines], ignore_index=True)
    else:
        start_date = f'{next_date:%Y-%m-%d %H:%M:%S}'
        end_date = f'{dt.datetime.today():%Y-%m-%d %H:%M:%S}'
        pos_order_lines = get_data(start_date, end_date)
        df = pd.concat([df, pos_order_lines], ignore_index=True)
    return df

def connect():
    common = client.ServerProxy("%s/xmlrpc/2/common" % options['url'])
    uid = common.authenticate(options['db'], options['user'], options['password'], {})
    if not uid:
        raise NameError
    return uid

def get_pos_sales(api, start_date, end_date):
    domain = ['&', 
        ('date_order', '>=', start_date), 
        ('date_order', '<=', end_date),
        ('state', 'in', ['paid', 'done']),
        ]
    fields = [
        'id',
        'date_order',
        'employee_id',
    ]
    data = api.execute_kw(options['db'], uid, options['password'],'pos.order', "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period
    orders = pd.DataFrame(data)

    # modify many2one fields that return a list
    orders['employee_id'] = orders['employee_id'].apply(replace, args=[0])
    orders.rename(columns={'id': 'order_id'}, inplace=True)
    return orders

def get_data(start_date, end_date):
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    orders = get_pos_sales(api, start_date, end_date)
    return orders

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
FactPosOrders = chunks()