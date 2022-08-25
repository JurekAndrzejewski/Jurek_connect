import logging
from datetime import date

today = date.today()
today = today.strftime('%d_%m_%Y')

logging.basicConfig(filename=('logs/baselinker_connect_' + today +'.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

REMOVE_DATE = 100 * 24 * 3600 # usuwanie zamówień starszych niż 100 dni 100 dni * 24 godziny * 3600 sekund

BL_ORDERS = 'csv_files/baselinker_orders.csv'

'''
Event type:
1 - Order creation
2 - DOF download (order confirmation)
3 - Payment of the order
4 - Removal of order/invoice/receipt
5 - Merging the orders
6 - Splitting the order
7 - Issuing an invoice
8 - Issuing a receipt
9 - Package creation
10 - Deleting a package
11 - Editing delivery data
12 - Adding a product to an order
13 - Editing the product in the order
14 - Removing the product from the order
15 - Adding a buyer to a blacklist
16 - Editing order data
17 - Copying an order
18 - Order status change
19 - Invoice deletion
20 - Receipt deletion
'''
LOG_TYPES = [9, 18]
PACKAGE_CREATED = 9
STATUS_CHANGED = 18

# TODO: zmapowanie statusów klienta na nasze
client_to_ours = {
    # status u klienta : nasz status
    116035: 241363,
    78042: 241364,
}

# TODO: sprawdzic sprzed ilu godzin chcemy pobierac zamowienia
HOURS_BEFORE = 72

# TODO: token klienta do baselinkera
CLIENT_TOKEN = ''

# TODO: nasz token do baselinkera
OUR_TOKEN = ''

# TODO: status typu ostatnia deska ratunku
LAST_RESORT_STATUS = 241509

