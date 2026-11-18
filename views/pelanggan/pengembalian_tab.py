from datetime import date

import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, label_form, rupiah, tgl
)
from views.shared.date_picker import DatePicker

KOSONG = "Tidak ada penyewaan yang bisa dikembalikan"


class PengembalianPelangganView(Halaman):
    """
    Pelanggan memilih tanggal pengembalian lewat kalender;
    keterlambatan dan denda langsung dihitung. Pengajuan
    dikonfirmasi admin setelah kendaraan diterima.
    """

    KOLOM = [
        ("id", "ID", 45),
        ("sewa", "ID Sewa", 70),
        ("kendaraan", "Kendaraan", 200, "w"),
        ("tanggal", "Tgl Kembali", 110),
        ("denda", "Denda", 120),
        ("status", "Status", 140),
    ]

    def __init__(self, master, pengembalian_controller):
        super().__init__(
            master, "Pengembalian Kendaraan",
            "Pilih tanggal pengembalian, denda dihitung otomatis."
        )

        self.controller = pengembalian_controller
        self.map_sewa = {}

        form = kartu(self.body)
        form.pack(fill="x", pady=(0, 12))
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(1, weight=2)
        form.grid_columnconfigure(2, weight=2)

        label_form(form, "Penyewaan yang sedang berjalan").grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 2)
        )
        self.combo_sewa = ctk.CTkComboBox(
            form, values=[KOSONG], state="readonly", height=38,
            command=lambda _: self.saat_sewa_berubah()
        )
        self.combo_sewa.grid(
            row=1, column=0, sticky="ew", padx=20, pady=2
        )

        label_form(form, "Tanggal Pengembalian").grid(
            row=0, column=1, sticky="w", padx=10, pady=(16, 2)
        )
        self.picker_kembali = DatePicker(
            form, command=self.perbarui_info
        )
        self.picker_kembali.grid(
            row=1, column=1, sticky="ew", padx=10, pady=2
        )

        # Ringkasan + denda
        self.label_info = ctk.CTkLabel(
            form, text="", justify="left", anchor="w",
            font=theme.F_LABEL, text_color=theme.TEKS
        )
        self.label_info.grid(
            row=2, column=0, columnspan=2, sticky="ew",
            padx=20, pady=(12, 4)
        )

        kotak_denda = ctk.CTkFrame(
            form, fg_color=theme.PERINGATAN_LATAR, corner_radius=10
        )
        kotak_denda.grid(
            row=0, column=2, rowspan=3, sticky="nsew",
            padx=(10, 20), pady=16
        )

        ctk.CTkLabel(
            kotak_denda, text="Denda",
            font=theme.F_LABEL, text_color=theme.TEKS_PUDAR
        ).pack(pady=(16, 0))

        self.label_denda = ctk.CTkLabel(
            kotak_denda, text="Rp 0", font=(theme.FONT, 26, "bold"),
            text_color=theme.SUKSES
        )
        self.label_denda.pack(pady=(0, 2))

        self.label_denda_ket = ctk.CTkLabel(
            kotak_denda, text="-", font=(theme.FONT, 11),
            text_color=theme.TEKS_PUDAR, wraplength=190
        )
        self.label_denda_ket.pack(padx=10, pady=(0, 16))

        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=3, column=0, columnspan=3, sticky="w",
                 padx=20, pady=(4, 18))

        tombol(
            bar, "Ajukan Pengembalian", self.ajukan,
            gaya="sukses", width=190
        ).pack(side="left", padx=(0, 8))

        tombol(
            bar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=110
        ).pack(side="left")

        self.tabel_data = TabelData(
            self.body, self.KOLOM,
            lambda p: (
                p["id"], p["penyewaan_id"],
                f'{p["merek"]} ({p["nomor_polisi"]})',
                tgl(p["tanggal_kembali"]), rupiah(p["denda"]),
                "Menunggu Konfirmasi" if p["status"] == "Diajukan"
                else "Selesai"
            ),
            judul="Riwayat Pengembalian Saya", tinggi=6,
            tag_fn=lambda p: (
                "Menunggu Konfirmasi" if p["status"] == "Diajukan"
                else "Selesai"
            )
        )
        self.tabel_data.pack(fill="both", expand=True)

        self.refresh_data()

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            berjalan = self.controller.daftar_penyewaan_berjalan_saya()

            self.map_sewa = {}
            pilihan = []

            for p in berjalan:
                # Yang sudah diajukan tinggal menunggu admin
                if p["status_pengembalian"]:
                    continue

                label = (
                    f'#{p["id"]} - {p["merek"]} ({p["nomor_polisi"]})'
                )
                self.map_sewa[label] = p
                pilihan.append(label)

            lama = self.combo_sewa.get()
            self.combo_sewa.configure(values=pilihan or [KOSONG])
            self.combo_sewa.set(
                lama if lama in self.map_sewa
                else (pilihan[0] if pilihan else KOSONG)
            )

            self.saat_sewa_berubah()

            self.tabel_data.set_data(self.controller.daftar_saya() or [])

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def saat_sewa_berubah(self):
        """Batas kalender: dari tanggal mulai sewa sampai hari ini."""
        p = self.map_sewa.get(self.combo_sewa.get())
        hari_ini = date.today()

        self.picker_kembali.set_max_date(hari_ini)

        if not p:
            self.picker_kembali.set_min_date(None)
            self.picker_kembali.clear()
            self.perbarui_info()
            return

        mulai = p["tanggal_mulai"]
        self.picker_kembali.set_min_date(mulai)

        if mulai > hari_ini:
            # Sewa belum dimulai: belum ada tanggal yang bisa dipilih
            self.picker_kembali.clear()
        else:
            # Default: hari ini
            kembali = self.picker_kembali.get_date()
            if kembali is None or kembali < mulai or kembali > hari_ini:
                self.picker_kembali.set(hari_ini)

        self.perbarui_info()

    def perbarui_info(self):
        """Hitung keterlambatan & denda langsung dari tanggal pilihan."""
        p = self.map_sewa.get(self.combo_sewa.get())

        if not p:
            self.label_info.configure(text=KOSONG + ".")
            self._set_denda(0, "-", False)
            return

        rencana = p["tanggal_rencana_kembali"]
        kembali = self.picker_kembali.get_date()

        teks = (
            f'Kendaraan: {p["merek"]} ({p["nomor_polisi"]})\n'
            f'Tanggal mulai: {tgl(p["tanggal_mulai"])}   |   '
            f'Rencana kembali: {tgl(rencana)}'
        )

        if not kembali:
            if p["tanggal_mulai"] > date.today():
                self.label_info.configure(
                    text=teks + "\nPenyewaan ini belum dimulai, "
                                "belum bisa dikembalikan."
                )
                self._set_denda(0, "Belum dimulai", False)
            else:
                self.label_info.configure(
                    text=teks + "\nPilih tanggal pengembalian."
                )
                self._set_denda(0, "Pilih tanggal dulu", False)
            return

        denda, terlambat, tarif = self.controller.hitung_denda(
            p["tarif_harian"], rencana, kembali
        )

        self.label_info.configure(
            text=teks + f"\nTanggal pengembalian: {tgl(kembali)}"
        )

        if terlambat > 0:
            self._set_denda(
                denda,
                f"Terlambat {terlambat} hari x {rupiah(tarif)}",
                True
            )
        else:
            self._set_denda(0, "Tepat waktu, tidak ada denda", False)

    def _set_denda(self, denda, keterangan, ada_denda):
        self.label_denda.configure(
            text=rupiah(denda),
            text_color=theme.BAHAYA if ada_denda else theme.SUKSES
        )
        self.label_denda_ket.configure(text=keterangan)

    def ajukan(self):
        p = self.map_sewa.get(self.combo_sewa.get())

        if not p:
            messagebox.showwarning(
                "Peringatan", KOSONG + ".", parent=self
            )
            return

        kembali = self.picker_kembali.get()

        if not kembali:
            messagebox.showwarning(
                "Peringatan", "Pilih tanggal pengembalian.", parent=self
            )
            return

        if not messagebox.askyesno(
            "Konfirmasi Pengembalian",
            f"Ajukan pengembalian pada {kembali}?\n\n"
            f"Denda: {self.label_denda.cget('text')} "
            f"({self.label_denda_ket.cget('text')})\n\n"
            "Admin akan mengonfirmasi setelah kendaraan diterima.",
            parent=self
        ):
            return

        try:
            hasil = self.controller.ajukan(p["id"], kembali)

            if not hasil:
                raise Exception("Pengajuan pengembalian gagal.")

            pesan = "Pengembalian berhasil diajukan."

            if hasil["terlambat"] > 0:
                pesan += (
                    f"\nTerlambat {hasil['terlambat']} hari, "
                    f"denda {rupiah(hasil['denda'])}."
                    "\nTagihan denda muncul di menu Pembayaran "
                    "setelah admin mengonfirmasi."
                )

            messagebox.showinfo("Berhasil", pesan, parent=self)
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal", str(exc), parent=self)
