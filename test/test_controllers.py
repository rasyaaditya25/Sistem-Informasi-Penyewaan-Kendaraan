"""Test controller: model diganti MagicMock, fokus pada hak akses & delegasi."""

import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from controllers.akses import ADMIN, PELANGGAN, PEMILIK
from test.helpers import login_sebagai, logout


def buat(kelas_controller, path_model):
    """Membuat controller dengan model MagicMock."""
    with patch(path_model) as kelas_model:
        controller = kelas_controller()
    return controller, kelas_model.return_value


class BaseTest(unittest.TestCase):
    def tearDown(self):
        logout()


class TestPengembalianController(BaseTest):

    def setUp(self):
        from controllers.pengembalian_controller import (
            PengembalianController
        )
        self.c, self.model = buat(
            PengembalianController,
            "controllers.pengembalian_controller.PengembalianModel"
        )

    def test_pelanggan_ajukan_dengan_tanggal_pilihan(self):
        login_sebagai(PELANGGAN)
        self.model.ajukan_pengembalian.return_value = {"denda": 0}

        self.c.ajukan(12, "2026-11-10")

        # id pelanggan diambil dari session, bukan dari parameter
        self.model.ajukan_pengembalian.assert_called_once_with(
            12, 7, "2026-11-10"
        )

    def test_admin_tidak_bisa_mengajukan(self):
        login_sebagai(ADMIN)
        with self.assertRaises(PermissionError):
            self.c.ajukan(12, "2026-11-10")
        self.model.ajukan_pengembalian.assert_not_called()

    def test_pelanggan_tidak_bisa_mengonfirmasi_atau_menolak(self):
        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            self.c.proses(1, "2026-11-10")
        with self.assertRaises(PermissionError):
            self.c.tolak(1)

    def test_admin_proses_dan_tolak(self):
        login_sebagai(ADMIN)
        self.c.proses(3, "2026-11-10")
        self.model.process_pengembalian.assert_called_once_with(
            3, "2026-11-10"
        )
        self.c.tolak(3)
        self.model.tolak_pengajuan.assert_called_once_with(3)

    def test_daftar_pengajuan_hanya_status_diajukan(self):
        login_sebagai(ADMIN)
        self.model.get_penyewaan_berjalan.return_value = [
            {"id": 1, "status_pengembalian": "Diajukan"},
            {"id": 2, "status_pengembalian": None},
        ]
        hasil = self.c.daftar_pengajuan()
        self.assertEqual([p["id"] for p in hasil], [1])

    def test_daftar_saya_memakai_id_login(self):
        login_sebagai(PELANGGAN)
        self.c.daftar_saya()
        self.model.get_all_pengembalian.assert_called_once_with(7)

    def test_pemilik_hanya_baca(self):
        login_sebagai(PEMILIK)
        self.c.daftar()
        self.model.get_all_pengembalian.assert_called_once_with()
        with self.assertRaises(PermissionError):
            self.c.proses(1, "2026-11-10")

    def test_hitung_denda_didelegasikan(self):
        self.model.hitung_denda.return_value = ("denda", 2, "tarif")
        hasil = self.c.hitung_denda(100000, date(2026, 1, 1),
                                    date(2026, 1, 3))
        self.assertEqual(hasil, ("denda", 2, "tarif"))


