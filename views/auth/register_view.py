import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import tombol
from views.auth import tampilan_auth as ui


ROLE_BAWAAN = "Pelanggan"


class RegisterView(ctk.CTkFrame):
    """Registrasi akun baru. Akun yang dibuat selalu berperan Pelanggan.

    Tampil di jendela yang sama dengan login, dengan desain yang sama.
    on_kembali: fungsi untuk kembali ke layar login.
    """

    def __init__(self, master, user_controller, on_kembali):
        super().__init__(master, fg_color=theme.LATAR_LOGO, corner_radius=0)

        self.user_controller = user_controller
        self.on_kembali = on_kembali

        self._buat_form(ui.siapkan_kerangka(self))

    def _buat_form(self, form):
        ui.judul(
            form, "Daftar akun",
            "Isi data untuk membuat akun GoRent.", jarak_bawah=20
        )

        self.entry_username = self._field(
            form, "Username", "Masukkan username"
        )
        self.entry_password = self._field(
            form, "Password (minimal 8 karakter)",
            "Masukkan password", show="*"
        )
        self.entry_identitas = self._field(
            form, "Nomor Identitas (KTP)", "Masukkan nomor identitas"
        )
        self.entry_telepon = self._field(
            form, "Nomor Telepon", "Masukkan nomor telepon"
        )

        tombol(
            form, "Daftar sekarang", self.register,
            gaya="aksen", height=46
        ).pack(fill="x", pady=(10, 0))

        ui.baris_tautan(
            form, "Sudah punya akun?", "Kembali ke login",
            self.on_kembali, lebar=130
        )

        for entry in (self.entry_username, self.entry_password,
                      self.entry_identitas, self.entry_telepon):
            entry.bind("<Return>", lambda _: self.register())

    def _field(self, form, label, placeholder, show=None):
        ui.label(form, label)
        entry = ui.entry(form, placeholder, show=show, tinggi=42)
        entry.pack(fill="x", pady=(4, 12))
        return entry

    def register(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        identitas = self.entry_identitas.get().strip()
        telepon = self.entry_telepon.get().strip()

        if not all([username, password, identitas, telepon]):
            messagebox.showwarning(
                "Peringatan", "Semua data wajib diisi.", parent=self
            )
            return

        if len(password) < 8:
            messagebox.showwarning(
                "Peringatan", "Password minimal 8 karakter.",
                parent=self
            )
            return

        try:
            berhasil = self.user_controller.register(
                username, password, identitas, telepon, ROLE_BAWAAN
            )

            if berhasil:
                messagebox.showinfo(
                    "Registrasi Berhasil",
                    "Akun berhasil dibuat. Silakan login.",
                    parent=self
                )
                self.on_kembali()
            else:
                messagebox.showerror(
                    "Registrasi Gagal",
                    "Akun gagal dibuat. Username atau nomor identitas "
                    "mungkin sudah digunakan.",
                    parent=self
                )

        except Exception as exc:
            messagebox.showerror("Kesalahan", str(exc), parent=self)
