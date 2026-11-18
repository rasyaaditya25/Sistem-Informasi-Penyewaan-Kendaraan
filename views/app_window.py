"""Jendela tunggal GoRent: bergantian menampilkan login & dashboard."""

import customtkinter as ctk

from views.shared import theme, aset
from views.auth.login_view import LoginView
from views.auth.register_view import RegisterView

UKURAN_AWAL = theme.UKURAN_JENDELA


class AppWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Disembunyikan dulu; loading screen tampil lebih dulu,
        # lalu tampil() dipanggil saat semuanya siap.
        self.withdraw()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        theme.terapkan_tema_ctk()

        self.title(f"{theme.NAMA_APP} - {theme.TAGLINE}")
        self.geometry(f"{UKURAN_AWAL[0]}x{UKURAN_AWAL[1]}")
        self.minsize(1100, 680)
        self.configure(fg_color=theme.LATAR)
        aset.pasang_ikon_tertunda(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.layar = None
        self._memuat = None

    # ---------------------------------------------------------

    def tampil(self):
        """Letakkan di tengah layar lalu tampilkan."""
        try:
            skala = ctk.ScalingTracker.get_window_scaling(self)
        except Exception:
            skala = 1.0

        lebar = round(UKURAN_AWAL[0] * skala)
        tinggi = round(UKURAN_AWAL[1] * skala)
        x = max((self.winfo_screenwidth() - lebar) // 2, 0)
        y = max((self.winfo_screenheight() - tinggi) // 2 - 20, 0)

        self.geometry(f"{UKURAN_AWAL[0]}x{UKURAN_AWAL[1]}+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()

    def _ganti_layar(self, layar):
        if self.layar is not None:
            self.layar.destroy()

        self.layar = layar
        self.layar.grid(row=0, column=0, sticky="nsew")

    # ---------------------------------------------------------

    def _tampilkan_memuat(self, teks):
        """Layar singkat 'memuat' saat dashboard sedang dibangun."""
        self._memuat = ctk.CTkFrame(
            self, fg_color=theme.LATAR_LOGO, corner_radius=0
        )
        self._memuat.place(x=0, y=0, relwidth=1, relheight=1)

        isi = ctk.CTkFrame(self._memuat, fg_color="transparent")
        isi.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            isi, text="", image=aset.ctk_image("logo_simbol.png", tinggi=110)
        ).pack()

        ctk.CTkLabel(
            isi, text=teks, font=theme.F_SUBJUDUL,
            text_color=theme.TEKS_PUDAR
        ).pack(pady=(16, 0))

        self.update()

    def _sembunyikan_memuat(self):
        if self._memuat is not None:
            self._memuat.destroy()
            self._memuat = None

    # ---------------------------------------------------------

    def tampilkan_login(self, user_controller, on_login_success):
        self.title(f"Masuk - {theme.NAMA_APP}")
        self._ganti_layar(
            LoginView(
                self, user_controller, on_login_success,
                on_daftar=lambda: self.tampilkan_register(
                    user_controller, on_login_success
                )
            )
        )

    def tampilkan_register(self, user_controller, on_login_success):
        """Layar login ditutup, diganti layar registrasi."""
        self.title(f"Daftar Akun - {theme.NAMA_APP}")
        self._ganti_layar(
            RegisterView(
                self, user_controller,
                on_kembali=lambda: self.tampilkan_login(
                    user_controller, on_login_success
                )
            )
        )

    def tampilkan_dashboard(self, pembuat, user):
        """pembuat: fungsi (master) -> frame dashboard."""
        self.title(
            f"{theme.NAMA_APP} - {user['username']} ({user['role']})"
        )

        self._tampilkan_memuat("Menyiapkan dashboard...")

        try:
            self._ganti_layar(pembuat(self))
        finally:
            self._sembunyikan_memuat()
