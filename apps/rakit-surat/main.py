#!/usr/bin/env python3
"""
Rakit Surat Pro - Template Surat Resmi Indonesia
Part of Palma OS Productivity Suite
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit,
    QTextEdit, QComboBox, QMessageBox, QFileDialog, QSplitter,
    QFormLayout, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
import sqlite3
from datetime import datetime


class Database:
    """SQLite database handler for templates and history"""
    
    def __init__(self):
        self.db_path = Path.home() / ".palma" / "data" / "rakit-surat.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                output_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            )
        """)
        self.conn.commit()
        self.seed_templates()
    
    def seed_templates(self):
        """Add default templates if database is empty"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM templates")
        if cursor.fetchone()[0] == 0:
            templates = [
                ("SK", "Surat Keputusan Umum", TEMPLATE_SK),
                ("SK", "SK Pengangkatan Guru", TEMPLATE_SK_GURU),
                ("Undangan", "Undangan Rapat", TEMPLATE_UNDANGAN_RAPAT),
                ("Undangan", "Undangan Acara Sekolah", TEMPLATE_UNDANGAN_SEKOLAH),
                ("Keterangan", "Surat Keterangan Domisili", TEMPLATE_SK_DOMISILI),
                ("Keterangan", "Surat Keterangan Usaha", TEMPLATE_SK_USAHA),
                ("Lamaran", "Surat Lamaran Kerja", TEMPLATE_LAMARAN),
                ("Kwitansi", "Kwitansi Pembayaran", TEMPLATE_KWITANSI),
            ]
            cursor.executemany(
                "INSERT INTO templates (category, name, content) VALUES (?, ?, ?)",
                templates
            )
            self.conn.commit()
    
    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM templates ORDER BY category")
        return [row[0] for row in cursor.fetchall()]
    
    def get_templates_by_category(self, category):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM templates WHERE category = ? ORDER BY name",
            (category,)
        )
        return cursor.fetchall()
    
    def get_template(self, template_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, content FROM templates WHERE id = ?",
            (template_id,)
        )
        return cursor.fetchone()


# Template contents
TEMPLATE_SK = """
SURAT KEPUTUSAN
Nomor: {{nomor_surat}}

TENTANG
{{perihal}}

{pejabat} yang bertanda tangan di bawah ini:

Nama    : {{nama_pejabat}}
Jabatan : {{jabatan_pejabat}}
Alamat  : {{alamat_instansi}}

MEMUTUSKAN

Menetapkan :
PERTAMA  : {{keputusan_1}}
KEDUA    : {{keputusan_2}}
KETIGA   : Surat Keputusan ini berlaku sejak tanggal ditetapkan.

Ditetapkan di : {{kota}}
Pada tanggal  : {{tanggal}}

{{jabatan_pejabat}},


{{nama_pejabat}}
"""

TEMPLATE_SK_GURU = """
SURAT KEPUTUSAN
Nomor: {{nomor_surat}}

TENTANG
PENGANGKATAN GURU HONORER

Kepala {{nama_sekolah}},

Menimbang:
a. Bahwa dalam rangka meningkatkan mutu pendidikan di {{nama_sekolah}};
b. Bahwa yang bersangkutan memenuhi syarat untuk diangkat sebagai Guru Honorer;

MEMUTUSKAN

Menetapkan:
PERTAMA  : Mengangkat Saudara {{nama_guru}} sebagai Guru Honorer {{mata_pelajaran}}
KEDUA    : Terhitung mulai tanggal {{tanggal_mulai}}
KETIGA   : Segala biaya yang timbul akibat keputusan ini dibebankan pada anggaran sekolah

Ditetapkan di : {{kota}}
Pada tanggal  : {{tanggal}}

Kepala Sekolah,


{{nama_kepala_sekolah}}
NIP. {{nip}}
"""

TEMPLATE_UNDANGAN_RAPAT = """
Nomor   : {{nomor_surat}}
Lampiran: -
Perihal : Undangan Rapat

Yth. {{nama_undangan}}
di Tempat

Dengan hormat,

Sehubungan dengan {{agenda_rapat}}, maka kami mengundang Bapak/Ibu untuk hadir pada:

