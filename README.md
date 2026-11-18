# GoRent - Sistem Informasi Penyewaan Kendaraan

**Kelompok 3 | Kelas C | Program Studi S1 Sistem Informasi**
Jurusan Teknologi Informasi, Fakultas Teknik, Universitas Tadulako, 2026
Proyek Praktikum Rekayasa Perangkat Lunak (UTS dan UAS)

## Anggota Kelompok

| No. | Nama | NIM | Peran Utama |
|----|------|-----|-------------|
| 1 | Rafli Lamatolo | F5212520085 | SRS |
| 2 | Jaya Rahman | F5212520086 | MVC |
| 3 | Triana Agista Karin Pombalawo | F5212520090 | UML |
| 4 | Muhammad Dzaki Kurniawan | F5212530102 | Database |
| 5 | Muhammad Refinaldy | F5212530111 | UML |
| 6 | Rasya Aditya | F5212530114 | MVC |

## Deskripsi

GoRent adalah aplikasi desktop untuk mengelola penyewaan kendaraan (motor dan mobil) pada usaha rental skala kecil. Aplikasi ini menggantikan pencatatan manual di buku tulis atau pesan singkat yang mudah hilang, sulit dicari, dan rawan salah hitung.

Aplikasi dibuat dengan Python, CustomTkinter, dan MySQL (Laragon), menggunakan arsitektur **Model, View, Controller (MVC)**. Total biaya sewa, denda keterlambatan, tagihan pembayaran, dan status kendaraan dihitung serta diperbarui otomatis oleh sistem.

Pengguna masuk melalui halaman **login** dan mendapat dashboard sesuai perannya. Sistem memiliki tiga aktor:

- **Admin (Petugas Rental)**: mengelola kendaraan dan pelanggan, memantau dan membatalkan penyewaan, memproses pengajuan pengembalian, dan mengelola status pembayaran.
- **Pelanggan**: mendaftar sendiri, melihat kendaraan, menyewa kendaraan, membayar tagihan, mengajukan pengembalian, dan melihat riwayat.
- **Pemilik Rental**: memantau data penyewaan dan pengembalian serta melihat laporan (hanya baca).

## Tujuan

- Menggantikan pencatatan manual dengan data yang tersimpan di basis data.
- Menghitung total biaya sewa dan denda keterlambatan secara otomatis.
- Menjaga status kendaraan tetap konsisten (Tersedia, Disewa, Perawatan) dan mencegah kendaraan disewakan ganda.
- Membatasi hak akses setiap aktor, baik di tampilan maupun di controller.
- Memberi Pemilik Rental ringkasan transaksi dan pendapatan per periode.
- Menerapkan arsitektur MVC pada aplikasi desktop Python yang terhubung ke MySQL.

## Fitur

### Umum

- Registrasi akun (Pelanggan atau Pemilik Rental), login, dan logout.
- Loading screen yang memeriksa koneksi database saat aplikasi dibuka.
- Pembatasan akses per peran (dekorator `wajib_role` di controller).
- Pemilih tanggal (date picker) pada form berisi tanggal.

### Admin

| Menu | Fungsi |
|------|--------|
| Kendaraan | Tambah kendaraan (status awal Tersedia), ubah status (Tersedia atau Perawatan), hapus kendaraan |
| Pelanggan | Lihat, ubah, dan hapus data pelanggan |
| Peminjaman | Lihat daftar penyewaan dan batalkan penyewaan yang belum dibayar |
| Pengembalian | Lihat pengajuan pengembalian, konfirmasi (tanggal dapat dikoreksi) atau tolak, serta lihat riwayat |
| Pembayaran | Lihat semua pembayaran dan ubah statusnya (Menunggu atau Lunas) |

### Pelanggan

| Menu | Fungsi |
|------|--------|
| Kendaraan | Melihat daftar kendaraan |
| Sewa Kendaraan | Memilih kendaraan yang tersedia dan membuat penyewaan sendiri |
| Pembayaran | Melihat tagihan dan membayar (Tunai, Transfer, atau E-Wallet) |
| Pengembalian | Mengajukan pengembalian pada tanggal pilihan dan melihat riwayatnya |
| Riwayat | Melihat riwayat penyewaan milik sendiri |

### Pemilik Rental (hanya baca)

| Menu | Fungsi |
|------|--------|
| Data Peminjaman | Melihat seluruh penyewaan |
| Data Pengembalian | Melihat seluruh pengembalian |
| Laporan | Ringkasan per periode: jumlah transaksi, pendapatan sewa, pendapatan denda, total, pembayaran menunggu, dan 10 kendaraan terlaris |

## Aturan Bisnis

