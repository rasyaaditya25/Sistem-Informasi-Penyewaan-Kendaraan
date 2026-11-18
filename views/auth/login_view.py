import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import tombol
from views.auth import tampilan_auth as ui


class LoginView(ctk.CTkFrame):
    """Halaman login: logo di kiri, formulir pada panel navy di kanan."""

    def __init__(self, master, user_controller, on_login_success,
                 on_daftar=None):
        super().__init__(master, fg_color=theme.LATAR_LOGO, corner_radius=0)

        self.user_controller = user_controller
        self.on_login_success = on_login_success
        self.on_daftar = on_daftar

        self._buat_form(ui.siapkan_kerangka(self))

    def _buat_form(self, form):
        ui.judul(
            form, "Selamat datang",
            "Masuk untuk mengelola penyewaan kendaraan.", jarak_bawah=30
        )

        ui.label(form, "Username")
        self.entry_username = ui.entry(form, "Masukkan username")
        self.entry_username.pack(fill="x", pady=(4, 16))

        ui.label(form, "Password")
        self.entry_password = ui.entry(form, "Masukkan password", show="*")
        self.entry_password.pack(fill="x", pady=(4, 10))

        self.var_show_password = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            form, text="Tampilkan password",
            variable=self.var_show_password,
            command=self.toggle_password,
            font=(theme.FONT, 11), text_color=theme.TEKS_SIDEBAR,
            fg_color=theme.AKSEN, hover_color=theme.AKSEN_HOVER,
            border_color=theme.GARIS_SIDEBAR, checkmark_color=theme.NAVY,
            checkbox_width=20, checkbox_height=20
        ).pack(anchor="w", pady=(0, 24))

        tombol(
            form, "Masuk", self.login, gaya="aksen", height=46
        ).pack(fill="x")

        ui.baris_tautan(
            form, "Belum memiliki akun?", "Daftar akun", self.buka_register
        )

        self.entry_username.bind("<Return>", lambda _: self.login())
        self.entry_password.bind("<Return>", lambda _: self.login())

    # ---------------------------------------------------------

    def toggle_password(self):
        self.entry_password.configure(
            show="" if self.var_show_password.get() else "*"
        )

    def reset_form(self):
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.var_show_password.set(False)
        self.entry_password.configure(show="*")

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning(
                "Peringatan", "Username dan password wajib diisi.",
                parent=self
            )
            return

        try:
            user = self.user_controller.login(username, password)

        except Exception as exc:
            messagebox.showerror("Kesalahan", str(exc), parent=self)
            return

        if not user:
            messagebox.showerror(
                "Login Gagal", "Username atau password salah.",
                parent=self
            )
            return

        self.on_login_success(user)

    def buka_register(self):
        """Layar login diganti layar register pada jendela yang sama."""
        if self.on_daftar:
            self.on_daftar()