Hari/Tanggal : {{hari_tanggal}}
Waktu        : {{waktu}} WIB - Selesai
Tempat       : {{tempat}}
Acara        : {{acara}}

Mengingat pentingnya acara tersebut, kami mohon kehadiran Bapak/Ibu tepat pada waktunya.

Demikian undangan ini kami sampaikan, atas perhatian dan kehadirannya kami ucapkan terima kasih.

{{kota}}, {{tanggal}}
{{jabatan}},


{{nama_pengundang}}
"""

TEMPLATE_UNDANGAN_SEKOLAH = """
UNDANGAN

Nomor: {{nomor_surat}}

Yth. Bapak/Ibu Orang Tua/Wali Murid
{{nama_siswa}}
Kelas {{kelas}}

Dengan hormat,

Dalam rangka {{kegiatan}}, kami mengundang Bapak/Ibu untuk hadir pada:

Hari/Tanggal : {{hari_tanggal}}
Pukul        : {{waktu}} WIB
Tempat       : {{tempat}}
Acara        : {{acara}}

Kehadiran Bapak/Ibu sangat kami harapkan.

{{kota}}, {{tanggal}}
Kepala {{nama_sekolah}},


{{nama_kepala_sekolah}}
"""

TEMPLATE_SK_DOMISILI = """
SURAT KETERANGAN DOMISILI
Nomor: {{nomor_surat}}

Yang bertanda tangan di bawah ini:
Nama    : {{nama_rt}}
Jabatan : Ketua RT {{nomor_rt}} / RW {{nomor_rw}}
Alamat  : {{alamat_rt}}

Dengan ini menerangkan bahwa:

Nama            : {{nama}}
Tempat/Tgl Lahir: {{ttl}}
NIK             : {{nik}}
Pekerjaan       : {{pekerjaan}}
Agama           : {{agama}}
Status          : {{status}}
Alamat          : {{alamat}}

Benar berdomisili di alamat tersebut di atas.

Demikian surat keterangan ini dibuat untuk dapat dipergunakan sebagaimana mestinya.

{{kota}}, {{tanggal}}
Ketua RT {{nomor_rt}},


{{nama_rt}}
"""

TEMPLATE_SK_USAHA = """
SURAT KETERANGAN USAHA
Nomor: {{nomor_surat}}

Yang bertanda tangan di bawah ini:
Nama    : {{nama_lurah}}
Jabatan : Lurah {{nama_kelurahan}}

Dengan ini menerangkan bahwa:

Nama         : {{nama_pengusaha}}
NIK          : {{nik}}
Alamat       : {{alamat}}
Nama Usaha   : {{nama_usaha}}
Jenis Usaha  : {{jenis_usaha}}
Alamat Usaha : {{alamat_usaha}}

Benar yang bersangkutan menjalankan usaha tersebut di wilayah {{nama_kelurahan}}.

Demikian surat keterangan ini dibuat untuk keperluan {{keperluan}}.

{{kota}}, {{tanggal}}
Lurah {{nama_kelurahan}},


{{nama_lurah}}
"""

TEMPLATE_LAMARAN = """
{{kota}}, {{tanggal}}

Yth. HRD {{nama_perusahaan}}
{{alamat_perusahaan}}

Dengan hormat,

Berdasarkan informasi lowongan pekerjaan yang saya peroleh dari {{sumber_info}}, 
dengan ini saya bermaksud melamar pekerjaan sebagai {{posisi}} di perusahaan yang Bapak/Ibu pimpin.

Saya yang bertanda tangan di bawah ini:
Nama            : {{nama}}
Tempat/Tgl Lahir: {{ttl}}
Pendidikan      : {{pendidikan}}
Alamat          : {{alamat}}
No. HP          : {{no_hp}}
Email           : {{email}}

Sebagai bahan pertimbangan, saya lampirkan:
1. Daftar Riwayat Hidup
2. Fotokopi KTP
3. Fotokopi Ijazah terakhir
4. Pas foto terbaru 3x4

Demikian surat lamaran ini saya buat dengan sebenarnya. Besar harapan saya untuk dapat 
bergabung di perusahaan yang Bapak/Ibu pimpin.

Hormat saya,


{{nama}}
"""

TEMPLATE_KWITANSI = """
═══════════════════════════════════════════════════════
                        KWITANSI
                    No: {{nomor_kwitansi}}
