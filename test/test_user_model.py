import hashlib
import unittest
from unittest.mock import MagicMock, patch

from models.user_model import UserModel


def buat_model():
    """UserModel dengan koneksi MagicMock. -> (model, conn, cursor)"""
    with patch("models.user_model.Database") as kelas_db:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        kelas_db.return_value.get_connection.return_value = conn
        model = UserModel()
    return model, conn, cursor


class TestUserModel(unittest.TestCase):

    def test_hash_password_sha256(self):
        self.assertEqual(
            UserModel.hash_password("rahasia123"),
            hashlib.sha256(b"rahasia123").hexdigest()
        )

    def test_autentikasi_memakai_password_ter_hash(self):
        model, _, cursor = buat_model()
        cursor.fetchone.return_value = {"id_user": 7, "role": "Pelanggan"}

        user = model.autentikasi("budi", "rahasia123")

        self.assertEqual(user["id_user"], 7)
        params = cursor.execute.call_args.args[1]
        self.assertEqual(params[0], "budi")
        self.assertNotEqual(params[1], "rahasia123")
        self.assertEqual(params[1], UserModel.hash_password("rahasia123"))

    def test_autentikasi_gagal(self):
        model, _, cursor = buat_model()
        cursor.fetchone.return_value = None
        self.assertIsNone(model.autentikasi("budi", "salah"))

    def test_register_pelanggan_berhasil(self):
        model, conn, cursor = buat_model()
        self.assertTrue(
            model.register_user("budi", "pass12345", "123", "08", "Pelanggan")
        )
        conn.commit.assert_called_once()

    def test_register_tidak_boleh_menjadi_admin(self):
        model, conn, cursor = buat_model()
        self.assertFalse(
            model.register_user("x", "pass12345", "1", "2", "Admin")
        )
        cursor.execute.assert_not_called()

    def test_register_data_kosong(self):
        model, _, cursor = buat_model()
        self.assertFalse(
            model.register_user("", "pass12345", "1", "2", "Pelanggan")
        )
        cursor.execute.assert_not_called()

    def test_register_duplikat_rollback(self):
        model, conn, cursor = buat_model()
        cursor.execute.side_effect = Exception("Duplicate entry")
        self.assertFalse(
            model.register_user("budi", "pass12345", "1", "2", "Pelanggan")
        )
        conn.rollback.assert_called_once()

    def test_tidak_ada_fitur_create_pelanggan(self):
        model, _, _ = buat_model()
        self.assertFalse(hasattr(model, "create_pelanggan"))

    def test_update_pelanggan(self):
        model, conn, cursor = buat_model()
        cursor.rowcount = 1
        self.assertTrue(model.update_pelanggan(7, "baru", "123", "08"))
        conn.commit.assert_called_once()

    def test_tanpa_koneksi(self):
        with patch("models.user_model.Database") as kelas_db:
            kelas_db.return_value.get_connection.return_value = None
            model = UserModel()
        self.assertIsNone(model.autentikasi("a", "b"))
        self.assertEqual(model.get_all_pelanggan(), [])


if __name__ == "__main__":
    unittest.main()
