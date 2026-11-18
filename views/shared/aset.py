"""Lokasi & pemuat gambar (logo, ikon). Bekerja di mode skrip maupun .exe."""

import sys
from pathlib import Path

from PIL import Image


def _folder_aset():
    # PyInstaller membongkar file ke sys._MEIPASS saat .exe dijalankan
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parents[2] / "assets"


def lokasi(nama):
    return str(_folder_aset() / nama)


def buka(nama):
    return Image.open(lokasi(nama)).convert("RGBA")


def ctk_image(nama, lebar=None, tinggi=None):
    """CTkImage dengan rasio asli. Cukup isi lebar ATAU tinggi."""
    import customtkinter as ctk

    gambar = buka(nama)
    rasio = gambar.width / gambar.height

    if lebar is None:
        lebar = round(tinggi * rasio)
    elif tinggi is None:
        tinggi = round(lebar / rasio)

    return ctk.CTkImage(
        light_image=gambar, dark_image=gambar, size=(lebar, tinggi)
    )


def pasang_ikon(jendela):
    """Ikon jendela + taskbar. Aman dipanggil berulang; gagal = diabaikan."""
    try:
        if sys.platform.startswith("win"):
            jendela.iconbitmap(lokasi("gorent.ico"))
        else:
            from PIL import ImageTk
            foto = ImageTk.PhotoImage(buka("icon_256.png"))
            jendela.iconphoto(True, foto)
            jendela._foto_ikon = foto   # cegah dibuang garbage collector
    except Exception:
        pass


def pasang_ikon_tertunda(jendela, ms=300):
    """CustomTkinter memasang ikon bawaannya ~200 ms setelah jendela dibuat
    (Windows); pasang ikon GoRent sesudahnya agar tidak tertimpa."""
    def _pasang():
        try:
            if jendela.winfo_exists():
                pasang_ikon(jendela)
        except Exception:
            pass

    jendela.after(ms, _pasang)


def set_id_aplikasi_windows():
    """Agar taskbar Windows memakai ikon GoRent, bukan ikon python.exe."""
    if not sys.platform.startswith("win"):
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "GoRent.SistemPenyewaanKendaraan"
        )
    except Exception:
        pass
