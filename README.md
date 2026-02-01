# Palma OS

> **"Hidupkan Kembali, Produktifkan Indonesia"**

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Ubuntu](https://img.shields.io/badge/base-Ubuntu%2024.04%20LTS-orange)

Palma OS adalah distro Linux berbasis **Ubuntu 24.04 LTS** dengan desktop **XFCE** yang dirancang khusus untuk:

- 🏫 **Chromebook sekolah** yang tidak produktif
- 💻 **Laptop lama** dengan RAM 2GB+
- 🏪 **UMKM** yang butuh solusi kasir offline
- 👨‍🏫 **Guru** yang kewalahan administrasi
- 🏘️ **RT/RW & Pemerintahan Desa** yang butuh digitalisasi

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Zero-Lisensi** | 100% gratis dan legal |
| **Ultra Ringan** | Jalan mulus di RAM 2GB, Storage 16GB |
| **Offline-First** | Semua aplikasi bekerja tanpa internet |
| **UX Familiar** | Tampilan mirip Windows 10 |
| **Apps Produktivitas** | Rakit Surat, Kasir Mikro, dll |

## 📦 Aplikasi Bawaan

### Core Apps (PyQt6)
- **Rakit Surat Pro** - Template 50+ surat resmi (SK, Undangan, Kwitansi)
- **Kasir Mikro** - POS sederhana dengan QR-Transfer
- **Palma Guard** - Keamanan flashdisk & anti-virus lokal

### Office & Internet
- **OnlyOffice** - Kompatibel dengan .docx/.xlsx
- **Firefox** - Browser modern
- **Evince** - PDF Reader

## 🛠️ Spesifikasi Minimum

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| CPU | Intel Dual Core (2010+) | Intel Core i3+ |
| RAM | 2 GB | 4 GB |
| Storage | 16 GB | 32 GB |
| Display | 1366x768 | 1920x1080 |

## 🚀 Quick Start

### Download ISO
```bash
# Coming soon - Release Q1 2026
```

### Build from Source
```bash
# Clone repository
git clone https://github.com/temamumtaza/palmaOS.git
cd palmaOS

# Build ISO (requires Ubuntu/Debian)
./build/build.sh
```

## 📁 Struktur Project

```
palmaOS/
├── apps/                  # Aplikasi PyQt6
│   ├── rakit-surat/       # Generator template surat
│   ├── kasir-mikro/       # Point of Sale
│   └── palma-guard/       # Security tool
├── build/                 # ISO build system
├── themes/                # XFCE themes
├── oobe/                  # First-run wizard
└── docs/                  # Dokumentasi
```

## 🤝 Kontribusi

Kami menyambut kontribusi dari komunitas! Baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan.

## 📄 Lisensi

Project ini dilisensikan di bawah [MIT License](LICENSE).

---

**Palma OS** - Hidupkan Laptop Lama, Produktifkan Indonesia 🇮🇩
