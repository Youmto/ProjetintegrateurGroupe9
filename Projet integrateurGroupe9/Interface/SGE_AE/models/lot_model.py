import logging
from datetime import date, datetime
from SGE_AE.database import execute_query # Assurez-vous que ce chemin est correct

logger = logging.getLogger(__name__)

def get_produit_details_in_colis(conn, id_colis, id_produit):
    """
    Récupère tous les détails d'un produit spécifique contenu dans un colis donné.
    Retourne un dictionnaire avec tous les champs du produit (matériel ou logiciel).
    """
    try:
        query = """
            SELECT
                C.idColis,
                P.idProduit,
                P.nom AS nomProduit,
                P.type AS type, -- Assurez-vous que l'alias 'type' est bien là
                C.quantite AS quantiteDansColis,
                PL.version,
                PL.typeLicence,
                PL.dateExpiration,
                PM.longueur,
                PM.largeur,
                PM.hauteur,
                PM.masse,
                PM.volume
            FROM PRODUIT P
            LEFT JOIN LOT L ON P.idProduit = L.idProduit
            LEFT JOIN CONTENIR C ON L.idLot = C.idLot
            LEFT JOIN produit_logiciel PL ON P.idProduit = PL.idProduit
            LEFT JOIN produit_materiel PM ON P.idProduit = PM.idProduit
            WHERE C.idColis = %s AND P.idProduit = %s;
        """
        rows = execute_query(conn, query, (id_colis, id_produit), fetch=True)

        if not rows:
            logger.warning(f"🔍 [get_produit_details_in_colis] Aucun détail trouvé pour colis {id_colis}, produit {id_produit}")
            return None

        # --- IMPORTANT : Convertir le tuple en dictionnaire ---
        # L'ordre des colonnes doit correspondre EXACTEMENT à l'ordre dans la requête SQL
        column_names = [
            "idColis", "idProduit", "nom", "type", "quantite",
            "version", "typeLicence", "dateExpiration",
            "longueur", "largeur", "hauteur", "masse", "volume"
        ]
        
        produit_details = {}
        # Puisque nous attendons une seule ligne pour les détails d'un produit spécifique
        product_tuple = rows[0] 
        for i, col_name in enumerate(column_names):
            value = product_tuple[i]
            # Convertir les objets date/datetime si nécessaire
            if col_name == "dateExpiration" and isinstance(value, (date, datetime)):
                produit_details[col_name] = value.isoformat() # Optionnel: convertir en string ISO pour consistance, ou laisser tel quel
            else:
                produit_details[col_name] = value

        return produit_details

    except Exception as e:
        logger.error(f"🔍 [get_produit_details_in_colis] Erreur lors de la récupération des détails pour colis {id_colis}, produit {id_produit}: {e}")
        return None


def get_produits_par_lot(conn, id_lot):
    try:
        query = """
            SELECT
                C.idColis,
                P.idProduit,
                P.nom AS nomProduit,
                P.type AS type, -- Assurez-vous que l'alias 'type' est bien là
                C.quantite AS quantiteDansColis,
                PL.version,
                PL.typeLicence,
                PL.dateExpiration,
                PM.longueur,
                PM.largeur,
                PM.hauteur,
                PM.masse,
                PM.volume
            FROM PRODUIT P
            JOIN LOT L ON P.idProduit = L.idProduit
            JOIN CONTENIR C ON L.idLot = C.idLot
            LEFT JOIN produit_logiciel PL ON P.idProduit = PL.idProduit
            LEFT JOIN produit_materiel PM ON P.idProduit = PM.idProduit
            WHERE L.idLot = %s
            ORDER BY C.idColis, P.nom;
        """
        raw_rows = execute_query(conn, query, (id_lot,), fetch=True)

        # --- IMPORTANT : Convertir les tuples en dictionnaires ---
        column_names = [
            "idColis", "idProduit", "nom", "type", "quantite",
            "version", "typeLicence", "dateExpiration",
            "longueur", "largeur", "hauteur", "masse", "volume"
        ]

        produits_dict_list = []
        for row in raw_rows:
            produit_dict = {}
            for i, col_name in enumerate(column_names):
                produit_dict[col_name] = row[i]
            produits_dict_list.append(produit_dict)

        return produits_dict_list
    except Exception as e:
        logger.error(f"🔍 [get_produits_par_lot] Erreur : {e}")
        return []

def supprimer_produit_dans_colis(conn, id_colis, id_produit): 
    try:
        # Nous avons besoin de l'idLot pour supprimer dans CONTENIR
        # car la PK de CONTENIR est (idColis, idLot)
        query_get_lot_id = """
            SELECT L.idLot
            FROM LOT L
            JOIN CONTENIR C ON L.idLot = C.idLot
            WHERE C.idColis = %s AND L.idProduit = %s
            LIMIT 1; -- Prend le premier lot trouvé si plusieurs existent pour ce produit/colis (peu probable mais sécurisant)
        """
        result_lot_id = execute_query(conn, query_get_lot_id, (id_colis, id_produit), fetch=True)
        
        if not result_lot_id:
            logger.warning(f"[supprimer_produit_dans_colis] Aucun lot trouvé pour la combinaison colis {id_colis} et produit {id_produit}. Aucune suppression effectuée.")
            return False

        # Extraire l'idLot du résultat (qui est un tuple de tuple)
        actual_id_lot = result_lot_id[0][0]

        query = "DELETE FROM CONTENIR WHERE idColis = %s AND idLot = %s;"
        execute_query(conn, query, (id_colis, actual_id_lot))
        logger.info(f"✔ [supprimer_produit_dans_colis] Produit ID {id_produit} supprimé du colis ID {id_colis} (via lot ID {actual_id_lot}).")
        conn.commit() # S'assurer que la transaction est commitée
        return True

    except Exception as e:
        conn.rollback() # Annuler la transaction en cas d'erreur
        logger.error(f"❌ [supprimer_produit_dans_colis] Erreur lors de la suppression du produit {id_produit} du colis {id_colis}: {e}")
        return False


