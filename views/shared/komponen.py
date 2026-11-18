"""Komponen tampilan yang dipakai bersama oleh semua halaman."""

import customtkinter as ctk
from tkinter import ttk, messagebox

from views.shared import theme


# =============================================================
# FORMAT
# =============================================================

def rupiah(nilai):
    try:
        return "Rp {:,.0f}".format(float(nilai or 0)).replace(",", ".")
    except (TypeError, ValueError):
        return "Rp 0"


def tgl(nilai):
    """Tanggal ke teks; kosong menjadi '-'."""
    if nilai is None or nilai == "":
        return "-"
    return nilai.isoformat() if hasattr(nilai, "isoformat") else str(nilai)


def status_sewa(p):
    """Status penyewaan untuk tampilan pelanggan/admin."""
    if p.get("status") == "Selesai":
        return "Selesai"

    if p.get("status_pengembalian") == "Diajukan":
        return "Menunggu Konfirmasi"

    return "Berjalan"


# =============================================================
# TOMBOL
# =============================================================

# gaya: (warna, warna saat disorot, warna teks)
_GAYA = {
    "utama": (theme.UTAMA, theme.UTAMA_HOVER, "#FFFFFF"),
    "aksen": (theme.AKSEN, theme.AKSEN_HOVER, theme.TEKS_AKTIF),
    "sukses": (theme.SUKSES, theme.SUKSES_HOVER, "#FFFFFF"),
    "bahaya": (theme.BAHAYA, theme.BAHAYA_HOVER, "#FFFFFF"),
    "netral": (theme.NETRAL, theme.NETRAL_HOVER, "#FFFFFF"),
}


def tombol(parent, teks, command, gaya="utama", **kw):
    warna, hover, warna_teks = _GAYA[gaya]
    kw.setdefault("height", 36)
    kw.setdefault("corner_radius", 8)
    return ctk.CTkButton(
        parent, text=teks, command=command,
        fg_color=warna, hover_color=hover, text_color=warna_teks,
        font=(theme.FONT, 12, "bold"), **kw
    )


def kartu(parent, **kw):
    kw.setdefault("fg_color", theme.KARTU)
    kw.setdefault("corner_radius", 12)
    kw.setdefault("border_width", 1)
    kw.setdefault("border_color", theme.GARIS)
    return ctk.CTkFrame(parent, **kw)


def label_form(parent, teks):
    return ctk.CTkLabel(
        parent, text=teks, anchor="w",
        font=theme.F_LABEL_BOLD, text_color=theme.TEKS
    )


# =============================================================
# HALAMAN DASAR: judul + area isi
# =============================================================

class Halaman(ctk.CTkFrame):
    """Semua halaman memakai ini agar judul & jarak seragam."""

    def __init__(self, master, judul, subjudul=None):
        super().__init__(master, fg_color="transparent")

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=26, pady=(22, 12))

        ctk.CTkLabel(
            header, text=judul, anchor="w",
            font=theme.F_JUDUL, text_color=theme.TEKS
        ).pack(fill="x")

        if subjudul:
            ctk.CTkLabel(
                header, text=subjudul, anchor="w",
                font=theme.F_SUBJUDUL, text_color=theme.TEKS_PUDAR
            ).pack(fill="x", pady=(2, 0))

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=26, pady=(0, 22))

    def refresh_data(self):  # diganti oleh subclass
        pass


# =============================================================
# TABEL
# =============================================================

def siapkan_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        rowheight=32,
        font=(theme.FONT, 10),
        background="#FFFFFF",
        fieldbackground="#FFFFFF",
        foreground=theme.TEKS,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        font=(theme.FONT, 10, "bold"),
        background=theme.TABEL_HEADER,
        foreground=theme.TEKS,
        relief="flat",
        padding=(6, 6)
    )
    style.map(
        "Treeview",
        background=[("selected", theme.PILIH)],
        foreground=[("selected", theme.TEKS)]
    )


