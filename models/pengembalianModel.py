from datetime import date
from decimal import Decimal
from config.database import Database


class PengembalianModel:

    def __init__(self):
        self.db = Database()
        self.table_name = "pengembalian"

    # ---------------------------------------------------------
    # UTILITAS
    # ---------------------------------------------------------

    @staticmethod
    def hitung_denda(tarif_harian, tanggal_rencana, tanggal_kembali):
        """
        Denda = tarif sewa 1 hari x jumlah hari terlambat.
        Terlambat 1 hari = 1x tarif, 2 hari = 2x tarif, dst.
        """
        terlambat = max(0, (tanggal_kembali - tanggal_rencana).days)
        tarif = Decimal(str(tarif_harian))
        return tarif * terlambat, terlambat, tarif

    @staticmethod
    def _baca_tanggal(nilai):
        """Menerima date atau teks YYYY-MM-DD."""
        if isinstance(nilai, date):
            return nilai

        try:
            return date.fromisoformat(nilai)
        except (TypeError, ValueError):
            raise ValueError("Tanggal pengembalian tidak valid.")

    def _ambil_semua(self, query, params=()):
        conn = self.db.get_connection()

        if not conn:
            return []

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # READ: riwayat pengembalian (semua / milik satu pelanggan)
    # ---------------------------------------------------------

    def get_all_pengembalian(self, pelanggan_id=None):
        query = f"""
            SELECT
                pg.id,
                pg.penyewaan_id,
                pg.tanggal_kembali,
                pg.denda,
                pg.status,
                p.total_biaya,
                u.username,
                k.merek,
                k.nomor_polisi
            FROM {self.table_name} pg
            JOIN penyewaan p ON p.id = pg.penyewaan_id
            JOIN user u ON u.id_user = p.pelanggan_id
            JOIN kendaraan k ON k.id = p.kendaraan_id
            WHERE u.role = 'Pelanggan'
        """
        params = ()

        if pelanggan_id is not None:
            query += " AND p.pelanggan_id = %s"
            params = (pelanggan_id,)

        query += " ORDER BY pg.id DESC"

        return self._ambil_semua(query, params)

    # ---------------------------------------------------------
    # READ: penyewaan yang masih berjalan
    # (status_pengembalian = 'Diajukan' bila pelanggan sudah
    #  mengajukan pengembalian dan menunggu konfirmasi admin)
    # ---------------------------------------------------------

    def get_penyewaan_berjalan(self, pelanggan_id=None):
        query = """
            SELECT
                p.id,
                p.pelanggan_id,
                p.kendaraan_id,
                p.tanggal_mulai,
                p.tanggal_rencana_kembali,
                p.total_biaya,
                u.username,
                k.merek,
                k.nomor_polisi,
                k.tarif_harian,
                pg.status AS status_pengembalian,
                pg.tanggal_kembali AS tanggal_pengajuan
            FROM penyewaan p
            JOIN user u ON u.id_user = p.pelanggan_id
            JOIN kendaraan k ON k.id = p.kendaraan_id
            LEFT JOIN pengembalian pg ON pg.penyewaan_id = p.id
            WHERE p.status = 'Berjalan'
              AND u.role = 'Pelanggan'
        """
        params = ()

        if pelanggan_id is not None:
            query += " AND p.pelanggan_id = %s"
            params = (pelanggan_id,)

        query += " ORDER BY p.id DESC"

        return self._ambil_semua(query, params)

    # ---------------------------------------------------------
    # PELANGGAN: mengajukan pengembalian pada tanggal yang dipilih
    # (YYYY-MM-DD). Denda langsung dihitung. Kendaraan baru
    # tersedia lagi setelah admin mengonfirmasi.
    # ---------------------------------------------------------

    def ajukan_pengembalian(
        self, penyewaan_id, pelanggan_id, tanggal_kembali
    ):
        kembali = self._baca_tanggal(tanggal_kembali)

        if kembali > date.today():
            raise ValueError(
                "Tanggal pengembalian tidak boleh melebihi hari ini."
            )

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.pelanggan_id,
                    p.tanggal_mulai,
                    p.tanggal_rencana_kembali,
                    p.status,
                    k.tarif_harian
                FROM penyewaan p
                JOIN kendaraan k ON k.id = p.kendaraan_id
                WHERE p.id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )
            sewa = cursor.fetchone()

            if not sewa or sewa["pelanggan_id"] != pelanggan_id:
                raise ValueError("Transaksi penyewaan tidak ditemukan.")

            if sewa["status"] != "Berjalan":
                raise ValueError("Penyewaan ini sudah dikembalikan.")

            if kembali < sewa["tanggal_mulai"]:
                raise ValueError(
                    "Tanggal pengembalian tidak boleh sebelum "
                    "tanggal mulai sewa."
                )

            cursor.execute(
                f"""
                SELECT id FROM {self.table_name}
                WHERE penyewaan_id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )

            if cursor.fetchone():
                raise ValueError(
                    "Pengembalian sudah diajukan dan menunggu "
                    "konfirmasi admin."
                )

            denda, terlambat, tarif = self.hitung_denda(
                sewa["tarif_harian"],
                sewa["tanggal_rencana_kembali"],
                kembali
            )

            cursor.execute(
                f"""
                INSERT INTO {self.table_name}
                (penyewaan_id, tanggal_kembali, denda, status)
                VALUES (%s, %s, %s, 'Diajukan')
                """,
                (penyewaan_id, kembali, denda)
            )

            conn.commit()

            return {
                "denda": denda,
                "terlambat": terlambat,
                "tarif_harian": tarif
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # ADMIN: memproses / mengonfirmasi pengembalian
    # ---------------------------------------------------------

    def process_pengembalian(self, penyewaan_id, tanggal_kembali):

        # Validasi format tanggal
        kembali = self._baca_tanggal(tanggal_kembali)

        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.kendaraan_id,
                    p.tanggal_mulai,
                    p.tanggal_rencana_kembali,
                    p.status,
                    k.tarif_harian
                FROM penyewaan p
                JOIN kendaraan k ON k.id = p.kendaraan_id
                WHERE p.id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )
            sewa = cursor.fetchone()

            if not sewa:
                raise ValueError("Transaksi penyewaan tidak ditemukan.")

            if sewa["status"] != "Berjalan":
                raise ValueError("Penyewaan ini sudah dikembalikan.")

            if kembali < sewa["tanggal_mulai"]:
                raise ValueError(
                    "Tanggal kembali tidak boleh sebelum "
                    "tanggal mulai sewa."
                )

            denda, terlambat, tarif = self.hitung_denda(
                sewa["tarif_harian"],
                sewa["tanggal_rencana_kembali"],
                kembali
            )

            # Admin hanya mengelola: pengembalian harus sudah
            # diajukan oleh pelanggan.
            cursor.execute(
                f"""
                SELECT id, status FROM {self.table_name}
                WHERE penyewaan_id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )
            pengajuan = cursor.fetchone()

            if not pengajuan or pengajuan["status"] != "Diajukan":
                raise ValueError(
                    "Pelanggan belum mengajukan pengembalian "
                    "untuk penyewaan ini."
                )

            cursor.execute(
                f"""
                UPDATE {self.table_name}
                SET tanggal_kembali = %s,
                    denda = %s,
                    status = 'Dikonfirmasi'
                WHERE id = %s
                """,
                (kembali, denda, pengajuan["id"])
            )

            cursor.execute(
                "UPDATE penyewaan SET status = 'Selesai' WHERE id = %s",
                (penyewaan_id,)
            )

            cursor.execute(
                "UPDATE kendaraan SET status = 'Tersedia' WHERE id = %s",
                (sewa["kendaraan_id"],)
            )

            # Tagihan denda otomatis bila terlambat
            if denda > 0:
                cursor.execute(
                    """                    INSERT INTO pembayaran
                    (penyewaan_id, jenis, jumlah, status)
                    VALUES (%s, 'Denda', %s, 'Menunggu')
                    ON DUPLICATE KEY UPDATE jumlah = VALUES(jumlah)
                    """,
                    (penyewaan_id, denda)
                )

            conn.commit()

            # Dict (bukan angka) agar tidak bernilai False
            # ketika denda = 0 (tepat waktu).
            return {
                "denda": denda,
                "terlambat": terlambat,
                "tarif_harian": tarif
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # ADMIN: menolak pengajuan (pelanggan bisa mengajukan ulang)
    # ---------------------------------------------------------

    def tolak_pengajuan(self, penyewaan_id):
        conn = self.db.get_connection()

        if not conn:
            return False

        cursor = None

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                f"""
                SELECT id, status FROM {self.table_name}
                WHERE penyewaan_id = %s
                FOR UPDATE
                """,
                (penyewaan_id,)
            )
            pengajuan = cursor.fetchone()

            if not pengajuan or pengajuan["status"] != "Diajukan":
                raise ValueError(
                    "Tidak ada pengajuan pengembalian yang bisa ditolak."
                )

            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE id = %s",
                (pengajuan["id"],)
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
