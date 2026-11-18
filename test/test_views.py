"""
Test tampilan dengan controller MagicMock (tanpa database).
Butuh layar; otomatis dilewati bila tidak ada display
(di Linux server gunakan:  xvfb-run -a python -m unittest discover -s test -t .)
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

try:
    import customtkinter as ctk
    _root = ctk.CTk()
    _root.withdraw()
    ADA_LAYAR = True
except Exception:  # tidak ada display / customtkinter
    ADA_LAYAR = False
    _root = None

if ADA_LAYAR:
    from models.pengembalianModel import PengembalianModel
    from views.shared.komponen import TabelData
    from views.shared.shell import DashboardShell, NAMA_LOGOUT
    from views.admin.dashboard import AdminDashboard
    from views.pelanggan.dashboard import PelangganDashboard
    from views.pemilik.dashboard import PemilikDashboard
    from views.pelanggan.pengembalian_tab import PengembalianPelangganView
    from views.admin.pengembalian_tab import PengembalianAdminView
    from views.admin.pelanggan_tab import KelolaPelangganView
    from views.admin.penyewaan_tab import PenyewaanAdminView

HARI_INI = date.today()
USER = {"id_user": 1, "username": "tester", "role": "Admin"}


def semua_widget(widget):
    hasil = [widget]
    for anak in widget.winfo_children():
        hasil.extend(semua_widget(anak))
    return hasil


def teks_tombol(widget):
    teks = []
    for w in semua_widget(widget):
        if isinstance(w, ctk.CTkButton):
            teks.append(w.cget("text"))
    return teks


def controllers_palsu():
    nama = ["user", "kendaraan", "penyewaan", "pengembalian",
            "pembayaran", "laporan"]
    c = {n: MagicMock(name=n) for n in nama}
    for n in nama:
        for fungsi in ("daftar", "daftar_saya", "daftar_pelanggan",
                       "daftar_pengajuan", "daftar_penyewaan_berjalan_saya",
                       "daftar_kendaraan_tersedia"):
            getattr(c[n], fungsi).return_value = []
    c["pengembalian"].hitung_denda.side_effect = PengembalianModel.hitung_denda
    c["laporan"].ringkasan.return_value = {
        "jumlah_transaksi": 0, "nilai_transaksi": 0, "sewa_lunas": 0,
        "denda_lunas": 0, "menunggu": 0, "terlaris": []
    }
    return c


@unittest.skipUnless(ADA_LAYAR, "tidak ada display")
class TestNavigasiDanLogout(unittest.TestCase):

    def buat(self, kelas, role):
        user = dict(USER, role=role)
        self.on_logout = MagicMock()
        shell = kelas(_root, controllers_palsu(), user, self.on_logout)
        self.addCleanup(shell.destroy)
        return shell

    def test_menu_admin(self):
        shell = self.buat(AdminDashboard, "Admin")
        self.assertEqual(
            list(shell.pembuat),
            ["Kendaraan", "Pelanggan", "Peminjaman",
             "Pengembalian", "Pembayaran"]
        )
        self.assertIn(NAMA_LOGOUT, shell.tombol_menu)

    def test_menu_pelanggan(self):
        shell = self.buat(PelangganDashboard, "Pelanggan")
        self.assertEqual(
            list(shell.pembuat),
            ["Kendaraan", "Sewa Kendaraan", "Pembayaran",
             "Pengembalian", "Riwayat"]
        )
        self.assertIn(NAMA_LOGOUT, shell.tombol_menu)

    def test_menu_pemilik(self):
        shell = self.buat(PemilikDashboard, "Pemilik Rental")
        self.assertEqual(
            list(shell.pembuat),
            ["Data Peminjaman", "Data Pengembalian", "Laporan"]
        )
        self.assertIn(NAMA_LOGOUT, shell.tombol_menu)

    def test_semua_halaman_bisa_dibuka(self):
        for kelas, role in ((AdminDashboard, "Admin"),
                            (PelangganDashboard, "Pelanggan"),
                            (PemilikDashboard, "Pemilik Rental")):
            shell = self.buat(kelas, role)
            for nama in list(shell.pembuat):
                shell.tampilkan(nama)
            self.assertEqual(shell.aktif, list(shell.pembuat)[-1])

    def test_tombol_logout_tidak_mengganti_halaman(self):
        shell = self.buat(AdminDashboard, "Admin")
        awal = shell.aktif
        with patch("tkinter.messagebox.askyesno", return_value=False):
            shell.tombol_menu[NAMA_LOGOUT].invoke()
        self.assertEqual(shell.aktif, awal)
        self.assertNotIn(NAMA_LOGOUT, shell.halaman)

    def test_tombol_logout_meminta_konfirmasi(self):
        shell = self.buat(AdminDashboard, "Admin")

        with patch("tkinter.messagebox.askyesno",
                   return_value=False) as tanya:
            shell.tombol_menu[NAMA_LOGOUT].invoke()
        tanya.assert_called_once()
        self.on_logout.assert_not_called()

        with patch("tkinter.messagebox.askyesno", return_value=True):
            shell.tombol_menu[NAMA_LOGOUT].invoke()
        self.on_logout.assert_called_once()


@unittest.skipUnless(ADA_LAYAR, "tidak ada display")
class TestPerubahanAdmin(unittest.TestCase):

    def buat(self, kelas, controller):
        view = kelas(_root, controller)
        self.addCleanup(view.destroy)
        return view

    def test_pelanggan_tanpa_tombol_tambah(self):
        view = self.buat(KelolaPelangganView, MagicMock(
            daftar_pelanggan=MagicMock(return_value=[])))
        for teks in teks_tombol(view):
            self.assertNotIn("tambah", teks.lower())
        self.assertFalse(hasattr(view, "tambah_pelanggan"))

    def test_pelanggan_ubah_dan_hapus_tetap_ada(self):
        view = self.buat(KelolaPelangganView, MagicMock(
            daftar_pelanggan=MagicMock(return_value=[])))
        teks = " ".join(teks_tombol(view))
        self.assertIn("Simpan Perubahan", teks)
        self.assertIn("Hapus Pelanggan", teks)

    def test_pelanggan_ubah_memanggil_controller(self):
        ctrl = MagicMock()
        ctrl.daftar_pelanggan.return_value = [{
            "id_user": 7, "username": "budi",
            "no_identitas": "123", "no_telepon": "08"
        }]
        view = self.buat(KelolaPelangganView, ctrl)
        view.pilih_pelanggan(ctrl.daftar_pelanggan.return_value[0])
        view.entry_telepon.delete(0, "end")
        view.entry_telepon.insert(0, "0899")

        with patch("tkinter.messagebox.askyesno", return_value=True), \
                patch("tkinter.messagebox.showinfo"):
            view.ubah_pelanggan()

        ctrl.ubah_pelanggan.assert_called_once_with(7, "budi", "123", "0899")

    def test_peminjaman_tanpa_tombol_tambah(self):
        view = self.buat(PenyewaanAdminView, MagicMock(
            daftar=MagicMock(return_value=[])))
        for teks in teks_tombol(view):
            self.assertNotIn("tambah", teks.lower())
        self.assertFalse(hasattr(view, "tambah_penyewaan"))
        self.assertFalse(hasattr(view, "picker_mulai"))

    def test_peminjaman_batalkan(self):
        ctrl = MagicMock()
        ctrl.daftar.return_value = [{
            "id": 3, "username": "budi", "jenis": "Mobil",
            "merek": "Avanza", "nomor_polisi": "DD 1 A",
            "tanggal_mulai": HARI_INI, "tanggal_rencana_kembali": HARI_INI,
            "total_biaya": 100000, "status": "Berjalan"
        }]
        view = self.buat(PenyewaanAdminView, ctrl)
        view.tabel_data.tabel.selection_set("0")
        view.update()

        with patch("tkinter.messagebox.askyesno", return_value=True), \
                patch("tkinter.messagebox.showinfo"):
            view.batalkan()

        ctrl.batalkan.assert_called_once_with(3)

    def test_pengembalian_admin_tanpa_form_tambah(self):
        view = self.buat(PengembalianAdminView, MagicMock(
            daftar=MagicMock(return_value=[]),
            daftar_pengajuan=MagicMock(return_value=[])))
        teks = " ".join(teks_tombol(view))
        self.assertIn("Konfirmasi", teks)
        self.assertIn("Tolak", teks)
        self.assertNotIn("Tambah", teks)
        self.assertNotIn("Proses Pengembalian", teks)

    def test_pengembalian_admin_konfirmasi_dengan_koreksi_tanggal(self):
        pengajuan = {
            "id": 3, "username": "budi", "merek": "Avanza",
            "nomor_polisi": "DD 1 A",
            "tanggal_mulai": HARI_INI - timedelta(days=5),
            "tanggal_rencana_kembali": HARI_INI - timedelta(days=3),
            "tanggal_pengajuan": HARI_INI,
            "tarif_harian": Decimal("100000"),
            "status_pengembalian": "Diajukan",
        }
        ctrl = MagicMock()
        ctrl.daftar.return_value = []
        ctrl.daftar_pengajuan.return_value = [pengajuan]
        ctrl.hitung_denda.side_effect = PengembalianModel.hitung_denda
        ctrl.proses.return_value = {"denda": 0, "terlambat": 0}

        view = self.buat(PengembalianAdminView, ctrl)
        view.tabel_pengajuan.tabel.selection_set("0")
        view.update()

        # tanggal pengajuan terisi otomatis, denda 3 hari x 100rb
        self.assertEqual(view.picker_kembali.get(), HARI_INI.isoformat())
        self.assertIn("300.000", view.label_denda.cget("text"))

        # admin mengoreksi tanggal ke tanggal rencana -> tanpa denda
        view.picker_kembali.set(HARI_INI - timedelta(days=3))
        view.perbarui_denda()
        self.assertIn("tepat waktu", view.label_denda.cget("text"))

        with patch("tkinter.messagebox.askyesno", return_value=True), \
                patch("tkinter.messagebox.showinfo"):
            view.konfirmasi()

        ctrl.proses.assert_called_once_with(
            3, (HARI_INI - timedelta(days=3)).isoformat()
        )

    def test_konfirmasi_tanpa_pilihan_tidak_memanggil_controller(self):
        ctrl = MagicMock()
        ctrl.daftar.return_value = []
        ctrl.daftar_pengajuan.return_value = []
        view = self.buat(PengembalianAdminView, ctrl)

        with patch("tkinter.messagebox.showwarning") as peringatan:
            view.konfirmasi()

        peringatan.assert_called_once()
        ctrl.proses.assert_not_called()


@unittest.skipUnless(ADA_LAYAR, "tidak ada display")
class TestPengembalianPelanggan(unittest.TestCase):

    def buat_view(self, mulai=-5, rencana=-3):
        ctrl = MagicMock()
        ctrl.daftar_saya.return_value = []
        ctrl.daftar_penyewaan_berjalan_saya.return_value = [{
            "id": 12, "pelanggan_id": 7, "kendaraan_id": 4,
            "tanggal_mulai": HARI_INI + timedelta(days=mulai),
            "tanggal_rencana_kembali": HARI_INI + timedelta(days=rencana),
            "total_biaya": 300000, "username": "budi",
            "merek": "Avanza", "nomor_polisi": "DD 1 A",
            "tarif_harian": Decimal("100000"),
            "status_pengembalian": None, "tanggal_pengajuan": None,
        }]
        ctrl.hitung_denda.side_effect = PengembalianModel.hitung_denda
        ctrl.ajukan.return_value = {
            "denda": Decimal("100000"), "terlambat": 1,
            "tarif_harian": Decimal("100000")
        }
        view = PengembalianPelangganView(_root, ctrl)
        self.addCleanup(view.destroy)
        return view, ctrl

    def test_ada_kalender_tanggal_pengembalian(self):
        from views.shared.date_picker import DatePicker
        view, _ = self.buat_view()
        self.assertIsInstance(view.picker_kembali, DatePicker)

    def test_default_hari_ini_dan_denda_langsung_dihitung(self):
        view, _ = self.buat_view()
        self.assertEqual(view.picker_kembali.get(), HARI_INI.isoformat())
        # rencana 3 hari lalu, kembali hari ini -> 3 x Rp 100.000
        self.assertEqual(view.label_denda.cget("text"), "Rp 300.000")
        self.assertIn("3 hari", view.label_denda_ket.cget("text"))

    def test_ganti_tanggal_memperbarui_denda(self):
        view, _ = self.buat_view()

        view.picker_kembali.set(HARI_INI - timedelta(days=2))
        view.perbarui_info()
        self.assertEqual(view.label_denda.cget("text"), "Rp 100.000")

        view.picker_kembali.set(HARI_INI - timedelta(days=3))
        view.perbarui_info()
        self.assertEqual(view.label_denda.cget("text"), "Rp 0")
        self.assertIn("Tepat waktu", view.label_denda_ket.cget("text"))

    def test_kalender_dibatasi_mulai_sewa_sampai_hari_ini(self):
        view, _ = self.buat_view()
        picker = view.picker_kembali
        self.assertTrue(picker._boleh(HARI_INI))
        self.assertFalse(picker._boleh(HARI_INI + timedelta(days=1)))
        self.assertFalse(picker._boleh(HARI_INI - timedelta(days=6)))

    def test_ajukan_mengirim_tanggal_terpilih(self):
        view, ctrl = self.buat_view()
        view.picker_kembali.set(HARI_INI - timedelta(days=2))
        view.perbarui_info()

        with patch("tkinter.messagebox.askyesno", return_value=True), \
                patch("tkinter.messagebox.showinfo"):
            view.ajukan()

        ctrl.ajukan.assert_called_once_with(
            12, (HARI_INI - timedelta(days=2)).isoformat()
        )

    def test_sewa_belum_dimulai_tidak_bisa_diajukan(self):
        view, ctrl = self.buat_view(mulai=2, rencana=4)
        self.assertEqual(view.picker_kembali.get(), "")

        with patch("tkinter.messagebox.showwarning") as peringatan:
            view.ajukan()

        peringatan.assert_called_once()
        ctrl.ajukan.assert_not_called()


@unittest.skipUnless(ADA_LAYAR, "tidak ada display")
class TestTabelData(unittest.TestCase):

    def test_pencarian_menyaring_baris(self):
        tabel = TabelData(
            _root, [("a", "Nama", 100)], lambda d: (d["nama"],)
        )
        self.addCleanup(tabel.destroy)
        tabel.set_data([{"nama": "Budi"}, {"nama": "Siti"}])
        self.assertEqual(len(tabel.tabel.get_children()), 2)

        tabel.entry_cari.insert(0, "sit")
        tabel._render()
        self.assertEqual(len(tabel.tabel.get_children()), 1)

        tabel.tabel.selection_set("0")
        self.assertEqual(tabel.dipilih(), {"nama": "Siti"})


if __name__ == "__main__":
    unittest.main()
