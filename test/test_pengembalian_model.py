"""Test PengembalianModel dengan koneksi database MagicMock."""

import unittest
from datetime import date, timedelta
from decimal import Decimal

from models.pengembalianModel import PengembalianModel
from test.helpers import database_palsu, sql_dijalankan

HARI_INI = date.today()


def sewa(mulai=-5, rencana=-3, status="Berjalan", tarif="100000"):
    """Baris penyewaan palsu (tanggal relatif terhadap hari ini)."""
    return {
        "id": 1,
        "pelanggan_id": 7,
        "kendaraan_id": 4,
        "tanggal_mulai": HARI_INI + timedelta(days=mulai),
        "tanggal_rencana_kembali": HARI_INI + timedelta(days=rencana),
        "status": status,
        "tarif_harian": Decimal(tarif),
    }


class TestHitungDenda(unittest.TestCase):

    def test_tepat_waktu_tanpa_denda(self):
        denda, telat, _ = PengembalianModel.hitung_denda(
            100000, date(2026, 11, 10), date(2026, 11, 10)
        )
        self.assertEqual((denda, telat), (0, 0))

    def test_lebih_awal_tanpa_denda(self):
        denda, telat, _ = PengembalianModel.hitung_denda(
            100000, date(2026, 11, 10), date(2026, 11, 8)
        )
        self.assertEqual((denda, telat), (0, 0))

    def test_denda_tarif_dikali_hari_terlambat(self):
        denda, telat, tarif = PengembalianModel.hitung_denda(
            "150000", date(2026, 11, 10), date(2026, 11, 13)
        )
        self.assertEqual(telat, 3)
        self.assertEqual(denda, Decimal("450000"))
        self.assertEqual(tarif, Decimal("150000"))


class TestAjukanPengembalian(unittest.TestCase):

    def jalankan(self, baris_sewa, sudah_ada, tanggal):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.side_effect = [baris_sewa, sudah_ada]
            model = PengembalianModel()
            try:
                hasil = model.ajukan_pengembalian(1, 7, tanggal)
                return hasil, conn, cursor, None
            except Exception as exc:
                return None, conn, cursor, exc

    def test_berhasil_denda_dihitung_dari_tanggal_pilihan(self):
        # rencana kembali 3 hari lalu, kembali kemarin -> terlambat 2 hari
        kemarin = (HARI_INI - timedelta(days=1)).isoformat()
        hasil, conn, cursor, err = self.jalankan(sewa(), None, kemarin)

        self.assertIsNone(err)
        self.assertEqual(hasil["terlambat"], 2)
        self.assertEqual(hasil["denda"], Decimal("200000"))
        conn.commit.assert_called_once()
        conn.rollback.assert_not_called()

        insert = [c for c in cursor.execute.call_args_list
                  if "INSERT INTO PENGEMBALIAN" in
                  " ".join(c.args[0].split()).upper()]
        self.assertEqual(len(insert), 1)
        self.assertEqual(
            insert[0].args[1],
            (1, HARI_INI - timedelta(days=1), Decimal("200000"))
        )

    def test_tepat_waktu_denda_nol(self):
        tanggal = (HARI_INI - timedelta(days=3)).isoformat()
        hasil, *_ , err = self.jalankan(sewa(), None, tanggal)
        self.assertIsNone(err)
        self.assertEqual(hasil["denda"], 0)
        self.assertEqual(hasil["terlambat"], 0)

    def test_tanggal_masa_depan_ditolak_sebelum_ke_database(self):
        besok = (HARI_INI + timedelta(days=1)).isoformat()
        with database_palsu("pengembalianModel") as (conn, cursor):
            model = PengembalianModel()
            with self.assertRaises(ValueError):
                model.ajukan_pengembalian(1, 7, besok)
            cursor.execute.assert_not_called()

    def test_sebelum_tanggal_mulai_ditolak(self):
        sebelum = (HARI_INI - timedelta(days=9)).isoformat()
        hasil, conn, cursor, err = self.jalankan(sewa(), None, sebelum)
        self.assertIsInstance(err, ValueError)
        conn.rollback.assert_called_once()

    def test_format_tanggal_salah(self):
        with database_palsu("pengembalianModel"):
            with self.assertRaises(ValueError):
                PengembalianModel().ajukan_pengembalian(1, 7, "10-11-2026")

    def test_milik_pelanggan_lain_ditolak(self):
        baris = sewa()
        baris["pelanggan_id"] = 99
        _, conn, _, err = self.jalankan(
            baris, None, HARI_INI.isoformat()
        )
        self.assertIsInstance(err, ValueError)
        conn.rollback.assert_called_once()

    def test_sudah_diajukan_ditolak(self):
        _, conn, _, err = self.jalankan(
            sewa(), {"id": 5}, HARI_INI.isoformat()
        )
        self.assertIsInstance(err, ValueError)
        self.assertIn("sudah diajukan", str(err))

    def test_penyewaan_selesai_ditolak(self):
        _, _, _, err = self.jalankan(
            sewa(status="Selesai"), None, HARI_INI.isoformat()
        )
        self.assertIsInstance(err, ValueError)

    def test_tanpa_koneksi_mengembalikan_false(self):
        with database_palsu("pengembalianModel"):
            pass
        from unittest.mock import patch
        with patch("models.pengembalianModel.Database") as db:
            db.return_value.get_connection.return_value = None
            self.assertFalse(
                PengembalianModel().ajukan_pengembalian(
                    1, 7, HARI_INI.isoformat()
                )
            )


