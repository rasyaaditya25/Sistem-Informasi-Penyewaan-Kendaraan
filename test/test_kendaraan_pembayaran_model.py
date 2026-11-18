import unittest
from datetime import date
from decimal import Decimal

from models.kendaraanModel import KendaraanModel
from models.pembayaranModel import PembayaranModel
from test.helpers import database_palsu, sql_dijalankan


class TestKendaraanModel(unittest.TestCase):

    def test_tambah_kendaraan(self):
        with database_palsu("kendaraanModel") as (conn, cursor):
            cursor.lastrowid = 3
            hasil = KendaraanModel().create_kendaraan(
                "Mobil", " Avanza ", "dd 1234 ab", "300000"
            )
            self.assertEqual(hasil, 3)
            params = cursor.execute.call_args.args[1]
            self.assertEqual(
                params, ("Mobil", "Avanza", "DD 1234 AB", Decimal("300000"))
            )

    def test_validasi_input(self):
        with database_palsu("kendaraanModel"):
            model = KendaraanModel()
            for args in (("Truk", "A", "B", 1), ("Mobil", "", "B", 1),
                         ("Mobil", "A", "", 1), ("Mobil", "A", "B", 0),
                         ("Mobil", "A", "B", "abc")):
                with self.assertRaises(ValueError, msg=args):
                    model.create_kendaraan(*args)

    def test_status_disewa_tidak_bisa_diatur_manual(self):
        with database_palsu("kendaraanModel"):
            with self.assertRaises(ValueError):
                KendaraanModel().update_status(1, "Disewa")

    def test_tidak_bisa_hapus_bila_ada_riwayat(self):
        with database_palsu("kendaraanModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                {"id": 1, "status": "Tersedia"}, {"jumlah": 2}
            ]
            with self.assertRaises(ValueError):
                KendaraanModel().delete_kendaraan(1)
            conn.rollback.assert_called_once()

    def test_hapus_berhasil(self):
        with database_palsu("kendaraanModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                {"id": 1, "status": "Tersedia"}, {"jumlah": 0}
            ]
            cursor.rowcount = 1
            self.assertTrue(KendaraanModel().delete_kendaraan(1))
            conn.commit.assert_called_once()


class TestPembayaranModel(unittest.TestCase):

    def test_bayar_milik_sendiri(self):
        with database_palsu("pembayaranModel") as (conn, cursor):
            cursor.fetchone.return_value = {
                "id": 1, "status": "Menunggu", "pelanggan_id": 7
            }
            self.assertTrue(PembayaranModel().bayar(1, 7, "Transfer"))
            update = cursor.execute.call_args.args
            self.assertEqual(update[1], ("Transfer", date.today(), 1))
            conn.commit.assert_called_once()

    def test_tidak_bisa_membayar_tagihan_orang_lain(self):
        with database_palsu("pembayaranModel") as (conn, cursor):
            cursor.fetchone.return_value = {
                "id": 1, "status": "Menunggu", "pelanggan_id": 99
            }
            with self.assertRaises(ValueError):
                PembayaranModel().bayar(1, 7, "Tunai")
            conn.rollback.assert_called_once()

    def test_tidak_bisa_membayar_dua_kali(self):
        with database_palsu("pembayaranModel") as (conn, cursor):
            cursor.fetchone.return_value = {
                "id": 1, "status": "Lunas", "pelanggan_id": 7
            }
            with self.assertRaises(ValueError):
                PembayaranModel().bayar(1, 7, "Tunai")

    def test_metode_tidak_valid(self):
        with database_palsu("pembayaranModel"):
            with self.assertRaises(ValueError):
                PembayaranModel().bayar(1, 7, "Kartu Kredit")

    def test_ubah_status_tidak_valid(self):
        with database_palsu("pembayaranModel"):
            with self.assertRaises(ValueError):
                PembayaranModel().ubah_status(1, "Batal")

    def test_daftar_pelanggan_difilter(self):
        with database_palsu("pembayaranModel") as (conn, cursor):
            cursor.fetchall.return_value = []
            PembayaranModel().get_all_pembayaran(pelanggan_id=7)
            query, params = cursor.execute.call_args.args
            self.assertIn("WHERE p.pelanggan_id = %s", query)
            self.assertEqual(params, (7,))


if __name__ == "__main__":
    unittest.main()
