PALMA OS v1.2 - BLUEPRINT PRODUK LENGKAP
(Validated Design Thinking & Localized Solutions)
Kode Proyek: Palma-01 Versi: 1.2 (Alpha Release) Target Rilis: Q1 2026 Platform Base: Linux (Ubuntu 22.04 LTS) Arsitektur: 64-bit (fokus kompatibilitas Chromebook x86 & Laptop lama)

1. VALIDASI MASALAH & KONTEKS (2025-2026)
Sebelum pengembangan, data berikut menjadi dasar fitur:
* Aset Sia-sia: Chromebook sekolah senilai Rp9 Triliun tak terpakai (siswa/game only, tidak produktif).
* Digital Gap: 35% UMKM belum digital karena infrastruktur mahal dan literasi minim.
* Beban Administrasi: Guru & RT/RW kewalahan kerja manual (Excel tulis tangan, kwitansi kertas sobek).
* Konektivitas: 12% daerah masih blank spot (wajib Offline-First).
* Sosial: Karyawan kecil bingung BPJS, Petani loss karena stok rusak tak tercatat.

2. VISION & MISI
2.1 Visi
Menjadi OS nasional yang Zero-Lisensi, ringan, dan produktif, mengubah "sampah" teknologi (laptop tua/chromebook bekas) menjadi aset produktif untuk Guru, UMKM, dan Pemerintahan Desa.
2.2 Misi
1. Zero Barrier: Gratis legal, jalan mulus di RAM 2GB & penyimpanan 16GB.
2. Hyper-Local UX: Antarmuka mirip Windows 10 dengan pintasan konteks Indonesia (Satu klik urus RT/Surat).
3. Offline-Viable: Fitur krusial harus bekerja tanpa internet (database SQLite lokal).
4. Asset Revival: Mengoptimalkan Chromebook bekas sekolah agar bermanfaat untuk admin guru.

3. PERSONA & SOLUSI (Validated Problems)
PALMA OS v1.5.1 - BLUEPRINT PRODUK (FINAL DRAFT)
High-Fidelity Consultant Grade Specification
Kode Proyek: PALMA-REV-1.5.1 Status: Final Draft (Siap Eksekusi) Target Rilis: Q4 2024 (Alpha) - Q3 2025 (Revival Release) Platform Base: Linux (Ubuntu 24.04.1 LTS Minimal) Arsitektur: 64-bit (Optimasi Chromebook x86 & Legacy Laptop)

1. POSISI STRATEGIS (The Core Vision)
Palma OS bukan sekadar distro Linux biasa. Ini adalah Sovereign Operating System (OS Berdaulat) yang dirancang khusus untuk produktivitas lokal tanpa ketergantungan pada lisensi mahal atau infrastruktur cloud berat.
* Value Proposition: Mentransformasi "sampah teknologi" menjadi stasiun kerja produktif untuk Pemerintahan, UMKM, Pendidikan, dan Pengguna Personal.
* Tagline: "Hidupkan Kembali, Produktifkan Indonesia."
* Model Bisnis:
    * B2G (Business to Government): Layanan kustom untuk instansi pemerintah, sekolah, dan kantor desa/kelurahan (Administrasi & TKDN).
    * B2B (Business to Business): Solusi digital terintegrasi untuk Koperasi dan UMKM.
    * B2C (Consumer): Dukungan donasi/paid support untuk pengguna personal (Rumahan).

2. ARSITEKTUR TEKNIS (The Performance Engine)
Sistem ini dibangun dengan filosofi "Performa Maksimal di Hardware Minimal".
2.1 Fondasi Sistem
* Base Distro: Ubuntu 24.04.1 LTS Minimal (Noble Numbat). Dukungan jangka panjang hingga 2029+.
* Kernel: Liquorix Kernel v6.x. Kernel modifikasi yang sangat agresif dalam manajemen proses, memberikan responsivitas desktop instan pada CPU dual-core lawas.
* Driver Khusus: Integrasi depthcharge-tools & sof-firmware terbaru untuk menjamin Speaker, Mikrofon, dan Touchpad pada Chromebook berfungsi out-of-the-box tanpa konfigurasi manual.
* Filesystem: Btrfs dengan opsi mount compress=zstd:3. Kompresi data transparan ini menghemat hingga 40% storage eMMC terbatas tanpa mengorbankan kecepatan baca/tulis.
2.2 Manajemen Memori (The 2GB Specialist)
Dirancang khusus agar tidak macet di RAM 2GB.
* Zram: Swap terkompresi di RAM (Kapasitas 150% dari fisik). Memungkinkan multitasking tanpa menyentuk harddisk lambat.
* EarlyOOM: Daemon cerdas yang otomatis menutup proses "nakal" atau yang membeku sebelum sistem mengalami kernel panic (hang total).
* Preload/Prelink: Menganalisis kebiasaan pengguna dan memuat aplikasi yang sering dipakai ke memori, mempercepat waktu buka aplikasi hingga 40%.

