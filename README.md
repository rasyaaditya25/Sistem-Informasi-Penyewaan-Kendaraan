# Sistem Informasi Penyewaan Kendaraan

**Kelompok 3 | Kelas C | Program Studi S1 Sistem Informasi**
Jurusan Teknologi Informasi, Fakultas Teknik, Universitas Tadulako, 2026
Proyek Ujian Tengah Semester (UTS) Praktikum Rekayasa Perangkat Lunak

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

Sistem Informasi Penyewaan Kendaraan adalah aplikasi desktop untuk mengelola data kendaraan, pelanggan, penyewaan, dan pengembalian pada usaha rental skala kecil. Aplikasi ini menggantikan pencatatan manual di buku tulis atau pesan singkat yang mudah hilang, sulit dicari, dan rawan salah hitung.

Aplikasi dibuat menggunakan Python dan MySQL (Laragon) dengan arsitektur **Model, View, Controller (MVC)** sesuai materi Modul 1 sampai Modul 5. Total biaya sewa, denda keterlambatan, dan status kendaraan dihitung serta diperbarui otomatis oleh sistem.

Sistem melibatkan tiga aktor:

- **Admin (Petugas Rental)**: operator yang mengelola kendaraan dan pelanggan, membuat transaksi penyewaan, dan memproses pengembalian.
- **Pelanggan**: memberi data identitas dan permintaan sewa, lalu menerima informasi total biaya, tanggal kembali, dan denda melalui Admin.
- **Pemilik Rental**: memantau data kendaraan, penyewaan, dan pengembalian (hanya baca).

Tampilan menggunakan **GUI desktop** (`views/main_view.py`) berbasis CustomTkinter dengan empat tab, yaitu Kendaraan, Pelanggan, Penyewaan, dan Pengembalian. Setiap tab memiliki form di sisi kiri dan tabel data di sisi kanan. GUI sudah terhubung ke Controller, Model, dan database MySQL, sehingga seluruh data yang ditampilkan dan disimpan berasal dari database `penyewaan_kendaraan`.

## Tujuan

- Menggantikan pencatatan manual dengan data yang tersimpan di basis data.
- Menghitung total biaya sewa dan denda keterlambatan secara otomatis.
- Menjaga status kendaraan tetap konsisten (Tersedia, Disewa, Perawatan) dan mencegah kendaraan disewakan ganda.
- Memudahkan Pemilik Rental memantau kendaraan dan transaksi yang sedang berjalan.
- Menerapkan arsitektur MVC pada aplikasi desktop Python.
- Menghubungkan Python dengan database MySQL.

## Fitur

| Kode | Fitur | Aktor |
|------|-------|-------|
| FR01 | Tambah data kendaraan (status awal Tersedia) | Admin |
| FR02 | Tampilkan daftar kendaraan | Admin, Pemilik Rental |
| FR03 | Hapus kendaraan yang berstatus Tersedia | Admin |
| FR04 | Ubah status kendaraan (Tersedia, Disewa, Perawatan) | Admin |
| FR05 | Tambah data pelanggan | Admin |
| FR06 | Tampilkan daftar pelanggan | Admin |
| FR07 | Buat transaksi penyewaan beserta total biaya | Admin |
| FR08 | Tampilkan daftar penyewaan | Admin, Pemilik Rental |
| FR09 | Proses pengembalian dan hitung denda | Admin |
| FR10 | Tampilkan riwayat pengembalian | Admin, Pemilik Rental |
| FR11 | Validasi input dan pesan kesalahan | Admin |

## Aturan Bisnis

- Jenis kendaraan hanya **Motor** atau **Mobil**; merek dan nomor polisi wajib diisi; tarif harian harus lebih dari nol; nomor polisi disimpan dalam huruf kapital.
- Tanggal berformat `YYYY-MM-DD` dan valid; tanggal kembali tidak boleh sebelum tanggal mulai.
- Transaksi hanya dapat dibuat untuk pelanggan terdaftar dan kendaraan berstatus Tersedia. Setelah transaksi dibuat, status kendaraan menjadi Disewa.
- **Total biaya** = jumlah hari × tarif harian, dengan jumlah hari = (tanggal rencana kembali − tanggal mulai) + 1.
- **Denda** = jumlah hari terlambat × tarif harian, dengan hari terlambat adalah selisih tanggal kembali aktual dan tanggal rencana kembali (minimal 0).
- Penyewaan hanya dapat dikembalikan satu kali. Setelah pengembalian, status penyewaan menjadi Selesai dan kendaraan kembali Tersedia.
- Kendaraan hanya dapat dihapus jika berstatus Tersedia.

