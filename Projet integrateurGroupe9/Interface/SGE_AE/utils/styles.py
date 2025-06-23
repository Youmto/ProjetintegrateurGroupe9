def get_stylesheet():
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }
    
    QWidget {
        font-family: Arial;
        font-size: 12px;
    }
    
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #45a049;
    }
    
    QLineEdit, QComboBox, QDateEdit {
        padding: 6px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    
    QTableWidget {
        background-color: white;
        border: 1px solid #ddd;
    }
    
    QHeaderView::section {
        background-color: #f8f8f8;
        padding: 8px;
        border: none;
    }
    
    QTabWidget::pane {
        border: 1px solid #ddd;
        top: -1px;
    }
    
    QTabBar::tab {
        background: #e0e0e0;
        padding: 8px 16px;
        border: 1px solid #ddd;
        border-bottom: none;
    }
    
    QTabBar::tab:selected {
        background: white;
        border-bottom: 1px solid white;
    }
    """