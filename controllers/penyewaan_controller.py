from datetime import date

from controllers.akses import (
    Session, wajib_role, ADMIN, PELANGGAN, PEMILIK
)
from models.penyewaanModel import PenyewaanModel


class PenyewaanController:

    def __init__(self):
        self.model = PenyewaanModel()

    # READ: seluruh data penyewaan (admin & pemilik)
    @wajib_role(ADMIN, PEMILIK)
    def daftar(self):
        return self.model.get_all_penyewaan()

    # READ: riwayat milik pelanggan yang sedang login
    @wajib_role(PELANGGAN)
    def daftar_saya(self):
        return self.model.get_penyewaan_pelanggan(Session.id_user())

    # READ: kendaraan yang tersedia (untuk form sewa pelanggan)
    @wajib_role(PELANGGAN)
    def daftar_kendaraan_tersedia(self):
        return self.model.get_kendaraan_tersedia()

    # CREATE: hanya pelanggan; pelanggan_id diambil dari akun login
    @wajib_role(PELANGGAN)
    def buat_sendiri(
        self, kendaraan_id, tanggal_mulai, tanggal_kembali
    ):
        if date.fromisoformat(tanggal_mulai) < date.today():
            raise ValueError(
                "Tanggal mulai tidak boleh sebelum hari ini."
            )

        return self.model.create_penyewaan(
            Session.id_user(),
            kendaraan_id,
            tanggal_mulai,
            tanggal_kembali
        )

    # ADMIN: membatalkan penyewaan (belum dibayar & belum dikembalikan)
    @wajib_role(ADMIN)
    def batalkan(self, penyewaan_id):
        return self.model.batalkan_penyewaan(penyewaan_id)
