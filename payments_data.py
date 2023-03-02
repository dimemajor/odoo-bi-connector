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

def get_payment_data(api, start_date, end_date):
    domain = [
        ('payment_date', '>=', start_date), 
        ('payment_date', '<=', end_date),
        ]
    fields = [
        'id',
        'pos_order_id',
        'amount',
        'payment_method_id',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "pos.payment", "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period
    payments = pd.DataFrame(data)

    # modify many2one fields that return a list
    payments['pos_order_id'] = payments['pos_order_id'].apply(replace, args=[0])
    payments['payment_method_id'] = payments['payment_method_id'].apply(replace)
    payments.rename(columns={
        'id': 'payment_id',
        }, 
        inplace=True)
    return payments

def get_data(start_date, end_date):
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    payments = get_payment_data(api, start_date, end_date)
    return payments

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
FactPosPayments = chunks()