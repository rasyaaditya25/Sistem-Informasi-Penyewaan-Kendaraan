"""Animasi logo GoRent untuk loading screen.

Murni Pillow (tanpa Tk) sehingga bisa diuji tanpa layar.
Urutan animasi:
  1. badan huruf G muncul + membesar halus
  2. dua busur cyan meluncur masuk dari arah berlawanan (kesan melaju)
  3. tulisan "GoRent" naik & muncul
  4. busur cyan bergoyang sangat pelan selama menunggu
"""

import math

from PIL import Image

from views.shared import aset


def _clamp(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def _ease_out(x):                       # melambat di akhir
    return 1 - (1 - _clamp(x)) ** 3


def _ease_in_out(x):
    x = _clamp(x)
    return 3 * x * x - 2 * x * x * x


class AnimasiLogo:

    def __init__(self, lebar, tinggi, latar, skala=1.0,
                 tinggi_simbol=180, lebar_tulisan=250, atas=50,
                 jarak=24):
        self.S = skala
        self.k = tinggi_simbol / 180.0   # gerakan ikut membesar
        self.W = round(lebar * skala)
        self.H = round(tinggi * skala)
        self.latar = latar
        self.atas = round(atas * skala)

        def siapkan(nama, tinggi=None, lebar=None):
            img = aset.buka(nama)
            if tinggi:
                lebar = round(img.width * tinggi / img.height)
            else:
                tinggi = round(img.height * lebar / img.width)
            return img.resize((lebar, tinggi), Image.LANCZOS)

        th = round(tinggi_simbol * skala)
        self.navy = siapkan("simbol_navy.png", tinggi=th)
        self.dalam = siapkan("simbol_cyan_dalam.png", tinggi=th)
        self.kiri = siapkan("simbol_cyan_kiri.png", tinggi=th)
        self.kanan = siapkan("simbol_cyan_kanan.png", tinggi=th)
        self.tulisan = siapkan("logo_tulisan.png",
                               lebar=round(lebar_tulisan * skala))

        self.jarak_tulisan = round(jarak * skala)
        self.tinggi_blok = th + self.jarak_tulisan + self.tulisan.height

    # -----------------------------------------------------------

    @staticmethod
    def _redam(layer, k):
        """Kalikan alpha layer dengan k (0..1)."""
        if k >= 0.999:
            return layer
        hasil = layer.copy()
        hasil.putalpha(
            layer.getchannel("A").point([int(i * k) for i in range(256)])
        )
        return hasil

    def _tempel(self, kanvas, layer, pusat_x, y, k=1.0, skala=1.0,
                dx=0.0, dy=0.0):
        if k <= 0.004:
            return
        if abs(skala - 1.0) > 0.002:
            layer = layer.resize(
                (max(1, round(layer.width * skala)),
                 max(1, round(layer.height * skala))),
                Image.BILINEAR
            )
        layer = self._redam(layer, k)
        x = round(pusat_x - layer.width / 2 + dx)
        y = round(y - (layer.height - self._tinggi_simbol_asli) / 2 + dy) \
            if skala != 1.0 else round(y + dy)
        kanvas.paste(layer, (x, y), layer)

    @property
    def _tinggi_simbol_asli(self):
        return self.navy.height

    # -----------------------------------------------------------

    def render(self, t):
        """Gambar RGB seluruh logo pada detik ke-t."""
        S = self.S
        kanvas = Image.new("RGB", (self.W, self.H), self.latar)
        cx = self.W / 2
        y0 = self.atas

        # 1. badan G + garis cyan dalam
        a1 = _ease_out((t - 0.05) / 0.75)
        sk = 0.90 + 0.10 * a1
        self._tempel(kanvas, self.navy, cx, y0, a1, sk)
        self._tempel(kanvas, self.dalam, cx, y0, _ease_out((t - 0.20) / 0.7),
                     sk)

        # 2. busur luar meluncur masuk, lalu bergoyang pelan
        goyang = 0.0
        if t > 1.3:
            goyang = math.sin((t - 1.3) * 2.4) * 2.5 * S * self.k * _clamp((t - 1.3) / 0.8)

        g = _ease_out((t - 0.45) / 0.75)
        jarak = 64 * S * self.k * (1 - g)
        self._tempel(kanvas, self.kiri, cx, y0, g, 1.0,
                     dx=-jarak - goyang, dy=-jarak * 0.45 - goyang * 0.4)
        self._tempel(kanvas, self.kanan, cx, y0, g, 1.0,
                     dx=jarak + goyang, dy=jarak * 0.45 + goyang * 0.4)

        # 3. tulisan GoRent
        w = _ease_out((t - 0.95) / 0.65)
        y_tulisan = y0 + self.navy.height + self.jarak_tulisan
        self._tempel(kanvas, self.tulisan, cx, y_tulisan, w, 1.0,
                     dy=16 * S * self.k * (1 - w))
        return kanvas
