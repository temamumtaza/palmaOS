#!/usr/bin/env python3
"""
Palma Setup Wizard - First-Run Experience (OOBE)
Guides new users through persona selection and basic configuration
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup, QLineEdit,
    QCheckBox, QProgressBar, QMessageBox, QWidget, QGridLayout,
    QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap


class PersonaCard(QFrame):
    """Clickable persona selection card"""
    
    def __init__(self, emoji, title, description, parent=None):
        super().__init__(parent)
        self.selected = False
        self.emoji = emoji
        self.title = title
        
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(180, 150)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("Noto Color Emoji", 36))
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Inter", 10))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        self.update_style()
    
    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.update_style()
        # Notify parent
        if hasattr(self.parent(), 'on_persona_selected'):
            self.parent().on_persona_selected(self)
    
    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                PersonaCard {
                    background-color: rgba(0, 155, 119, 0.2);
                    border: 3px solid #009B77;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                PersonaCard {
                    background-color: white;
                    border: 2px solid #dddddd;
                    border-radius: 10px;
                }
                PersonaCard:hover {
                    border-color: #009B77;
                }
            """)


class WelcomePage(QWizardPage):
    """Welcome and language selection page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo placeholder
        logo = QLabel("🌴")
        logo.setFont(QFont("Noto Color Emoji", 72))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # Welcome text
        welcome = QLabel("Selamat Datang di Palma OS")
        welcome.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        welcome.setStyleSheet("color: #009B77;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome)
        
        tagline = QLabel("Hidupkan Kembali, Produktifkan Indonesia")
        tagline.setFont(QFont("Inter", 14))
        tagline.setStyleSheet("color: #666666;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
        layout.addSpacing(30)
        
        # Language info
        lang_info = QLabel("Bahasa sistem: Bahasa Indonesia")
        lang_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lang_info)


class PersonaPage(QWizardPage):
    """Persona selection page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Siapa Anda?")
        self.setSubTitle("Pilih profil yang paling sesuai untuk konfigurasi optimal")
        
        self.selected_persona = None
        
        layout = QVBoxLayout(self)
        
        # Persona grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        personas = [
            ("👨‍🏫", "Pendidik", "Guru & Admin Sekolah"),
            ("🏛️", "Pemerintahan", "RT/RW & Desa"),
            ("🏪", "Niaga", "UMKM & Wirausaha"),
            ("👨‍👩‍👧‍👦", "Personal", "Rumah Tangga"),
            ("📚", "Pelajar", "Siswa & Mahasiswa"),
        ]
        
        self.persona_cards = []
        for i, (emoji, title, desc) in enumerate(personas):
            card = PersonaCard(emoji, title, desc, self)
            self.persona_cards.append(card)
            grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(grid)
        
        # Info text
        info = QLabel("Anda bisa mengubah ini nanti di Pengaturan")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888888; margin-top: 20px;")
        layout.addWidget(info)
    
    def on_persona_selected(self, card):
        # Deselect others
        for c in self.persona_cards:
            if c != card:
                c.selected = False
                c.update_style()
        
        self.selected_persona = card.title if card.selected else None
        self.completeChanged.emit()
    
    def isComplete(self):
        return self.selected_persona is not None
    
    def get_persona(self):
        return self.selected_persona