Contoh: kendaraan bertarif Rp250.000 per hari disewa 3 hari menghasilkan total biaya Rp750.000. Jika terlambat 2 hari, denda Rp500.000.

## Teknologi

- Python
- CustomTkinter (tampilan GUI desktop)
- mysql-connector-python (koneksi database, mendukung parameterized query)
- MySQL 8.x dengan Laragon
- Draw.io (pemodelan diagram)
- Visual Studio Code, Git, dan GitHub

## Arsitektur

```
Pengguna -> View -> Controller -> Model -> config/database.py -> MySQL
```

- **View** menerima isian form dan klik tombol, lalu meneruskannya ke Controller.
- **Controller** memeriksa input dan memanggil Model yang sesuai (satu Controller untuk setiap Model).
- **Model** menjalankan query SQL, menghitung biaya dan denda, serta menjalankan proses penyewaan dan pengembalian dalam satu transaksi (di-rollback bila gagal).

## Struktur Proyek

```
sistem_penyewaan_kendaraan/
├── app.py                          # titik masuk aplikasi GUI
├── config/
│   └── database.py                 # koneksi MySQL (class Database)
├── models/
│   ├── kendaraanModel.py           # Model: tabel kendaraan
│   ├── pelangganModel.py           # Model: tabel pelanggan
│   ├── penyewaanModel.py           # Model: tabel penyewaan
│   └── pengembalianModel.py        # Model: tabel pengembalian
├── controllers/
│   ├── kendaraan_controller.py     # Controller: kendaraan
│   ├── pelanggan_controller.py     # Controller: pelanggan
│   ├── penyewaan_controller.py     # Controller: penyewaan
│   └── pengembalian_controller.py  # Controller: pengembalian
├── views/
│   └── main_view.py                # View GUI (CustomTkinter, 4 tab)
└── README.md
```

## Basis Data

Nama database: `penyewaan_kendaraan` (empat tabel).

| Tabel | Isi Utama | Relasi |
|-------|-----------|--------|
| `kendaraan` | jenis, merek, nomor_polisi (unik), tarif_harian, status | Satu kendaraan dapat muncul pada banyak penyewaan |
| `pelanggan` | nama, no_identitas (unik), no_telepon | Satu pelanggan dapat melakukan banyak penyewaan |
| `penyewaan` | pelanggan_id, kendaraan_id, tanggal_mulai, tanggal_rencana_kembali, total_biaya, status (Berjalan atau Selesai) | FK ke `pelanggan` dan `kendaraan` |
| `pengembalian` | penyewaan_id (unik), tanggal_kembali, denda | Satu penyewaan paling banyak satu pengembalian |

## Cara Menjalankan

1. Jalankan MySQL di Laragon.
2. Pasang dependensi:
   ```bash
   pip install mysql-connector-python customtkinter
   ```
3. Siapkan database `penyewaan_kendaraan` beserta keempat tabelnya (sesuai bagian Basis Data di atas).
4. Sesuaikan `host`, `username`, `password`, dan nama database pada `config/database.py` bila berbeda dengan pengaturan Laragon Anda.
5. Jalankan aplikasi:
   ```bash
   python app.py
   ```

Tanggal pada form ditulis dengan format `YYYY-MM-DD` (contoh: `2026-10-31`).

## Status Integrasi

| Komponen | Status |
|----------|--------|
| Model (4 berkas) | Terhubung |
| Controller (4 berkas) | Terhubung |
| View GUI (4 tab) | Terhubung |

## Batasan dan Rencana Pengembangan (UAS)

Belum tersedia pada versi UTS: login dan pembatasan hak akses per aktor, ubah dan hapus data pelanggan maupun penyewaan, pembayaran dan uang muka, pencarian data, serta laporan dan ekspor PDF atau CSV. Fitur-fitur ini direncanakan pada tahap UAS di atas struktur MVC yang sama.

## Dokumentasi

Dokumentasi teknis lengkap (SRS, DFD, Use Case, Activity, Sequence, Class Diagram, ERD, dan rancangan antarmuka) tersedia pada laporan UTS Kelompok 3.
