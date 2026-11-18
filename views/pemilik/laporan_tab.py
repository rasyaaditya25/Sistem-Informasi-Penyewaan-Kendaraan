from datetime import date

import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, rupiah
)
from views.shared.date_picker import DatePicker


class LaporanView(Halaman):
    """Laporan pendapatan & kendaraan terlaris per periode."""

    KOLOM = [
        ("no", "No", 45),
        ("kendaraan", "Kendaraan", 260, "w"),
        ("jumlah", "Jumlah Sewa", 120),
        ("total", "Total Nilai Sewa", 160),
    ]

    def __init__(self, master, laporan_controller):
        super().__init__(
            master, "Laporan",
            "Ringkasan pendapatan dan kendaraan terlaris per periode."
        )

        self.controller = laporan_controller

        filter_frame = kartu(self.body)
        filter_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            filter_frame,
            text="Periode (berdasarkan tanggal mulai sewa):",
            font=theme.F_LABEL_BOLD
        ).pack(side="left", padx=(18, 10), pady=14)

        self.picker_dari = DatePicker(filter_frame, width=120)
        self.picker_dari.pack(side="left", padx=4)

        ctk.CTkLabel(filter_frame, text="s/d").pack(side="left", padx=6)

        self.picker_sampai = DatePicker(filter_frame, width=120)
        self.picker_sampai.pack(side="left", padx=4)

        tombol(
            filter_frame, "Tampilkan", self.refresh_data, width=110
        ).pack(side="left", padx=14)

        hari_ini = date.today()
        self.picker_dari.set(hari_ini.replace(day=1))
        self.picker_sampai.set(hari_ini)

        # Kartu ringkasan
        kartu_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        kartu_frame.pack(fill="x", pady=(0, 12))

        self.kartu = {}
        for i, (kunci, judul) in enumerate([
            ("jumlah", "Jumlah Transaksi"),
            ("sewa", "Pendapatan Sewa (Lunas)"),
            ("denda", "Pendapatan Denda (Lunas)"),
            ("total", "Total Pendapatan"),
            ("menunggu", "Belum Dibayar"),
        ]):
            kartu_frame.grid_columnconfigure(i, weight=1, uniform="k")

            kotak = kartu(kartu_frame)
            kotak.grid(
                row=0, column=i, padx=(0 if i == 0 else 8, 0),
                sticky="nsew"
            )

            ctk.CTkLabel(
                kotak, text=judul, font=(theme.FONT, 11),
                text_color=theme.TEKS_PUDAR
            ).pack(padx=12, pady=(14, 2))

            label = ctk.CTkLabel(
                kotak, text="-", font=(theme.FONT, 17, "bold"),
                text_color=theme.UTAMA
            )
            label.pack(padx=12, pady=(0, 14))
            self.kartu[kunci] = label

        self.tabel_data = TabelData(
            self.body, self.KOLOM,
            lambda r: r, judul="Kendaraan Terlaris", tinggi=8,
            cari=False
        )
        self.tabel_data.pack(fill="both", expand=True)

        self.refresh_data()

    def refresh_data(self):
        dari = self.picker_dari.get()
        sampai = self.picker_sampai.get()

        try:
            if not dari or not sampai:
                raise ValueError("Pilih tanggal awal dan tanggal akhir.")

            hasil = self.controller.ringkasan(dari, sampai)

            if not hasil:
                raise Exception("Data laporan tidak dapat dimuat.")

            self.kartu["jumlah"].configure(
                text=str(hasil["jumlah_transaksi"])
            )
            self.kartu["sewa"].configure(text=rupiah(hasil["sewa_lunas"]))
            self.kartu["denda"].configure(
                text=rupiah(hasil["denda_lunas"])
            )
            self.kartu["total"].configure(
                text=rupiah(hasil["sewa_lunas"] + hasil["denda_lunas"])
            )
            self.kartu["menunggu"].configure(
                text=rupiah(hasil["menunggu"])
            )

            self.tabel_data.set_data([
                (
                    i, f'{k["merek"]} ({k["nomor_polisi"]})',
                    k["jumlah"], rupiah(k["total"])
                )
                for i, k in enumerate(hasil["terlaris"], start=1)
            ])

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Laporan", str(exc), parent=self
            )
