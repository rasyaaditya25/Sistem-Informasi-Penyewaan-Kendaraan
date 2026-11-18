from controllers.akses import Session, ADMIN, PELANGGAN, PEMILIK
from controllers.user_controller import UserController
from controllers.kendaraan_controller import KendaraanController
from controllers.penyewaan_controller import PenyewaanController
from controllers.pengembalian_controller import PengembalianController
from controllers.pembayaran_controller import PembayaranController
from controllers.laporan_controller import LaporanController

from views.app_window import AppWindow
from views.shared.splash import SplashScreen
from views.admin.dashboard import AdminDashboard
from views.pelanggan.dashboard import PelangganDashboard
from views.pemilik.dashboard import PemilikDashboard

DASHBOARD = {
    ADMIN: AdminDashboard,
    PELANGGAN: PelangganDashboard,
    PEMILIK: PemilikDashboard,
}


class AuthController:
    """Mengatur alur: login -> dashboard sesuai role -> logout."""

    def __init__(self):
        self.user_controller = UserController()
        self.window = AppWindow()
        self.window.protocol("WM_DELETE_WINDOW", self.tutup_aplikasi)

        self.tampilkan_login()

        # Loading screen: jendela utama baru muncul setelah selesai.
        SplashScreen(
            self.window, self.periksa_database, self.window.tampil
        )

    @staticmethod
    def periksa_database():
        """Dipanggil loading screen (di thread terpisah)."""
        from config.database import Database

        koneksi = Database().get_connection()

        if koneksi is None:
            return False

        koneksi.close()
        return True

    def tampilkan_login(self):
        self.window.tampilkan_login(
            self.user_controller, self.proses_login_berhasil
        )

    def proses_login_berhasil(self, user):
        kelas = DASHBOARD.get(user["role"])

        if kelas is None:
            Session.logout()
            raise ValueError(f"Role tidak dikenali: {user['role']}")

        controllers = {
            "user": self.user_controller,
            "kendaraan": KendaraanController(),
            "penyewaan": PenyewaanController(),
            "pengembalian": PengembalianController(),
            "pembayaran": PembayaranController(),
            "laporan": LaporanController(),
        }

        self.window.tampilkan_dashboard(
            lambda master: kelas(master, controllers, user, self.logout),
            user
        )

    def logout(self):
        self.user_controller.logout()
        self.tampilkan_login()

    def tutup_aplikasi(self):
        Session.logout()
        self.window.destroy()

    def run(self):
        self.window.mainloop()
