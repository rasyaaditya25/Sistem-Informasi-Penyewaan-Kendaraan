from datetime import date

import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, label_form, rupiah, tgl
)
from views.shared.date_picker import DatePicker


class PengembalianAdminView(Halaman):
    """
    Admin mengelola pengembalian. Pengembalian diajukan oleh pelanggan;
    admin memeriksa, mengonfirmasi (tanggal boleh dikoreksi) atau
    menolak pengajuan.
    """

    KOLOM_PENGAJUAN = [
        ("sewa", "ID Sewa", 60),
        ("pelanggan", "Pelanggan", 100, "w"),
        ("kendaraan", "Kendaraan", 170, "w"),
        ("rencana", "Rencana", 90),
        ("diajukan", "Diajukan", 90),
    ]

    KOLOM_RIWAYAT = [
        ("id", "ID", 45),
        ("sewa", "ID Sewa", 70),
        ("pelanggan", "Pelanggan", 130, "w"),
        ("kendaraan", "Kendaraan", 200, "w"),
        ("tanggal", "Tgl Kembali", 110),
        ("denda", "Denda", 110),
        ("status", "Status", 130),
    ]

    def __init__(self, master, pengembalian_controller):
        super().__init__(
            master, "Kelola Data Pengembalian",
            "Pengembalian diajukan oleh pelanggan. Admin memeriksa "
            "lalu mengonfirmasi atau menolaknya."
        )

        self.controller = pengembalian_controller

        # ---- Pengajuan + panel konfirmasi ----
        atas = ctk.CTkFrame(self.body, fg_color="transparent")
        atas.pack(fill="x")
        atas.grid_columnconfigure(0, weight=3)
        atas.grid_columnconfigure(1, weight=2, minsize=360)

        self.tabel_pengajuan = TabelData(
            atas, self.KOLOM_PENGAJUAN,
            lambda p: (
                p["id"], p["username"],
                f'{p["merek"]} ({p["nomor_polisi"]})',
                tgl(p["tanggal_rencana_kembali"]),
                tgl(p["tanggal_pengajuan"])
            ),
            judul="Menunggu Konfirmasi", tinggi=5,
            on_pilih=self.pilih_pengajuan
        )
        self.tabel_pengajuan.grid(
            row=0, column=0, sticky="nsew", padx=(0, 14)
        )

        self._buat_panel(atas)

        # ---- Riwayat ----
        self.tabel_riwayat = TabelData(
            self.body, self.KOLOM_RIWAYAT,
            lambda p: (
                p["id"], p["penyewaan_id"], p["username"],
                f'{p["merek"]} ({p["nomor_polisi"]})',
                tgl(p["tanggal_kembali"]), rupiah(p["denda"]),
                "Menunggu Konfirmasi" if p["status"] == "Diajukan"
                else "Dikonfirmasi"
            ),
            judul="Riwayat Pengembalian", tinggi=6,
            tag_fn=lambda p: (
                "Menunggu Konfirmasi" if p["status"] == "Diajukan"
                else "Dikonfirmasi"
            )
        )
        self.tabel_riwayat.pack(fill="both", expand=True, pady=(12, 0))

        tombol(
            self.tabel_riwayat.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self.refresh_data()

    def _buat_panel(self, parent):
        panel = kartu(parent)
        panel.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            panel, text="Konfirmasi Pengembalian",
            font=theme.F_SECTION, text_color=theme.TEKS
        ).pack(anchor="w", padx=18, pady=(16, 4))

        self.label_info = ctk.CTkLabel(
            panel, text="Pilih pengajuan di tabel.",
            font=theme.F_LABEL, text_color=theme.TEKS_PUDAR,
            justify="left", anchor="w", wraplength=330
        )
        self.label_info.pack(fill="x", padx=18, pady=(0, 8))

        label_form(panel, "Tanggal pengembalian (dapat dikoreksi)").pack(
            fill="x", padx=18
        )
        self.picker_kembali = DatePicker(
            panel, command=self.perbarui_denda
        )
        self.picker_kembali.pack(fill="x", padx=18, pady=(3, 8))

        self.label_denda = ctk.CTkLabel(
            panel, text="Denda: -", font=(theme.FONT, 14, "bold"),
            text_color=theme.TEKS, anchor="w"
        )
        self.label_denda.pack(fill="x", padx=18, pady=(0, 10))

        bar = ctk.CTkFrame(panel, fg_color="transparent")
        bar.pack(fill="x", padx=18, pady=(0, 16))

        tombol(
            bar, "Konfirmasi", self.konfirmasi, gaya="sukses", width=140
        ).pack(side="left", padx=(0, 8))

        tombol(
            bar, "Tolak", self.tolak, gaya="bahaya", width=100
        ).pack(side="left")

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            self.tabel_pengajuan.set_data(
                self.controller.daftar_pengajuan() or []
            )
            self.tabel_riwayat.set_data(self.controller.daftar() or [])
            self._reset_panel()

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def _reset_panel(self):
        self.label_info.configure(text="Pilih pengajuan di tabel.")
        self.label_denda.configure(text="Denda: -", text_color=theme.TEKS)
        self.picker_kembali.clear()
        self.picker_kembali.set_min_date(None)
        self.picker_kembali.set_max_date(None)

    def pilih_pengajuan(self, p):
        if not p:
            return

        self.picker_kembali.set_min_date(p["tanggal_mulai"])
        self.picker_kembali.set_max_date(date.today())
        self.picker_kembali.set(p["tanggal_pengajuan"])

        self.label_info.configure(
            text=f'Penyewaan #{p["id"]} - {p["username"]}\n'
                 f'{p["merek"]} ({p["nomor_polisi"]})\n'
                 f'Mulai {tgl(p["tanggal_mulai"])}, rencana kembali '
                 f'{tgl(p["tanggal_rencana_kembali"])}',
            text_color=theme.TEKS
        )
        self.perbarui_denda()

    def perbarui_denda(self):
        p = self.tabel_pengajuan.dipilih()
        kembali = self.picker_kembali.get_date()

        if not p or not kembali:
            return

        denda, terlambat, tarif = self.controller.hitung_denda(
            p["tarif_harian"], p["tanggal_rencana_kembali"], kembali
        )

        if terlambat > 0:
            self.label_denda.configure(
                text=f"Denda: {rupiah(denda)} "
                     f"({terlambat} hari x {rupiah(tarif)})",
                text_color=theme.BAHAYA
            )
        else:
            self.label_denda.configure(
                text="Denda: Rp 0 (tepat waktu)", text_color=theme.SUKSES
            )

    def konfirmasi(self):
        p = self.tabel_pengajuan.dipilih()

        if not p:
            messagebox.showwarning(
                "Pilih Pengajuan",
                "Pilih pengajuan pengembalian terlebih dahulu.",
                parent=self
            )
            return

        kembali = self.picker_kembali.get()

        if not kembali:
            messagebox.showwarning(
                "Peringatan", "Tanggal pengembalian wajib dipilih.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Konfirmasi Pengembalian",
            f"Konfirmasi pengembalian penyewaan #{p['id']} "
            f"pada {kembali}?\n\n" + self.label_denda.cget("text"),
            parent=self
        ):
            return

        try:
            hasil = self.controller.proses(p["id"], kembali)

            if not hasil:
                raise Exception("Pengembalian gagal diproses.")

            if hasil["terlambat"] > 0:
                pesan = (
                    "Pengembalian dikonfirmasi.\n\n"
                    f"Terlambat: {hasil['terlambat']} hari\n"
                    f"Denda: {rupiah(hasil['denda'])}\n"
                    "Tagihan denda sudah dibuat untuk pelanggan."
                )
            else:
                pesan = (
                    "Pengembalian dikonfirmasi.\n"
                    "Tepat waktu, tidak ada denda."
                )

            messagebox.showinfo("Berhasil", pesan, parent=self)
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Kesalahan", str(exc), parent=self)

    def tolak(self):
        p = self.tabel_pengajuan.dipilih()

        if not p:
            messagebox.showwarning(
                "Pilih Pengajuan",
                "Pilih pengajuan pengembalian terlebih dahulu.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Tolak Pengajuan",
            f"Tolak pengajuan pengembalian penyewaan #{p['id']}?\n"
            "Pelanggan dapat mengajukan ulang.",
            parent=self
        ):
            return

        try:
            self.controller.tolak(p["id"])
            messagebox.showinfo(
                "Berhasil", "Pengajuan ditolak.", parent=self
            )
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Tidak Dapat Ditolak", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror("Kesalahan", str(exc), parent=self)
