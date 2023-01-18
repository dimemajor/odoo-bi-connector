from xmlrpc import client
import pandas as pd
import datetime as dt

def replace(cell, index=1):
    # use this to replace many2one fields that
    # return a list of the id and name
    # with just the id of the related field  
    cell = list(cell)
    try:
        cell = cell[index]
    except:
        try:
            cell = cell[0]
        except:
            return None
    return cell

def connect():
    common = client.ServerProxy("%s/xmlrpc/2/common" % url)
    uid = common.authenticate(db, user, password, {})
    if not uid:
        raise NameError
    return uid
    
def get_data(uid):
    api = client.ServerProxy("%s/xmlrpc/2/object" % url)
    domain = ['&', 
        ('date_order', '>=', start_date), 
        ('date_order', '<=', end_date),
        ('state', 'in', ['paid', 'done']),
        ]
    data = api.execute_kw(db, uid, password, "pos.order", "search_read", [], {"domain": domain, "fields": ['id', 'date_order'], }) # get all orders within specified period
    order_df = pd.DataFrame(data)
    order_df.rename(columns={'id': 'order_id'}, inplace=True) 
    data = [_id['id'] for _id in data]
    domain = [
        ('order_id', 'in', data),
        ]
    fields = [
        'order_id', 
        'product_id',
        "full_product_name",
        'company_id',
        "qty", 
        'total_cost', 
        'margin', 
        'margin_percent', 
        'discount', 
        'price_subtotal', 
        'price_subtotal_incl',
    ]
    data = api.execute_kw(db, uid, password, "pos.order.line", "search_read", [], {"domain": domain, "fields": fields}) # get individual product order lines in all orders that were made
    orders = pd.DataFrame(data)

    # modify many2one fields that return a list
    orders['company_id'] = orders['company_id'].apply(replace)
    orders['product_id'] = orders['product_id'].apply(replace, args=[0])
    orders['order_id'] = orders['order_id'].apply(replace, args=[0])


    orders.drop(columns=['id'], axis=1, inplace=True) # order_line ids are not needed
    orders = orders.merge(order_df, on='order_id', how='left') # The date stamp from 'order_df' table is needed I could import them seperately tho and link the tables in excel
    orders.drop(columns=['order_id'], axis=1, inplace=True)
    data = [_id['product_id'][0] for _id in data]
    domain = [
        ('id', 'in', data),
        ('active', 'in', [True, False]),
        ]
    fields = [
        'id',
        'categ_id', 
        'active',
    ]

    # the categories of the products could be useful for analysis
    data = api.execute_kw(db, uid, password, "product.product", "search_read", [], {"domain": domain, "fields": fields})
    products = pd.DataFrame(data)
    products['categ_id'] = products['categ_id'].apply(replace)
    return orders, products

url = "domain" # with http:// or https://
user = "email"
password = "password"
db = "database name" 
company = ['Company 1'] # Put company name here (case sensitive)
start_date = '2023-01-01 00:00:00' # time is set to from start of 2023 UTC, no need to adjust for user timezone. This must be the format if you need to change
end_date = f'{dt.datetime.today():%Y-%m-%d %H:%M:%S}'

uid = connect()
orders, products = get_data(uid)
