import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, rupiah, tgl
)

KOLOM = [
    ("id", "ID", 45),
    ("sewa", "ID Sewa", 70),
    ("pelanggan", "Pelanggan", 120, "w"),
    ("kendaraan", "Kendaraan", 180, "w"),
    ("jenis", "Jenis", 70),
    ("jumlah", "Jumlah", 110),
    ("metode", "Metode", 90),
    ("status", "Status", 90),
    ("tanggal", "Tgl Bayar", 100),
]


def ke_baris(p):
    return (
        p["id"], p["penyewaan_id"], p["username"],
        f'{p["merek"]} ({p["nomor_polisi"]})',
        p["jenis"], rupiah(p["jumlah"]),
        p["metode"] or "-", p["status"], tgl(p["tanggal_bayar"]),
    )


class PembayaranAdminView(Halaman):
    """Admin: mengelola data pembayaran (lihat + ubah status)."""

    def __init__(self, master, pembayaran_controller):
        super().__init__(
            master, "Kelola Data Pembayaran",
            "Pantau tagihan sewa dan denda, ubah status bila perlu."
        )

        self.controller = pembayaran_controller

        panel = kartu(self.body)
        panel.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            panel, text="Ubah status pembayaran terpilih:",
            font=theme.F_LABEL_BOLD
        ).pack(side="left", padx=(18, 8), pady=14)

        self.combo_status = ctk.CTkComboBox(
            panel, values=["Menunggu", "Lunas"],
            width=140, height=36, state="readonly"
        )
        self.combo_status.set("Lunas")
        self.combo_status.pack(side="left", padx=4)

        tombol(
            panel, "Simpan Status", self.simpan_status,
            gaya="sukses", width=140
        ).pack(side="left", padx=10)

        self.tabel_data = TabelData(
            self.body, KOLOM, ke_baris, judul="Daftar Pembayaran",
            tag_fn=lambda p: p["status"], on_pilih=self.pilih
        )
        self.tabel_data.pack(fill="both", expand=True)

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self.refresh_data()

    def refresh_data(self):
        try:
            self.tabel_data.set_data(self.controller.daftar() or [])

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def pilih(self, p):
        if p:
            self.combo_status.set(p["status"])

    def simpan_status(self):
        p = self.tabel_data.dipilih()

        if not p:
            messagebox.showwarning(
                "Pilih Data",
                "Pilih pembayaran yang ingin diubah statusnya.",
                parent=self
            )
            return

        status = self.combo_status.get()

        try:
            self.controller.ubah_status(p["id"], status)
            self.refresh_data()

            messagebox.showinfo(
                "Berhasil",
                f"Status pembayaran #{p['id']} diubah menjadi {status}.",
                parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal", str(exc), parent=self)
