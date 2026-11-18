from datetime import date
from config.database import Database

METODE = ("Tunai", "Transfer", "E-Wallet")
STATUS = ("Menunggu", "Lunas")


class PembayaranModel:

    def __init__(self):
        self.db = Database()
        self.table_name = "pembayaran"

    # READ: semua pembayaran, atau milik satu pelanggan
    def get_all_pembayaran(self, pelanggan_id=None):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            query = f"""
                SELECT
                    pb.id,
                    pb.penyewaan_id,
                    pb.jenis,
                    pb.jumlah,
                    pb.metode,
                    pb.status,
                    pb.tanggal_bayar,
                    u.username,
                    k.merek,
                    k.nomor_polisi
                FROM {self.table_name} pb
                JOIN penyewaan p ON p.id = pb.penyewaan_id
                JOIN user u ON u.id_user = p.pelanggan_id
                JOIN kendaraan k ON k.id = p.kendaraan_id
            """
            params = ()

            if pelanggan_id is not None:
                query += " WHERE p.pelanggan_id = %s"
                params = (pelanggan_id,)

            query += " ORDER BY pb.id DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # PELANGGAN: membayar tagihan miliknya sendiri
    def bayar(self, pembayaran_id, pelanggan_id, metode):
        if metode not in METODE:
            raise ValueError("Pilih metode pembayaran yang valid.")

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                f"""
                SELECT pb.id, pb.status, p.pelanggan_id
                FROM {self.table_name} pb
                JOIN penyewaan p ON p.id = pb.penyewaan_id
                WHERE pb.id = %s
                FOR UPDATE
                """,
                (pembayaran_id,)
            )
            data = cursor.fetchone()

            if not data or data["pelanggan_id"] != pelanggan_id:
                raise ValueError("Data pembayaran tidak ditemukan.")

            if data["status"] == "Lunas":
                raise ValueError("Pembayaran ini sudah lunas.")

            cursor.execute(
                f"""
                UPDATE {self.table_name}
                SET status = 'Lunas',
                    metode = %s,
                    tanggal_bayar = %s
                WHERE id = %s
                """,
                (metode, date.today(), pembayaran_id)
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

    # ADMIN: mengubah status pembayaran
    def ubah_status(self, pembayaran_id, status):
        if status not in STATUS:
            raise ValueError("Status pembayaran tidak valid.")

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor()

            if status == "Lunas":
                # Dicatat tunai bila belum ada metode (diterima admin)
                cursor.execute(
                    f"""
                    UPDATE {self.table_name}
                    SET status = 'Lunas',
                        metode = COALESCE(metode, 'Tunai'),
                        tanggal_bayar = COALESCE(tanggal_bayar, %s)
                    WHERE id = %s
                    """,
                    (date.today(), pembayaran_id)
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE {self.table_name}
                    SET status = 'Menunggu',
                        metode = NULL,
                        tanggal_bayar = NULL
                    WHERE id = %s
                    """,
                    (pembayaran_id,)
                )

            # rowcount bisa 0 bila status sudah sama, jadi cek keberadaan
            cursor.execute(
                f"SELECT id FROM {self.table_name} WHERE id = %s",
                (pembayaran_id,)
            )

            if not cursor.fetchone():
                raise ValueError("Data pembayaran tidak ditemukan.")

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()