class TabelData(ctk.CTkFrame):
    """
    Kartu berisi judul, kotak cari, dan tabel.

    kolom    : list of (key, judul, lebar[, anchor])
    ke_baris : fungsi dict -> tuple nilai kolom
    tag_fn   : (opsional) fungsi dict -> nama tag/status untuk warna baris
    on_pilih : (opsional) fungsi yang dipanggil dengan dict baris terpilih
    """

    def __init__(self, master, kolom, ke_baris, judul=None,
                 tag_fn=None, on_pilih=None, tinggi=10, cari=True):
        super().__init__(
            master, fg_color=theme.KARTU, corner_radius=12,
            border_width=1, border_color=theme.GARIS
        )
        siapkan_style()

        self.ke_baris = ke_baris
        self.tag_fn = tag_fn
        self.on_pilih = on_pilih
        self._semua = []
        self._tampil = []

        # Kolom pertama bernama "id"/"id_user" ditampilkan sebagai
        # nomor urut (1, 2, 3, ...) agar tidak acak. ID asli di database
        # tidak berubah dan tetap dipakai pada aksi (ubah/hapus/dll).
        self._pakai_nomor = bool(kolom) and kolom[0][0] in ("id", "id_user")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Bar atas
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))

        if judul:
            ctk.CTkLabel(
                bar, text=judul, font=theme.F_SECTION,
                text_color=theme.TEKS
            ).pack(side="left")

        self.toolbar = ctk.CTkFrame(
            bar, fg_color="transparent", height=32
        )
        self.toolbar.pack(side="right")

        self.entry_cari = None

        if cari:
            # Tanpa textvariable agar placeholder tetap tampil
            self.entry_cari = ctk.CTkEntry(
                self.toolbar, width=200, height=32,
                placeholder_text="Cari data..."
            )
            self.entry_cari.pack(side="left")
            self.entry_cari.bind(
                "<KeyRelease>", lambda _e: self._render()
            )

        # Tabel + scrollbar
        wadah = ctk.CTkFrame(self, fg_color="transparent")
        wadah.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 6))
        wadah.grid_columnconfigure(0, weight=1)
        wadah.grid_rowconfigure(0, weight=1)

        self.tabel = ttk.Treeview(
            wadah, columns=[k[0] for k in kolom], show="headings",
            height=tinggi, selectmode="browse"
        )

        for k in kolom:
            key, teks, lebar = k[0], k[1], k[2]
            if self._pakai_nomor and k is kolom[0]:
                teks = "No"
            anchor = k[3] if len(k) > 3 else "center"
            self.tabel.heading(key, text=teks, anchor=anchor)
            self.tabel.column(
                key, width=lebar, minwidth=40, anchor=anchor
            )

        scroll = ttk.Scrollbar(
            wadah, orient="vertical", command=self.tabel.yview
        )
        self.tabel.configure(yscrollcommand=scroll.set)
        self.tabel.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        for nama, warna in theme.WARNA_STATUS.items():
            self.tabel.tag_configure(nama, foreground=warna)

        self.tabel.bind("<<TreeviewSelect>>", self._saat_pilih)

        self.label_info = ctk.CTkLabel(
            self, text="", anchor="w", font=(theme.FONT, 11),
            text_color=theme.TEKS_PUDAR
        )
        self.label_info.grid(
            row=2, column=0, sticky="ew", padx=16, pady=(0, 10)
        )

    # ---------------------------------------------------------

    def set_data(self, data):
        self._semua = list(data or [])
        self._render()

    def _render(self):
        kata = (
            self.entry_cari.get().strip().lower()
            if self.entry_cari else ""
        )

        self._tampil = [
            d for d in self._semua
            if not kata or kata in " ".join(
                str(v) for v in self.ke_baris(d)
            ).lower()
        ]

        for item in self.tabel.get_children():
            self.tabel.delete(item)

        for i, d in enumerate(self._tampil):
            tag = self.tag_fn(d) if self.tag_fn else ""
            baris = tuple(self.ke_baris(d))
            if self._pakai_nomor:
                baris = (i + 1,) + baris[1:]
            self.tabel.insert(
                "", "end", iid=str(i),
                values=baris, tags=(tag,) if tag else ()
            )

        if not self._semua:
            self.label_info.configure(text="Belum ada data.")
        elif not self._tampil:
            self.label_info.configure(text="Tidak ada data yang cocok.")
        else:
            self.label_info.configure(
                text=f"{len(self._tampil)} dari {len(self._semua)} data"
            )

    def dipilih(self):
        pilihan = self.tabel.selection()

        if not pilihan:
            return None

        indeks = int(pilihan[0])
        return self._tampil[indeks] if indeks < len(self._tampil) else None

    def kosongkan_pilihan(self):
        for item in self.tabel.selection():
            self.tabel.selection_remove(item)

    def _saat_pilih(self, _event=None):
        if self.on_pilih:
            self.on_pilih(self.dipilih())


class TabelView(Halaman):
    """Halaman hanya-baca: judul + tabel + tombol Refresh."""

    def __init__(self, master, judul, kolom, loader, ke_baris,
                 subjudul=None, tag_fn=None):
        super().__init__(master, judul, subjudul)

        self.loader = loader

        self.tabel_data = TabelData(
            self.body, kolom, ke_baris, tag_fn=tag_fn
        )
        self.tabel_data.pack(fill="both", expand=True)

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self.refresh_data()

    def refresh_data(self):
        try:
            self.tabel_data.set_data(self.loader() or [])

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def dipilih(self):
        return self.tabel_data.dipilih()
