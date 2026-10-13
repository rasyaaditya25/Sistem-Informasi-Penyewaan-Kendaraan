from datetime import date
from config.database import Database


class PenyewaanModel:
    def __init__(self):
        self.db = Database()
        self.table_name = "penyewaan"

    # READ
    def get_all_penyewaan(self):
        conn = self.db.get_connection()
        if not conn:
            return []

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""
                SELECT p.id, p.tanggal_mulai, p.tanggal_rencana_kembali,
                       p.total_biaya, p.status,
                       pl.nama AS nama_pelanggan,
                       k.jenis, k.merek, k.nomor_polisi
                FROM {self.table_name} p
                JOIN pelanggan pl ON pl.id = p.pelanggan_id
                JOIN kendaraan k ON k.id = p.kendaraan_id
                ORDER BY p.id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conn.close()

    # CREATE
    def create_penyewaan(
        self, pelanggan_id, kendaraan_id, tanggal_mulai, tanggal_kembali
    ):
        mulai = date.fromisoformat(tanggal_mulai)
        kembali = date.fromisoformat(tanggal_kembali)
        if kembali < mulai:
            raise ValueError(
                "Tanggal kembali tidak boleh sebelum tanggal mulai."
            )

        jumlah_hari = (kembali - mulai).days + 1

        conn = self.db.get_connection()
        if not conn:
            return False

        cursor = None
        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            # Cek status dan tarif kendaraan
            cursor.execute(
                "SELECT tarif_harian, status FROM kendaraan WHERE id=%s FOR UPDATE",
                (kendaraan_id,),
            )
            kendaraan = cursor.fetchone()
            if not kendaraan:
                raise ValueError("Kendaraan tidak ditemukan.")
            if kendaraan["status"] != "Tersedia":
                raise ValueError("Kendaraan tidak tersedia.")

            # Cek keberadaan pelanggan
            cursor.execute(
                "SELECT id FROM pelanggan WHERE id=%s", (pelanggan_id,)
            )
            if not cursor.fetchone():
                raise ValueError("Pelanggan tidak ditemukan.")

            total = jumlah_hari * float(kendaraan["tarif_harian"])

            # Insert ke tabel penyewaan
            query_insert = f"""
                INSERT INTO {self.table_name}
                (pelanggan_id, kendaraan_id, tanggal_mulai,
                 tanggal_rencana_kembali, total_biaya, status)
                VALUES (%s, %s, %s, %s, %s, 'Berjalan')
            """
            cursor.execute(
                query_insert,
                (pelanggan_id, kendaraan_id, mulai, kembali, total),
            )
            penyewaan_id = cursor.lastrowid

            # Update status kendaraan
            cursor.execute(
                "UPDATE kendaraan SET status='Disewa' WHERE id=%s",
                (kendaraan_id,),
            )

            conn.commit()
            return penyewaan_id

        except Exception:
            conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conn.close()