class TestPenyewaanController(BaseTest):

    def setUp(self):
        from controllers.penyewaan_controller import PenyewaanController
        self.c, self.model = buat(
            PenyewaanController,
            "controllers.penyewaan_controller.PenyewaanModel"
        )

    def test_admin_tidak_punya_fitur_membuat_penyewaan(self):
        self.assertFalse(hasattr(self.c, "buat"))
        self.assertFalse(hasattr(self.c, "daftar_pelanggan"))

    def test_pelanggan_menyewa_atas_namanya_sendiri(self):
        login_sebagai(PELANGGAN)
        besok = date.today() + timedelta(days=1)

        self.c.buat_sendiri(5, date.today().isoformat(), besok.isoformat())

        self.model.create_penyewaan.assert_called_once_with(
            7, 5, date.today().isoformat(), besok.isoformat()
        )

    def test_tanggal_mulai_lampau_ditolak(self):
        login_sebagai(PELANGGAN)
        kemarin = (date.today() - timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            self.c.buat_sendiri(5, kemarin, date.today().isoformat())
        self.model.create_penyewaan.assert_not_called()

    def test_admin_dan_pemilik_tidak_bisa_menyewa(self):
        for role in (ADMIN, PEMILIK):
            login_sebagai(role)
            with self.assertRaises(PermissionError):
                self.c.buat_sendiri(
                    5, date.today().isoformat(), date.today().isoformat()
                )

    def test_batalkan_hanya_admin(self):
        login_sebagai(ADMIN)
        self.c.batalkan(4)
        self.model.batalkan_penyewaan.assert_called_once_with(4)

        for role in (PELANGGAN, PEMILIK):
            login_sebagai(role)
            with self.assertRaises(PermissionError):
                self.c.batalkan(4)

    def test_daftar_admin_dan_pemilik(self):
        for role in (ADMIN, PEMILIK):
            login_sebagai(role)
            self.c.daftar()
        self.assertEqual(self.model.get_all_penyewaan.call_count, 2)

        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            self.c.daftar()


class TestUserController(BaseTest):

    def setUp(self):
        from controllers.user_controller import UserController
        self.c, self.model = buat(
            UserController, "controllers.user_controller.UserModel"
        )

    def test_admin_tidak_punya_fitur_tambah_pelanggan(self):
        self.assertFalse(hasattr(self.c, "tambah_pelanggan"))

    def test_login_berhasil_mengisi_session(self):
        from controllers.akses import Session
        self.model.autentikasi.return_value = {
            "id_user": 7, "username": "budi", "role": PELANGGAN
        }
        self.assertIsNotNone(self.c.login("budi", "rahasia123"))
        self.assertEqual(Session.role(), PELANGGAN)

    def test_login_gagal_tidak_mengisi_session(self):
        from controllers.akses import Session
        self.model.autentikasi.return_value = None
        self.assertIsNone(self.c.login("budi", "salah"))
        self.assertIsNone(Session.user)

    def test_logout(self):
        from controllers.akses import Session
        login_sebagai(PELANGGAN)
        self.c.logout()
        self.assertIsNone(Session.user)

    def test_register_tanpa_login(self):
        self.c.register("a", "password1", "123", "08", PELANGGAN)
        self.model.register_user.assert_called_once_with(
            "a", "password1", "123", "08", PELANGGAN
        )

    def test_kelola_pelanggan_hanya_admin(self):
        login_sebagai(ADMIN)
        self.c.daftar_pelanggan()
        self.c.ubah_pelanggan(7, "x", "1", "2")
        self.c.hapus_pelanggan(7)
        self.model.update_pelanggan.assert_called_once_with(7, "x", "1", "2")
        self.model.delete_pelanggan.assert_called_once_with(7)

        login_sebagai(PELANGGAN)
        for fn, args in ((self.c.daftar_pelanggan, ()),
                         (self.c.ubah_pelanggan, (7, "x", "1", "2")),
                         (self.c.hapus_pelanggan, (7,))):
            with self.assertRaises(PermissionError):
                fn(*args)


class TestKendaraanController(BaseTest):

    def setUp(self):
        from controllers.kendaraan_controller import KendaraanController
        self.c, self.model = buat(
            KendaraanController,
            "controllers.kendaraan_controller.KendaraanModel"
        )

    def test_semua_role_boleh_melihat(self):
        for role in (ADMIN, PELANGGAN, PEMILIK):
            login_sebagai(role)
            self.c.daftar()
        self.assertEqual(self.model.get_all_kendaraan.call_count, 3)

    def test_hanya_admin_mengelola(self):
        login_sebagai(ADMIN)
        self.c.tambah("Mobil", "Avanza", "DD 1 A", 300000)
        self.model.create_kendaraan.assert_called_once()

        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            self.c.tambah("Mobil", "Avanza", "DD 1 A", 300000)
        with self.assertRaises(PermissionError):
            self.c.hapus(1)
        with self.assertRaises(PermissionError):
            self.c.ubah_status(1, "Perawatan")


class TestPembayaranController(BaseTest):

    def setUp(self):
        from controllers.pembayaran_controller import PembayaranController
        self.c, self.model = buat(
            PembayaranController,
            "controllers.pembayaran_controller.PembayaranModel"
        )

    def test_pelanggan_bayar_tagihan_sendiri(self):
        login_sebagai(PELANGGAN)
        self.c.bayar(3, "Transfer")
        self.model.bayar.assert_called_once_with(3, 7, "Transfer")

    def test_hanya_admin_ubah_status(self):
        login_sebagai(ADMIN)
        self.c.ubah_status(3, "Lunas")
        self.model.ubah_status.assert_called_once_with(3, "Lunas")

        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            self.c.ubah_status(3, "Lunas")


class TestLaporanController(BaseTest):

    def setUp(self):
        from controllers.laporan_controller import LaporanController
        self.c, self.model = buat(
            LaporanController,
            "controllers.laporan_controller.LaporanModel"
        )

    def test_pemilik_melihat_laporan(self):
        login_sebagai(PEMILIK)
        self.c.ringkasan("2026-11-01", "2026-11-30")
        self.model.ringkasan.assert_called_once_with(
            "2026-11-01", "2026-11-30"
        )

    def test_periode_terbalik_ditolak(self):
        login_sebagai(PEMILIK)
        with self.assertRaises(ValueError):
            self.c.ringkasan("2026-11-30", "2026-11-01")

    def test_pelanggan_tidak_boleh(self):
        login_sebagai(PELANGGAN)
        with self.assertRaises(PermissionError):
            self.c.ringkasan("2026-11-01", "2026-11-30")


if __name__ == "__main__":
    unittest.main()
