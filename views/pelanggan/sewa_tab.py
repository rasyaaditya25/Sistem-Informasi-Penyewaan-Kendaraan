from datetime import date

import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, kartu, tombol, label_form, rupiah
)
from views.shared.date_picker import DatePicker


class PenyewaanPelangganView(Halaman):
    """Pelanggan menyewa kendaraan (pelanggan = akun yang login)."""

    def __init__(self, master, penyewaan_controller, user):
        super().__init__(
            master, "Sewa Kendaraan",
            "Pilih kendaraan dan tentukan lama sewa."
        )

        self.controller = penyewaan_controller
        self.user = user
        self.data_kendaraan = {}

        form = kartu(self.body)
        form.pack(fill="x", anchor="n")
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            form, text=f"Penyewa: {user['username']}",
            font=theme.F_SECTION, text_color=theme.TEKS
        ).grid(row=0, column=0, columnspan=2, sticky="w",
               padx=22, pady=(20, 6))

        label_form(form, "Kendaraan").grid(
            row=1, column=0, columnspan=2, sticky="w",
            padx=22, pady=(8, 2)
        )
        self.combo_kendaraan = ctk.CTkComboBox(
            form, values=["Pilih Kendaraan"], state="readonly",
            height=38, command=lambda _: self.hitung_total()
        )
        self.combo_kendaraan.grid(
            row=2, column=0, columnspan=2, sticky="ew",
            padx=22, pady=2
        )

        label_form(form, "Tanggal Mulai").grid(
            row=3, column=0, sticky="w", padx=22, pady=(14, 2)
        )
        self.picker_mulai = DatePicker(
            form, command=self.saat_mulai_berubah
        )
        self.picker_mulai.grid(
            row=4, column=0, sticky="ew", padx=22, pady=2
        )

        label_form(form, "Tanggal Rencana Kembali").grid(
            row=3, column=1, sticky="w", padx=22, pady=(14, 2)
        )
        self.picker_kembali = DatePicker(
            form, command=self.hitung_total
        )
        self.picker_kembali.grid(
            row=4, column=1, sticky="ew", padx=22, pady=2
        )

        ringkasan = ctk.CTkFrame(
            form, fg_color=theme.BIRU_MUDA, corner_radius=10
        )
        ringkasan.grid(
            row=5, column=0, columnspan=2, sticky="ew",
            padx=22, pady=(18, 6)
        )

        ctk.CTkLabel(
            ringkasan, text="Estimasi Total Biaya",
            font=theme.F_LABEL, text_color=theme.TEKS_PUDAR
        ).pack(anchor="w", padx=16, pady=(12, 0))

        self.label_total = ctk.CTkLabel(
            ringkasan, text="Rp 0", font=theme.F_ANGKA,
            text_color=theme.UTAMA
        )
        self.label_total.pack(anchor="w", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            form,
            text="Denda keterlambatan: tarif 1 hari x jumlah hari "
                 "terlambat dari tanggal rencana kembali.",
            font=(theme.FONT, 11), text_color=theme.TEKS_PUDAR
        ).grid(row=6, column=0, columnspan=2, sticky="w",
               padx=22, pady=(4, 6))

        tombol_bar = ctk.CTkFrame(form, fg_color="transparent")
        tombol_bar.grid(row=7, column=0, columnspan=2, sticky="w",
                        padx=22, pady=(6, 22))

        tombol(
            tombol_bar, "Sewa Sekarang", self.sewa,
            gaya="sukses", width=160
        ).pack(side="left", padx=(0, 8))

        tombol(
            tombol_bar, "Bersihkan", self.bersihkan_form,
            gaya="netral", width=120
        ).pack(side="left")

        self.bersihkan_form()
        self.refresh_data()

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            kendaraan = self.controller.daftar_kendaraan_tersedia()
            lama = self.combo_kendaraan.get()

            self.data_kendaraan = {}
            pilihan = []

            for k in kendaraan:
                tarif = float(k["tarif_harian"])
                label = (
                    f'{k["id"]} - {k["merek"]} ({k["nomor_polisi"]}) - '
                    f'{rupiah(tarif)}/hari'
                )
                self.data_kendaraan[label] = {
                    "id": k["id"], "tarif": tarif
                }
                pilihan.append(label)

            kosong = "Tidak ada kendaraan tersedia"
            self.combo_kendaraan.configure(values=pilihan or [kosong])

            if lama in self.data_kendaraan:
                self.combo_kendaraan.set(lama)
            else:
                self.combo_kendaraan.set(pilihan[0] if pilihan else kosong)

            self.hitung_total()

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def saat_mulai_berubah(self):
        mulai = self.picker_mulai.get_date()
        self.picker_kembali.set_min_date(mulai)

        kembali = self.picker_kembali.get_date()
        if mulai and kembali and kembali < mulai:
            self.picker_kembali.clear()

        self.hitung_total()

    def hitung_total(self):
        label = self.combo_kendaraan.get()
        mulai = self.picker_mulai.get_date()
        kembali = self.picker_kembali.get_date()

        if (
            label not in self.data_kendaraan
            or not mulai or not kembali or kembali < mulai
        ):
            self.label_total.configure(text="Rp 0")
            return

        # Hari mulai dan hari kembali sama-sama dihitung
        hari = (kembali - mulai).days + 1
        tarif = self.data_kendaraan[label]["tarif"]

        self.label_total.configure(
            text=f"{rupiah(tarif * hari)}   "
                 f"({hari} hari x {rupiah(tarif)})"
        )

    def sewa(self):
        try:
            label = self.combo_kendaraan.get()

            if label not in self.data_kendaraan:
                raise ValueError("Silakan pilih kendaraan.")

            mulai = self.picker_mulai.get()
            kembali = self.picker_kembali.get()

            if not mulai:
                raise ValueError("Silakan pilih tanggal mulai.")

            if not kembali:
                raise ValueError("Silakan pilih tanggal rencana kembali.")

            if kembali < mulai:
                raise ValueError(
                    "Tanggal kembali tidak boleh sebelum tanggal mulai."
                )

            if not messagebox.askyesno(
                "Konfirmasi Penyewaan",
                f"Sewa kendaraan ini?\n\n{label}\n"
                f"{mulai} s/d {kembali}\n"
                f"Total: {self.label_total.cget('text')}",
                parent=self
            ):
                return

            hasil = self.controller.buat_sendiri(
                self.data_kendaraan[label]["id"], mulai, kembali
            )

            if hasil is False:
                raise Exception("Penyewaan gagal disimpan.")

            messagebox.showinfo(
                "Berhasil",
                "Penyewaan berhasil dibuat.\n"
                "Silakan lakukan pembayaran di menu Pembayaran.",
                parent=self
            )

            self.bersihkan_form()
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal Menyewa", str(exc), parent=self)

    def bersihkan_form(self):
        hari_ini = date.today()

        self.picker_mulai.set_min_date(hari_ini)
        self.picker_mulai.set(hari_ini)

        self.picker_kembali.set_min_date(hari_ini)
        self.picker_kembali.clear()

        self.label_total.configure(text="Rp 0")
