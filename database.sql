
CREATE DATABASE IF NOT EXISTS Gorent
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE Gorent;

-- =========================================
-- 1. TABEL USER
-- =========================================

CREATE TABLE IF NOT EXISTS user (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    no_identitas VARCHAR(30) NOT NULL UNIQUE,
    no_telepon VARCHAR(20) NOT NULL,
    role ENUM(
        'Admin',
        'Pelanggan',
        'Pemilik Rental'
    ) NOT NULL DEFAULT 'Pelanggan'
);

-- =========================================
-- 2. TABEL KENDARAAN
-- =========================================

CREATE TABLE IF NOT EXISTS kendaraan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jenis ENUM('Motor', 'Mobil') NOT NULL,
    merek VARCHAR(100) NOT NULL,
    nomor_polisi VARCHAR(20) NOT NULL UNIQUE,
    tarif_harian DECIMAL(12,2) NOT NULL,
    status ENUM(
        'Tersedia',
        'Disewa',
        'Perawatan'
    ) NOT NULL DEFAULT 'Tersedia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 3. TABEL PENYEWAAN
-- =========================================

CREATE TABLE IF NOT EXISTS penyewaan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pelanggan_id INT NOT NULL,
    kendaraan_id INT NOT NULL,
    tanggal_mulai DATE NOT NULL,
    tanggal_rencana_kembali DATE NOT NULL,
    total_biaya DECIMAL(12,2) NOT NULL,
    status ENUM(
        'Berjalan',
        'Selesai'
    ) NOT NULL DEFAULT 'Berjalan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_penyewaan_user
        FOREIGN KEY (pelanggan_id)
        REFERENCES user(id_user),

    CONSTRAINT fk_penyewaan_kendaraan
        FOREIGN KEY (kendaraan_id)
        REFERENCES kendaraan(id)
);

-- =========================================
-- 4. TABEL PENGEMBALIAN
-- =========================================

CREATE TABLE IF NOT EXISTS pengembalian (
    id INT AUTO_INCREMENT PRIMARY KEY,
    penyewaan_id INT NOT NULL UNIQUE,
    tanggal_kembali DATE NOT NULL,
    denda DECIMAL(12,2) NOT NULL DEFAULT 0,
    status ENUM(
        'Diajukan',
        'Dikonfirmasi'
    ) NOT NULL DEFAULT 'Dikonfirmasi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pengembalian_penyewaan
        FOREIGN KEY (penyewaan_id)
        REFERENCES penyewaan(id)
);

-- =========================================
-- 5. TABEL PEMBAYARAN
-- =========================================

CREATE TABLE IF NOT EXISTS pembayaran (
    id INT AUTO_INCREMENT PRIMARY KEY,
    penyewaan_id INT NOT NULL,
    jenis ENUM('Sewa', 'Denda') NOT NULL,
    jumlah DECIMAL(12,2) NOT NULL,
    metode ENUM('Tunai', 'Transfer', 'E-Wallet') NULL,
    status ENUM('Menunggu', 'Lunas') NOT NULL DEFAULT 'Menunggu',
    tanggal_bayar DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_pembayaran (penyewaan_id, jenis),

    CONSTRAINT fk_pembayaran_penyewaan
        FOREIGN KEY (penyewaan_id)
        REFERENCES penyewaan(id)
);


-- =========================================
-- 6. AKUN ADMIN AWAL
-- Username: admin | Password: admin12345
-- Segera ganti setelah login pertama.
-- (Password disimpan sebagai SHA-256, sama seperti UserModel)
-- =========================================

INSERT INTO user
    (username, password, no_identitas, no_telepon, role)
VALUES
    ('Admin', SHA2('admin123', 256), 'ADMIN-0001', '0000000000', 'Admin'),

    ('Rasya', SHA2('rasya123', 256), 'RASYA-0001', '0000000001', 'Pemilik Rental');


INSERT INTO kendaraan
(id, jenis, merek, nomor_polisi, tarif_harian, status, created_at)
VALUES
(1, 'Mobil', 'Toyota Avanza', 'DN 1001 AB', 350000.00, 'Tersedia', '2026-11-16 21:33:05'),

(2, 'Mobil', 'Honda Brio', 'DN 1002 AB', 300000.00, 'Tersedia', '2026-11-16 21:33:05'),

(4, 'Mobil', 'Toyota Innova', 'DN 1004 AB', 500000.00, 'Tersedia', '2026-11-16 21:33:05'),

(5, 'Mobil', 'Suzuki Ertiga', 'DN 1005 AB', 350000.00, 'Tersedia', '2026-11-16 21:33:05'),

(6, 'Motor', 'Honda Beat', 'DN 2001 AB', 75000.00, 'Tersedia', '2026-11-16 21:33:08'),

(7, 'Motor', 'Honda Vario 125', 'DN 2002 AB', 85000.00, 'Tersedia', '2026-11-16 21:33:08'),

(8, 'Motor', 'Yamaha NMAX', 'DN 2003 AB', 150000.00, 'Tersedia', '2026-11-16 21:33:08'),

(9, 'Motor', 'Yamaha Aerox', 'DN 2004 AB', 125000.00, 'Tersedia', '2026-11-16 21:33:08'),

(10, 'Motor', 'Honda Scoopy', 'DN 2005 AB', 90000.00, 'Tersedia', '2026-11-16 21:33:08');