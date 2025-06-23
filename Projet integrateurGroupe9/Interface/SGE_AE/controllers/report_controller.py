from models.report_model import (
    generate_stock_report, generate_movement_report,
    generate_exception_reports, generate_stockouts,
    generate_expiring_products
)
def handle_stock_report(conn):
    return generate_stock_report(conn)

def handle_movement_report(conn, id_produit):
    return generate_movement_report(conn, id_produit)

def handle_exception_report(conn):
    return generate_exception_reports(conn)
def handle_stockout_report(conn):
    return generate_stockouts(conn)

def handle_expiring_report(conn, days):
    return generate_expiring_products(conn, days)