3. MODULAR PERSONA ENGINE (The OOBE)
Palma Setup Wizard akan muncul saat first-boot. Sistem akan menanyakan peran pengguna dan mengkonfigurasi OS secara otomatis sesuai kebutuhan.
Profil	Paket Aplikasi Utama	Fokus UX & Fitur
Pendidik (Sekolah)	Rakit Surat Pro, OnlyOffice, Kiwix Edu, PDF Tools	Administrasi Cepat: Prioritas manajemen rapor & print.
Pemerintahan (Publik)	Admin Publik, Sensus Lokal, Digital Sign, Flatpak Scanner	Keamanan Data: Enkripsi data warga/pasien & legalitas dokumen.
Niaga (UMKM)	Kasir Mikro, Inventaris Barang, Palma Share, WhatsApp Bridge	Kecepatan Transaksi: Struk instan & laporan laba rugi sederhana.
Personal (Rumahan)	Browser, Media Player, Palma Guard, Photo Editor	Simpel & Aman: Fokus browsing, hiburan, dan keamanan keluarga.
Pelajar	Mode Fokus, KBBI Offline, Khan Academy Offline, LaTeX Light	Proteksi Konten: Blokir game/distraksi, minimalkan notifikasi.
4. PALMA PRODUCTIVITY SUITE (Custom Python Apps)
Semua aplikasi inti dibangun menggunakan PyQt6 (Modern & Cepat) dengan konsumsi RAM rata-rata <25MB per aplikasi.
1. Rakit Surat Pro:
    * Tool administrasi birokrasi instan.
    * Database 100+ template surat resmi (SK, Undangan, Izin, Surat Keterangan, Surat Dinas).
    * Fitur Unggulan: Mail Merge (Impor data Excel daftar nama -> Otomatis buat 100 surat sekaligus).
2. Admin Publik (General Government):
    * Database lokal terenkripsi (AES-256) yang fleksibel. Bisa untuk data Warga (Desa/Kelurahan), Siswa (Sekolah), atau Pasien (Puskesmas).
    * Fitur pencatatan administrasi (Iuran, SPP, Pajak) dengan status visual (Lunas/Hutang).
    * Ekspor laporan bulanan PDF otomatis untuk keperluan rapat atau audit.
3. Kasir Mikro:
    * Point-of-Sale (POS) minimalis untuk warung/toko kelontong.
    * Fitur Unggulan: QR-Transfer. Sistem membuat link pembayaran/struk digital yang bisa langsung dikirim ke WA pelanggan sebagai bukti bayar.
4. Palma Guard:
    * Solusi anti-virus khas Indonesia untuk Personal & Kantor.
    * Mode "Auto Read-Only" pada Flashdisk terdeteksi untuk mencegah penyebaran virus shortcut tanpa perlu antivirus berat.
5. Palma Share:
    * Aplikasi Transfer File P2P Lokal. Kirim file (foto/dokumen) antar laptop di jaringan Wi-Fi yang sama tanpa kabel data dan tanpa internet (seperti LocalSend tapi integrasi native). Sangat berguna untuk pengguna Personal & UMKM.
6. Gudang Benih:
    * Sistem backup disaster recovery satu-klik.
    * Mem-backup seluruh database Palma (Surat, Data Publik, Transaksi, Foto Keluarga) ke penyimpanan eksternal/Flashdisk dengan otomatis.

