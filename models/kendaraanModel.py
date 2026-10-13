from config.database import Database


class KendaraanModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "kendaraan"

    # READ
    def get_all_kendaraan(self):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            query = f"SELECT * FROM {self.table_name} ORDER BY id DESC"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        return []

    # CREATE
    def create_kendaraan(self, jenis, merek, nomor_polisi, tarif_harian):
        if jenis not in ("Motor", "Mobil"):
            raise ValueError("Jenis kendaraan harus Motor atau Mobil.")
        if not merek.strip() or not nomor_polisi.strip():
            raise ValueError("Merek dan nomor polisi wajib diisi.")
        if tarif_harian <= 0:
            raise ValueError("Tarif harian harus lebih dari nol.")

        if self.conn:
            cursor = self.conn.cursor()
            query = f"""
                INSERT INTO {self.table_name} (jenis, merek, nomor_polisi, tarif_harian, status)
                VALUES (%s, %s, %s, %s, 'Tersedia')
            """
            cursor.execute(
                query,
                (jenis, merek.strip(), nomor_polisi.strip().upper(), tarif_harian),
            )
            self.conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        return False

    # UPDATE STATUS
    def update_status(self, kendaraan_id, status):
        if status not in ("Tersedia", "Disewa", "Perawatan"):
            raise ValueError("Status tidak valid.")

        if self.conn:
            cursor = self.conn.cursor()
            query = f"UPDATE {self.table_name} SET status=%s WHERE id=%s"
            cursor.execute(query, (status, kendaraan_id))
            self.conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        return False

    # DELETE
    def delete_kendaraan(self, kendaraan_id):
        if self.conn:
            cursor = self.conn.cursor()
            query = f"DELETE FROM {self.table_name} WHERE id=%s AND status='Tersedia'"
            cursor.execute(query, (kendaraan_id,))
            self.conn.commit()
            deleted = cursor.rowcount > 0
            cursor.close()
            return deleted
        return False