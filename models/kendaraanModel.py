
from decimal import Decimal, InvalidOperation
from config.database import Database


class KendaraanModel:

    def __init__(self):
        self.db = Database()
        self.table_name = "kendaraan"

    # READ
    def get_all_kendaraan(self):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT *
                FROM kendaraan
                ORDER BY id DESC
            """

            cursor.execute(query)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # CREATE
    def create_kendaraan(
        self, jenis, merek, nomor_polisi, tarif_harian
    ):
        if jenis not in ("Motor", "Mobil"):
            raise ValueError(
                "Jenis kendaraan harus Motor atau Mobil."
            )

        if not merek or not merek.strip():
            raise ValueError("Merek kendaraan wajib diisi.")

        if not nomor_polisi or not nomor_polisi.strip():
            raise ValueError("Nomor polisi wajib diisi.")

        try:
            tarif = Decimal(str(tarif_harian))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Tarif harian harus berupa angka yang valid.")

        if not tarif.is_finite() or tarif <= 0:
            raise ValueError("Tarif harian harus lebih dari nol.")

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            cursor = conn.cursor()

            query = """
                INSERT INTO kendaraan
                (jenis, merek, nomor_polisi, tarif_harian, status)
                VALUES (%s, %s, %s, %s, 'Tersedia')
            """

            cursor.execute(
                query,
                (
                    jenis,
                    merek.strip(),
                    nomor_polisi.strip().upper(),
                    tarif
                )
            )

            conn.commit()
            return cursor.lastrowid

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # UPDATE STATUS
    def update_status(self, kendaraan_id, status):

        if status not in ("Tersedia", "Disewa", "Perawatan"):
            raise ValueError("Status kendaraan tidak valid.")

        # Status Disewa dikelola otomatis oleh transaksi penyewaan.
        if status == "Disewa":
            raise ValueError(
                "Status Disewa hanya dapat diatur melalui proses penyewaan."
            )

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            # Kunci data kendaraan agar tidak berubah bersamaan
            cursor.execute(
                """
                SELECT id, status
                FROM kendaraan
                WHERE id = %s
                FOR UPDATE
                """,
                (kendaraan_id,)
            )

            kendaraan = cursor.fetchone()

            if not kendaraan:
                raise ValueError("Kendaraan tidak ditemukan.")

            if kendaraan["status"] == "Disewa":
                raise ValueError(
                    "Kendaraan sedang disewa. Status tidak dapat diubah."
                )

            cursor.execute(
                """
                UPDATE kendaraan
                SET status = %s
                WHERE id = %s
                """,
                (status, kendaraan_id)
            )

            updated = cursor.rowcount > 0
            conn.commit()

            return updated

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # DELETE
    def delete_kendaraan(self, kendaraan_id):

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            # Kunci kendaraan agar tidak dihapus ketika sedang diproses
            cursor.execute(
                """
                SELECT id, status
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
                raise ValueError(
                    "Hanya kendaraan berstatus Tersedia yang dapat dihapus."
                )

            # Cek seluruh riwayat penyewaan
            cursor.execute(
                """
                SELECT COUNT(*) AS jumlah
                FROM penyewaan
                WHERE kendaraan_id = %s
                """,
                (kendaraan_id,)
            )

            riwayat = cursor.fetchone()["jumlah"]

            if riwayat > 0:
                raise ValueError(
                    "Kendaraan memiliki riwayat penyewaan. "
                    "Data tidak dapat dihapus agar riwayat transaksi tetap terjaga."
                )

            cursor.execute(
                """
                DELETE FROM kendaraan
                WHERE id = %s
                """,
                (kendaraan_id,)
            )

            deleted = cursor.rowcount > 0
            conn.commit()

            return deleted

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()