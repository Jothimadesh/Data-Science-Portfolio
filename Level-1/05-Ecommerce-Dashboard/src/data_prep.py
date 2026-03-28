# src/data_prep.py
import pandas as pd
from sqlalchemy import create_engine

def load_data(path='data/'):
    orders = pd.read_csv(path + 'orders.csv', parse_dates=['order_date'])
    products = pd.read_csv(path + 'products.csv')
    customers = pd.read_csv(path + 'customers.csv')
    return orders, products, customers

def clean_orders(orders):
    orders.columns = orders.columns.str.strip().str.lower()
    orders['quantity'] = orders['quantity'].fillna(1).astype(int)
    orders['unit_price'] = orders['unit_price'].fillna(0).astype(float)
    orders['revenue'] = orders['quantity'] * orders['unit_price']
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders = orders.drop_duplicates()
    return orders

def save_to_sql(orders, products, customers, db_path='sqlite:///data/ecom.db'):
    engine = create_engine(db_path)
    orders.to_sql('orders', engine, if_exists='replace', index=False)
    products.to_sql('products', engine, if_exists='replace', index=False)
    customers.to_sql('customers', engine, if_exists='replace', index=False)
    return engine

if __name__ == '__main__':
    orders, products, customers = load_data()
    orders = clean_orders(orders)
    engine = save_to_sql(orders, products, customers)
    print("Data cleaned and saved to SQLite.")
