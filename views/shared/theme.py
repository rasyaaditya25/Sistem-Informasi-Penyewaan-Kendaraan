"""Warna & font GoRent. Ubah di sini untuk mengganti tampilan seluruh aplikasi.

Palet diambil langsung dari logo: biru navy (badan huruf G) dan cyan
(goresan kecepatan + tulisan "Go"). Warna lain hanyalah turunan terang/gelap
dari keduanya, kecuali warna status (sukses / bahaya / peringatan).
"""

import sys

import customtkinter as ctk

NAMA_APP = "GoRent"
TAGLINE = "Sistem Informasi Penyewaan Kendaraan"

# Ukuran jendela utama (login) - loading screen memakai ukuran yang sama
UKURAN_JENDELA = (1280, 780)

# ---- Warna logo ------------------------------------------------
NAVY = "#192F5B"
NAVY_TERANG = "#27427D"
NAVY_GELAP = "#11224A"
CYAN = "#24BBE0"
CYAN_HOVER = "#55CDEA"
CYAN_GELAP = "#0B7A9C"        # cyan untuk teks di atas latar putih

# ---- Peran warna di aplikasi -----------------------------------
SIDEBAR = NAVY
SIDEBAR_HOVER = NAVY_TERANG
GARIS_SIDEBAR = "#33508C"
AKTIF = CYAN                   # menu aktif
TEKS_AKTIF = NAVY              # teks di atas cyan (kontras jauh lebih baik dari putih)
LATAR = "#F2F6FA"
LATAR_LOGO = "#F7F9FC"
KARTU = "#FFFFFF"
GARIS = "#DCE4EE"
GARIS_INPUT = "#C5D2E2"
TEKS = "#16233F"
TEKS_PUDAR = "#5A6A84"
TEKS_SIDEBAR = "#C5D3EA"
TEKS_INPUT_KOSONG = "#8A97AD"

UTAMA = NAVY
UTAMA_HOVER = NAVY_TERANG
AKSEN = CYAN
AKSEN_HOVER = CYAN_HOVER

BIRU_MUDA = "#E3F5FB"          # kotak info, hover lembut
PILIH = "#CDEFFA"              # baris tabel / tanggal terpilih
TABEL_HEADER = "#E7EEF8"

SUKSES = "#177A5A"
SUKSES_HOVER = "#106048"
BAHAYA = "#B42318"
BAHAYA_HOVER = "#8F1D14"
NETRAL = "#66758C"
NETRAL_HOVER = "#4F5C70"
PERINGATAN_LATAR = "#FFF4E0"

# ---- Font ------------------------------------------------------
# Segoe UI ada di semua Windows; di OS lain Tk memilih font pengganti.
FONT = "Segoe UI" if sys.platform.startswith("win") else "Helvetica"
F_JUDUL = (FONT, 22, "bold")
F_SUBJUDUL = (FONT, 13)
F_SECTION = (FONT, 15, "bold")
F_LABEL = (FONT, 12)
F_LABEL_BOLD = (FONT, 12, "bold")
F_ANGKA = (FONT, 20, "bold")

# Warna baris tabel berdasarkan status. Hanya status yang butuh
# perhatian diberi warna; status "baik" memakai warna teks biasa.
WARNA_STATUS = {
    "Disewa": "#B45309",
    "Perawatan": "#B91C1C",
    "Menunggu": "#B45309",
    "Berjalan": CYAN_GELAP,
    "Menunggu Konfirmasi": "#B45309",
}


def terapkan_tema_ctk():
    """Menyelaraskan warna bawaan widget CustomTkinter dengan logo.

    Harus dipanggil setelah ctk.set_default_color_theme() dan sebelum
    widget pertama dibuat.
    """
    def atur(widget, **nilai):
        tema = ctk.ThemeManager.theme.setdefault(widget, {})
        for kunci, v in nilai.items():
            tema[kunci] = v if isinstance(v, (int, float)) else [v, v]

    atur("CTkButton", fg_color=UTAMA, hover_color=UTAMA_HOVER,
         text_color="#FFFFFF", text_color_disabled="#A9B4C6")
    atur("CTkEntry", fg_color="#FFFFFF", border_color=GARIS_INPUT,
         text_color=TEKS, placeholder_text_color=TEKS_INPUT_KOSONG,
         border_width=1, corner_radius=8)
    atur("CTkComboBox", fg_color="#FFFFFF", border_color=GARIS_INPUT,
         button_color=UTAMA, button_hover_color=UTAMA_HOVER,
         text_color=TEKS, dropdown_fg_color="#FFFFFF",
         dropdown_hover_color=PILIH, dropdown_text_color=TEKS,
         border_width=1, corner_radius=8)
    atur("CTkOptionMenu", fg_color=UTAMA, button_color=UTAMA_HOVER,
         button_hover_color=NAVY_GELAP, text_color="#FFFFFF")
    atur("CTkCheckBox", fg_color=AKSEN, hover_color=CYAN_HOVER,
         border_color=GARIS_INPUT, checkmark_color=NAVY, text_color=TEKS)
    atur("CTkScrollbar", button_color="#C5D2E2", button_hover_color=CYAN)
    atur("CTkProgressBar", fg_color=GARIS, progress_color=AKSEN)
    atur("CTkSwitch", progress_color=AKSEN, button_color="#FFFFFF",
         button_hover_color="#F1F5FA")
