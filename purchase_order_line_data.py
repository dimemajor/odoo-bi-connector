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
    options={
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
    domain = [#'&', 
        #('date_approve', '>=', start_date), 
        ('id', '=', '454'), 
        #('date_approve', '<=', end_date),
        ('state', '=', 'purchase'),
        ]
    fields = [
        'id',
        'date_approve',
        'partner_id',
        'invoice_status',
    ]
    data = api.execute_kw(options['db'], uid, options['password'],'purchase.order', "search_read", [], {"domain": domain, "fields": fields}) # get all orders within specified period
    orders = pd.DataFrame(data)
    if orders.empty:
        return orders
    orders['partner_id'] = orders['partner_id'].apply(replace, args=[0])

    order_ids = [rec['id'] for rec in data]
    orders.rename(columns={
        'id': 'order_id',
        },
        inplace=True)

    domain = [
        ('order_id', 'in', order_ids),
        ]
    fields = [
        'order_id', 
        'product_id',
        'company_id',
        "product_qty", 
        "product_uom", 
        "price_unit",
        'price_subtotal', #without tax
        'price_total', #with tax
    ]
    data = api.execute_kw(options['db'], uid, options['password'], "purchase.order.line", "search_read", [], {"domain": domain, "fields": fields}) # get individual product order lines in all orders that were made
    order_lines = pd.DataFrame(data)
    # modify many2one fields that return a list
    order_lines['company_id'] = order_lines['company_id'].apply(replace, args=[0])
    order_lines['product_uom'] = order_lines['product_uom'].apply(replace)
    order_lines['product_id'] = order_lines['product_id'].apply(replace, args=[0])
    order_lines['order_id'] = order_lines['order_id'].apply(replace, args=[0])
    
    order_lines = order_lines.merge(orders, on='order_id', how='left') # The date stamp from 'order_df' table is needed I could import them seperately tho and link the tables in excel
    order_lines.rename(columns={
        'company_id': 'company',
        },
        inplace=True)
    return order_lines

def get_data(start_date, end_date):
    api = client.ServerProxy("%s/xmlrpc/2/object" % options['url'])
    purchase_order_lines = get_pos_sales(api, start_date, end_date)
    return purchase_order_lines

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
FactPurchaseOrderLines = chunks()
print(FactPurchaseOrderLines)