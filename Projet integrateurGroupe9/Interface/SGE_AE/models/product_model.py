def get_all_products(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT idProduit, reference, nom, description, marque, modele, type, estMaterielEmballage FROM PRODUIT")
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def add_product(conn, product):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO PRODUIT (idProduit, reference, nom, description, marque, modele, type, estMaterielEmballage)
            VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
        """, (
            product["reference"], product["nom"], product["description"],
            product["marque"], product["modele"], product["type"],
            product["estMaterielEmballage"]
        ))
        conn.commit()

def update_product(conn, id_produit, product):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE PRODUIT SET reference=%s, nom=%s, description=%s,
                marque=%s, modele=%s, type=%s, estMaterielEmballage=%s
            WHERE idProduit=%s
        """, (
            product["reference"], product["nom"], product["description"],
            product["marque"], product["modele"], product["type"],
            product["estMaterielEmballage"], id_produit
        ))
        conn.commit()
