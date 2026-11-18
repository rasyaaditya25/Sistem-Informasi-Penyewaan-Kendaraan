from controllers.akses import wajib_role, ADMIN, PELANGGAN, PEMILIK
from models.kendaraanModel import KendaraanModel


class KendaraanController:

    def __init__(self):
        self.model = KendaraanModel()

    # READ (semua role boleh melihat)
    @wajib_role(ADMIN, PELANGGAN, PEMILIK)
    def daftar(self):
        return self.model.get_all_kendaraan()

    # CREATE
    @wajib_role(ADMIN)
    def tambah(self, jenis, merek, nomor_polisi, tarif_harian):
        return self.model.create_kendaraan(
            jenis,
            merek,
            nomor_polisi,
            tarif_harian
        )

    # UPDATE STATUS
    @wajib_role(ADMIN)
    def ubah_status(self, kendaraan_id, status):
        return self.model.update_status(
            kendaraan_id,
            status
        )

    # DELETE
    @wajib_role(ADMIN)
    def hapus(self, kendaraan_id):
        return self.model.delete_kendaraan(kendaraan_id)