**Kendaraan**
- Jenis hanya **Motor** atau **Mobil**; merek dan nomor polisi wajib diisi; tarif harian harus angka lebih dari nol.
- Status **Disewa** tidak dapat diatur manual, hanya berubah lewat proses penyewaan. Status kendaraan yang sedang disewa tidak dapat diubah.
- Kendaraan hanya dapat dihapus jika berstatus Tersedia **dan** belum pernah memiliki riwayat penyewaan.

**Penyewaan**
- Tanggal berformat `YYYY-MM-DD`; tanggal kembali tidak boleh sebelum tanggal mulai; pelanggan tidak dapat memilih tanggal mulai yang sudah lewat.
- Transaksi hanya untuk akun berperan Pelanggan dan kendaraan berstatus Tersedia. Baris kendaraan dikunci (`FOR UPDATE`) agar tidak terjadi sewa ganda.
- **Total biaya** = jumlah hari x tarif harian, dengan jumlah hari = (tanggal rencana kembali - tanggal mulai) + 1.
- Saat penyewaan dibuat, tagihan pembayaran jenis **Sewa** (status Menunggu) dibuat otomatis dan kendaraan menjadi Disewa.
- Admin dapat membatalkan penyewaan hanya jika masih Berjalan, belum ada pengajuan pengembalian, dan belum ada pembayaran Lunas. Saat dibatalkan, kendaraan kembali Tersedia.

**Pengembalian**
- Pelanggan mengajukan pengembalian (status **Diajukan**) pada tanggal pilihannya; denda langsung dihitung.
- Admin mengonfirmasi (status **Dikonfirmasi**) atau menolak pengajuan. Admin tidak dapat memproses pengembalian yang belum diajukan pelanggan.
- **Denda** = jumlah hari terlambat x tarif harian, dengan hari terlambat = selisih tanggal kembali dan tanggal rencana kembali (minimal 0).
- Saat dikonfirmasi: status penyewaan menjadi **Selesai**, kendaraan kembali **Tersedia**, dan bila terlambat dibuat tagihan jenis **Denda** (status Menunggu).
- Satu penyewaan hanya dapat dikembalikan satu kali.

**Pembayaran**
- Jenis pembayaran: **Sewa** atau **Denda**; satu penyewaan paling banyak satu tagihan per jenis.
- Pelanggan hanya dapat membayar tagihan miliknya sendiri dan tagihan yang belum lunas. Metode: Tunai, Transfer, atau E-Wallet.
- Admin dapat mengubah status menjadi Lunas (metode otomatis Tunai bila kosong) atau mengembalikannya ke Menunggu.

**Akun**
- Password disimpan sebagai hash **SHA-256**.
- Registrasi mandiri hanya untuk peran Pelanggan dan Pemilik Rental; akun Admin berasal dari data awal di `database.sql`.
- Username dan nomor identitas harus unik.

Contoh: kendaraan bertarif Rp250.000 per hari disewa 3 hari menghasilkan total biaya Rp750.000. Jika dikembalikan terlambat 2 hari, denda Rp500.000.

## Teknologi

- Python 3.10 atau lebih baru
- CustomTkinter (GUI desktop) dan Pillow (gambar dan logo)
- mysql-connector-python (koneksi database dengan parameterized query)
- MySQL 8.x dengan Laragon
- pytest dan pytest-cov (pengujian otomatis)
- GitHub Actions (CI: Flake8 dan Pytest)
- Draw.io (pemodelan diagram), Visual Studio Code, Git, dan GitHub

## Arsitektur

```
Pengguna -> View -> Controller -> Model -> config/database.py -> MySQL
```

- **View** menampilkan form, tabel, dan dashboard per peran, lalu meneruskan aksi pengguna ke Controller.
- **Controller** memeriksa hak akses (`controllers/akses.py`) dan memanggil Model yang sesuai.
- **Model** menjalankan query SQL, menghitung biaya dan denda, serta menjalankan proses penyewaan, pengembalian, pembayaran, dan pembatalan dalam satu transaksi (di-rollback bila gagal).
- **AuthController** mengatur alur login, dashboard sesuai peran, dan logout.

## Struktur Proyek

