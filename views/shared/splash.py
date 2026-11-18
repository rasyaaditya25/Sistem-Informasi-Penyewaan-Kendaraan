"""Loading screen GoRent: jendela tanpa bingkai yang tampil saat aplikasi dibuka.

Selama animasi berjalan, `tugas` (mis. cek koneksi database) dikerjakan di
thread terpisah supaya animasi tidak tersendat. Status di bawah logo
mengikuti kemajuan tugas yang sebenarnya.
"""

import math
import threading
import time
import tkinter as tk

from PIL import ImageTk

from views.shared import theme
from views.shared.animasi_logo import AnimasiLogo

LEBAR, TINGGI = theme.UKURAN_JENDELA     # sama dengan jendela login
DURASI_MIN = 2.8        # detik; supaya animasi logo selesai terlihat
BATAS_TUNGGU = 8.0      # detik; tugas yang macet dianggap gagal
JEDA_GAGAL = 1.4        # detik; waktu membaca pesan bila tugas gagal
FPS_MS = 16

WARNA_PERINGATAN = "#B45309"


class SplashScreen(tk.Toplevel):
    """
    master : jendela utama (boleh sedang disembunyikan)
    tugas  : fungsi tanpa argumen -> True bila siap, False bila bermasalah
    setelah: fungsi yang dipanggil saat loading selesai (menampilkan app)
    """

    def __init__(self, master, tugas, setelah):
        super().__init__(master)

        self.tugas = tugas
        self.setelah = setelah

        self._hasil = None
        self._waktu_hasil = None
        self._target = 0.0
        self._progres = 0.0
        self._terakhir = 0.0
        self._keluar_dipanggil = False

        self.overrideredirect(True)
        self.configure(
            bg=theme.LATAR_LOGO, highlightthickness=1,
            highlightbackground=theme.GARIS
        )

        skala = self._hitung_skala()
        self.S = skala
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.W = min(round(LEBAR * skala), sw)
        self.H = min(round(TINGGI * skala), sh)

        # posisi sama persis dengan AppWindow.tampil()
        x = max((sw - self.W) // 2, 0)
        y = max((sh - self.H) // 2 - 20, 0)
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

        try:
            self.attributes("-topmost", True)
        except tk.TclError:
            pass

        # Semua posisi dihitung dari titik tengah jendela
        tengah = self.H / 2
        self.anim = AnimasiLogo(
            760, 460, theme.LATAR_LOGO, skala=skala,
            tinggi_simbol=290, lebar_tulisan=400, atas=20, jarak=36
        )

        self.kanvas = tk.Canvas(
            self, width=self.W, height=self.H, bg=theme.LATAR_LOGO,
            highlightthickness=0, bd=0
        )
        self.kanvas.pack(fill="both", expand=True)

        self._foto = ImageTk.PhotoImage(self.anim.render(0))
        self._gambar = self.kanvas.create_image(
            (self.W - self.anim.W) // 2, round(tengah - 280 * skala),
            anchor="nw", image=self._foto
        )

        # Bar kemajuan: garis tebal berujung bulat
        lebar_bar = round(380 * skala)
        self._x0 = (self.W - lebar_bar) / 2
        self._x1 = self._x0 + lebar_bar
        self._y_bar = round(tengah + 210 * skala)
        tebal = max(5, round(6 * skala))

        self.kanvas.create_line(
            self._x0, self._y_bar, self._x1, self._y_bar,
            width=tebal, capstyle="round", fill=theme.GARIS
        )
        self._isi_bar = self.kanvas.create_line(
            self._x0, self._y_bar, self._x0, self._y_bar,
            width=tebal, capstyle="round", fill=theme.CYAN, state="hidden"
        )

        self._teks = self.kanvas.create_text(
            self.W / 2, round(tengah + 247 * skala),
            text="Memuat komponen...",
            fill=theme.TEKS_PUDAR, font=(theme.FONT, 12)
        )

        self.update()

        self._mulai = time.perf_counter()
        self._target = 0.25
        self.after(250, self._mulai_tugas)
        self.after(FPS_MS, self._tick)

    # ---------------------------------------------------------

    def _hitung_skala(self):
        try:
            return min(max(self.winfo_fpixels("1i") / 96.0, 1.0), 2.5)
        except tk.TclError:
            return 1.0

    def _mulai_tugas(self):
        self._atur_status("Memeriksa koneksi database...", 0.6)
        threading.Thread(target=self._kerjakan, daemon=True).start()

    def _kerjakan(self):
        try:
            ok = bool(self.tugas())
        except Exception:
            ok = False

        self._waktu_hasil = time.perf_counter() - self._mulai
        self._hasil = ok          # ditulis terakhir; dibaca oleh _tick

    def _atur_status(self, teks, target, warna=None):
        self._target = max(self._target, target)
        self.kanvas.itemconfig(
            self._teks, text=teks, fill=warna or theme.TEKS_PUDAR
        )

    # ---------------------------------------------------------

    def _tick(self):
        if self._keluar_dipanggil:
            return

        try:
            self._perbarui()
        except tk.TclError:
            return                      # jendela sudah ditutup

        self.after(FPS_MS, self._tick)

    def _perbarui(self):
        t = time.perf_counter() - self._mulai
        dt = max(t - self._terakhir, 0.001)
        self._terakhir = t

        hasil = self._hasil
        if hasil is None and t > BATAS_TUNGGU:
            hasil = False
            self._waktu_hasil = t

        siap = False
        if hasil is not None:
            if hasil and self._target < 1.0:
                self._atur_status("Menyiapkan tampilan...", 0.9)
            elif not hasil and self._target < 0.9:
                self._atur_status(
                    "Database belum terhubung. Periksa MySQL.",
                    0.9, WARNA_PERINGATAN
                )

            batas = DURASI_MIN
            if not hasil:
                batas = max(batas, (self._waktu_hasil or t) + JEDA_GAGAL)

            if t >= batas:
                if hasil:
                    self._atur_status("Siap", 1.0)
                else:
                    self._target = 1.0
                siap = True

        # Bar tidak pernah melompat: mengejar target dengan halus
        tujuan = min(self._target, t / (DURASI_MIN - 0.3))
        self._progres += (tujuan - self._progres) * (1 - math.exp(-dt * 7))
        self._gambar_bar()

        self._foto.paste(self.anim.render(t))

        if siap and self._progres > 0.985:
            self._selesai()

    def _gambar_bar(self):
        if self._progres < 0.03:
            return
        x = self._x0 + (self._x1 - self._x0) * min(self._progres, 1.0)
        self.kanvas.coords(self._isi_bar, self._x0, self._y_bar, x, self._y_bar)
        self.kanvas.itemconfig(self._isi_bar, state="normal")

    # ---------------------------------------------------------

    def _selesai(self):
        """Tampilkan aplikasi di belakang splash, lalu pudarkan splash."""
        self._keluar_dipanggil = True

        try:
            self.setelah()
        finally:
            self._pudar(1.0)

    def _pudar(self, alpha):
        try:
            if alpha <= 0.05:
                self.destroy()
                return
            self.attributes("-alpha", alpha)
        except tk.TclError:
            try:
                self.destroy()
            except tk.TclError:
                pass
            return

        self.after(FPS_MS, lambda: self._pudar(alpha - 0.1))
