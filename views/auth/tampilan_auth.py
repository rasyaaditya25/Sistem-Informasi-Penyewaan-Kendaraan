"""Kerangka tampilan yang dipakai bersama oleh Login dan Register:
logo di kiri, formulir pada panel navy di kanan."""

import customtkinter as ctk

from views.shared import theme, aset


def siapkan_kerangka(frame):
    """Atur kolom kiri (logo) dan kanan (form) pada frame layar penuh."""
    frame.grid_columnconfigure(0, weight=11)
    frame.grid_columnconfigure(1, weight=9, minsize=480)
    frame.grid_rowconfigure(0, weight=1)

    buat_sisi_logo(frame)
    return buat_panel_form(frame)


def buat_sisi_logo(frame):
    kiri = ctk.CTkFrame(frame, fg_color=theme.LATAR_LOGO, corner_radius=0)
    kiri.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(
        kiri, text="", image=aset.ctk_image("logo_penuh.png", lebar=330)
    ).place(relx=0.5, rely=0.46, anchor="center")

    ctk.CTkLabel(
        kiri, text=theme.TAGLINE,
        font=(theme.FONT, 14), text_color=theme.TEKS_PUDAR
    ).place(relx=0.5, rely=0.88, anchor="center")


def buat_panel_form(frame):
    """Panel navy di kanan; mengembalikan frame tempat form diletakkan."""
    kanan = ctk.CTkFrame(frame, fg_color=theme.SIDEBAR, corner_radius=0)
    kanan.grid(row=0, column=1, sticky="nsew")

    form = ctk.CTkFrame(kanan, fg_color="transparent", width=350)
    form.place(relx=0.5, rely=0.5, anchor="center")
    return form


def judul(form, teks, subteks, jarak_bawah=26):
    ctk.CTkLabel(
        form, text=teks, anchor="w",
        font=(theme.FONT, 28, "bold"), text_color="#FFFFFF"
    ).pack(fill="x")

    ctk.CTkLabel(
        form, text=subteks, anchor="w", font=theme.F_SUBJUDUL,
        text_color=theme.TEKS_SIDEBAR
    ).pack(fill="x", pady=(2, jarak_bawah))


def label(form, teks):
    ctk.CTkLabel(
        form, text=teks, anchor="w",
        font=theme.F_LABEL_BOLD, text_color="#FFFFFF"
    ).pack(fill="x")


def entry(form, placeholder, show=None, tinggi=44):
    return ctk.CTkEntry(
        form, height=tinggi, placeholder_text=placeholder,
        show=show or "", fg_color="#FFFFFF", border_color="#FFFFFF",
        text_color=theme.TEKS,
        placeholder_text_color=theme.TEKS_INPUT_KOSONG,
        corner_radius=10
    )


def baris_tautan(form, pertanyaan, teks_tautan, perintah, lebar=90):
    """Baris kecil: 'Belum memiliki akun?  Daftar akun'."""
    baris = ctk.CTkFrame(form, fg_color="transparent")
    baris.pack(pady=(22, 0))

    ctk.CTkLabel(
        baris, text=pertanyaan, font=theme.F_LABEL,
        text_color=theme.TEKS_SIDEBAR
    ).pack(side="left")

    ctk.CTkButton(
        baris, text=teks_tautan, width=lebar, height=28,
        fg_color="transparent", text_color=theme.AKSEN,
        hover_color=theme.SIDEBAR_HOVER,
        font=(theme.FONT, 12, "bold"), command=perintah
    ).pack(side="left", padx=(4, 0))
