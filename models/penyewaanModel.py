
from datetime import date
from config.database import Database


class PenyewaanModel:
    def __init__(self):
        self.db = Database()
        self.table_name = "penyewaan"

    # READ ALL PENYEWAAN
    def get_all_penyewaan(self):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            query = f"""
                SELECT
                    p.id,
                    p.pelanggan_id,
                    p.kendaraan_id,
                    p.tanggal_mulai,
                    p.tanggal_rencana_kembali,
                    p.total_biaya,
                    p.status,
                    u.username,
                    k.jenis,
                    k.merek,
                    k.nomor_polisi
                FROM {self.table_name} p
                JOIN user u
                    ON u.id_user = p.pelanggan_id
                JOIN kendaraan k
                    ON k.id = p.kendaraan_id
                WHERE u.role = 'Pelanggan'
                ORDER BY p.id DESC
            """

            cursor.execute(query)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            conn.close()

    # CREATE PENYEWAAN
    def create_penyewaan(
        self,
        pelanggan_id,
        kendaraan_id,
        tanggal_mulai,
        tanggal_kembali
    ):
        # Validasi format tanggal
        mulai = date.fromisoformat(tanggal_mulai)
        kembali = date.fromisoformat(tanggal_kembali)

        if kembali < mulai:
            raise ValueError(
                "Tanggal kembali tidak boleh sebelum tanggal mulai."
            )

        if kembali == mulai:
            jumlah_hari = 1
        else:
            jumlah_hari = (kembali - mulai).days + 1

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()

            cursor = conn.cursor(dictionary=True)

            # CEK KENDARAAN DAN KUNCI BARIS
            cursor.execute(
                """
                SELECT id, tarif_harian, status
                FROM kendaraan
                WHERE id = %s
                FOR UPDATE
                """,
                (kendaraan_id,)
            )

            kendaraan = cursor.fetchone()

            if not kendaraan:
                raise ValueError("Kendaraan tidak ditemukan.")

            if kendaraan["status"] != "Tersedia":
                raise ValueError("Kendaraan tidak tersedia.")

            # CEK PELANGGAN PADA TABEL USER
            cursor.execute(
                """
                SELECT id_user
                FROM user
                WHERE id_user = %s
                AND role = 'Pelanggan'
                """,
                (pelanggan_id,)
            )

            pelanggan = cursor.fetchone()

            if not pelanggan:
                raise ValueError("Pelanggan tidak ditemukan.")

            # HITUNG TOTAL BIAYA
            total = kendaraan["tarif_harian"] * jumlah_hari

            # INSERT DATA PENYEWAAN
            query_insert = f"""
                INSERT INTO {self.table_name}
                (
                    pelanggan_id,
                    kendaraan_id,
                    tanggal_mulai,
                    tanggal_rencana_kembali,
                    total_biaya,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, 'Berjalan')
            """

            cursor.execute(
                query_insert,
                (
                    pelanggan_id,
                    kendaraan_id,
                    mulai,
                    kembali,
                    total
                )
            )

            penyewaan_id = cursor.lastrowid

            # BUAT TAGIHAN PEMBAYARAN SEWA
            cursor.execute(
                """
                INSERT INTO pembayaran
                (penyewaan_id, jenis, jumlah, status)
                VALUES (%s, 'Sewa', %s, 'Menunggu')
                """,
                (penyewaan_id, total)
            )

            # UPDATE STATUS KENDARAAN
            cursor.execute(
                """
                UPDATE kendaraan
                SET status = 'Disewa'
                WHERE id = %s
                """,
                (kendaraan_id,)
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

    # READ: Riwayat penyewaan milik satu pelanggan
    def get_penyewaan_pelanggan(self, pelanggan_id):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.tanggal_mulai,
                    p.tanggal_rencana_kembali,
                    p.total_biaya,
                    p.status,
                    k.jenis,
                    k.merek,
                    k.nomor_polisi,
                    pg.status AS status_pengembalian,
                    pg.tanggal_kembali,
                    pg.denda
                FROM penyewaan p
                JOIN kendaraan k ON k.id = p.kendaraan_id
                LEFT JOIN pengembalian pg ON pg.penyewaan_id = p.id
                WHERE p.pelanggan_id = %s
                ORDER BY p.id DESC
                """,
                (pelanggan_id,)
            )

            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            conn.close()

    # READ: Mengambil kendaraan yang tersedia
    def get_kendaraan_tersedia(self):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT id, jenis, merek, nomor_polisi, tarif_harian
                FROM kendaraan
                WHERE status = 'Tersedia'
                ORDER BY id DESC
            """

            cursor.execute(query)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            conn.close()

    # ADMIN: membatalkan penyewaan yang belum dibayar & belum dikembalikan
    def batalkan_penyewaan(self, penyewaan_id):
        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                f"""
                SELECT id, kendaraan_id, status
                FROM {self.table_name}
                WHERE id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )
            sewa = cursor.fetchone()

            if not sewa:
                raise ValueError("Data penyewaan tidak ditemukan.")

            if sewa["status"] != "Berjalan":
                raise ValueError(
                    "Penyewaan yang sudah selesai tidak dapat dibatalkan."
                )

            cursor.execute(
                "SELECT id FROM pengembalian WHERE penyewaan_id = %s",
                (penyewaan_id,)
            )

            if cursor.fetchone():
                raise ValueError(
                    "Pelanggan sudah mengajukan pengembalian. "
                    "Proses atau tolak pengajuan di menu Pengembalian."
                )

            cursor.execute(
                "SELECT COUNT(*) AS jumlah FROM pembayaran "
                "WHERE penyewaan_id = %s AND status = 'Lunas'",
                (penyewaan_id,)
            )

            if cursor.fetchone()["jumlah"] > 0:
                raise ValueError(
                    "Penyewaan sudah dibayar sehingga tidak dapat "
                    "dibatalkan."
                )

            cursor.execute(
                "DELETE FROM pembayaran WHERE penyewaan_id = %s",
                (penyewaan_id,)
            )
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE id = %s",
                (penyewaan_id,)
            )
            cursor.execute(
                "UPDATE kendaraan SET status = 'Tersedia' WHERE id = %s",
                (sewa["kendaraan_id"],)
            )

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()
