CREATE DATABASE IF NOT EXISTS penyewaan_kendaraan
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE penyewaan_kendaraan;

CREATE TABLE IF NOT EXISTS kendaraan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jenis ENUM('Motor', 'Mobil') NOT NULL,
    merek VARCHAR(100) NOT NULL,
    nomor_polisi VARCHAR(20) NOT NULL UNIQUE,
    tarif_harian DECIMAL(12,2) NOT NULL,
    status ENUM('Tersedia', 'Disewa', 'Perawatan') NOT NULL DEFAULT 'Tersedia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pelanggan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(120) NOT NULL,
    no_identitas VARCHAR(40) NOT NULL UNIQUE,
    no_telepon VARCHAR(25) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS penyewaan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pelanggan_id INT NOT NULL,
    kendaraan_id INT NOT NULL,
    tanggal_mulai DATE NOT NULL,
    tanggal_rencana_kembali DATE NOT NULL,
    total_biaya DECIMAL(12,2) NOT NULL,
    status ENUM('Berjalan', 'Selesai') NOT NULL DEFAULT 'Berjalan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_penyewaan_pelanggan FOREIGN KEY (pelanggan_id)
        REFERENCES pelanggan(id),
    CONSTRAINT fk_penyewaan_kendaraan FOREIGN KEY (kendaraan_id)
        REFERENCES kendaraan(id)
);

CREATE TABLE IF NOT EXISTS pengembalian (
    id INT AUTO_INCREMENT PRIMARY KEY,
    penyewaan_id INT NOT NULL UNIQUE,
    tanggal_kembali DATE NOT NULL,
    denda DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pengembalian_penyewaan FOREIGN KEY (penyewaan_id)
        REFERENCES penyewaan(id)
);
