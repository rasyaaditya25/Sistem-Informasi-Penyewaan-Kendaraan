"""Kerangka aplikasi: sidebar navigasi + area konten."""

import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme, aset

NAMA_LOGOUT = "Logout"


class DashboardShell(ctk.CTkFrame):
    """
    daftar_halaman: [(nama_menu, lambda parent: Halaman), ...]
    Menu "Logout" ditambahkan otomatis di bagian bawah sidebar dan
    menampilkan kotak konfirmasi lalu langsung keluar jika dijawab Ya.
    """

    def __init__(self, master, user, daftar_halaman, on_logout):
        super().__init__(master, fg_color=theme.LATAR, corner_radius=0)

        self.user = user
        self.pembuat = dict(daftar_halaman)
        self.halaman = {}
        self.tombol_menu = {}
        self.aktif = None
        self.on_logout = on_logout

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._buat_sidebar([n for n, _ in daftar_halaman])

        self.konten = ctk.CTkFrame(self, fg_color=theme.LATAR,
                                   corner_radius=0)
        self.konten.grid(row=0, column=1, sticky="nsew")

        self.tampilkan(daftar_halaman[0][0])

    # ---------------------------------------------------------

    def _buat_sidebar(self, nama_menu):
        side = ctk.CTkFrame(
            self, fg_color=theme.SIDEBAR, corner_radius=0, width=240
        )
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        side.pack_propagate(False)

        ctk.CTkLabel(
            side, text="", image=aset.ctk_image("logo_sidebar.png", tinggi=48)
        ).pack(anchor="w", padx=22, pady=(28, 0))

        ctk.CTkLabel(
            side, text=self.user["role"],
            fg_color=theme.AKSEN, text_color=theme.TEKS_AKTIF,
            corner_radius=10, height=22,
            font=(theme.FONT, 11, "bold")
        ).pack(anchor="w", padx=24, pady=(14, 26))

        for nama in nama_menu:
            self._buat_menu(side, nama).pack(
                fill="x", padx=12, pady=2
            )

        # Bagian bawah: info user + logout
        ctk.CTkFrame(side, fg_color="transparent").pack(
            fill="both", expand=True
        )

        ctk.CTkFrame(side, fg_color=theme.GARIS_SIDEBAR, height=1).pack(
            fill="x", padx=18, pady=(0, 10)
        )

        ctk.CTkLabel(
            side, text=self.user["username"], text_color="#FFFFFF",
            font=(theme.FONT, 13, "bold")
        ).pack(anchor="w", padx=24)

        ctk.CTkLabel(
            side, text="Sedang login", text_color=theme.TEKS_SIDEBAR,
            font=(theme.FONT, 11)
        ).pack(anchor="w", padx=24, pady=(0, 8))

        self._buat_menu(side, NAMA_LOGOUT).pack(
            fill="x", padx=12, pady=(0, 18)
        )

    def _konfirmasi_logout(self):
        if messagebox.askyesno(
            "Konfirmasi Logout",
            "Apakah Anda yakin ingin logout?",
            parent=self
        ):
            self.on_logout()

    def _buat_menu(self, parent, nama):
        tombol_menu = ctk.CTkButton(
            parent, text=nama, anchor="w", height=42,
            corner_radius=10, fg_color="transparent",
            hover_color=theme.SIDEBAR_HOVER,
            text_color=theme.TEKS_SIDEBAR,
            font=(theme.FONT, 13, "bold"),
            command=(
                self._konfirmasi_logout if nama == NAMA_LOGOUT
                else lambda: self.tampilkan(nama)
            )
        )
        self.tombol_menu[nama] = tombol_menu
        return tombol_menu

    # ---------------------------------------------------------

    def tampilkan(self, nama):
        if self.aktif == nama:
            return

        if self.aktif is not None:
            self.halaman[self.aktif].pack_forget()
            self.tombol_menu[self.aktif].configure(
                fg_color="transparent", text_color=theme.TEKS_SIDEBAR
            )

        baru = nama not in self.halaman

        if baru:
            self.halaman[nama] = self.pembuat[nama](self.konten)

        self.halaman[nama].pack(fill="both", expand=True)
        self.tombol_menu[nama].configure(
            fg_color=theme.AKTIF, text_color=theme.TEKS_AKTIF
        )
        self.aktif = nama

        # Halaman yang baru dibuat sudah memuat datanya sendiri;
        # halaman lama dimuat ulang agar selalu terbaru.
        if not baru:
            self.halaman[nama].refresh_data()
