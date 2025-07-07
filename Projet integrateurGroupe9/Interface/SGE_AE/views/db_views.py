from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTableWidget,
                           QTableWidgetItem, QTextEdit, QMessageBox,
                           QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
from utils.styles import get_module_style
from database import execute_query, get_table_names

class DBModule(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setStyleSheet(get_module_style("db_views"))
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Groupe requête SQL
        query_group = QGroupBox("Requête SQL")
        query_layout = QVBoxLayout()
        
        self.sql_edit = QTextEdit()
        self.sql_edit.setPlaceholderText("Saisissez votre requête SQL...")
        query_layout.addWidget(self.sql_edit)
        
        # Boutons d'actions
        btn_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("Exécuter")
        self.execute_btn.clicked.connect(self.execute_query)
        btn_layout.addWidget(self.execute_btn)
        
        self.tables_btn = QPushButton("Lister tables")
        self.tables_btn.clicked.connect(self.show_tables)
        btn_layout.addWidget(self.tables_btn)
        
        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.clicked.connect(self.clear_query)
        btn_layout.addWidget(self.clear_btn)
        
        query_layout.addLayout(btn_layout)
        query_group.setLayout(query_layout)
        layout.addWidget(query_group)
        
        # Groupe résultats
        result_group = QGroupBox("Résultats")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(1)
        self.result_table.setHorizontalHeaderLabels(["Données"])
        result_layout.addWidget(self.result_table)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Status
        self.status_label = QLabel("Prêt")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def execute_query(self):
        query = self.sql_edit.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Requête vide", "Veuillez saisir une requête SQL")
            return
            
        try:
            fetch = query.strip().lower().startswith('select')
            result = execute_query(self.conn, query, fetch=fetch)
            self.display_result(result)
            self.status_label.setText("Requête exécutée")
        except Exception as e:
            QMessageBox.critical(self, "Erreur SQL", str(e))
            self.status_label.setText("Erreur d'exécution")

    def show_tables(self):
        try:
            tables = get_table_names(self.conn)
            self.display_result(tables)
            self.status_label.setText(f"{len(tables)} tables trouvées")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            self.status_label.setText("Erreur de récupération")

    def clear_query(self):
        self.sql_edit.clear()
        self.result_table.setRowCount(0)
        self.status_label.setText("Prêt")

    def display_result(self, result):
        self.result_table.setRowCount(0)
        
        if not result:
            self.result_table.setRowCount(1)
            self.result_table.setItem(0, 0, QTableWidgetItem("Aucun résultat"))
            return
            
        if isinstance(result[0], (list, tuple)):
            # Résultats multi-colonnes
            cols = len(result[0])
            self.result_table.setColumnCount(cols)
            self.result_table.setRowCount(len(result))
            
            for row_idx, row in enumerate(result):
                for col_idx, val in enumerate(row):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
        else:
            # Résultats simples
            self.result_table.setColumnCount(1)
            self.result_table.setRowCount(len(result))
            
            for row_idx, val in enumerate(result):
                self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(val)))
        
        self.result_table.resizeColumnsToContents()
        
    def handle_report_command(self):
        """Génère un fichier texte avec tous les rapports disponibles"""
        try:
            # Collecter tous les rapports
            reports = self.collect_all_reports()
        
           # Demander où sauvegarder le fichier
            path, _ = QFileDialog.getSaveFileName(
               self, 
                "Enregistrer les rapports", 
                "rapports_complets.txt", 
                "Fichiers texte (*.txt)"
            )
        
            if not path:
                return
            
            # Écrire les rapports dans le fichier
            with open(path, 'w', encoding='utf-8') as f:
                for report_name, report_data in reports.items():
                    f.write(f"=== {report_name} ===\n\n")
                    if isinstance(report_data, list) and report_data:
                        # Si c'est une liste de dictionnaires (rapports structurés)
                        headers = report_data[0].keys()
                        f.write("\t".join(headers) + "\n")
                        for item in report_data:
                            f.write("\t".join(str(item.get(h, '')) for h in headers) + "\n")
                    elif isinstance(report_data, list):
                        # Si c'est une liste simple
                        f.write("\n".join(str(item) for item in report_data) + "\n")
                    else:
                        # Autres types de données
                        f.write(str(report_data) + "\n")
                    f.write("\n\n")
                
            QMessageBox.information(self, "Rapports générés", 
                              f"Tous les rapports ont été sauvegardés dans {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération des rapports: {str(e)}")

    def collect_all_reports(self):
        """Collecte tous les rapports disponibles"""
        from controllers.report_controller import (
            handle_stock_report,
            handle_movement_report,
            handle_exception_report,
            handle_stockout_report,
            handle_expiring_report
        )
    
        reports = {
           "Rapport de stock global": handle_stock_report(self.conn),
           "Rapport des exceptions récentes": handle_exception_report(self.conn),
           "Rapport des ruptures de stock": handle_stockout_report(self.conn),
           "Rapport des produits expirant": handle_expiring_report(self.conn, 30),
        }
    
        # Pour le rapport de mouvement, on prend le premier produit disponible comme exemple
        try:
            first_product = execute_query(self.conn, "SELECT id FROM produits LIMIT 1;", fetch=True)
            if first_product:
                reports["Rapport de mouvement (exemple)"] = handle_movement_report(
                   self.conn, first_product[0][0]
                )
        except:
            pass
          
        return reports

    # Modifiez la méthode execute_query pour intercepter la commande "rapport"
    def execute_query(self):
        query = self.sql_edit.toPlainText().strip().lower()
    
        if query == "rapport":
            self.handle_report_command()
            return
        
        # Le reste du code existant...
        if not query:
            QMessageBox.warning(self, "Requête vide", "Veuillez saisir une requête SQL")
            return
        
        try:
            fetch = query.strip().lower().startswith('select')
            result = execute_query(self.conn, query, fetch=fetch)
            self.display_result(result)
            self.status_label.setText("Requête exécutée")
        except Exception as e:
            QMessageBox.critical(self, "Erreur SQL", str(e))
            self.status_label.setText("Erreur d'exécution")