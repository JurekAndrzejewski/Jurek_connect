import json
import requests
import time
import csv
from datetime import datetime
import pandas as pd
import time
import logging
from datetime import date
import numpy as np
from constants import *


today = date.today()
today = today.strftime('%d_%m_%Y')

logging.basicConfig(filename=('logs/baselinker_connect_' + today +'.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def get_orders():
    print('get_orders')
    return_table = []
    '''
    Orders are passed further without any edition
    '''
    date_from = int(time.time()) - HOURS_BEFORE * 3600
    counter = 0
    while True:
        if counter == 3:
            return return_table
        params = {
            'date_from': date_from,
            'get_unconfirmed_orders': 'true',
            # TODO: mozna przefiltrowac po source id
            #'filter_order_source_id': '',
            # TODO: albo po statusie
            #'status_id': '',
            }
        data = {
            'token': CLIENT_TOKEN,
            'method': 'getOrders',
            'parameters': json.dumps(params)
        }
        r = requests.post('https://api.baselinker.com/connector.php', data=data)
        if not json.loads(r.text)['orders']:
            return return_table
        logging.info('GET ORDERS FROM BASELINKER')
        logging.info('parameters')
        logging.info(data)
        logging.info('response')
        for x in json.loads(r.text)['orders']:
            return_table.append(x)
            logging.info('get order from bl {}'.format(x['order_id']))
        date_from = x['date_add']+1
        counter += 1

def add_order(order):
    bl_body = {
        'order_status_id': '241362', # TODO: W jaki status ma wpadać nowe zamówienie, ewentualnie client_to_ours[int(order['order_status_id'])]
        'date_add': order['date_add'],
        'user_login': order['user_login'],
        'payment_method': order['payment_method'],
        'delivery_company': order['delivery_company'],
        'delivery_method': order['delivery_method'],
        'user_comments': order['user_comments'],
        'admin_comments': order['admin_comments'],
        'phone': order['phone'],
        'email': order['email'],
        'currency': order['currency'],
        'paid': str(np.logical_not(int(order['payment_method_cod'])).astype(int)),
        'delivery_price': order['delivery_price'],
        'delivery_fullname': order['delivery_fullname'],
        'delivery_address': order['delivery_address'],
        'delivery_city': order['delivery_city'],
        'delivery_postcode': order['delivery_postcode'],
        'delivery_country_code': order['delivery_country_code'],
        'invoice_fullname': order['invoice_fullname'],
        'invoice_address': order['invoice_address'],
        'invoice_city': order['invoice_city'],
        'invoice_company': order['invoice_company'],
        'invoice_postcode': order['invoice_postcode'],
        'invoice_country_code': order['invoice_country_code'],
        'delivery_point_id': order['delivery_point_id'],
        'delivery_point_name': order['delivery_point_name'],
        'delivery_point_address': order['delivery_point_address'],
        'delivery_point_postcode': order['delivery_point_postcode'],
        'delivery_point_city': order['delivery_point_city'],
        'extra_field_1': order['extra_field_1'],
        'extra_field_2': order['extra_field_2'],
        'invoice_nip': order['invoice_nip'],
        'custom_source_id': '33466', # TODO: ustawienie id source, np wpada z AMD to mapujemy na ID AMD z baselinkera
        'products': []
    }
    for prod in order['products']:
        bl_product = {
            'storage': 'db',
            'storage_id': 0,
            'product_id': prod['product_id'],
            'name': prod['name'],
            'sku': prod['sku'],
            'price_brutto': prod['price_brutto'],
            'tax_rate': prod['tax_rate'],
            'quantity': prod['quantity'],
            'weight': prod['weight'],
            'ean': prod['ean'],
            'location': prod['location'],
            'attributes': prod['attributes']
            }
        bl_body['products'].append(bl_product) 
    
    data = {
      'token': OUR_TOKEN,
      'method': 'addOrder',
      'parameters': json.dumps(bl_body)
      }
    r = requests.post('https://api.baselinker.com/connector.php', data=data)
    logging.info('added order: our id {} client id {}'.format(str(order['order_id']), json.loads(r.text)['order_id']))
    return json.loads(r.text)['order_id']
    
def modify_orders(orders):
    result_orders = []
    for order in orders:
        our_order_id = add_order(order)
        x = {
            'client_order_id': order['order_id'],
            'our_order_id': our_order_id,
            'status': order['order_status_id'],
            'tracking': '',
            'date_add': order['date_add']
        }
        result_orders.append(x)
    save(result_orders)

def save(orders):
    keys = orders[0].keys()

    with open('csv_files/baselinker_orders.csv', 'a', newline='', encoding = 'utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
        dict_writer.writerows(orders)

def execute():
    modify_orders(get_orders())