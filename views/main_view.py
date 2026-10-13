import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, timedelta


# =====================================================================
# FUNGSI BANTU (HELPER)
# =====================================================================
def rupiah(nilai):
    """Format angka menjadi 'Rp 1.000.000'."""
    try:
        return "Rp {:,.0f}".format(float(nilai or 0)).replace(",", ".")
    except (TypeError, ValueError):
        return "Rp 0"


def tanggal_hari_ini():
    """Tanggal hari ini dalam format YYYY-MM-DD."""
    return date.today().isoformat()


# =====================================================================
# KELAS UTAMA VIEW
# =====================================================================
class PenyewaanKendaraanView(ctk.CTk):

    # -----------------------------------------------------------------
    # INISIALISASI
    # -----------------------------------------------------------------
    def __init__(
        self,
        kendaraan_controller,
        pelanggan_controller,
        penyewaan_controller,
        pengembalian_controller,
    ):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        super().__init__()

        # Controller (diterima dari main.py)
        self.kendaraan_controller = kendaraan_controller
        self.pelanggan_controller = pelanggan_controller
        self.penyewaan_controller = penyewaan_controller
        self.pengembalian_controller = pengembalian_controller

        # Pengaturan jendela
        self.title("Sistem Penyewaan Kendaraan")
        self.geometry("1200x760")
        self.minsize(1050, 650)

        # Penyimpanan data
        self.kendaraan_data = []
        self.pelanggan_data = []
        self.penyewaan_data = []
        self.pengembalian_data = []

        # Pemetaan teks dropdown -> data
        self.kendaraan_map = {}
        self.pelanggan_map = {}
        self.sewa_map = {}

        # Bangun tampilan
        self._setup_style()
        self._setup_layout()
        self.refresh_all()

    # -----------------------------------------------------------------
    # SETUP TAMPILAN UTAMA
    # -----------------------------------------------------------------
    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------- Header ----------
        header = ctk.CTkFrame(self, corner_radius=12)
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        ctk.CTkLabel(
            header, text="Sistem Penyewaan Kendaraan",
            font=("Arial", 23, "bold"),
        ).pack(side="left", padx=18, pady=14)

        # ---------- Tab ----------
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=16, pady=(8, 16), sticky="nsew")
        self.tab_kendaraan = self.tabview.add("Kendaraan")
        self.tab_pelanggan = self.tabview.add("Pelanggan")
        self.tab_penyewaan = self.tabview.add("Penyewaan")
        self.tab_pengembalian = self.tabview.add("Pengembalian")

        self._setup_tab_kendaraan()
        self._setup_tab_pelanggan()
        self._setup_tab_penyewaan()
        self._setup_tab_pengembalian()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview", rowheight=29, font=("Arial", 10),
                        background="#FFFFFF", fieldbackground="#FFFFFF",
                        foreground="#202020")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), padding=7)
        style.map("Treeview",
                  background=[("selected", "#B9D7F5")],
                  foreground=[("selected", "#111111")])

    # =================================================================
    # KOMPONEN UI REUSABLE
    # =================================================================
    def _buat_tabel(self, parent, kolom, judul, lebar, anchors=None):
        """Membuat frame berisi Treeview + scrollbar."""
        wrap = ctk.CTkFrame(parent)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(0, weight=1)

        # ---------- Treeview + scrollbar ----------
        tree_frame = ctk.CTkFrame(wrap)
        tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        tree = ttk.Treeview(tree_frame, columns=kolom, show="headings")
        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        # ---------- Kolom ----------
        for i, key in enumerate(kolom):
            tree.heading(key, text=judul[i])
            tree.column(key, width=lebar[i], anchor=(anchors or {}).get(key, "w"),
                        minwidth=45, stretch=True)

        # ---------- Warna baris & status ----------
        tree.tag_configure("odd", background="#F0F6FC")
        tree.tag_configure("even", background="#FFFFFF")
        tree.tag_configure("Tersedia", foreground="#147D3F")
        tree.tag_configure("Disewa", foreground="#B45309")
        tree.tag_configure("Perawatan", foreground="#B91C1C")
        tree.tag_configure("Berjalan", foreground="#147D3F")
        tree.tag_configure("Selesai", foreground="#555555")
        tree.tag_configure("late", foreground="#B91C1C")
        return wrap, tree

    def _isi_tabel(self, tree, rows):
        """Mengisi Treeview dengan data."""
        tree.delete(*tree.get_children())
        for i, row in enumerate(rows):
            values = row["values"]
            tags = ["even" if i % 2 == 0 else "odd"]
            if row.get("status_tag"):
                tags.append(row["status_tag"])
            if row.get("late"):
                tags.append("late")
            tree.insert("", "end", iid=str(row.get("iid", i)),
                        values=values, tags=tuple(tags))

    def _form_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, anchor="w").pack(fill="x", padx=15, pady=(8, 0))

    # =================================================================
    # SETUP TAB: KENDARAAN
    # =================================================================
    def _setup_tab_kendaraan(self):
        tab = self.tab_kendaraan
        tab.grid_columnconfigure(0, weight=0, minsize=285)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # ---------- Form ----------
        form = ctk.CTkFrame(tab)
        form.grid(row=0, column=0, padx=(8, 5), pady=8, sticky="nsew")
        ctk.CTkLabel(form, text="Data Kendaraan", font=("Arial", 17, "bold")).pack(pady=15)

        self.combo_jenis = ctk.CTkComboBox(form, values=["Mobil", "Motor"], state="readonly")
        self.combo_jenis.set("Mobil")
        self.combo_jenis.pack(fill="x", padx=15, pady=7)

        self.entry_merek = ctk.CTkEntry(form, placeholder_text="Merek / model kendaraan")
        self.entry_merek.pack(fill="x", padx=15, pady=7)
        self.entry_nopol = ctk.CTkEntry(form, placeholder_text="Nomor polisi")
        self.entry_nopol.pack(fill="x", padx=15, pady=7)
        self.entry_tarif = ctk.CTkEntry(form, placeholder_text="Tarif harian (angka)")
        self.entry_tarif.pack(fill="x", padx=15, pady=7)

        # ---------- Tombol ----------
        ctk.CTkButton(form, text="＋ Tambah Kendaraan", command=self.tambah_kendaraan,
                      fg_color="#16803D").pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkButton(form, text="Hapus Kendaraan Terpilih", command=self.hapus_kendaraan,
                      fg_color="#B42318").pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(form, text="Bersihkan Form", command=self.bersihkan_form_kendaraan,
                      fg_color="gray").pack(fill="x", padx=15, pady=5)

        # ---------- Tabel ----------
        kolom = ("id", "jenis", "merek", "nopol", "tarif", "status")
        judul = ("ID", "Jenis", "Merek", "No. Polisi", "Tarif/Hari", "Status")
        lebar = (45, 70, 150, 105, 115, 95)
        self.frame_tabel_kendaraan, self.tabel_kendaraan = self._buat_tabel(
            tab, kolom, judul, lebar, {"id": "center", "tarif": "e", "status": "center"})
        self.frame_tabel_kendaraan.grid(row=0, column=1, padx=(5, 8), pady=8, sticky="nsew")

    # =================================================================
    # SETUP TAB: PELANGGAN
    # =================================================================
    def _setup_tab_pelanggan(self):
        tab = self.tab_pelanggan
        tab.grid_columnconfigure(0, weight=0, minsize=285)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # ---------- Form ----------
        form = ctk.CTkFrame(tab)
        form.grid(row=0, column=0, padx=(8, 5), pady=8, sticky="nsew")
        ctk.CTkLabel(form, text="Data Pelanggan", font=("Arial", 17, "bold")).pack(pady=15)

        self.entry_nama_pelanggan = ctk.CTkEntry(form, placeholder_text="Nama lengkap")
        self.entry_nama_pelanggan.pack(fill="x", padx=15, pady=7)
        self.entry_identitas = ctk.CTkEntry(form, placeholder_text="Nomor identitas / KTP")
        self.entry_identitas.pack(fill="x", padx=15, pady=7)
        self.entry_telepon = ctk.CTkEntry(form, placeholder_text="Nomor telepon")
        self.entry_telepon.pack(fill="x", padx=15, pady=7)

        # ---------- Tombol ----------
        ctk.CTkButton(form, text="＋ Tambah Pelanggan", command=self.tambah_pelanggan,
                      fg_color="#16803D").pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkButton(form, text="Bersihkan Form", command=self.bersihkan_form_pelanggan,
                      fg_color="gray").pack(fill="x", padx=15, pady=5)

        # ---------- Tabel ----------
        kolom = ("id", "nama", "identitas", "telepon")
        judul = ("ID", "Nama Pelanggan", "No. Identitas", "No. Telepon")
        lebar = (45, 180, 140, 120)
        self.frame_tabel_pelanggan, self.tabel_pelanggan = self._buat_tabel(
            tab, kolom, judul, lebar, {"id": "center"})
        self.frame_tabel_pelanggan.grid(row=0, column=1, padx=(5, 8), pady=8, sticky="nsew")

    # =================================================================
    # SETUP TAB: PENYEWAAN
    # =================================================================
    def _setup_tab_penyewaan(self):
        tab = self.tab_penyewaan
        tab.grid_columnconfigure(0, weight=0, minsize=310)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # ---------- Form ----------
        form = ctk.CTkScrollableFrame(tab, width=275)
        form.grid(row=0, column=0, padx=(8, 5), pady=8, sticky="nsew")
        ctk.CTkLabel(form, text="Transaksi Penyewaan", font=("Arial", 17, "bold")).pack(pady=12)

        # Dropdown pelanggan & kendaraan
        self._form_label(form, "Pelanggan")
        self.combo_sewa_pelanggan = ctk.CTkComboBox(
            form, values=[""], state="readonly",
            command=lambda _v: self.hitung_estimasi())
        self.combo_sewa_pelanggan.pack(fill="x", padx=15, pady=6)

        self._form_label(form, "Kendaraan tersedia")
        self.combo_sewa_kendaraan = ctk.CTkComboBox(
            form, values=[""], state="readonly",
            command=lambda _v: self.hitung_estimasi())
        self.combo_sewa_kendaraan.pack(fill="x", padx=15, pady=6)

        # Input tanggal
        self._form_label(form, "Tanggal mulai (YYYY-MM-DD)")
        self.entry_tgl_mulai = ctk.CTkEntry(form)
        self.entry_tgl_mulai.pack(fill="x", padx=15, pady=6)

        self._form_label(form, "Tanggal kembali (YYYY-MM-DD)")
        self.entry_tgl_kembali_rencana = ctk.CTkEntry(form)
        self.entry_tgl_kembali_rencana.pack(fill="x", padx=15, pady=6)

        # Tombol durasi cepat
        quick = ctk.CTkFrame(form, fg_color="transparent")
        quick.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(quick, text="Durasi cepat:").pack(anchor="w", padx=5)
        buttons = ctk.CTkFrame(quick, fg_color="transparent")
        buttons.pack(fill="x")
        for days in (1, 3, 7):
            ctk.CTkButton(buttons, text=f"{days} hari", width=70,
                          command=lambda d=days: self.set_durasi(d)
                          ).pack(side="left", expand=True, padx=3, pady=4)

        # Label estimasi
        self.label_estimasi = ctk.CTkLabel(
            form, text="Estimasi biaya: Rp 0",
            font=("Arial", 14, "bold"), text_color="#16803D")
        self.label_estimasi.pack(fill="x", padx=15, pady=(10, 2))
        self.label_denda_estimasi = ctk.CTkLabel(
            form, text="Denda per hari terlambat: Rp 0",
            text_color="#B45309", wraplength=250)
        self.label_denda_estimasi.pack(fill="x", padx=15, pady=2)

        # Tombol aksi
        ctk.CTkButton(form, text="＋ Buat Penyewaan", command=self.buat_penyewaan,
                      fg_color="#16803D").pack(fill="x", padx=15, pady=(14, 5))
        ctk.CTkButton(form, text="Bersihkan Form", command=self.bersihkan_form_sewa,
                      fg_color="gray").pack(fill="x", padx=15, pady=5)

        # Nilai awal & binding hitung otomatis
        self.entry_tgl_mulai.insert(0, tanggal_hari_ini())
        self.entry_tgl_kembali_rencana.insert(0, tanggal_hari_ini())
        self.entry_tgl_mulai.bind("<KeyRelease>", lambda _e: self.hitung_estimasi())
        self.entry_tgl_kembali_rencana.bind("<KeyRelease>", lambda _e: self.hitung_estimasi())

        # ---------- Tabel ----------
        kolom = ("id", "pelanggan", "kendaraan", "mulai", "kembali", "total", "status")
        judul = ("ID", "Pelanggan", "Kendaraan", "Tgl Mulai", "Tgl Kembali", "Total Biaya", "Status")
        lebar = (42, 125, 165, 95, 100, 120, 85)
        anchors = {"id": "center", "mulai": "center", "kembali": "center",
                   "total": "e", "status": "center"}
        self.frame_tabel_penyewaan, self.tabel_penyewaan = self._buat_tabel(
            tab, kolom, judul, lebar, anchors)
        self.frame_tabel_penyewaan.grid(row=0, column=1, padx=(5, 8), pady=8, sticky="nsew")

    # =================================================================
    # SETUP TAB: PENGEMBALIAN
    # =================================================================
    def _setup_tab_pengembalian(self):
        tab = self.tab_pengembalian
        tab.grid_columnconfigure(0, weight=0, minsize=310)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # ---------- Form ----------
        form = ctk.CTkFrame(tab)
        form.grid(row=0, column=0, padx=(8, 5), pady=8, sticky="nsew")
        ctk.CTkLabel(form, text="Proses Pengembalian", font=("Arial", 17, "bold")).pack(pady=15)

        ctk.CTkLabel(form, text="Pilih penyewaan yang masih berjalan", anchor="w",
                     wraplength=250).pack(fill="x", padx=15, pady=(5, 0))
        self.combo_kembali_sewa = ctk.CTkComboBox(
            form, values=[""], state="readonly",
            command=lambda _v: self.hitung_denda_pengembalian())
        self.combo_kembali_sewa.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(form, text="Tanggal kembali aktual (YYYY-MM-DD)", anchor="w"
                     ).pack(fill="x", padx=15, pady=(8, 0))
        self.entry_tgl_kembali_real = ctk.CTkEntry(form)
        self.entry_tgl_kembali_real.pack(fill="x", padx=15, pady=8)
        self.entry_tgl_kembali_real.insert(0, tanggal_hari_ini())
        self.entry_tgl_kembali_real.bind("<KeyRelease>", lambda _e: self.hitung_denda_pengembalian())

        self.label_denda_aktual = ctk.CTkLabel(
            form, text="Estimasi denda: Rp 0",
            font=("Arial", 14, "bold"), text_color="#B45309")
        self.label_denda_aktual.pack(fill="x", padx=15, pady=10)

        # ---------- Tombol ----------
        ctk.CTkButton(form, text="✓ Proses Pengembalian", command=self.proses_pengembalian,
                      fg_color="#1D4ED8").pack(fill="x", padx=15, pady=(12, 5))
        ctk.CTkButton(form, text="Bersihkan Tanggal", command=self.reset_tanggal_kembali,
                      fg_color="gray").pack(fill="x", padx=15, pady=5)

        # ---------- Tabel ----------
        kolom = ("id", "sewa_id", "pelanggan", "kendaraan", "tanggal", "denda")
        judul = ("ID", "ID Sewa", "Pelanggan", "Kendaraan", "Tgl Kembali", "Denda")
        lebar = (42, 65, 145, 165, 110, 120)
        anchors = {"id": "center", "sewa_id": "center", "tanggal": "center", "denda": "e"}
        self.frame_tabel_pengembalian, self.tabel_pengembalian = self._buat_tabel(
            tab, kolom, judul, lebar, anchors)
        self.frame_tabel_pengembalian.grid(row=0, column=1, padx=(5, 8), pady=8, sticky="nsew")

    # =================================================================
    # REFRESH DATA & DROPDOWN
    # =================================================================
    def refresh_all(self):
        """Memuat ulang semua data dari controller lalu render ulang tampilan."""
        try:
            self.kendaraan_data = self.kendaraan_controller.daftar() or []
            self.pelanggan_data = self.pelanggan_controller.daftar() or []
            self.penyewaan_data = self.penyewaan_controller.daftar() or []
            self.pengembalian_data = self.pengembalian_controller.daftar() or []

            self._render_kendaraan()
            self._render_pelanggan()
            self._render_penyewaan()
            self._render_pengembalian()
            self._refresh_dropdowns()
        except Exception as exc:
            messagebox.showerror("Gagal memuat data", str(exc), parent=self)

    def _refresh_dropdowns(self):
        """Mengisi ulang pilihan dropdown pada tab Penyewaan & Pengembalian."""
        self.kendaraan_map = {
            f'{k["id"]} | {k.get("jenis", "")} {k.get("merek", "")} - '
            f'{k.get("nomor_polisi", "")} ({rupiah(k.get("tarif_harian"))}/hari)': k
            for k in self.kendaraan_data if k.get("status") == "Tersedia"
        }
        self.pelanggan_map = {
            f'{p["id"]} | {p.get("nama", "")} - {p.get("no_telepon", "")}': p
            for p in self.pelanggan_data
        }
        self.sewa_map = {
            f'{s["id"]} | {s.get("nama_pelanggan", "")} - {s.get("merek", "")} '
            f'{s.get("nomor_polisi", "")} (kembali {s.get("tanggal_rencana_kembali", "")})': s
            for s in self.penyewaan_data if s.get("status") == "Berjalan"
        }

        self.combo_sewa_pelanggan.configure(values=list(self.pelanggan_map) or [""])
        self.combo_sewa_kendaraan.configure(values=list(self.kendaraan_map) or [""])
        self.combo_kembali_sewa.configure(values=list(self.sewa_map) or [""])

        # Reset pilihan yang sudah tidak valid
        if self.combo_sewa_pelanggan.get() not in self.pelanggan_map:
            self.combo_sewa_pelanggan.set("")
        if self.combo_sewa_kendaraan.get() not in self.kendaraan_map:
            self.combo_sewa_kendaraan.set("")
        if self.combo_kembali_sewa.get() not in self.sewa_map:
            self.combo_kembali_sewa.set("")

        self.hitung_estimasi()
        self.hitung_denda_pengembalian()

    # =================================================================
    # RENDER TABEL
    # =================================================================
    def _render_kendaraan(self):
        rows = [
            {"iid": k["id"],
             "values": (k.get("id"), k.get("jenis"), k.get("merek"), k.get("nomor_polisi"),
                        rupiah(k.get("tarif_harian")), k.get("status")),
             "status_tag": k.get("status")}
            for k in self.kendaraan_data
        ]
        self._isi_tabel(self.tabel_kendaraan, rows)

    def _render_pelanggan(self):
        rows = [
            {"iid": p["id"],
             "values": (p.get("id"), p.get("nama"),
                        p.get("no_identitas"), p.get("no_telepon"))}
            for p in self.pelanggan_data
        ]
        self._isi_tabel(self.tabel_pelanggan, rows)

    def _render_penyewaan(self):
        rows = []
        for s in self.penyewaan_data:
            kendaraan = f'{s.get("jenis", "")} {s.get("merek", "")} ({s.get("nomor_polisi", "")})'
            rows.append({
                "iid": s["id"],
                "values": (s.get("id"), s.get("nama_pelanggan"), kendaraan,
                           s.get("tanggal_mulai"), s.get("tanggal_rencana_kembali"),
                           rupiah(s.get("total_biaya")), s.get("status")),
                "status_tag": s.get("status"),
            })
        self._isi_tabel(self.tabel_penyewaan, rows)

    def _render_pengembalian(self):
        rows = []
        for p in self.pengembalian_data:
            kendaraan = f'{p.get("merek", "")} ({p.get("nomor_polisi", "")})'
            rows.append({
                "iid": p["id"],
                "values": (p.get("id"), p.get("penyewaan_id"), p.get("nama_pelanggan"),
                           kendaraan, p.get("tanggal_kembali"), rupiah(p.get("denda"))),
            })
        self._isi_tabel(self.tabel_pengembalian, rows)

    # =================================================================
    # AKSI: KENDARAAN
    # =================================================================
    def tambah_kendaraan(self):
        try:
            jenis = self.combo_jenis.get().strip()
            merek = self.entry_merek.get().strip()
            nopol = self.entry_nopol.get().strip()
            tarif = int(self.entry_tarif.get().strip())
            if not merek or not nopol:
                raise ValueError("Merek dan nomor polisi wajib diisi.")

            self.kendaraan_controller.tambah(jenis, merek, nopol, tarif)
            messagebox.showinfo("Berhasil", "Kendaraan berhasil ditambahkan.", parent=self)
            self.bersihkan_form_kendaraan()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Tidak dapat menambah kendaraan", str(exc), parent=self)

    def hapus_kendaraan(self):
        selected = self.tabel_kendaraan.selection()
        if not selected:
            messagebox.showwarning("Pilih kendaraan",
                                   "Pilih baris kendaraan yang ingin dihapus.", parent=self)
            return

        kendaraan_id = int(selected[0])
        if not messagebox.askyesno(
                "Konfirmasi",
                "Hapus kendaraan terpilih? Kendaraan harus berstatus Tersedia.",
                parent=self):
            return

        try:
            if not self.kendaraan_controller.hapus(kendaraan_id):
                raise ValueError("Kendaraan tidak dapat dihapus. Pastikan statusnya Tersedia.")
            self.refresh_all()
            messagebox.showinfo("Berhasil", "Kendaraan berhasil dihapus.", parent=self)
        except Exception as exc:
            messagebox.showerror("Gagal menghapus", str(exc), parent=self)

    def bersihkan_form_kendaraan(self):
        for entry in (self.entry_merek, self.entry_nopol, self.entry_tarif):
            entry.delete(0, "end")
        self.combo_jenis.set("Mobil")

    # =================================================================
    # AKSI: PELANGGAN
    # =================================================================
    def tambah_pelanggan(self):
        try:
            self.pelanggan_controller.tambah(
                self.entry_nama_pelanggan.get().strip(),
                self.entry_identitas.get().strip(),
                self.entry_telepon.get().strip(),
            )
            messagebox.showinfo("Berhasil", "Pelanggan berhasil ditambahkan.", parent=self)
            self.bersihkan_form_pelanggan()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Tidak dapat menambah pelanggan", str(exc), parent=self)

    def bersihkan_form_pelanggan(self):
        for entry in (self.entry_nama_pelanggan, self.entry_identitas, self.entry_telepon):
            entry.delete(0, "end")

    # =================================================================
    # AKSI: PENYEWAAN
    # =================================================================
    def _pilih_kendaraan_sewa(self):
        return self.kendaraan_map.get(self.combo_sewa_kendaraan.get())

    def set_durasi(self, days):
        """Mengisi tanggal mulai (hari ini) dan tanggal kembali sesuai durasi."""
        mulai = date.today()
        kembali = mulai + timedelta(days=days - 1)
        self.entry_tgl_mulai.delete(0, "end")
        self.entry_tgl_mulai.insert(0, mulai.isoformat())
        self.entry_tgl_kembali_rencana.delete(0, "end")
        self.entry_tgl_kembali_rencana.insert(0, kembali.isoformat())
        self.hitung_estimasi()

    def hitung_estimasi(self):
        """Menghitung estimasi biaya sewa dan denda per hari."""
        kendaraan = self._pilih_kendaraan_sewa()
        tarif = float(kendaraan.get("tarif_harian", 0)) if kendaraan else 0
        try:
            mulai = date.fromisoformat(self.entry_tgl_mulai.get().strip())
            kembali = date.fromisoformat(self.entry_tgl_kembali_rencana.get().strip())
            if kembali < mulai:
                raise ValueError()
            hari = (kembali - mulai).days + 1
            self.label_estimasi.configure(
                text=f"Estimasi biaya ({hari} hari): {rupiah(hari * tarif)}")
        except (ValueError, TypeError):
            self.label_estimasi.configure(text="Estimasi biaya: periksa tanggal")
        self.label_denda_estimasi.configure(
            text=f"Denda per hari terlambat: {rupiah(tarif)}")

    def buat_penyewaan(self):
        try:
            pelanggan = self.pelanggan_map.get(self.combo_sewa_pelanggan.get())
            kendaraan = self._pilih_kendaraan_sewa()
            if not pelanggan:
                raise ValueError("Pilih pelanggan dari dropdown.")
            if not kendaraan:
                raise ValueError("Pilih kendaraan yang berstatus Tersedia.")

            mulai = date.fromisoformat(self.entry_tgl_mulai.get().strip())
            kembali = date.fromisoformat(self.entry_tgl_kembali_rencana.get().strip())
            if kembali < mulai:
                raise ValueError("Tanggal kembali tidak boleh sebelum tanggal mulai.")

            hari = (kembali - mulai).days + 1
            total = hari * float(kendaraan.get("tarif_harian", 0))

            konfirmasi = (
                f"Pelanggan: {pelanggan.get('nama')}\n"
                f"Kendaraan: {kendaraan.get('merek')} - {kendaraan.get('nomor_polisi')}\n"
                f"Durasi: {hari} hari\n"
                f"Estimasi total: {rupiah(total)}\n\n"
                f"Buat transaksi?"
            )
            if not messagebox.askyesno("Konfirmasi penyewaan", konfirmasi, parent=self):
                return

            result = self.penyewaan_controller.buat(
                int(pelanggan["id"]), int(kendaraan["id"]),
                mulai.isoformat(), kembali.isoformat())
            if result is False:
                raise RuntimeError("Transaksi tidak tersimpan. Periksa koneksi database.")

            messagebox.showinfo("Berhasil",
                                f"Penyewaan berhasil dibuat. Total: {rupiah(total)}", parent=self)
            self.bersihkan_form_sewa()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Gagal membuat penyewaan", str(exc), parent=self)

    def bersihkan_form_sewa(self):
        self.combo_sewa_pelanggan.set("")
        self.combo_sewa_kendaraan.set("")
        self.entry_tgl_mulai.delete(0, "end")
        self.entry_tgl_mulai.insert(0, tanggal_hari_ini())
        self.entry_tgl_kembali_rencana.delete(0, "end")
        self.entry_tgl_kembali_rencana.insert(0, tanggal_hari_ini())
        self.hitung_estimasi()

    # =================================================================
    # AKSI: PENGEMBALIAN
    # =================================================================
    def _sewa_terpilih(self):
        return self.sewa_map.get(self.combo_kembali_sewa.get())

    def hitung_denda_pengembalian(self):
        """Menghitung estimasi denda berdasarkan keterlambatan."""
        try:
            sewa = self._sewa_terpilih()
            if not sewa:
                self.label_denda_aktual.configure(text="Estimasi denda: pilih penyewaan")
                return

            kembali = date.fromisoformat(self.entry_tgl_kembali_real.get().strip())
            rencana = date.fromisoformat(str(sewa["tanggal_rencana_kembali"])[:10])

            # Tarif harian tidak ada di daftar penyewaan -> ambil dari data kendaraan
            nopol = sewa.get("nomor_polisi")
            kendaraan = next(
                (k for k in self.kendaraan_data if k.get("nomor_polisi") == nopol), None)
            tarif = float(kendaraan.get("tarif_harian", 0)) if kendaraan else 0

            terlambat = max(0, (kembali - rencana).days)
            self.label_denda_aktual.configure(
                text=f"Estimasi denda: {rupiah(terlambat * tarif)} ({terlambat} hari terlambat)")
        except (ValueError, TypeError):
            self.label_denda_aktual.configure(text="Estimasi denda: periksa tanggal")

    def proses_pengembalian(self):
        try:
            sewa = self._sewa_terpilih()
            if not sewa:
                raise ValueError("Pilih penyewaan berstatus Berjalan.")

            kembali = date.fromisoformat(self.entry_tgl_kembali_real.get().strip())
            mulai = date.fromisoformat(str(sewa["tanggal_mulai"])[:10])
            if kembali < mulai:
                raise ValueError("Tanggal kembali tidak boleh sebelum tanggal mulai.")

            konfirmasi = (
                f"Transaksi #{sewa['id']}\n"
                f"Tanggal kembali: {kembali.isoformat()}\n"
                f"{self.label_denda_aktual.cget('text')}\n\n"
                f"Proses pengembalian?"
            )
            if not messagebox.askyesno("Konfirmasi pengembalian", konfirmasi, parent=self):
                return

            denda = self.pengembalian_controller.proses(int(sewa["id"]), kembali.isoformat())
            if denda is False:
                raise RuntimeError("Pengembalian tidak tersimpan. Periksa koneksi database.")

            messagebox.showinfo("Berhasil",
                                f"Pengembalian selesai. Denda: {rupiah(denda)}", parent=self)
            self.combo_kembali_sewa.set("")
            self.reset_tanggal_kembali()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Gagal memproses pengembalian", str(exc), parent=self)

    def reset_tanggal_kembali(self):
        self.entry_tgl_kembali_real.delete(0, "end")
        self.entry_tgl_kembali_real.insert(0, tanggal_hari_ini())
        self.hitung_denda_pengembalian()


# =====================================================================
# MENJALANKAN LANGSUNG (OPSIONAL, UNTUK TESTING)
# Disarankan menjalankan lewat main.py
# =====================================================================
if __name__ == "__main__":
    from controllers.kendaraan_controller import KendaraanController
    from controllers.pelanggan_controller import PelangganController
    from controllers.penyewaan_controller import PenyewaanController
    from controllers.pengembalian_controller import PengembalianController

    app = PenyewaanKendaraanView(
        KendaraanController(),
        PelangganController(),
        PenyewaanController(),
        PengembalianController(),
    )
    app.mainloop()