5. UI/UX: NATIVE COMFORT
Antarmuka yang familiar tapi ringan.
* Desktop Environment: XFCE 4.18 (Heavily Customized).
* Visual Identity: "Palma Glass". Menggunakan warna Emerald Green dan Golden Palm dengan efek transparansi modern.
* Typography: Kombinasi Inter (UI) & Noto Sans (Dokumen) untuk keterbacaan maksimal di layar resolusi rendah (1366x768).
* Dashboard Aksi Cepat (F1): Sidebar pop-up transparan yang berisi:
    * Kalkulator.
    * Kalender Pajak/Tanggal Merah.
    * Pintasan 5 aplikasi favorit pengguna.

6. OFFICE SUITE STRATEGI (Pergeseran Besar)
Perubahan Kritis: Mengganti pendekatan PWA (Browser-based) dengan Aplikasi Native.
* Pilihan Utama: OnlyOffice Desktop Editors.
* Alasan Konsultan:
    * Jauh lebih ringan daripada LibreOffice.
    * Kompatibilitas format .docx/.xlsx sangat tinggi (lebih baik dari LibreOffice).
    * Mampu bekerja 100% Offline (Tidak ada risiko "loading circle" karena gangguan internet).
    * Tampilan sangat mirip Microsoft Office 2016+, meminimalkan kurva belajar user Personal maupun Pemerintahan.

7. DATA GOVERNANCE: LOCAL-FIRST
Indonesia memiliki masalah konektivitas. Palma mengutamakan kedaulatan data.
* Kedaulatan Data: Semua database SQLite disimpan lokal di /home/user/.palma/data/.
* Zero-Telemetri: Tidak ada data penggunaan (usage stats) yang dikirim ke server pusat tanpa izin eksplisit pengguna.
* Encrypted Sync: Modul opsional (via Rclone atau GUI) untuk sinkronisasi folder dokumen terpilih ke Google Drive/OneDrive hanya jika user mengaktifkannya.

8. STRATEGI DISTRIBUSI & HARDWARE
8.1 Palma Flash-Tool
Aplikasi installer mandiri untuk Windows (.exe) yang membantu pengguna awam membuat USB Bootable Palma.
* Dilengkapi panduan visual animasi khusus untuk membuka BIOS Chromebook berdasarkan merk (Acer, Asus, HP, Lenovo).
8.2 Hardware Compatibility List (HCL)
Palma akan merilis daftar perangkat yang divalidasi:
* Gold Tier: Kompatibilitas 100% (Speaker, Mic, WiFi, Bluetooth, Touchpad berfungsi sempurna).
* Silver Tier: Kompatibilitas 90% (Mungkin memerlukan dongle USB untuk WiFi/Fungsi tertentu).

9. ROADMAP EKSEKUSI (2024-2025)
* Q4 2024: Finalisasi 6 Aplikasi Inti (OnlyOffice Integrasi), Build Beta v1.5.1.
* Q1 2025: Pilot Project B2G di 5 Lokasi (Campuran Desa, Sekolah, dan Puskesmas) untuk validasi fitur "Admin Publik".
* Q2 2025: Optimasi Driver Audio/Touchpad untuk Top 10 Model Chromebook Hibah Sekolah.
* Q3 2025: Peluncuran Publik Palma OS v1.5 "Revival".

10. REKOMENDASI KRITIS KONSULTAN (Must-Do)
1. Sertifikasi TKDN (Tingkat Komponen Dalam Negeri):
    * Segera daftarkan aspek software dan modifikasi kernel Palma OS ke lembaga sertifikasi.
    * Tujuan: Memenuhi syarat wajib pengadaan barang/jasa di instansi pemerintah (e-Katalog/LKPP). Ini adalah "Golden Ticket" pasar B2G.
2. Pendekatan "Personal" (Rumahan):
    * Untuk pasar personal, tonjolkan fitur "Anti-Virus" dan "Anak-anak Aman" (Mode Pelajar/Parental Control sederhana).
    * Jualan ke ibu-ibu atau orang tua yang khawatir anaknya main game tidak jelas atau laptop kena virus.
3. Model Dukungan Komunitas:
    * Bangun forum dukungan lokal yang kuat (Telegram/FB Group).
    * Tim inti fokus pengembangan fitur, sementara komunitas menangani masalah driver spesifik laptop (Crowdsourcing support).

Dokumen ini adalah standar final untuk pengembangan Palma OS v1.5.1.

