from views.shared.shell import DashboardShell
from views.pemilik.penyewaan_tab import buat_tab_penyewaan
from views.pemilik.pengembalian_tab import buat_tab_pengembalian
from views.pemilik.laporan_tab import LaporanView


class PemilikDashboard(DashboardShell):
    """Pemilik rental: hanya melihat data dan laporan."""

    def __init__(self, master, controllers, user, on_logout):
        super().__init__(
            master, user,
            [
                ("Data Peminjaman", lambda p: buat_tab_penyewaan(
                    p, controllers["penyewaan"])),
                ("Data Pengembalian", lambda p: buat_tab_pengembalian(
                    p, controllers["pengembalian"])),
                ("Laporan", lambda p: LaporanView(
                    p, controllers["laporan"])),
            ],
            on_logout
        )