```
Gorent/
├── main.py                          # titik masuk aplikasi
├── database.sql                     # skema database dan akun admin awal
├── requirements.txt                 # dependensi
├── config/
│   └── database.py                  # koneksi MySQL (class Database)
├── models/
│   ├── user_model.py                # akun, autentikasi, data pelanggan
│   ├── kendaraanModel.py            # tabel kendaraan
│   ├── penyewaanModel.py            # tabel penyewaan
│   ├── pengembalianModel.py         # tabel pengembalian dan denda
│   ├── pembayaranModel.py           # tabel pembayaran
│   └── laporanModel.py              # ringkasan laporan
├── controllers/
│   ├── akses.py                     # Session dan dekorator wajib_role
│   ├── auth_controller.py           # alur login, dashboard, logout
│   ├── user_controller.py
│   ├── kendaraan_controller.py
│   ├── penyewaan_controller.py
│   ├── pengembalian_controller.py
│   ├── pembayaran_controller.py
│   └── laporan_controller.py
├── views/
│   ├── app_window.py                # jendela utama
│   ├── auth/                        # login dan registrasi
│   ├── admin/                       # dashboard dan tab Admin
│   ├── pelanggan/                   # dashboard dan tab Pelanggan
│   ├── pemilik/                     # dashboard dan tab Pemilik Rental
│   └── shared/                      # tema, komponen, date picker, splash, aset
├── assets/                          # logo dan ikon aplikasi
├── test/                            # pengujian otomatis (pytest)
└── .github/workflows/ci_pipeline.yml  # CI GitHub Actions
```

## Basis Data

Nama database: `Gorent` (lima tabel), dibuat melalui `database.sql`.

| Tabel | Isi Utama | Relasi |
|-------|-----------|--------|
| `user` | username (unik), password (hash), no_identitas (unik), no_telepon, role (Admin, Pelanggan, Pemilik Rental) | Satu pelanggan dapat melakukan banyak penyewaan |
| `kendaraan` | jenis, merek, nomor_polisi (unik), tarif_harian, status (Tersedia, Disewa, Perawatan) | Satu kendaraan dapat muncul pada banyak penyewaan |
| `penyewaan` | pelanggan_id, kendaraan_id, tanggal_mulai, tanggal_rencana_kembali, total_biaya, status (Berjalan atau Selesai) | FK ke `user` dan `kendaraan` |
| `pengembalian` | penyewaan_id (unik), tanggal_kembali, denda, status (Diajukan atau Dikonfirmasi) | Satu penyewaan paling banyak satu pengembalian |
| `pembayaran` | penyewaan_id, jenis (Sewa atau Denda), jumlah, metode, status (Menunggu atau Lunas), tanggal_bayar | FK ke `penyewaan`; unik per (penyewaan_id, jenis) |

## Cara Menjalankan

1. Jalankan MySQL di Laragon.
2. Buat database dan tabel dengan mengimpor `database.sql` (lewat HeidiSQL/phpMyAdmin di Laragon atau `mysql -u root < database.sql`).
3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Sesuaikan `host`, `username`, `password`, dan nama database pada `config/database.py` bila berbeda dengan pengaturan Laragon Anda (bawaan: `localhost`, `root`, tanpa password, database `Gorent`).
5. Jalankan aplikasi:
   ```bash
   python main.py
   ```
6. Login dengan akun Admin awal, atau daftar akun Pelanggan atau Pemilik Rental dari halaman registrasi:

   | Username | Password |
   |----------|----------|
   | `admin` | `admin12345` |

   Segera ganti password akun admin awal setelah dipakai.

Tanggal pada form dipilih melalui date picker, dengan format penyimpanan `YYYY-MM-DD` (contoh: `2026-10-31`).

## Pengujian

Pengujian berada di folder `test/` dan memakai database palsu (MagicMock), jadi **tidak membutuhkan MySQL**.

```bash
python -m pytest test/ -v
```

Test tampilan (`test_views.py`) membutuhkan layar dan otomatis dilewati bila tidak ada display. Di Linux server jalankan dengan layar virtual:

```bash
xvfb-run -a python -m pytest test/ -v
```

Cakupan pengujian: hak akses dan session, controller, model pengguna, kendaraan, pembayaran, penyewaan, pengembalian (termasuk perhitungan denda), dan tampilan.

## Integrasi Berkelanjutan (CI)

Workflow `.github/workflows/ci_pipeline.yml` berjalan otomatis pada setiap push dan pull request ke branch `main`: menyiapkan Python 3.11, memasang dependensi, memeriksa kode dengan Flake8, lalu menjalankan Pytest (test tampilan memakai Xvfb).

## Status Integrasi

| Komponen | Status |
|----------|--------|
| Model (6 berkas) | Terhubung |
| Controller (7 berkas dan modul akses) | Terhubung |
| View GUI (login, registrasi, dan 3 dashboard) | Terhubung |
| Login dan pembatasan hak akses per peran | Tersedia |
| Pembayaran, laporan, dan pengajuan pengembalian | Tersedia |

## Batasan dan Rencana Pengembangan

Belum tersedia: ubah dan hapus data penyewaan secara bebas (hanya pembatalan oleh Admin), ubah data kendaraan selain status, ganti password dari dalam aplikasi, serta ekspor laporan ke PDF atau CSV.

## Dokumentasi

Dokumentasi teknis lengkap (SRS, DFD, Use Case, Activity, Sequence, Class Diagram, ERD, dan rancangan antarmuka) tersedia pada laporan proyek Kelompok 3.
