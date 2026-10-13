from datetime import date
from config.database import Database


class PengembalianModel:

    def __init__(self):
        self.db = Database()
        self.table_name = "pengembalian"

    # READ
    def get_all_pengembalian(self):
        conn = self.db.get_connection()
        if not conn:
            return []

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""
                SELECT pg.id, pg.penyewaan_id, pg.tanggal_kembali,
                       pg.denda, p.total_biaya, pl.nama AS nama_pelanggan,
                       k.merek, k.nomor_polisi
                FROM {self.table_name} pg
                JOIN penyewaan p ON p.id = pg.penyewaan_id
                JOIN pelanggan pl ON pl.id = p.pelanggan_id
                JOIN kendaraan k ON k.id = p.kendaraan_id
                ORDER BY pg.id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conn.close()

    # CREATE / PROCESS
    def process_pengembalian(self, penyewaan_id, tanggal_kembali):
        kembali = date.fromisoformat(tanggal_kembali)

        conn = self.db.get_connection()
        if not conn:
            return False

        cursor = None
        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            # Ambil data penyewaan beserta tarif harian kendaraan
            query_sewa = """
                SELECT p.id, p.kendaraan_id, p.tanggal_rencana_kembali, p.status, k.tarif_harian
                FROM penyewaan p
                JOIN kendaraan k ON k.id = p.kendaraan_id
                WHERE p.id=%s FOR UPDATE
            """
            cursor.execute(query_sewa, (penyewaan_id,))
            sewa = cursor.fetchone()

            if not sewa:
                raise ValueError("Transaksi penyewaan tidak ditemukan.")
            if sewa["status"] != "Berjalan":
                raise ValueError("Penyewaan ini sudah dikembalikan.")

            # Hitung keterlambatan (hari)
            selisih_hari = (kembali - sewa["tanggal_rencana_kembali"]).days
            terlambat = max(0, selisih_hari)

            # Denda otomatis = jumlah hari terlambat * tarif harian kendaraan
            denda_per_hari = float(sewa["tarif_harian"])
            denda = terlambat * denda_per_hari

            # Catat pengembalian
            query_insert = f"""
                INSERT INTO {self.table_name} (penyewaan_id, tanggal_kembali, denda)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_insert, (penyewaan_id, kembali, denda))

            # Update status penyewaan dan kendaraan
            cursor.execute(
                "UPDATE penyewaan SET status='Selesai' WHERE id=%s",
                (penyewaan_id,),
            )
            cursor.execute(
                "UPDATE kendaraan SET status='Tersedia' WHERE id=%s",
                (sewa["kendaraan_id"],),
            )

            conn.commit()
            return denda

        except Exception:
            conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conn.close()