def modifier_produit_dans_colis(conn, id_colis, id_produit, **update_data):
    try:
        # Récupérer l'idLot associé à ce produit et colis
        query_lot_id = """
            SELECT L.idLot
            FROM LOT L
            JOIN CONTENIR C ON L.idLot = C.idLot
            WHERE C.idColis = %s AND L.idProduit = %s
            LIMIT 1;
        """
        result_lot_id = execute_query(conn, query_lot_id, (id_colis, id_produit), fetch=True)
        
        if not result_lot_id:
            logger.error(f"[modifier_produit_dans_colis] Aucun lot trouvé pour colis {id_colis} et produit {id_produit}")
            return False

        id_lot = result_lot_id[0][0]

        # 1. Mise à jour de la quantité dans CONTENIR
        if 'quantite' in update_data:
            quantite = update_data['quantite']
            query_quantite = """
                UPDATE CONTENIR
                SET quantite = %s
                WHERE idColis = %s AND idLot = %s;
            """
            execute_query(conn, query_quantite, (quantite, id_colis, id_lot))
            logger.info(f"✔ [modifier_produit_dans_colis] Quantité du produit {id_produit} dans colis {id_colis} mise à jour à {quantite}.")
        
        # 2. Déterminer le type de produit pour mettre à jour les attributs spécifiques
        query_type = """
            SELECT type -- Colonne 'type' du tableau PRODUIT
            FROM PRODUIT
            WHERE idProduit = %s;
        """
        prod_type_result = execute_query(conn, query_type, (id_produit,), fetch=True)
        if not prod_type_result:
            logger.warning(f"[modifier_produit_dans_colis] Type de produit introuvable pour idProduit {id_produit}. Impossible de mettre à jour les attributs spécifiques.")
            return False
        
        product_type = prod_type_result[0][0] # Le type de produit (ex: 'logiciel' ou 'materiel')
        
        # 3. Mise à jour des attributs spécifiques (logiciel ou matériel)
        if product_type == 'logiciel':
            # Vérifier si au moins un des champs de logiciel est dans update_data
            if any(k in update_data for k in ['version', 'type_licence', 'date_expiration']):
                version = update_data.get('version')
                type_licence = update_data.get('type_licence')
                date_expiration = update_data.get('date_expiration') # Ceci sera déjà un objet date ou None

                query_logiciel = """
                    INSERT INTO produit_logiciel (idProduit, version, typeLicence, dateExpiration)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (idProduit) DO UPDATE
                    SET version = COALESCE(EXCLUDED.version, produit_logiciel.version),
                        typeLicence = COALESCE(EXCLUDED.typeLicence, produit_logiciel.typeLicence),
                        dateExpiration = COALESCE(EXCLUDED.dateExpiration, produit_logiciel.dateExpiration);
                """
                execute_query(conn, query_logiciel, (id_produit, version, type_licence, date_expiration))
                logger.info(f"✔ [modifier_produit_dans_colis] Attributs logiciel du produit {id_produit} mis à jour.")

        elif product_type == 'materiel':
            # Vérifier si au moins un des champs de matériel est dans update_data
            if any(k in update_data for k in ['longueur', 'largeur', 'hauteur', 'masse', 'volume']):
                longueur = update_data.get('longueur')
                largeur = update_data.get('largeur')
                hauteur = update_data.get('hauteur')
                masse = update_data.get('masse')
                volume = update_data.get('volume')

                query_materiel = """
                    INSERT INTO produit_materiel (idProduit, longueur, largeur, hauteur, masse, volume)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (idProduit) DO UPDATE
                    SET longueur = COALESCE(EXCLUDED.longueur, produit_materiel.longueur),
                        largeur = COALESCE(EXCLUDED.largeur, produit_materiel.largeur),
                        hauteur = COALESCE(EXCLUDED.hauteur, produit_materiel.hauteur),
                        masse = COALESCE(EXCLUDED.masse, produit_materiel.masse),
                        volume = COALESCE(EXCLUDED.volume, produit_materiel.volume);
                """
                execute_query(conn, query_materiel, (id_produit, longueur, largeur, hauteur, masse, volume))
                logger.info(f"✔ [modifier_produit_dans_colis] Attributs matériel du produit {id_produit} mis à jour.")
        
        conn.commit() # Confirmer toutes les modifications si aucune erreur
        return True

    except Exception as e:
        conn.rollback() # Annuler les modifications en cas d'erreur
        logger.error(f"❌ [modifier_produit_dans_colis] Erreur lors de la modification du produit {id_produit} dans le colis {id_colis}: {e}")
        return False


def get_all_lots(conn):
    try:
        query = "SELECT idLot, numeroLot FROM LOT ORDER BY numeroLot;"
        rows = execute_query(conn, query, fetch=True)
        return rows
    except Exception as e:
        logger.error(f"[get_all_lots] Erreur : {e}")
        return []