═══════════════════════════════════════════════════════

Telah terima dari : {{nama_pembayar}}
Uang sejumlah     : Rp {{jumlah_angka}}
Terbilang         : {{jumlah_terbilang}}
Untuk pembayaran  : {{keterangan}}

═══════════════════════════════════════════════════════

{{kota}}, {{tanggal}}

                                        Penerima,


                                        {{nama_penerima}}
═══════════════════════════════════════════════════════
"""


class RakitSuratWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_template_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Rakit Surat Pro - Palma OS")
        self.setMinimumSize(1024, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Template selection
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Editor and preview
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([300, 700])
        
        # Apply styling
        self.apply_styles()
    
    def create_left_panel(self):
        """Create template selection panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📝 Template Surat")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Category selector
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.db.get_categories())
        self.category_combo.currentTextChanged.connect(self.load_templates)
        layout.addWidget(self.category_combo)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
        
        # Load initial templates
        self.load_templates(self.category_combo.currentText())
        
        return panel
    
    def create_right_panel(self):
        """Create editor panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📋 Editor Surat")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Form area (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Preview area
        preview_label = QLabel("📄 Preview:")
        preview_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(200)
        layout.addWidget(self.preview_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("🔄 Preview")
        self.preview_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(self.preview_btn)
        
        self.export_btn = QPushButton("💾 Export PDF")
        self.export_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(self.export_btn)
        
        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.clicked.connect(self.print_document)
        button_layout.addWidget(self.print_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def load_templates(self, category):
        """Load templates for selected category"""
        self.template_list.clear()
        templates = self.db.get_templates_by_category(category)
        for template_id, name in templates:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, template_id)
            self.template_list.addItem(item)
    
    def on_template_selected(self, item):
        """Handle template selection"""
        self.current_template_id = item.data(Qt.ItemDataRole.UserRole)
        template = self.db.get_template(self.current_template_id)
        if template:
            self.load_template_form(template[1])
    
    def load_template_form(self, template_content):
        """Generate form fields from template placeholders"""
        # Clear existing form
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Find all placeholders
        import re
        placeholders = re.findall(r'\{\{(\w+)\}\}', template_content)
        placeholders = list(dict.fromkeys(placeholders))  # Remove duplicates
        
        self.form_fields = {}
        for placeholder in placeholders:
            label = placeholder.replace('_', ' ').title()
            field = QLineEdit()
            
            # Auto-fill common fields
            if placeholder == 'tanggal':
                field.setText(datetime.now().strftime("%d %B %Y"))
            elif placeholder == 'kota':
                field.setText("Jakarta")
            
            self.form_fields[placeholder] = field
            self.form_layout.addRow(label + ":", field)
        
        self.template_content = template_content
    
    def update_preview(self):
        """Update preview with filled template"""
        if not hasattr(self, 'template_content'):
            return
        
        content = self.template_content
        for key, field in self.form_fields.items():
            content = content.replace(f"{{{{{key}}}}}", field.text())
        
        self.preview_text.setPlainText(content)
    
    def export_pdf(self):
        """Export to PDF"""
        self.update_preview()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                # Simple text-based PDF using WeasyPrint
                from weasyprint import HTML
                
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Noto Sans', sans-serif; padding: 40px; white-space: pre-wrap; }}
                    </style>
                </head>
                <body>{self.preview_text.toPlainText()}</body>
                </html>
                """
                
                HTML(string=html_content).write_pdf(file_path)
                QMessageBox.information(self, "Sukses", f"PDF berhasil disimpan ke:\n{file_path}")
            except ImportError:
                # Fallback: save as text
                file_path = file_path.replace('.pdf', '.txt')
                with open(file_path, 'w') as f:
                    f.write(self.preview_text.toPlainText())
                QMessageBox.information(self, "Sukses", f"Disimpan sebagai TXT:\n{file_path}")
    
    def print_document(self):
        """Print document"""
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        
        self.update_preview()
        
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.preview_text.print(printer)
    
    def apply_styles(self):
        """Apply Palma OS styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #009B77;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007B5F;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #009B77;
                color: white;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Rakit Surat Pro")
    
    window = RakitSuratWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
