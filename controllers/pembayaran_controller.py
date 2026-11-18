from controllers.akses import (
    Session, wajib_role, ADMIN, PELANGGAN, PEMILIK
)
from models.pembayaranModel import PembayaranModel


class PembayaranController:

    def __init__(self):
        self.model = PembayaranModel()

    @wajib_role(ADMIN, PEMILIK)
    def daftar(self):
        return self.model.get_all_pembayaran()

    @wajib_role(PELANGGAN)
    def daftar_saya(self):
        return self.model.get_all_pembayaran(Session.id_user())

    @wajib_role(PELANGGAN)
    def bayar(self, pembayaran_id, metode):
        return self.model.bayar(
            pembayaran_id,
            Session.id_user(),
            metode
        )

    @wajib_role(ADMIN)
    def ubah_status(self, pembayaran_id, status):
        return self.model.ubah_status(pembayaran_id, status)
