from config.database import Database


class LaporanModel:

    def __init__(self):
        self.db = Database()

    def ringkasan(self, dari, sampai):
        """
        Ringkasan untuk transaksi yang tanggal mulainya berada
        pada periode [dari, sampai] (format YYYY-MM-DD).
        """
        conn = self.db.get_connection()

        if not conn:
            return None

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT COUNT(*) AS jumlah,
                       COALESCE(SUM(total_biaya), 0) AS nilai
                FROM penyewaan
                WHERE tanggal_mulai BETWEEN %s AND %s
                """,
                (dari, sampai)
            )
            transaksi = cursor.fetchone()

            cursor.execute(
                """
                SELECT pb.jenis, pb.status,
                       COALESCE(SUM(pb.jumlah), 0) AS total
                FROM pembayaran pb
                JOIN penyewaan p ON p.id = pb.penyewaan_id
                WHERE p.tanggal_mulai BETWEEN %s AND %s
                GROUP BY pb.jenis, pb.status
                """,
                (dari, sampai)
            )
            pembayaran = cursor.fetchall()

            cursor.execute(
                """
                SELECT k.merek, k.nomor_polisi,
                       COUNT(*) AS jumlah,
                       COALESCE(SUM(p.total_biaya), 0) AS total
                FROM penyewaan p
                JOIN kendaraan k ON k.id = p.kendaraan_id
                WHERE p.tanggal_mulai BETWEEN %s AND %s
                GROUP BY k.id, k.merek, k.nomor_polisi
                ORDER BY jumlah DESC, total DESC
                LIMIT 10
                """,
                (dari, sampai)
            )
            terlaris = cursor.fetchall()

            hasil = {
                "jumlah_transaksi": transaksi["jumlah"],
                "nilai_transaksi": transaksi["nilai"],
                "sewa_lunas": 0,
                "denda_lunas": 0,
                "menunggu": 0,
                "terlaris": terlaris,
            }

            for baris in pembayaran:
                if baris["status"] == "Menunggu":
                    hasil["menunggu"] += baris["total"]
                elif baris["jenis"] == "Sewa":
                    hasil["sewa_lunas"] += baris["total"]
                else:
                    hasil["denda_lunas"] += baris["total"]

            return hasil

        finally:
            if cursor:
                cursor.close()
            conn.close()
