import tkinter as tk
from tkinter import messagebox


# =====================================================================
# HELPER: TAMPILKAN ERROR
# =====================================================================
def tampilkan_error(judul, pesan):
    """Menampilkan dialog error tanpa membuka jendela utama."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(judul, pesan)
    root.destroy()


# =====================================================================
# FUNGSI UTAMA
# =====================================================================
def main():
    # ---------- 1. Muat controller (koneksi database) ----------
    try:
        from controllers.kendaraan_controller import KendaraanController
        from controllers.pelanggan_controller import PelangganController
        from controllers.penyewaan_controller import PenyewaanController
        from controllers.pengembalian_controller import PengembalianController

        kendaraan = KendaraanController()
        pelanggan = PelangganController()
        penyewaan = PenyewaanController()
        pengembalian = PengembalianController()
    except Exception as exc:
        tampilkan_error(
            "Gagal memulai aplikasi",
            f"Tidak dapat memuat controller/database.\n\nDetail: {exc}",
        )
        return

    # ---------- 2. Buka GUI ----------
    try:
        from views.main_view import PenyewaanKendaraanView

        app = PenyewaanKendaraanView(kendaraan, pelanggan, penyewaan, pengembalian)
        app.mainloop()
    except Exception as exc:
        tampilkan_error(
            "Gagal membuka GUI",
            f"Tidak dapat membuka tampilan aplikasi.\n\nDetail: {exc}",
        )


# =====================================================================
# ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    main()