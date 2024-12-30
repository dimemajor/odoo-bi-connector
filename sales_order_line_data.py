import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
from xmlrpc import client
#from config import get_options

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
    options = {
        'url': 'localhost:8069',
        'user': 'admin',
        'password': 'admin',
        'db': 'testdb',
        'chunk_interval': 30,
        'inception': '2022-10-01 00:00:00'
        }
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
    domain = [
        '&', 
        ('date_order', '>=', start_date), 
        ('date_order', '<=', end_date),
        ('state', 'in', ['sale']),
        ]
    fields = [
        'id',
        'date_order',
        'user_id',
        'partner_id',
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "sale.order", "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period

    orders = pd.DataFrame(data)
    if orders.empty:
        return orders
    
    orders['user_id'] = orders['user_id'].apply(replace, args=[0])
    orders['partner_id'] = orders['partner_id'].apply(replace, args=[0])

    order_ids = [rec['id'] for rec in data]
    orders.rename(columns={
        'id': 'order_id',
        'user_id': 'sales rep',
        'partner_id': 'customer',
        },
        inplace=True)

    domain = [
        ('order_id', 'in', order_ids),
        ]
    fields = [
        'order_id',
        'product_id',
        'company_id',
        "product_uom_qty",
        "product_uom",
        'discount',
        'price_subtotal', #without tax
        'price_total', #with tax
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "sale.order.line", "search_read", [], {"domain": domain, "fields": fields}) # get individual product order lines in all orders that were made

    order_lines = pd.DataFrame(data)
    
    # modify many2one fields that return a list
    order_lines['company_id'] = order_lines['company_id'].apply(replace, args=[0])
    order_lines['product_uom'] = order_lines['product_uom'].apply(replace)
    order_lines['product_id'] = order_lines['product_id'].apply(replace, args=[0])
    order_lines['order_id'] = order_lines['order_id'].apply(replace, args=[0])
    
    order_lines.drop(columns=['id'], axis=1, inplace=True) # order_line ids are not needed
    order_lines = order_lines.merge(orders, on='order_id', how='left') # The date stamp from 'order_df' table is needed I could import them seperately tho and link the tables in excel
    order_lines.rename(columns={'company_id': 'company'}, inplace=True)
    return order_lines
    
def get_data(start_date, end_date):
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    sale_order_lines = get_pos_sales(api, start_date, end_date)
    return sale_order_lines

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
FactSaleOrderLines = chunks()
print(FactSaleOrderLines)
