from views.shared.shell import DashboardShell
from views.admin.kendaraan_tab import KendaraanAdminView
from views.admin.pelanggan_tab import KelolaPelangganView
from views.admin.penyewaan_tab import PenyewaanAdminView
from views.admin.pengembalian_tab import PengembalianAdminView
from views.admin.pembayaran_tab import PembayaranAdminView


class AdminDashboard(DashboardShell):
    """Admin: kelola kendaraan, pelanggan, peminjaman,
    pengembalian, dan pembayaran."""

    def __init__(self, master, controllers, user, on_logout):
        super().__init__(
            master, user,
            [
                ("Kendaraan", lambda p: KendaraanAdminView(
                    p, controllers["kendaraan"])),
                ("Pelanggan", lambda p: KelolaPelangganView(
                    p, controllers["user"])),
                ("Peminjaman", lambda p: PenyewaanAdminView(
                    p, controllers["penyewaan"])),
                ("Pengembalian", lambda p: PengembalianAdminView(
                    p, controllers["pengembalian"])),
                ("Pembayaran", lambda p: PembayaranAdminView(
                    p, controllers["pembayaran"])),
            ],
            on_logout
        )
