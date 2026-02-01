#!/usr/bin/env python3
"""
Kasir Mikro - POS Sederhana untuk UMKM
Part of Palma OS Productivity Suite
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QGroupBox, QGridLayout, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap
import sqlite3


class Database:
    """SQLite database handler for products and transactions"""
    
    def __init__(self):
        self.db_path = Path.home() / ".palma" / "data" / "kasir-mikro.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                total REAL NOT NULL,
                payment REAL NOT NULL,
                change REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                subtotal REAL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.conn.commit()
        self.seed_sample_products()
    
    def seed_sample_products(self):
        """Add sample products if database is empty"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            products = [
                ("SKU001", "Indomie Goreng", 3500, 100, "Makanan"),
                ("SKU002", "Aqua 600ml", 4000, 50, "Minuman"),
                ("SKU003", "Teh Botol Sosro", 5000, 30, "Minuman"),
                ("SKU004", "Roti Tawar", 15000, 20, "Makanan"),
                ("SKU005", "Kopi Sachet", 2500, 200, "Minuman"),
                ("SKU006", "Minyak Goreng 1L", 18000, 15, "Kebutuhan"),
                ("SKU007", "Gula Pasir 1kg", 14000, 25, "Kebutuhan"),
                ("SKU008", "Beras 5kg", 65000, 10, "Kebutuhan"),
            ]
            cursor.executemany(
                "INSERT INTO products (code, name, price, stock, category) VALUES (?, ?, ?, ?, ?)",
                products
            )
            self.conn.commit()
    
    def get_products(self, search=""):
        cursor = self.conn.cursor()
        if search:
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE ? OR code LIKE ?",
                (f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute("SELECT * FROM products")
        return cursor.fetchall()
    
    def get_product(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return cursor.fetchone()
    
    def add_product(self, code, name, price, stock, category):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO products (code, name, price, stock, category) VALUES (?, ?, ?, ?, ?)",
            (code, name, price, stock, category)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def update_stock(self, product_id, quantity):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )
        self.conn.commit()
    
    def save_transaction(self, invoice_no, items, total, payment, change):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (invoice_no, total, payment, change) VALUES (?, ?, ?, ?)",
            (invoice_no, total, payment, change)
        )
        transaction_id = cursor.lastrowid
        
        for item in items:
            cursor.execute(
                "INSERT INTO transaction_items (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                (transaction_id, item['product_id'], item['quantity'], item['subtotal'])
            )
            self.update_stock(item['product_id'], item['quantity'])
        
        self.conn.commit()
        return transaction_id
    
    def generate_invoice_no(self):
        return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class AddProductDialog(QDialog):
    """Dialog for adding new products"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Produk")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.code_input = QLineEdit()
        layout.addRow("Kode:", self.code_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Nama:", self.name_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 100000000)
        self.price_input.setPrefix("Rp ")
        layout.addRow("Harga:", self.price_input)
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 100000)
        layout.addRow("Stok:", self.stock_input)
        
        self.category_input = QComboBox()
        self.category_input.addItems(["Makanan", "Minuman", "Kebutuhan", "Lainnya"])
        self.category_input.setEditable(True)
        layout.addRow("Kategori:", self.category_input)
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 Simpan")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ Batal")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
    
    def get_data(self):
        return {
            'code': self.code_input.text(),
            'name': self.name_input.text(),
            'price': self.price_input.value(),
            'stock': self.stock_input.value(),
            'category': self.category_input.currentText()
        }


class KasirMikroWindow(QMainWindow):
    """Main POS application window"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.cart = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Kasir Mikro - Palma OS")
        self.setMinimumSize(1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Products
        left_panel = self.create_products_panel()
        main_layout.addWidget(left_panel, stretch=3)
        
        # Right panel - Cart
        right_panel = self.create_cart_panel()
        main_layout.addWidget(right_panel, stretch=2)
        
        self.apply_styles()
        self.load_products()
    
    def create_products_panel(self):
        """Create products listing panel"""
        panel = QGroupBox("🏪 Daftar Produk")
        layout = QVBoxLayout(panel)
        
        # Search and add
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari produk...")
        self.search_input.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ Tambah Produk")
        add_btn.clicked.connect(self.show_add_product_dialog)
        search_layout.addWidget(add_btn)
        
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(
            ["ID", "Kode", "Nama", "Harga", "Stok", "Aksi"]
        )
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.products_table)
        
        return panel
    
    def create_cart_panel(self):
        """Create shopping cart panel"""
        panel = QGroupBox("🛒 Keranjang Belanja")
        layout = QVBoxLayout(panel)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(
            ["Nama", "Harga", "Qty", "Subtotal", "Hapus"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cart_table)
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("TOTAL:")
        total_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        total_layout.addWidget(total_label)
        
        self.total_display = QLabel("Rp 0")
        self.total_display.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        self.total_display.setStyleSheet("color: #009B77;")
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self.total_display)
        
        layout.addLayout(total_layout)
        
        # Payment input
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Bayar:")
        payment_layout.addWidget(payment_label)
        
        self.payment_input = QDoubleSpinBox()
        self.payment_input.setRange(0, 100000000)
        self.payment_input.setPrefix("Rp ")
        self.payment_input.valueChanged.connect(self.calculate_change)
        payment_layout.addWidget(self.payment_input)
        
        layout.addLayout(payment_layout)
        
        # Change display
        change_layout = QHBoxLayout()
        change_label = QLabel("Kembalian:")
        change_layout.addWidget(change_label)
        
        self.change_display = QLabel("Rp 0")
        self.change_display.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.change_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        change_layout.addWidget(self.change_display)
        
        layout.addLayout(change_layout)
        
        # Action buttons
        buttons_layout = QGridLayout()
        
        clear_btn = QPushButton("🗑️ Kosongkan")
        clear_btn.clicked.connect(self.clear_cart)
        buttons_layout.addWidget(clear_btn, 0, 0)
        
        qr_btn = QPushButton("📱 QR Transfer")
        qr_btn.clicked.connect(self.generate_qr)
        buttons_layout.addWidget(qr_btn, 0, 1)
        
        checkout_btn = QPushButton("✅ BAYAR")
        checkout_btn.setStyleSheet("background-color: #FFD700; color: black; font-size: 16px;")
        checkout_btn.clicked.connect(self.checkout)
        buttons_layout.addWidget(checkout_btn, 1, 0, 1, 2)
        
        layout.addLayout(buttons_layout)
        
        return panel
    
    def load_products(self):
        """Load products into table"""
        search = self.search_input.text()
        products = self.db.get_products(search)
        
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.products_table.setItem(row, 2, QTableWidgetItem(product[2]))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"Rp {product[3]:,.0f}"))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product[4])))
            
            add_btn = QPushButton("➕")
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            self.products_table.setCellWidget(row, 5, add_btn)
    
    def show_add_product_dialog(self):
        """Show dialog to add new product"""
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_product(
                    data['code'], data['name'], data['price'],
                    data['stock'], data['category']
                )
                self.load_products()
                QMessageBox.information(self, "Sukses", "Produk berhasil ditambahkan!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan produk: {e}")
    
    def add_to_cart(self, product):
        """Add product to cart"""
        # Check if already in cart
        for item in self.cart:
            if item['product_id'] == product[0]:
                item['quantity'] += 1
                item['subtotal'] = item['quantity'] * item['price']
                self.update_cart_display()
                return
        
        # Add new item
        self.cart.append({
            'product_id': product[0],
            'name': product[2],
            'price': product[3],
            'quantity': 1,
            'subtotal': product[3]
        })
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart table display"""
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"Rp {item['price']:,.0f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"Rp {item['subtotal']:,.0f}"))
            
            remove_btn = QPushButton("🗑️")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)
            
            total += item['subtotal']
        
        self.total_display.setText(f"Rp {total:,.0f}")
        self.calculate_change()
    
    def remove_from_cart(self, row):
        """Remove item from cart"""
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart = []
        self.update_cart_display()
        self.payment_input.setValue(0)
    
    def calculate_change(self):
        """Calculate change amount"""
        total = sum(item['subtotal'] for item in self.cart)
        payment = self.payment_input.value()
        change = payment - total
        
        if change >= 0:
            self.change_display.setText(f"Rp {change:,.0f}")
            self.change_display.setStyleSheet("color: #009B77;")
        else:
            self.change_display.setText(f"Rp {change:,.0f}")
            self.change_display.setStyleSheet("color: red;")
    
    def checkout(self):
        """Process checkout"""
        if not self.cart:
            QMessageBox.warning(self, "Peringatan", "Keranjang masih kosong!")
            return
        
        total = sum(item['subtotal'] for item in self.cart)
        payment = self.payment_input.value()
        
        if payment < total:
            QMessageBox.warning(self, "Peringatan", "Pembayaran kurang!")
            return
        
        change = payment - total
        invoice_no = self.db.generate_invoice_no()
        
        # Save transaction
        self.db.save_transaction(invoice_no, self.cart, total, payment, change)
        
        # Show receipt
        receipt = self.generate_receipt(invoice_no, total, payment, change)
        QMessageBox.information(self, "Transaksi Berhasil", receipt)
        
        self.clear_cart()
        self.load_products()  # Refresh stock
    
    def generate_receipt(self, invoice_no, total, payment, change):
        """Generate text receipt"""
        lines = [
            "═" * 40,
            "           KASIR MIKRO",
            "        Struk Pembayaran",
            "═" * 40,
            f"No. Invoice: {invoice_no}",
            f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "-" * 40,
        ]
        
        for item in self.cart:
            lines.append(f"{item['name']}")
            lines.append(f"  {item['quantity']} x Rp {item['price']:,.0f} = Rp {item['subtotal']:,.0f}")
        
        lines.extend([
            "-" * 40,
            f"TOTAL: Rp {total:,.0f}",
            f"BAYAR: Rp {payment:,.0f}",
            f"KEMBALI: Rp {change:,.0f}",
            "═" * 40,
            "Terima kasih!",
        ])
        
        return "\n".join(lines)
    
    def generate_qr(self):
        """Generate QR code for payment"""
        if not self.cart:
            QMessageBox.warning(self, "Peringatan", "Keranjang masih kosong!")
            return
        
        total = sum(item['subtotal'] for item in self.cart)
        
        try:
            import qrcode
            
            # Generate payment QR (example: QRIS format)
            qr_data = f"PALMA-PAY:{total}"
            qr = qrcode.make(qr_data)
            
            qr_path = Path.home() / ".palma" / "temp" / "payment_qr.png"
            qr_path.parent.mkdir(parents=True, exist_ok=True)
            qr.save(str(qr_path))
            
            QMessageBox.information(
                self, "QR Transfer",
                f"QR Code tersimpan di:\n{qr_path}\n\nTotal: Rp {total:,.0f}"
            )
        except ImportError:
            QMessageBox.warning(self, "Error", "Module qrcode tidak tersedia")
    
    def apply_styles(self):
        """Apply Palma OS styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #009B77;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #009B77;
            }
            QPushButton {
                background-color: #009B77;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007B5F;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Kasir Mikro")
    
    window = KasirMikroWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
