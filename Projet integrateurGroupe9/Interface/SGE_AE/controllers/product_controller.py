from models.product_model import get_all_products, add_product, update_product

def handle_get_all_products(conn):
    return get_all_products(conn)

def handle_add_product(conn, product_data):
    return add_product(conn, product_data)

def handle_update_product(conn, id_produit, product_data):
    return update_product(conn, id_produit, product_data)
