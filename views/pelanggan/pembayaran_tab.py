import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, rupiah, tgl
)


class PembayaranPelangganView(Halaman):

    KOLOM = [
        ("id", "ID", 45),
        ("sewa", "ID Sewa", 70),
        ("kendaraan", "Kendaraan", 190, "w"),
        ("jenis", "Jenis", 70),
        ("jumlah", "Jumlah", 120),
        ("metode", "Metode", 90),
        ("status", "Status", 90),
        ("tanggal", "Tgl Bayar", 100),
    ]

    def __init__(self, master, pembayaran_controller):
        super().__init__(
            master, "Pembayaran",
            "Bayar tagihan sewa dan denda Anda."
        )

        self.controller = pembayaran_controller

        panel = kartu(self.body)
        panel.pack(fill="x", pady=(0, 12))

        self.label_tagihan = ctk.CTkLabel(
            panel, text="", font=theme.F_SECTION,
            text_color=theme.TEKS, anchor="w"
        )
        self.label_tagihan.pack(
            side="left", padx=18, pady=16
        )

        tombol(
            panel, "Bayar Sekarang", self.bayar,
            gaya="sukses", width=150
        ).pack(side="right", padx=(8, 18), pady=16)

        self.combo_metode = ctk.CTkComboBox(
            panel, values=["Tunai", "Transfer", "E-Wallet"],
            width=140, height=36, state="readonly"
        )
        self.combo_metode.set("Transfer")
        self.combo_metode.pack(side="right", pady=16)

        ctk.CTkLabel(
            panel, text="Metode:", font=theme.F_LABEL_BOLD
        ).pack(side="right", padx=8)

        self.tabel_data = TabelData(
            self.body, self.KOLOM,
            lambda p: (
                p["id"], p["penyewaan_id"],
                f'{p["merek"]} ({p["nomor_polisi"]})',
                p["jenis"], rupiah(p["jumlah"]),
                p["metode"] or "-", p["status"], tgl(p["tanggal_bayar"])
            ),
            judul="Daftar Tagihan",
            tag_fn=lambda p: p["status"]
        )
        self.tabel_data.pack(fill="both", expand=True)

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self.refresh_data()

    def refresh_data(self):
        try:
            data = self.controller.daftar_saya() or []
            self.tabel_data.set_data(data)

            menunggu = [p for p in data if p["status"] == "Menunggu"]
            total = sum(float(p["jumlah"]) for p in menunggu)

            self.label_tagihan.configure(
                text=f"Belum dibayar: {len(menunggu)} tagihan "
                     f"({rupiah(total)})"
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def bayar(self):
        p = self.tabel_data.dipilih()

        if not p:
            messagebox.showwarning(
                "Pilih Tagihan",
                "Pilih tagihan di tabel yang ingin dibayar.",
                parent=self
            )
            return

        if p["status"] == "Lunas":
            messagebox.showinfo(
                "Informasi", "Tagihan ini sudah lunas.", parent=self
            )
            return

        metode = self.combo_metode.get()

        if not messagebox.askyesno(
            "Konfirmasi Pembayaran",
            f"Bayar {p['jenis'].lower()} {rupiah(p['jumlah'])} "
            f"via {metode}?",
            parent=self
        ):
            return

        try:
            self.controller.bayar(p["id"], metode)

            messagebox.showinfo(
                "Berhasil", "Pembayaran berhasil.", parent=self
            )
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal", str(exc), parent=self)
