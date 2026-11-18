import customtkinter as ctk
from tkinter import messagebox

from views.shared import theme
from views.shared.komponen import (
    Halaman, TabelData, kartu, tombol, label_form, rupiah
)


class KendaraanAdminView(Halaman):
    """Admin mengelola data kendaraan: tambah, ubah status, hapus."""

    def __init__(self, master, kendaraan_controller):
        super().__init__(
            master, "Kelola Data Kendaraan",
            "Tambah kendaraan baru, ubah status, atau hapus kendaraan."
        )

        self.controller = kendaraan_controller

        self.body.grid_columnconfigure(0, weight=0, minsize=310)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self._buat_form()

        self.tabel_data = TabelData(
            self.body,
            [
                ("id", "ID", 45),
                ("jenis", "Jenis", 80),
                ("merek", "Merek", 180, "w"),
                ("nopol", "No. Polisi", 120),
                ("tarif", "Tarif / Hari", 120),
                ("status", "Status", 100),
            ],
            lambda k: (
                k["id"], k["jenis"], k["merek"], k["nomor_polisi"],
                rupiah(k["tarif_harian"]), k["status"]
            ),
            judul="Daftar Kendaraan",
            tag_fn=lambda k: k["status"],
            on_pilih=self.pilih_kendaraan
        )
        self.tabel_data.grid(row=0, column=1, sticky="nsew")

        tombol(
            self.tabel_data.toolbar, "Muat Ulang", self.refresh_data,
            gaya="netral", width=100, height=32
        ).pack(side="left", padx=(8, 0))

        self.refresh_data()

    def _buat_form(self):
        form = kartu(self.body)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ctk.CTkLabel(
            form, text="Form Kendaraan", font=theme.F_SECTION,
            text_color=theme.TEKS
        ).pack(anchor="w", padx=18, pady=(18, 8))

        label_form(form, "Jenis Kendaraan").pack(fill="x", padx=18)
        self.combo_jenis = ctk.CTkComboBox(
            form, values=["Mobil", "Motor"], state="readonly", height=36
        )
        self.combo_jenis.set("Mobil")
        self.combo_jenis.pack(fill="x", padx=18, pady=(3, 10))

        label_form(form, "Merek / Model").pack(fill="x", padx=18)
        self.entry_merek = ctk.CTkEntry(
            form, height=36, placeholder_text="Contoh: Toyota Avanza"
        )
        self.entry_merek.pack(fill="x", padx=18, pady=(3, 10))

        label_form(form, "Nomor Polisi").pack(fill="x", padx=18)
        self.entry_nopol = ctk.CTkEntry(
            form, height=36, placeholder_text="Contoh: DD 1001 AB"
        )
        self.entry_nopol.pack(fill="x", padx=18, pady=(3, 10))

        label_form(form, "Tarif Harian (Rp)").pack(fill="x", padx=18)
        self.entry_tarif = ctk.CTkEntry(
            form, height=36, placeholder_text="Contoh: 350000"
        )
        self.entry_tarif.pack(fill="x", padx=18, pady=(3, 12))

        tombol(
            form, "+ Tambah Kendaraan", self.tambah_kendaraan,
            gaya="sukses"
        ).pack(fill="x", padx=18, pady=(2, 14))

        ctk.CTkFrame(form, fg_color=theme.GARIS, height=1).pack(
            fill="x", padx=18, pady=(0, 12)
        )

        label_form(form, "Ubah Status Kendaraan Terpilih").pack(
            fill="x", padx=18
        )
        self.combo_status = ctk.CTkComboBox(
            form, values=["Tersedia", "Perawatan"],
            state="readonly", height=36
        )
        self.combo_status.set("Tersedia")
        self.combo_status.pack(fill="x", padx=18, pady=(3, 8))

        tombol(
            form, "Simpan Status", self.update_status_kendaraan
        ).pack(fill="x", padx=18, pady=(0, 6))

        tombol(
            form, "Hapus Kendaraan", self.hapus_kendaraan, gaya="bahaya"
        ).pack(fill="x", padx=18, pady=(0, 6))

        tombol(
            form, "Bersihkan Form", self.bersihkan_form, gaya="netral"
        ).pack(fill="x", padx=18, pady=(0, 18))

    # ---------------------------------------------------------

    def refresh_data(self):
        try:
            self.tabel_data.set_data(self.controller.daftar() or [])

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memuat Data", str(exc), parent=self
            )

    def pilih_kendaraan(self, kendaraan):
        if not kendaraan:
            return

        self.combo_jenis.set(kendaraan.get("jenis") or "Mobil")

        self.entry_merek.delete(0, "end")
        self.entry_merek.insert(0, kendaraan.get("merek") or "")

        self.entry_nopol.delete(0, "end")
        self.entry_nopol.insert(0, kendaraan.get("nomor_polisi") or "")

        self.entry_tarif.delete(0, "end")
        self.entry_tarif.insert(
            0, str(int(float(kendaraan.get("tarif_harian") or 0)))
        )

        # "Disewa" diatur otomatis oleh penyewaan, tidak ada di pilihan
        if kendaraan.get("status") in ("Tersedia", "Perawatan"):
            self.combo_status.set(kendaraan["status"])

    def tambah_kendaraan(self):
        try:
            jenis = self.combo_jenis.get().strip()
            merek = self.entry_merek.get().strip()
            nopol = self.entry_nopol.get().strip()

            try:
                tarif = int(self.entry_tarif.get().strip())
            except ValueError:
                raise ValueError("Tarif harian harus berupa angka bulat.")

            if not merek or not nopol:
                raise ValueError("Merek dan nomor polisi wajib diisi.")

            if tarif <= 0:
                raise ValueError("Tarif harian harus lebih dari 0.")

            hasil = self.controller.tambah(jenis, merek, nopol, tarif)

            if hasil is False:
                raise ValueError("Kendaraan gagal ditambahkan.")

            messagebox.showinfo(
                "Berhasil", "Kendaraan berhasil ditambahkan.", parent=self
            )
            self.bersihkan_form()
            self.refresh_data()

        except ValueError as exc:
            messagebox.showwarning(
                "Validasi Data", str(exc), parent=self
            )

        except Exception as exc:
            messagebox.showerror(
                "Tidak Dapat Menambah Kendaraan", str(exc), parent=self
            )

    def update_status_kendaraan(self):
        kendaraan = self.tabel_data.dipilih()

        if not kendaraan:
            messagebox.showwarning(
                "Pilih Kendaraan",
                "Pilih kendaraan di tabel terlebih dahulu.",
                parent=self
            )
            return

        status = self.combo_status.get().strip()

        if not messagebox.askyesno(
            "Konfirmasi",
            f"Ubah status {kendaraan['merek']} menjadi '{status}'?",
            parent=self
        ):
            return

        try:
            hasil = self.controller.ubah_status(kendaraan["id"], status)

            if hasil is False:
                raise ValueError("Status kendaraan gagal diperbarui.")

            self.refresh_data()
            messagebox.showinfo(
                "Berhasil", "Status kendaraan berhasil diperbarui.",
                parent=self
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal Memperbarui Status", str(exc), parent=self
            )

    def hapus_kendaraan(self):
        kendaraan = self.tabel_data.dipilih()

        if not kendaraan:
            messagebox.showwarning(
                "Pilih Kendaraan",
                "Pilih kendaraan di tabel yang ingin dihapus.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Konfirmasi",
            f"Hapus {kendaraan['merek']} ({kendaraan['nomor_polisi']})?\n"
            "Kendaraan harus berstatus Tersedia dan belum pernah disewa.",
            parent=self
        ):
            return

        try:
            if not self.controller.hapus(kendaraan["id"]):
                raise ValueError(
                    "Kendaraan tidak dapat dihapus. Pastikan statusnya "
                    "Tersedia dan tidak memiliki riwayat penyewaan."
                )

            self.bersihkan_form()
            self.refresh_data()
            messagebox.showinfo(
                "Berhasil", "Kendaraan berhasil dihapus.", parent=self
            )

        except Exception as exc:
            messagebox.showerror("Gagal Menghapus", str(exc), parent=self)

    def bersihkan_form(self):
        self.combo_jenis.set("Mobil")
        self.entry_merek.delete(0, "end")
        self.entry_nopol.delete(0, "end")
        self.entry_tarif.delete(0, "end")
        self.combo_status.set("Tersedia")
        self.tabel_data.kosongkan_pilihan()
