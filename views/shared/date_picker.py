import calendar
from datetime import date

import customtkinter as ctk

from views.shared import theme

NAMA_BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
NAMA_HARI = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


class DatePicker(ctk.CTkFrame):
    """
    Input tanggal dengan popup kalender.
    Nilai selalu berformat YYYY-MM-DD dan tidak bisa diketik manual.

    - get()            -> str "YYYY-MM-DD" atau "" jika kosong
    - get_date()       -> datetime.date atau None
    - set(value)       -> value berupa date atau str "YYYY-MM-DD"
    - clear()          -> mengosongkan nilai
    - set_min_date(d)  -> tanggal sebelum d tidak bisa dipilih
    - set_max_date(d)  -> tanggal setelah d tidak bisa dipilih
    - command          -> fungsi tanpa argumen, dipanggil saat tanggal berubah
    """

    def __init__(self, master, width=250, command=None,
                 placeholder="Pilih tanggal", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.command = command
        self._value = None
        self._min_date = None
        self._max_date = None
        self._popup = None
        self._view_year = date.today().year
        self._view_month = date.today().month

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self, width=width, placeholder_text=placeholder
        )
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.configure(state="readonly")
        self.entry.bind("<Button-1>", self._buka_popup)

        self.tombol = ctk.CTkButton(
            self, text="Pilih", width=60, command=self._buka_popup
        )
        self.tombol.grid(row=0, column=1, padx=(6, 0))

    # ---------------------------------------------------------
    # API PUBLIK
    # ---------------------------------------------------------

    def get(self):
        return self._value.isoformat() if self._value else ""

    def get_date(self):
        return self._value

    def set(self, value):
        if isinstance(value, str):
            value = date.fromisoformat(value) if value else None

        self._value = value
        self._tampilkan()

        if value:
            self._view_year = value.year
            self._view_month = value.month

    def clear(self):
        self._value = None
        self._tampilkan()

    def set_min_date(self, min_date):
        self._min_date = min_date

    def set_max_date(self, max_date):
        self._max_date = max_date

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    def _boleh(self, tanggal):
        if self._min_date is not None and tanggal < self._min_date:
            return False
        if self._max_date is not None and tanggal > self._max_date:
            return False
        return True

    def _tampilkan(self):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        if self._value:
            self.entry.insert(0, self._value.isoformat())
        self.entry.configure(state="readonly")

    def _buka_popup(self, event=None):
        if self._popup is not None and self._popup.winfo_exists():
            self._popup.focus_force()
            return "break"

        popup = ctk.CTkToplevel(self)
        popup.title("Pilih Tanggal")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        self._popup = popup

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        popup.geometry(f"+{x}+{y}")

        self._gambar_kalender()

        # grab harus ditunda sampai jendela benar-benar tampil
        popup.after(150, self._ambil_fokus)
        return "break"

    def _ambil_fokus(self):
        try:
            if self._popup is not None and self._popup.winfo_exists():
                self._popup.grab_set()
                self._popup.focus_force()
        except Exception:
            pass

    def _tutup_popup(self):
        if self._popup is not None and self._popup.winfo_exists():
            self._popup.grab_release()
            self._popup.destroy()
        self._popup = None

    def _gambar_kalender(self):
        popup = self._popup

        for widget in popup.winfo_children():
            widget.destroy()

        # Header bulan
        header = ctk.CTkFrame(popup, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(
            header, text="<", width=32,
            command=lambda: self._ganti_bulan(-1)
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"{NAMA_BULAN[self._view_month]} {self._view_year}",
            font=("Arial", 14, "bold")
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            header, text=">", width=32,
            command=lambda: self._ganti_bulan(1)
        ).pack(side="right")

        # Grid hari
        grid = ctk.CTkFrame(popup, fg_color="transparent")
        grid.pack(padx=10, pady=5)

        for kolom, nama in enumerate(NAMA_HARI):
            ctk.CTkLabel(
                grid, text=nama, width=36,
                font=("Arial", 11, "bold")
            ).grid(row=0, column=kolom, padx=1, pady=1)

        hari_ini = date.today()
        minggu = calendar.Calendar(firstweekday=0).monthdayscalendar(
            self._view_year, self._view_month
        )

        for baris, pekan in enumerate(minggu, start=1):
            for kolom, hari in enumerate(pekan):
                if hari == 0:
                    continue

                tgl = date(self._view_year, self._view_month, hari)
                nonaktif = not self._boleh(tgl)

                if tgl == self._value:
                    warna, teks = theme.UTAMA, "white"
                elif tgl == hari_ini:
                    warna, teks = theme.PILIH, theme.TEKS
                else:
                    warna, teks = "transparent", theme.TEKS

                ctk.CTkButton(
                    grid,
                    text=str(hari),
                    width=36,
                    height=30,
                    fg_color=warna,
                    text_color=teks,
                    text_color_disabled="#A9B4C6",
                    hover_color=theme.PILIH,
                    state="disabled" if nonaktif else "normal",
                    command=lambda t=tgl: self._pilih(t)
                ).grid(row=baris, column=kolom, padx=1, pady=1)

        # Tombol bawah
        bawah = ctk.CTkFrame(popup, fg_color="transparent")
        bawah.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            bawah, text="Hari Ini", width=80,
            command=lambda: self._pilih(hari_ini),
            state="normal" if self._boleh(hari_ini) else "disabled"
        ).pack(side="left")

        ctk.CTkButton(
            bawah, text="Tutup", width=80,
            fg_color=theme.NETRAL, hover_color=theme.NETRAL_HOVER,
            command=self._tutup_popup
        ).pack(side="right")

    def _ganti_bulan(self, arah):
        bulan = self._view_month + arah
        tahun = self._view_year

        if bulan < 1:
            bulan, tahun = 12, tahun - 1
        elif bulan > 12:
            bulan, tahun = 1, tahun + 1

        self._view_month, self._view_year = bulan, tahun
        self._gambar_kalender()

    def _pilih(self, tanggal):
        self.set(tanggal)
        self._tutup_popup()

        if self.command:
            self.command()
