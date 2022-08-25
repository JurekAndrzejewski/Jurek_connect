import os
import get_bl_orders
import update_orders
def prepare_workspace():
    if(not os.path.exists('logs')):
        os.mkdir('logs')
    if(not os.path.exists('csv_files')):
        os.remove('csv_files')
        
def main():
    get_bl_orders.execute()
    update_orders.execute()
    
if __name__ == "__main__":
    main()
