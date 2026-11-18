import unittest

from controllers.akses import Session, wajib_role, ADMIN, PELANGGAN, PEMILIK
from test.helpers import login_sebagai, logout


@wajib_role(ADMIN)
def hanya_admin():
    return "ok"


@wajib_role(ADMIN, PEMILIK)
def admin_atau_pemilik():
    return "ok"


class TestSession(unittest.TestCase):

    def tearDown(self):
        logout()

    def test_login_menyimpan_user(self):
        login_sebagai(PELANGGAN)
        self.assertEqual(Session.role(), PELANGGAN)
        self.assertEqual(Session.id_user(), 7)

    def test_logout_menghapus_user(self):
        login_sebagai(ADMIN)
        Session.logout()
        self.assertIsNone(Session.user)
        self.assertIsNone(Session.role())
        self.assertIsNone(Session.id_user())


class TestWajibRole(unittest.TestCase):

    def tearDown(self):
        logout()

    def test_tanpa_login_ditolak(self):
        logout()
        with self.assertRaises(PermissionError):
            hanya_admin()

    def test_role_diizinkan(self):
        login_sebagai(ADMIN)
        self.assertEqual(hanya_admin(), "ok")

    def test_role_tidak_diizinkan(self):
        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            hanya_admin()

    def test_beberapa_role(self):
        for role in (ADMIN, PEMILIK):
            login_sebagai(role)
            self.assertEqual(admin_atau_pemilik(), "ok")

        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            admin_atau_pemilik()


if __name__ == "__main__":
    unittest.main()
