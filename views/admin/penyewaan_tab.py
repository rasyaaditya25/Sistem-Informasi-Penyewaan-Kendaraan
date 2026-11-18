import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, rupiah, tgl
)

SEMUA = "Semua Status"


class PenyewaanAdminView(Halaman):
    """
    Admin mengelola data penyewaan. Penyewaan dibuat sendiri oleh
    pelanggan, jadi di sini admin hanya memantau dan dapat
    membatalkan penyewaan yang belum dibayar.
    """

    def __init__(self, master, penyewaan_controller):
        super().__init__(
            master, "Kelola Data Peminjaman",
            "Penyewaan dibuat oleh pelanggan. Admin memantau dan "
            "mengelola datanya."
        )

        self.controller = penyewaan_controller
        self.semua = []

        self.tabel_data = TabelData(
            self.body,
            [
                ("id", "ID", 45),
                ("pelanggan", "Pelanggan", 130, "w"),
                ("kendaraan", "Kendaraan", 200, "w"),
                ("mulai", "Mulai", 100),
                ("rencana", "Rencana Kembali", 120),
                ("total", "Total Biaya", 120),
                ("status", "Status", 90),
            ],
            lambda p: (
                p["id"], p["username"],
                f'{p["merek"]} ({p["nomor_polisi"]})',
                tgl(p["tanggal_mulai"]), tgl(p["tanggal_rencana_kembali"]),
                rupiah(p["total_biaya"]), p["status"]
            ),
            judul="Daftar Peminjaman",
            tag_fn=lambda p: p["status"],
            on_pilih=self.pilih
        )
        self.tabel_data.pack(fill="both", expand=True)

        self.combo_filter = ctk.CTkComboBox(
            self.tabel_data.toolbar,
            values=[SEMUA, "Berjalan", "Selesai"],
            state="readonly", width=130, height=32,
            command=lambda _: self._terapkan_filter()
        )
        self.combo_filter.set(SEMUA)
        self.combo_filter.pack(side="left", padx=(0, 8))

        # Pindahkan kotak cari ke kanan filter
        self.tabel_data.entry_cari.pack_forget()
        self.tabel_data.entry_cari.pack(side="left")

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        # Panel aksi
        panel = kartu(self.body)
        panel.pack(fill="x", pady=(12, 0))

        self.label_detail = ctk.CTkLabel(
            panel, text="Pilih penyewaan di tabel untuk melihat detail.",
            font=theme.F_LABEL, text_color=theme.TEKS_PUDAR,
            anchor="w", justify="left"
        )
        self.label_detail.pack(
            side="left", fill="x", expand=True, padx=18, pady=14
        )

        tombol(
            panel, "Batalkan Penyewaan", self.batalkan,
            gaya="bahaya", width=180
        ).pack(side="right", padx=18, pady=14)

        self.refresh_data()

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            self.semua = self.controller.daftar() or []
            self._terapkan_filter()

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def _terapkan_filter(self):
        status = self.combo_filter.get()
        data = [
            p for p in self.semua
            if status == SEMUA or p["status"] == status
        ]
        self.tabel_data.set_data(data)
        self.pilih(None)

    def pilih(self, p):
        if not p:
            self.label_detail.configure(
                text="Pilih penyewaan di tabel untuk melihat detail."
            )
            return

        self.label_detail.configure(
            text=f'Penyewaan #{p["id"]}  |  {p["username"]}  |  '
                 f'{p["jenis"]} {p["merek"]} ({p["nomor_polisi"]})\n'
                 f'{tgl(p["tanggal_mulai"])} s/d '
                 f'{tgl(p["tanggal_rencana_kembali"])}  |  '
                 f'Total {rupiah(p["total_biaya"])}  |  {p["status"]}',
            text_color=theme.TEKS
        )

    def batalkan(self):
        p = self.tabel_data.dipilih()

        if not p:
            messagebox.showwarning(
                "Pilih Penyewaan",
                "Pilih penyewaan di tabel yang ingin dibatalkan.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Konfirmasi Pembatalan",
            f"Batalkan penyewaan #{p['id']} atas nama {p['username']}?\n\n"
            "Hanya bisa untuk penyewaan yang belum dibayar dan belum "
            "diajukan pengembaliannya. Kendaraan akan kembali Tersedia.",
            parent=self
        ):
            return

        try:
            self.controller.batalkan(p["id"])

            messagebox.showinfo(
                "Berhasil", "Penyewaan berhasil dibatalkan.", parent=self
            )
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Tidak Dapat Dibatalkan", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal", str(exc), parent=self)