4. SPESIFIKASI TEKNIS (The Foundation)
4.1 Base System & Kernel
* Distro: Ubuntu 22.04 LTS (Jammy Jellyfish) - Stabil & support panjang.
* Kernel: Linux Kernel 5.15 LTS (Kompatibel driver laptop tua & Chromebook).
* Desktop Environment: XFCE 4.18 + Compositor (Picit).
* Display Server: Xorg (Pilih Xorg daripada Wayland untuk kompatibilitas Chromebook/laptop tua).
* Optimasi Boot: Implementasi Preload & Zram (Swap terkompresi di RAM) agar boot <30 detik di RAM 2GB.
4.2 Database Engine
* SQLite 3: Wajib untuk semua aplikasi custom Python. Ringan, serverless, single file database. Aman dari kehilangan data karena listrik padam mendadak (transactional).
4.3 Hardware Target (Minimum Viable)
* CPU: Intel Dual Core / AMD APU (Tahun 2010 ke atas) / Intel Celeron (Chromebook).
* RAM: 2 GB (Bisa jalan), 4 GB (Recommended).
* Storage: 16 GB (SSD/eMMC).
* Screen: Resolusi 1366x768 ke bawah tetap readable (scaling font otomatis).

5. DESAIN & USER EXPERIENCE (UX/UI)
5.1 Identitas Visual: "Tropical Modern"
* Palet Warna:
    * Palma Green: #009B77 (Taskbar, Header, Tombol Utama).
    * Golden Palm: #FFD700 (Start Button, Notifikasi Penting).
    * Background: Default wallpaper "Pagi di Sawah" (Art style bersih).
* Tipografi: Noto Sans (Support huruf Latin & Indonesia sempurna).
5.2 Dashboard Home: "Apa Masalah Hari Ini?"
Ini adalah fitur UX pembeda. Saat OS booting, user tidak melihat desktop kosong, melainkan Dashboard sederhana dengan tombol besar berbasis Problem Solving:
1. [Saya Guru] -> Buka Rakit Surat & Absensi.
2. [Saya Warga] -> Buka Admin RW.
3. [Saya Usaha] -> Buka Kwitansi Digital.
4. [Saya Belajar] -> Buka Mode Fokus & Wiki.
5.3 File Manager (Thunar Custom)
* Breadcrumb Lokal: Path tidak menampilkan /home/user, tapi "Dokumen Saya > Sekolah > Rapor" atau "Dokumen Saya > RT > Iuran".
* Sidebar: Shortcut otomatis ke folder Google Drive Offline (jika ada) dan Folder Proyek Palma.

6. CORE APPLICATIONS (Super Lengkap)
6.1 Office & Web Suite (The Standard)
* Office: Google Docs, Sheets, Slides (via Google Chrome PWA - Progressive Web App).
    * Mode "Open as Window" diaktifkan agar seperti aplikasi native.
    * Offline Access aktif by default.
* PDF Tools: Evince (Reader) + PDF-Shuffler (Merge/Split).
* Browser: Google Chrome (Stabil untuk PWA).
6.2 Custom Python Apps (8 Total - PyQt5/Tkinter)
Semua aplikasi dibuat agar RAM usage <30MB per app. Backend HTML-to-PDF.
1. Rakit Surat v2 (Flagship)
    * Fitur: 50+ Template (SK, Undangan, Surat Lamaran, Kwitansi).
    * Baru: Modul Absensi Kelas (Import data siswa, cetak laporan kehadiran Excel/PDF, Scan QR Code manual entry).
2. Pembersih Daun (System Cleaner)
    * Fitur: Satu klik flush cache browser, temp file, dan memori swap.
3. Gudang Benih (Backup Tool)
    * Fitur: Deteksi otomatis Flashdisk -> Backup folder "Dokumen Saya" & "Database Palma".
4. Admin RW v1 (Community)
    * Fitur: Database warga (RT/RW), Pencatatan Iuran Bulanan (Status Lunas/Belum), Export Laporan Keuangan PDF.
5. Kwitansi Digital v1 (UMKM)
    * Fitur: Input transaksi -> Generate PDF Kwitansi profesional -> Logo UMKM (opsional) -> Tombol "Share ke WA" (membuka WA Web dengan file terlampir).
6. Cek BPJS v1 (Employment)
    * Fitur: Input Gaji -> Simulasi potongan JHT/JP -> Export surat keterangan estimasi iuran. (Bukan akses data real, tapi alat bantu hitung).