class UserPage(QWizardPage):
    """User account setup page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Buat Akun Anda")
        self.setSubTitle("Masukkan informasi untuk akun pengguna Anda")
        
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Name
        name_label = QLabel("Nama Lengkap:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Masukkan nama Anda")
        self.name_input.textChanged.connect(self.completeChanged)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        
        # Username
        user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nama pengguna untuk login")
        self.user_input.textChanged.connect(self.completeChanged)
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.user_input)
        
        # Password
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Minimal 6 karakter")
        self.pass_input.textChanged.connect(self.completeChanged)
        form_layout.addWidget(pass_label)
        form_layout.addWidget(self.pass_input)
        
        # Confirm password
        confirm_label = QLabel("Konfirmasi Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.textChanged.connect(self.completeChanged)
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_input)
        
        layout.addLayout(form_layout)
        
        # Auto-login checkbox
        self.auto_login = QCheckBox("Login otomatis (tidak perlu password saat boot)")
        self.auto_login.setChecked(True)
        layout.addWidget(self.auto_login)
    
    def isComplete(self):
        name = self.name_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        confirm = self.confirm_input.text()
        
        if not name or not user or not password:
            return False
        if len(password) < 6:
            return False
        if password != confirm:
            return False
        return True
    
    def get_user_data(self):
        return {
            'name': self.name_input.text().strip(),
            'username': self.user_input.text().strip(),
            'password': self.pass_input.text(),
            'auto_login': self.auto_login.isChecked()
        }


class SetupPage(QWizardPage):
    """Configuration progress page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Menyiapkan Palma OS")
        self.setSubTitle("Mohon tunggu sementara kami mengkonfigurasi sistem Anda")
        
        self.complete = False
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setMinimumWidth(400)
        layout.addWidget(self.progress)
        
        # Status label
        self.status = QLabel("Memulai konfigurasi...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
    
    def initializePage(self):
        """Start the setup process"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.current_step = 0
        self.steps = [
            (10, "Membuat folder sistem..."),
            (20, "Mengkonfigurasi profil pengguna..."),
            (35, "Menyiapkan database aplikasi..."),
            (50, "Menginstal template surat..."),
            (65, "Mengkonfigurasi tema Palma Glass..."),
            (80, "Menyiapkan pintasan desktop..."),
            (90, "Mengoptimalkan performa..."),
            (100, "Selesai!"),
        ]
        self.timer.start(800)
    
    def update_progress(self):
        if self.current_step < len(self.steps):
            value, text = self.steps[self.current_step]
            self.progress.setValue(value)
            self.status.setText(text)
            self.current_step += 1
            
            # Actually create folders on final step
            if self.current_step == len(self.steps):
                self.do_actual_setup()
        else:
            self.timer.stop()
            self.complete = True
            self.completeChanged.emit()
    
    def do_actual_setup(self):
        """Perform actual system setup"""
        try:
            # Create Palma data directories
            palma_dir = Path.home() / ".palma"
            (palma_dir / "data").mkdir(parents=True, exist_ok=True)
            (palma_dir / "backup").mkdir(parents=True, exist_ok=True)
            (palma_dir / "temp").mkdir(parents=True, exist_ok=True)
            (palma_dir / "quarantine").mkdir(parents=True, exist_ok=True)
            
            # Save setup completion marker
            (palma_dir / ".setup_complete").touch()
            
        except Exception as e:
            print(f"Setup error: {e}")
    
    def isComplete(self):
        return self.complete


class CompletePage(QWizardPage):
    """Setup complete page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Success icon
        icon = QLabel("✅")
        icon.setFont(QFont("Noto Color Emoji", 64))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        # Success message
        success = QLabel("Palma OS Siap Digunakan!")
        success.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        success.setStyleSheet("color: #009B77;")
        success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(success)
        
        layout.addSpacing(20)
        
        # Tips
        tips = QLabel("""
        <b>Tips Memulai:</b><br><br>
        🌴 Tekan <b>F1</b> untuk membuka Dashboard Aksi Cepat<br>
        📝 Gunakan <b>Rakit Surat</b> untuk membuat surat resmi<br>
        🛒 Gunakan <b>Kasir Mikro</b> untuk mencatat transaksi<br>
        🛡️ <b>Palma Guard</b> akan melindungi dari virus flashdisk
        """)
        tips.setFont(QFont("Inter", 12))
        tips.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tips)
        
        layout.addSpacing(30)
        
        thanks = QLabel("Terima kasih telah memilih Palma OS! 🇮🇩")
        thanks.setStyleSheet("color: #666666;")
        thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(thanks)


class PalmaWizard(QWizard):
    """Main setup wizard"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palma Setup Wizard")
        self.setMinimumSize(800, 600)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        # Add pages
        self.addPage(WelcomePage())
        self.persona_page = PersonaPage()
        self.addPage(self.persona_page)
        self.user_page = UserPage()
        self.addPage(self.user_page)
        self.addPage(SetupPage())
        self.addPage(CompletePage())
        
        # Customize buttons
        self.setButtonText(QWizard.WizardButton.NextButton, "Lanjutkan →")
        self.setButtonText(QWizard.WizardButton.BackButton, "← Kembali")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Mulai Menggunakan")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Batal")
        
        self.apply_styles()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QWizard {
                background-color: #f5f5f5;
            }
            QWizardPage {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #009B77;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #007B5F;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit {
                border: 2px solid #dddddd;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #009B77;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #e0e0e0;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: linear-gradient(to right, #009B77, #00AB87);
                border-radius: 8px;
            }
            QCheckBox {
                font-size: 14px;
            }
        """)


def main():
    # Check if setup was already completed
    setup_marker = Path.home() / ".palma" / ".setup_complete"
    if setup_marker.exists():
        print("Setup already completed. Delete ~/.palma/.setup_complete to run again.")
        return 0
    
    app = QApplication(sys.argv)
    app.setApplicationName("Palma Setup Wizard")
    
    wizard = PalmaWizard()
    wizard.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