class TestProsesPengembalian(unittest.TestCase):

    def test_admin_mengonfirmasi_pengajuan(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                sewa(), {"id": 5, "status": "Diajukan"}
            ]
            hasil = PengembalianModel().process_pengembalian(
                1, HARI_INI.isoformat()
            )

            # rencana kembali 3 hari lalu, kembali hari ini -> telat 3 hari
            self.assertEqual(hasil["terlambat"], 3)
            self.assertEqual(hasil["denda"], Decimal("300000"))
            conn.commit.assert_called_once()

            sql = sql_dijalankan(cursor)
            self.assertTrue(any("SET STATUS = 'SELESAI'" in s for s in sql))
            self.assertTrue(any(
                "UPDATE KENDARAAN SET STATUS = 'TERSEDIA'" in s
                for s in sql
            ))
            self.assertTrue(any(
                "INSERT INTO PEMBAYARAN" in s for s in sql
            ), "tagihan denda harus dibuat saat terlambat")

    def test_tepat_waktu_tidak_membuat_tagihan_denda(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.side_effect = [
                sewa(rencana=0), {"id": 5, "status": "Diajukan"}
            ]
            hasil = PengembalianModel().process_pengembalian(
                1, HARI_INI.isoformat()
            )
            self.assertEqual(hasil["denda"], 0)
            self.assertTrue(hasil)  # dict tetap truthy walau denda 0
            self.assertFalse(any(
                "INSERT INTO PEMBAYARAN" in s
                for s in sql_dijalankan(cursor)
            ))

    def test_tanpa_pengajuan_pelanggan_ditolak(self):
        """Admin tidak bisa membuat pengembalian sendiri."""
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.side_effect = [sewa(), None]
            with self.assertRaises(ValueError):
                PengembalianModel().process_pengembalian(
                    1, HARI_INI.isoformat()
                )
            conn.rollback.assert_called_once()
            conn.commit.assert_not_called()
            self.assertFalse(any(
                s.startswith("INSERT INTO PENGEMBALIAN")
                for s in sql_dijalankan(cursor)
            ))

    def test_tanggal_sebelum_mulai_ditolak(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.side_effect = [sewa(), {"id": 5, "status": "Diajukan"}]
            with self.assertRaises(ValueError):
                PengembalianModel().process_pengembalian(
                    1, (HARI_INI - timedelta(days=30)).isoformat()
                )
            conn.rollback.assert_called_once()


class TestTolakPengajuan(unittest.TestCase):

    def test_menghapus_pengajuan(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.return_value = {"id": 5, "status": "Diajukan"}
            self.assertTrue(PengembalianModel().tolak_pengajuan(1))
            self.assertTrue(any(
                s.startswith("DELETE FROM PENGEMBALIAN")
                for s in sql_dijalankan(cursor)
            ))
            conn.commit.assert_called_once()

    def test_yang_sudah_dikonfirmasi_tidak_bisa_ditolak(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.return_value = {"id": 5, "status": "Dikonfirmasi"}
            with self.assertRaises(ValueError):
                PengembalianModel().tolak_pengajuan(1)
            conn.rollback.assert_called_once()

    def test_tanpa_pengajuan(self):
        with database_palsu("pengembalianModel") as (conn, cursor):
            cursor.fetchone.return_value = None
            with self.assertRaises(ValueError):
                PengembalianModel().tolak_pengajuan(1)


if __name__ == "__main__":
    unittest.main()
