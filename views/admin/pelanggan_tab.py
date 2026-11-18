import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, label_form
)


class KelolaPelangganView(Halaman):
    """
    Admin mengelola data pelanggan (ubah & hapus).
    Pelanggan tidak ditambahkan di sini: mereka mendaftar sendiri
    lewat form registrasi dan memiliki akunnya masing-masing.
    """

    def __init__(self, master, user_controller):
        super().__init__(
            master, "Kelola Data Pelanggan",
            "Pelanggan mendaftar sendiri lewat form registrasi. "
            "Di sini Anda dapat memperbarui atau menghapus datanya."
        )

        self.controller = user_controller
        self.id_terpilih = None

        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=0, minsize=310)
        self.body.grid_rowconfigure(0, weight=1)

        self.tabel_data = TabelData(
            self.body,
            [
                ("id_user", "ID", 55),
                ("username", "Username", 170, "w"),
                ("identitas", "No. Identitas", 170, "w"),
                ("telepon", "No. Telepon", 140, "w"),
            ],
            lambda p: (
                p["id_user"], p["username"],
                p["no_identitas"], p["no_telepon"]
            ),
            judul="Daftar Pelanggan",
            on_pilih=self.pilih_pelanggan
        )
        self.tabel_data.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self._buat_form()
        self._atur_form(False)
        self.refresh_data()

    def _buat_form(self):
        form = kartu(self.body)
        form.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            form, text="Detail Pelanggan", font=theme.F_SECTION,
            text_color=theme.TEKS
        ).pack(anchor="w", padx=18, pady=(18, 2))

        self.label_petunjuk = ctk.CTkLabel(
            form, text="Pilih pelanggan di tabel untuk melihat "
                       "dan mengubah datanya.",
            font=(theme.FONT, 11), text_color=theme.TEKS_PUDAR,
            wraplength=260, justify="left", anchor="w"
        )
        self.label_petunjuk.pack(fill="x", padx=18, pady=(0, 10))

        label_form(form, "Username").pack(fill="x", padx=18)
        self.entry_username = ctk.CTkEntry(form, height=36)
        self.entry_username.pack(fill="x", padx=18, pady=(3, 10))

        label_form(form, "Nomor Identitas (KTP)").pack(fill="x", padx=18)
        self.entry_identitas = ctk.CTkEntry(form, height=36)
        self.entry_identitas.pack(fill="x", padx=18, pady=(3, 10))

        label_form(form, "Nomor Telepon").pack(fill="x", padx=18)
        self.entry_telepon = ctk.CTkEntry(form, height=36)
        self.entry_telepon.pack(fill="x", padx=18, pady=(3, 14))

        self.btn_simpan = tombol(
            form, "Simpan Perubahan", self.ubah_pelanggan
        )
        self.btn_simpan.pack(fill="x", padx=18, pady=(0, 6))

        self.btn_hapus = tombol(
            form, "Hapus Pelanggan", self.hapus_pelanggan, gaya="bahaya"
        )
        self.btn_hapus.pack(fill="x", padx=18, pady=(0, 6))

        self.btn_batal = tombol(
            form, "Batal", self.bersihkan_form, gaya="netral"
        )
        self.btn_batal.pack(fill="x", padx=18, pady=(0, 18))

    def _atur_form(self, aktif):
        status = "normal" if aktif else "disabled"

        for entry in (
            self.entry_username, self.entry_identitas, self.entry_telepon
        ):
            entry.configure(state=status)

        for btn in (self.btn_simpan, self.btn_hapus, self.btn_batal):
            btn.configure(state=status)

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            self.tabel_data.set_data(self.controller.daftar_pelanggan())

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def pilih_pelanggan(self, pelanggan):
        if not pelanggan:
            return

        self.id_terpilih = pelanggan["id_user"]
        self._atur_form(True)

        for entry, nilai in (
            (self.entry_username, pelanggan["username"]),
            (self.entry_identitas, pelanggan["no_identitas"]),
            (self.entry_telepon, pelanggan["no_telepon"]),
        ):
            entry.delete(0, "end")
            entry.insert(0, nilai or "")

    def ubah_pelanggan(self):
        if self.id_terpilih is None:
            return

        username = self.entry_username.get().strip()
        identitas = self.entry_identitas.get().strip()
        telepon = self.entry_telepon.get().strip()

        if not username or not identitas or not telepon:
            messagebox.showwarning(
                "Validasi Data", "Semua data pelanggan wajib diisi.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Konfirmasi", "Perbarui data pelanggan ini?", parent=self
        ):
            return

        try:
            hasil = self.controller.ubah_pelanggan(
                self.id_terpilih, username, identitas, telepon
            )

            if hasil is False:
                raise ValueError(
                    "Data gagal diperbarui. Username atau nomor "
                    "identitas mungkin sudah dipakai."
                )

            messagebox.showinfo(
                "Berhasil", "Data pelanggan berhasil diperbarui.",
                parent=self
            )
            self.bersihkan_form()
            self.refresh_data()

        except Exception as exc:
            messagebox.showerror(
                "Gagal Mengubah Pelanggan", str(exc), parent=self
            )

    def hapus_pelanggan(self):
        if self.id_terpilih is None:
            return

        if not messagebox.askyesno(
            "Konfirmasi", "Hapus pelanggan ini?", parent=self
        ):
            return

        try:
            if not self.controller.hapus_pelanggan(self.id_terpilih):
                raise ValueError(
                    "Pelanggan tidak dapat dihapus. Pastikan pelanggan "
                    "tidak memiliki riwayat penyewaan."
                )

            messagebox.showinfo(
                "Berhasil", "Pelanggan berhasil dihapus.", parent=self
            )
            self.bersihkan_form()
            self.refresh_data()

        except Exception as exc:
            messagebox.showerror(
                "Gagal Menghapus Pelanggan", str(exc), parent=self
            )

    def bersihkan_form(self):
        self.id_terpilih = None
        self._atur_form(True)  # entry harus normal agar bisa dikosongkan

        for entry in (
            self.entry_username, self.entry_identitas, self.entry_telepon
        ):
            entry.delete(0, "end")

        self._atur_form(False)
        self.tabel_data.kosongkan_pilihan()
