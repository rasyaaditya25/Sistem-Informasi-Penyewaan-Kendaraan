import unittest
from datetime import date, timedelta
from decimal import Decimal

from models.penyewaanModel import PenyewaanModel
from test.helpers import database_palsu, sql_dijalankan

HARI_INI = date.today()


class TestCreatePenyewaan(unittest.TestCase):

    def test_total_biaya_hari_mulai_dan_kembali_dihitung(self):
        mulai = HARI_INI
        kembali = HARI_INI + timedelta(days=2)  # 3 hari

        with database_palsu("penyewaanModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                {"id": 4, "tarif_harian": Decimal("200000"),
                 "status": "Tersedia"},
                {"id_user": 7},
            ]
            cursor.lastrowid = 11

            hasil = PenyewaanModel().create_penyewaan(
                7, 4, mulai.isoformat(), kembali.isoformat()
            )

            self.assertEqual(hasil, 11)
            insert = next(
                c for c in cursor.execute.call_args_list
                if "INSERT INTO PENYEWAAN" in
                " ".join(c.args[0].split()).upper()
            )
            self.assertEqual(insert.args[1][-1], Decimal("600000"))

            sql = sql_dijalankan(cursor)
            self.assertTrue(any("INSERT INTO PEMBAYARAN" in s for s in sql))
            self.assertTrue(any(
                "SET STATUS = 'DISEWA'" in s for s in sql
            ))
            conn.commit.assert_called_once()

    def test_sehari_dihitung_satu_hari(self):
        with database_palsu("penyewaanModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                {"id": 4, "tarif_harian": Decimal("100000"),
                 "status": "Tersedia"},
                {"id_user": 7},
            ]
            PenyewaanModel().create_penyewaan(
                7, 4, HARI_INI.isoformat(), HARI_INI.isoformat()
            )
            insert = next(
                c for c in cursor.execute.call_args_list
                if "INSERT INTO PENYEWAAN" in
                " ".join(c.args[0].split()).upper()
            )
            self.assertEqual(insert.args[1][-1], Decimal("100000"))

    def test_kendaraan_tidak_tersedia(self):
        with database_palsu("penyewaanModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                {"id": 4, "tarif_harian": Decimal("1"), "status": "Disewa"}
            ]
            with self.assertRaises(ValueError):
                PenyewaanModel().create_penyewaan(
                    7, 4, HARI_INI.isoformat(), HARI_INI.isoformat()
                )
            conn.rollback.assert_called_once()

    def test_tanggal_kembali_sebelum_mulai(self):
        with database_palsu("penyewaanModel") as (conn, cursor):
            with self.assertRaises(ValueError):
                PenyewaanModel().create_penyewaan(
                    7, 4, HARI_INI.isoformat(),
                    (HARI_INI - timedelta(days=1)).isoformat()
                )
            cursor.execute.assert_not_called()


class TestBatalkanPenyewaan(unittest.TestCase):

    def jalankan(self, fetchone):
        with database_palsu("penyewaanModel") as (conn, cursor):
            cursor.fetchone.side_effect = fetchone
            model = PenyewaanModel()
            try:
                return model.batalkan_penyewaan(3), conn, cursor, None
            except ValueError as exc:
                return None, conn, cursor, exc

    def test_berhasil_menghapus_dan_membebaskan_kendaraan(self):
        hasil, conn, cursor, err = self.jalankan([
            {"id": 3, "kendaraan_id": 4, "status": "Berjalan"},
            None,                  # belum ada pengembalian
            {"jumlah": 0},         # belum ada pembayaran lunas
        ])
        self.assertTrue(hasil)
        sql = sql_dijalankan(cursor)
        self.assertTrue(any(s.startswith("DELETE FROM PEMBAYARAN") for s in sql))
        self.assertTrue(any(s.startswith("DELETE FROM PENYEWAAN") for s in sql))
        self.assertTrue(any(
            "UPDATE KENDARAAN SET STATUS = 'TERSEDIA'" in s for s in sql
        ))
        conn.commit.assert_called_once()

    def test_tidak_ditemukan(self):
        _, conn, _, err = self.jalankan([None])
        self.assertIsInstance(err, ValueError)
        conn.rollback.assert_called_once()

    def test_sudah_selesai(self):
        _, _, _, err = self.jalankan(
            [{"id": 3, "kendaraan_id": 4, "status": "Selesai"}]
        )
        self.assertIn("selesai", str(err).lower())

    def test_sudah_diajukan_pengembalian(self):
        _, _, _, err = self.jalankan([
            {"id": 3, "kendaraan_id": 4, "status": "Berjalan"},
            {"id": 8},
        ])
        self.assertIn("pengembalian", str(err).lower())

    def test_sudah_dibayar(self):
        _, conn, cursor, err = self.jalankan([
            {"id": 3, "kendaraan_id": 4, "status": "Berjalan"},
            None,
            {"jumlah": 1},
        ])
        self.assertIn("dibayar", str(err))
        self.assertFalse(any(
            s.startswith("DELETE") for s in sql_dijalankan(cursor)
        ))
        conn.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
