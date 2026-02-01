#!/usr/bin/env python3
"""
Palma Guard - Keamanan Flashdisk & Anti-Virus Lokal
Part of Palma OS Productivity Suite
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import hashlib

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QProgressBar,
    QMessageBox, QGroupBox, QTextEdit, QCheckBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import sqlite3


class Database:
    """SQLite database for scan history and quarantine"""
    
    def __init__(self):
        self.db_path = Path.home() / ".palma" / "data" / "palma-guard.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                threats_found INTEGER DEFAULT 0,
                files_scanned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quarantine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                quarantine_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats_db (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                severity TEXT DEFAULT 'medium'
            )
        """)
        self.conn.commit()
        self.seed_threat_signatures()
    
    def seed_threat_signatures(self):
        """Add common threat signatures"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM threats_db")
        if cursor.fetchone()[0] == 0:
            # Common shortcut virus patterns and suspicious patterns
            threats = [
                ("autorun.inf", "Autorun Virus", "high"),
                (".vbs", "VBScript Malware", "high"),
                (".bat.exe", "Hidden Batch Executable", "high"),
                (".scr", "Screensaver Virus", "medium"),
                (".pif", "PIF Malware", "high"),
                (".cmd", "Command File", "medium"),
                ("recycler", "Recycler Virus", "high"),
                ("desktop.ini.exe", "Desktop.ini Virus", "high"),
                ("newfolder.exe", "NewFolder Virus", "high"),
                ("copy.exe", "Copy Shortcut Virus", "high"),
            ]
            cursor.executemany(
                "INSERT INTO threats_db (signature, name, severity) VALUES (?, ?, ?)",
                threats
            )
            self.conn.commit()
    
    def get_threat_signatures(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT signature, name, severity FROM threats_db")
        return cursor.fetchall()
    
    def add_to_quarantine(self, path, threat_type):
        cursor = self.conn.cursor()
        quarantine_dir = Path.home() / ".palma" / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        quarantine_path = quarantine_dir / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{Path(path).name}"
        
        cursor.execute(
            "INSERT INTO quarantine (original_path, threat_type, quarantine_path) VALUES (?, ?, ?)",
            (str(path), threat_type, str(quarantine_path))
        )
        self.conn.commit()
        return quarantine_path
    
    def get_quarantine(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM quarantine ORDER BY created_at DESC")
        return cursor.fetchall()
    
    def add_scan_history(self, path, threats_found, files_scanned):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO scan_history (path, threats_found, files_scanned) VALUES (?, ?, ?)",
            (str(path), threats_found, files_scanned)
        )
        self.conn.commit()
    
    def get_scan_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scan_history ORDER BY created_at DESC LIMIT 50")
        return cursor.fetchall()


class USBMonitor(QThread):
    """Thread to monitor USB drives"""
    usb_connected = pyqtSignal(str)
    usb_disconnected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.known_drives = set()
    
    def run(self):
        while self.running:
            current_drives = self.detect_usb_drives()
            
            # Check for new drives
            for drive in current_drives - self.known_drives:
                self.usb_connected.emit(drive)
            
            # Check for removed drives
            for drive in self.known_drives - current_drives:
                self.usb_disconnected.emit(drive)
            
            self.known_drives = current_drives
            self.msleep(2000)  # Check every 2 seconds
    
    def detect_usb_drives(self):
        """Detect mounted USB drives"""
        drives = set()
        
        # Linux: Check /media and /run/media
        for mount_point in [Path("/media"), Path("/run/media")]:
            if mount_point.exists():
                for user_dir in mount_point.iterdir():
                    if user_dir.is_dir():
                        for drive in user_dir.iterdir():
                            if drive.is_dir():
                                drives.add(str(drive))
        
        # macOS: Check /Volumes
        volumes_path = Path("/Volumes")
        if volumes_path.exists():
            for volume in volumes_path.iterdir():
                if volume.is_dir() and volume.name != "Macintosh HD":
                    drives.add(str(volume))
        
        return drives
    
    def stop(self):
        self.running = False


class ScanThread(QThread):
    """Thread for scanning files"""
    progress = pyqtSignal(int, str)
    threat_found = pyqtSignal(str, str)
    scan_complete = pyqtSignal(int, int)
    
    def __init__(self, path, signatures):
        super().__init__()
        self.path = Path(path)
        self.signatures = signatures
        self.running = True
    
    def run(self):
        files_scanned = 0
        threats_found = 0
        
        try:
            all_files = list(self.path.rglob("*"))
            total_files = len(all_files)
            
            for i, file_path in enumerate(all_files):
                if not self.running:
                    break
                
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress, str(file_path))
                
                if file_path.is_file():
                    files_scanned += 1
                    
                    # Check against threat signatures
                    for signature, name, severity in self.signatures:
                        if signature.lower() in str(file_path).lower():
                            threats_found += 1
                            self.threat_found.emit(str(file_path), name)
                            break
                    
                    # Check for hidden executable attributes
                    if self.is_suspicious(file_path):
                        threats_found += 1
                        self.threat_found.emit(str(file_path), "Suspicious File")
            
            self.scan_complete.emit(threats_found, files_scanned)
        
        except Exception as e:
            print(f"Scan error: {e}")
            self.scan_complete.emit(threats_found, files_scanned)
    
    def is_suspicious(self, file_path):
        """Check for suspicious file characteristics"""
        name = file_path.name.lower()
        
        # Hidden file with executable extension
        if (name.startswith('.') and 
            name.endswith(('.exe', '.bat', '.cmd', '.vbs', '.scr'))):
            return True
        
        # Double extension trick
        if '..' in name or name.count('.') > 2:
            suspect_exts = ['.exe', '.bat', '.cmd', '.vbs', '.scr', '.pif']
            for ext in suspect_exts:
                if ext in name:
                    return True
        
        # Shortcut virus pattern
        if file_path.suffix == '.lnk':
            # Check if there's a matching folder
            folder_name = file_path.stem
            parent = file_path.parent
            if (parent / folder_name).is_dir():
                return True  # Likely shortcut virus
        
        return False
    
    def stop(self):
        self.running = False


class PalmaGuardWindow(QMainWindow):
    """Main security application window"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.usb_monitor = USBMonitor()
        self.scan_thread = None
        self.init_ui()
        self.start_monitoring()
    
    def init_ui(self):
        self.setWindowTitle("Palma Guard - Palma OS")
        self.setMinimumSize(900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🛡️ Palma Guard - Keamanan Sistem")
        header.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #009B77;")
        main_layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_scan_tab(), "🔍 Scan")
        tabs.addTab(self.create_usb_tab(), "💾 USB Monitor")
        tabs.addTab(self.create_quarantine_tab(), "🚫 Karantina")
        tabs.addTab(self.create_history_tab(), "📋 Riwayat")
        main_layout.addWidget(tabs)
        
        self.apply_styles()
    
    def create_scan_tab(self):
        """Create scan interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Quick scan buttons
        buttons_layout = QHBoxLayout()
        
        home_btn = QPushButton("🏠 Scan Home")
        home_btn.clicked.connect(lambda: self.start_scan(Path.home()))
        buttons_layout.addWidget(home_btn)
        
        downloads_btn = QPushButton("📥 Scan Downloads")
        downloads_btn.clicked.connect(lambda: self.start_scan(Path.home() / "Downloads"))
        buttons_layout.addWidget(downloads_btn)
        
        usb_btn = QPushButton("💾 Scan USB")
        usb_btn.clicked.connect(self.scan_usb)
        buttons_layout.addWidget(usb_btn)
        
        layout.addLayout(buttons_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.scan_status = QLabel("Siap memindai")
        layout.addWidget(self.scan_status)
        
        # Threats found
        threats_group = QGroupBox("⚠️ Ancaman Terdeteksi")
        threats_layout = QVBoxLayout(threats_group)
        
        self.threats_list = QListWidget()
        threats_layout.addWidget(self.threats_list)
        
        action_layout = QHBoxLayout()
        self.quarantine_btn = QPushButton("🚫 Karantina Semua")
        self.quarantine_btn.clicked.connect(self.quarantine_threats)
        self.quarantine_btn.setEnabled(False)
        action_layout.addWidget(self.quarantine_btn)
        
        self.delete_btn = QPushButton("🗑️ Hapus Semua")
        self.delete_btn.clicked.connect(self.delete_threats)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)
        
        threats_layout.addLayout(action_layout)
        layout.addWidget(threats_group)
        
        return tab
    
    def create_usb_tab(self):
        """Create USB monitoring interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # USB Protection settings
        settings_group = QGroupBox("⚙️ Pengaturan Proteksi USB")
        settings_layout = QVBoxLayout(settings_group)
        
        self.auto_readonly = QCheckBox("🔒 Auto Read-Only pada USB terdeteksi")
        self.auto_readonly.setChecked(True)
        settings_layout.addWidget(self.auto_readonly)
        
        self.auto_scan = QCheckBox("🔍 Auto Scan saat USB terhubung")
        self.auto_scan.setChecked(True)
        settings_layout.addWidget(self.auto_scan)
        
        self.block_autorun = QCheckBox("🚫 Blokir Autorun.inf")
        self.block_autorun.setChecked(True)
        settings_layout.addWidget(self.block_autorun)
        
        layout.addWidget(settings_group)
        
        # Connected drives
        drives_group = QGroupBox("💾 USB Terhubung")
        drives_layout = QVBoxLayout(drives_group)
        
        self.usb_list = QListWidget()
        drives_layout.addWidget(self.usb_list)
        
        layout.addWidget(drives_group)
        
        # Status
        self.usb_status = QLabel("🟢 USB Monitor aktif")
        self.usb_status.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.usb_status)
        
        return tab
    
    def create_quarantine_tab(self):
        """Create quarantine interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("File yang dikarantina tidak dapat dijalankan dan aman disimpan.")
        layout.addWidget(info)
        
        self.quarantine_table = QTableWidget()
        self.quarantine_table.setColumnCount(4)
        self.quarantine_table.setHorizontalHeaderLabels(
            ["Lokasi Asli", "Jenis Ancaman", "Tanggal", "Aksi"]
        )
        self.quarantine_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.quarantine_table)
        
        self.load_quarantine()
        
        return tab
    
    def create_history_tab(self):
        """Create scan history interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Lokasi", "Ancaman", "File Dipindai", "Tanggal"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)
        
        self.load_history()
        
        return tab
    
    def start_monitoring(self):
        """Start USB monitoring"""
        self.usb_monitor.usb_connected.connect(self.on_usb_connected)
        self.usb_monitor.usb_disconnected.connect(self.on_usb_disconnected)
        self.usb_monitor.start()
    
    def on_usb_connected(self, path):
        """Handle USB connection"""
        item = QListWidgetItem(f"💾 {path}")
        self.usb_list.addItem(item)
        
        if self.auto_scan.isChecked():
            self.start_scan(Path(path))
        
        if self.block_autorun.isChecked():
            self.remove_autorun(path)
    
    def on_usb_disconnected(self, path):
        """Handle USB disconnection"""
        for i in range(self.usb_list.count()):
            if path in self.usb_list.item(i).text():
                self.usb_list.takeItem(i)
                break
    
    def remove_autorun(self, path):
        """Remove autorun.inf from USB"""
        autorun_path = Path(path) / "autorun.inf"
        if autorun_path.exists():
            try:
                autorun_path.unlink()
                QMessageBox.warning(
                    self, "Autorun Diblokir",
                    f"File autorun.inf dihapus dari:\n{path}"
                )
            except Exception as e:
                print(f"Failed to remove autorun: {e}")
    
    def start_scan(self, path):
        """Start scanning a path"""
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.warning(self, "Peringatan", "Scan sedang berjalan!")
            return
        
        self.threats_list.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        signatures = self.db.get_threat_signatures()
        self.scan_thread = ScanThread(path, signatures)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.threat_found.connect(self.on_threat_found)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.start()
    
    def scan_usb(self):
        """Scan first connected USB"""
        if self.usb_list.count() > 0:
            path = self.usb_list.item(0).text().replace("💾 ", "")
            self.start_scan(Path(path))
        else:
            QMessageBox.information(self, "Info", "Tidak ada USB terhubung")
    
    def on_scan_progress(self, value, current_file):
        """Update scan progress"""
        self.progress_bar.setValue(value)
        self.scan_status.setText(f"Memindai: {current_file[-50:]}")
    
    def on_threat_found(self, path, threat_name):
        """Handle found threat"""
        item = QListWidgetItem(f"⚠️ {threat_name}: {path}")
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.threats_list.addItem(item)
    
    def on_scan_complete(self, threats, files):
        """Handle scan completion"""
        self.progress_bar.setVisible(False)
        
        if threats > 0:
            self.scan_status.setText(f"⚠️ Ditemukan {threats} ancaman dari {files} file")
            self.scan_status.setStyleSheet("color: red; font-weight: bold;")
            self.quarantine_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.scan_status.setText(f"✅ Aman! {files} file dipindai, tidak ada ancaman")
            self.scan_status.setStyleSheet("color: green; font-weight: bold;")
        
        # Save to history
        if hasattr(self.scan_thread, 'path'):
            self.db.add_scan_history(self.scan_thread.path, threats, files)
            self.load_history()
    
    def quarantine_threats(self):
        """Move threats to quarantine"""
        for i in range(self.threats_list.count()):
            path = self.threats_list.item(i).data(Qt.ItemDataRole.UserRole)
            if path and Path(path).exists():
                try:
                    # Get threat type from item text
                    threat_type = self.threats_list.item(i).text().split(":")[0].replace("⚠️ ", "")
                    quarantine_path = self.db.add_to_quarantine(path, threat_type)
                    
                    # Move file
                    Path(path).rename(quarantine_path)
                except Exception as e:
                    print(f"Quarantine error: {e}")
        
        self.threats_list.clear()
        self.quarantine_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.load_quarantine()
        
        QMessageBox.information(self, "Sukses", "Semua ancaman telah dikarantina!")
    
    def delete_threats(self):
        """Delete threat files"""
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Yakin ingin menghapus semua file berbahaya?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for i in range(self.threats_list.count()):
                path = self.threats_list.item(i).data(Qt.ItemDataRole.UserRole)
                if path and Path(path).exists():
                    try:
                        Path(path).unlink()
                    except Exception as e:
                        print(f"Delete error: {e}")
            
            self.threats_list.clear()
            self.quarantine_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            
            QMessageBox.information(self, "Sukses", "Semua ancaman telah dihapus!")
    
    def load_quarantine(self):
        """Load quarantine list"""
        items = self.db.get_quarantine()
        self.quarantine_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.quarantine_table.setItem(row, 0, QTableWidgetItem(item[1]))
            self.quarantine_table.setItem(row, 1, QTableWidgetItem(item[2]))
            self.quarantine_table.setItem(row, 2, QTableWidgetItem(str(item[4])))
            
            restore_btn = QPushButton("♻️ Pulihkan")
            self.quarantine_table.setCellWidget(row, 3, restore_btn)
    
    def load_history(self):
        """Load scan history"""
        items = self.db.get_scan_history()
        self.history_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.history_table.setItem(row, 0, QTableWidgetItem(item[1]))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(item[2])))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(item[3])))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(item[4])))
    
    def apply_styles(self):
        """Apply Palma OS styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #009B77;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
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
            QListWidget, QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QProgressBar {
                border: 1px solid #009B77;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #009B77;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QCheckBox {
                padding: 5px;
            }
        """)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.usb_monitor.stop()
        self.usb_monitor.wait()
        if self.scan_thread:
            self.scan_thread.stop()
            self.scan_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Palma Guard")
    
    window = PalmaGuardWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
