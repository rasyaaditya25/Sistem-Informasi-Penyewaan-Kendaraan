
import hashlib
from config.database import Database


class UserModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        if self.conn:
            # Hindari data basi (snapshot lama) pada koneksi yang dipakai lama
            self.conn.autocommit = True
        self.table_name = "user"

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(
            password.encode('utf-8')
        ).hexdigest()

    # AUTENTIKASI
    def autentikasi(self, username, password):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            password_hash = self.hash_password(password)

            query = f"""
                SELECT id_user, username, no_identitas,
                       no_telepon, role
                FROM {self.table_name}
                WHERE username = %s AND password = %s
            """

            cursor.execute(query, (username, password_hash))
            user = cursor.fetchone()
            cursor.close()

            return user

        return None

    # REGISTER USER
    def register_user(self, username, password, no_identitas,
                    no_telepon, role):

        if not self.conn:
            return False

        # Validasi role
        if role not in ['Pelanggan', 'Pemilik Rental']:
            print("Role tidak valid!")
            return False

        # Validasi data
        if not all([username, password, no_identitas, no_telepon]):
            print("Semua data wajib diisi!")
            return False

        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)

        query = f"""
            INSERT INTO {self.table_name}
            (username, password, no_identitas, no_telepon, role)
            VALUES (%s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query,
                (
                    username,
                    password_hash,
                    no_identitas,
                    no_telepon,
                    role
                )
            )

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Registrasi gagal: {e}")
            return False

        finally:
            cursor.close()

    # READ ALL PELANGGAN
    def get_all_pelanggan(self):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)

            query = """
                SELECT id_user, username, no_identitas, no_telepon
                FROM user
                WHERE role = 'Pelanggan'
                ORDER BY id_user DESC
            """

            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()

            return result

        return []

    # READ PELANGGAN BY ID
    def get_pelanggan_by_id(self, id_user):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)

            query = """
                SELECT id_user, username, no_identitas, no_telepon
                FROM user
                WHERE id_user = %s AND role = 'Pelanggan'
            """

            cursor.execute(query, (id_user,))
            result = cursor.fetchone()
            cursor.close()

            return result

        return None

    # UPDATE PELANGGAN
    def update_pelanggan(self, id_user, username,
                         no_identitas, no_telepon):

        if self.conn:
            cursor = self.conn.cursor()

            query = """
                UPDATE user
                SET username = %s,
                    no_identitas = %s,
                    no_telepon = %s
                WHERE id_user = %s AND role = 'Pelanggan'
            """

            try:
                cursor.execute(
                    query,
                    (username, no_identitas, no_telepon, id_user)
                )

                self.conn.commit()
                return cursor.rowcount > 0

            except Exception as e:
                self.conn.rollback()
                print(f"Gagal mengubah pelanggan: {e}")
                return False

            finally:
                cursor.close()

        return False

    # DELETE PELANGGAN
    def delete_pelanggan(self, id_user):
        if self.conn:
            cursor = self.conn.cursor()

            query = """
                DELETE FROM user
                WHERE id_user = %s AND role = 'Pelanggan'
            """

            try:
                cursor.execute(query, (id_user,))
                self.conn.commit()
                return cursor.rowcount > 0

            except Exception as e:
                self.conn.rollback()
                print(f"Gagal menghapus pelanggan: {e}")
                return False

            finally:
                cursor.close()

        return False
