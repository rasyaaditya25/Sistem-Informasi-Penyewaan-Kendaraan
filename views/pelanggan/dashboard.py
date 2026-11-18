from views.shared.shell import DashboardShell
from views.pelanggan.kendaraan_tab import buat_tab_kendaraan
from views.pelanggan.sewa_tab import PenyewaanPelangganView
from views.pelanggan.pembayaran_tab import PembayaranPelangganView
from views.pelanggan.pengembalian_tab import PengembalianPelangganView
from views.pelanggan.riwayat_tab import buat_tab_riwayat


class PelangganDashboard(DashboardShell):
    """Pelanggan: lihat kendaraan, sewa, bayar, kembalikan, riwayat."""

    def __init__(self, master, controllers, user, on_logout):
        super().__init__(
            master, user,
            [
                ("Kendaraan", lambda p: buat_tab_kendaraan(
                    p, controllers["kendaraan"])),
                ("Sewa Kendaraan", lambda p: PenyewaanPelangganView(
                    p, controllers["penyewaan"], user)),
                ("Pembayaran", lambda p: PembayaranPelangganView(
                    p, controllers["pembayaran"])),
                ("Pengembalian", lambda p: PengembalianPelangganView(
                    p, controllers["pengembalian"])),
                ("Riwayat", lambda p: buat_tab_riwayat(
                    p, controllers["penyewaan"])),
            ],
            on_logout
        )
