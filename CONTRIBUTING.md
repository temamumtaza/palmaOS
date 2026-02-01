# Panduan Kontribusi Palma OS

Terima kasih atas minat Anda untuk berkontribusi ke Palma OS! 🌴

## Cara Berkontribusi

### 1. Fork & Clone
```bash
git fork https://github.com/temamumtaza/palmaOS
git clone https://github.com/YOUR_USERNAME/palmaOS.git
cd palmaOS
```

### 2. Buat Branch Baru
```bash
git checkout -b fitur/nama-fitur
# atau
git checkout -b fix/nama-bug
```

### 3. Development Setup

#### Untuk Aplikasi PyQt6:
```bash
cd apps/rakit-surat  # atau app lainnya
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Untuk Build ISO:
```bash
# Membutuhkan Ubuntu/Debian
sudo apt install live-build debootstrap squashfs-tools
./build/build.sh --test
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: deskripsi singkat perubahan"
git push origin fitur/nama-fitur
```

### 5. Buat Pull Request
Buka GitHub dan buat Pull Request ke branch `main`.

## Coding Standards

### Python (PyQt6 Apps)
- Gunakan Python 3.11+
- Format dengan `black`
- Lint dengan `flake8`
- Type hints dianjurkan

### Shell Scripts
- Gunakan `#!/bin/bash`
- Ikuti Google Shell Style Guide
- Semua script harus executable

## Struktur Commit Message

```
<type>: <subject>

<body> (opsional)
```

**Types:**
- `feat`: Fitur baru
- `fix`: Bug fix
- `docs`: Dokumentasi
- `style`: Formatting
- `refactor`: Refactoring code
- `test`: Menambah tests
- `chore`: Maintenance

## Area Kontribusi

| Area | Skill | Prioritas |
|------|-------|-----------|
| Apps PyQt6 | Python, Qt | 🔴 High |
| ISO Build | Bash, Linux | 🟡 Medium |
| Themes | GTK, CSS | 🟢 Low |
| Docs | Markdown | 🟢 Low |
| Testing | Python, VM | 🟡 Medium |

## Kontak

- GitHub Issues: Untuk bug reports & feature requests
- Discussions: Untuk diskusi umum

---

Setiap kontribusi, sekecil apapun, sangat berarti! 🙏