7. Catat Panen v1 (Agriculture)
    * Fitur: Input stok panen -> Tanggal panen -> Notifikasi jika melewati tanggal kadaluarsa ( estimasi busuk) -> Catat harga jual rata-rata.
8. Pesan Sekolah (Communication)
    * Fitur: Template surat pemberitahuan untuk orang tua (Wali Murid), Cetak pengumuman libur/ujian dalam sekejap.
6.3 Edukasi & Hiburan
* Knowledge: Wikipedia Offline (Kiwix) + KBBI Offline (SQLite DB).
* Media: VLC Media Player (Support semua format), Simple Paint (Gantikan MS Paint).

7. LOKALISASI PENUH (Indonesianization)
* Bahasa Sistem: Bahasa Indonesia (Formal & Baku).
* Format:
    * Tanggal: DD/MM/YYYY.
    * Angka/Uang: Rp 10.000 (Pemisah ribuan titik, desimal koma).
    * Jam: 24 Jam (Militer) atau AM/PM (User toggle).
* Dokumentasi: File "Panduan Palma.pdf" (20 Halaman) di Desktop:
    * Bab 1: Mengatasi Admin Guru (Pakai Rakit Surat).
    * Bab 2: Digitalisasi Iuran RT (Pakai Admin RW).
    * Bab 3: Tips UMKM Offline (Pakai Kwitansi Digital).
    * Bab 4: Troubleshooting (Wi-Fi, Printer).

8. WORKFLOW PEMBUATAN (Development Pipeline)
1. Environment Setup: Install Ubuntu 22.04 di VirtualBox (RAM 2GB setting untuk simulasi low-spec).
2. ISO Customization: Gunakan Cubic.
3. Coding Phase:
    * Kembangkan 8 App Python (PyQt5).
    * Pastikan semua app error-free saat database kosong (First run).
4. Integration Phase (Cubic):
    * Install xubuntu-desktop meta-package.
    * Copy file-file Python App ke /opt/palma-apps/.
    * Copy file .desktop (shortcut) ke /usr/share/applications/.
    * Copy Tema GTK "Palma Green" ke /usr/share/themes.
5. Preloading & Tweaking: Edit /etc/rc.local atau systemd service untuk load aplikasi daemon backup di background.
6. QA (Quality Assurance):
    * Beta Test di grup Facebook "Guru Indonesia", "UMKM Digital", "Komunitas RW".
    * Fokus: "Apak aplikasi jalan saat offline total?"

9. KEAMANAN & STABILITAS
* User Policy: Default user bukan root. Password dibutuhkan untuk install aplikasi/update.
* Firewall: UFW (Uncomplicated Firewall) aktif default (deny incoming, allow outgoing).
* App Sandboxing: Custom Python apps berjalan di user level, tidak memodifikasi system file.
* Offline Privacy: Karena banyak data tersimpan lokal (SQLite), data warga/iuran/keuangan tidak bocor ke cloud. Aman dari peretasan cloud-based.

10. PELUNCURAN & DISTRIBUSI
* Website: palma-os.id.
    * CTA: "Download Gratis".
    * Konten: Video Demo singkat (30 detik) guru membuat surat SK dalam 10 detik.
* File ISO: Maksimal 3.0 GB (Masih muat di Flashdisk 4GB murah).
* Strategi Viral: Share manual ke Grup WA RT/RW dan Grup Guru Provinsi.
* Tagline: "Hidupkan Laptop Lama, Produktifkan Indonesia."

11. ROADMAP MASA DEPAN (v2.0+)
* Sync Cloud Gratis: Integrasi otomatis ke Google Drive khusus folder Palma (One-way sync).
* Kebun Apps: App Store kurasi khusus (Pembelajaran SD/SMP, Simulasi UNBK offline).
* Hardware Ekspansi: Versi ARM untuk Raspberry Pi (Sebagai server sekolah desa murah).
* AI Integration: Fitur AI sederhana di "Catat Panen" (Prediksi harga pasar berdasarkan data historis).
* Remote Support: Tool built-in bantu jarak jauh (Via AnyDesk/Open source alternative) untuk pusat bantuan Palma.

Dokumen ini adalah sumber kebenaran mutlak bagi tim pengembang Palma OS.
