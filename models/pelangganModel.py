from config.database import Database


class PelangganModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "pelanggan"

    # READ
    def get_all_pelanggan(self):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            query = f"SELECT * FROM {self.table_name} ORDER BY id DESC"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        return []

    # CREATE
    def create_pelanggan(self, nama, no_identitas, no_telepon):
        if not nama.strip() or not no_identitas.strip() or not no_telepon.strip():
            raise ValueError("Nama, nomor identitas, dan telepon wajib diisi.")

        if self.conn:
            cursor = self.conn.cursor()
            query = f"""
                INSERT INTO {self.table_name} (nama, no_identitas, no_telepon)
                VALUES (%s, %s, %s)
            """
            cursor.execute(
                query, (nama.strip(), no_identitas.strip(), no_telepon.strip())
            )
            self.conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        return False