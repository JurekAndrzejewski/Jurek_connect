import time
import pandas as pd
import json
import copy
import requests
import csv
from constants import *



def send_request(params, token, method, additional_data):
    """
    Function to send requests both to our baselinker and to client's

    Args:
        params (dictionary): dictionary of parameters used for a request
        token (str): token used to communicate with baselinker
        method (str): method used in a request
        additional_data (str): any string that will be used in logging

    Returns:
        str: return text of a request response
    """    
    data = {
        'token': token,
        'method': method,
        'parameters': json.dumps(params)
    }
    
    r = requests.post('https://api.baselinker.com/connector.php', data=data)
    
    logging.info('{} {}: {}'.format(method, additional_data, r.text))
    
    return r.text
    
def read_csv(csv_file):
    """
    Reads CSV

    Args:
        csv_file (str): name of a CSV file

    Returns:
        list: list of dictionaries, where each dictionary is a record from CSV
    """    
    return pd.read_csv(csv_file, sep = ';').to_dict('records')

def modify_statuses(statuses):
    """
    Sets statuses in our baselinker if they were changed

    Args:
        statuses (list): list of orders with their statuses
    """    
    for order in statuses:
        method = 'setOrderStatus'
        params = {
            'order_id': order[0],
            'status_id': '' # mapowanko
        }
        try:
            params['status_id'] = client_to_ours[int(order[1])]
        except:
            params['status_id'] = LAST_RESORT_STATUS

        send_request(params = params, token = OUR_TOKEN, method = method, additional_data = order[0])

def get_order_packages(order):
    """
    Gets packages of certain order

    Args:
        order (int): id of the order

    Returns:
        list: list of packages of certain order
    """    
    method = 'getOrderPackages'
    params = {
        'order_id': order,
    }
    r = send_request(params = params, token = CLIENT_TOKEN, method = method, additional_data = order)
    return json.loads(r)['packages']

def create_package_manual(package, order_id):
    """
    Creates package for order in our baselinker

    Args:
        package (dictionary): dictionary of package to be created
        order_id (int): id of order to which package wants to be added 
    """    
    method = 'createPackageManual'
    params = {
        'order_id': order_id,
        'courier_code': package['courier_code'],
        'package_number': package['courier_package_nr'],
        'pickup_date': package['tracking_status_date']
    }
    params['courier_code'] = package['courier_other_name'] if package['courier_code'] == 'other' else package['courier_code']
    params['courier_code'] = package['courier_other_name'] if package['courier_code'] == 'olzalogistic' else package['courier_code']
    dict_index = next((index for (index, d) in enumerate(bl_orders) if d['our_order_id'] == order_id), None)
    bl_orders[dict_index]['tracking'] = package['courier_package_nr']
    
    send_request(params = params, token = OUR_TOKEN, method = method, additional_data = order_id)

        
def add_packages(packages):
    """
    Manager of orders to which packages were added

    Args:
        packages (list): list of orders to which packages were added
    """    
    for order in packages:
        client_order_id = order[0]
        our_order_id = order[1]
        
        packages = get_order_packages(client_order_id)
        
        for package in packages:
            create_package_manual(package, our_order_id)
        
def clear_bl_orders():
    """
    Clears baselinker CSV of orders older than REMOVE_DATA
    """    
    bl_orders_to_save = copy.deepcopy(bl_orders)
    
    for order in bl_orders:
        if int(time.time()) - order['date_add'] >= REMOVE_DATE: 
            try:
                bl_orders_to_save.remove(order)
                logging.info('removed order {}'.format(order['order_id']))
            except:
                logging.info('Error while trying to remove {}'.format(order['order_id']))
    
    for order_to_save in bl_orders_to_save:
        if str(order_to_save['tracking']) == 'nan':
            order_to_save['tracking'] = ''
        
    save(bl_orders_to_save)
    
def save(orders):
    """
    saves dictionary to CSV file

    Args:
        orders (list): list of dictionaries with orders to be saved
    """    
    keys = orders[0].keys()

    with open('csv_files/baselinker_orders.csv', 'w', newline='', encoding = 'utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(orders)
            
def get_journal_list():
    """
    Downloads last events on orders
    """    
    last_log_id = 0
    packages = []
    statuses = []
    log_list = []
    method = 'getJournalList'
    with open('last_log_id.txt', 'r') as f:
        last_log_id = f.readline()
        
    params = {
        'last_log_id': last_log_id,
        'logs_types': LOG_TYPES
    }
    while True:
        if log_list:
            if log_list[-1]['log_id'] == json.loads(r)['logs'][-1]['log_id']:
                break
        r = send_request(params, CLIENT_TOKEN, method, additional_data = '')
        log_list += json.loads(r)['logs']
        
    
    with open('last_log_id.txt', 'w') as f:
        f.write(str(log_list[-1]['log_id']))
    
    for x in log_list:
        dict_index = next((index for (index, d) in enumerate(bl_orders) if int(d['client_order_id']) == int(x['order_id'])), None)
        if dict_index is not None:
            if int(x['log_type']) == PACKAGE_CREATED:
                logging.info(x)
                packages.append([x['order_id'], bl_orders[dict_index]['our_order_id']])
            elif int(x['log_type']) == STATUS_CHANGED:
                statuses.append([bl_orders[dict_index]['our_order_id'], x['object_id']])
            else:
                logging.info('log type not in log types list {}'.format(x['log_type']))
    
    modify_statuses(statuses)
    add_packages(packages)
            
def execute():
    global bl_orders
    bl_orders = read_csv(BL_ORDERS)
    get_journal_list()
    clear_bl_orders()