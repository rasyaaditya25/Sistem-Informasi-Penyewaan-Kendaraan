from models.kendaraanModel import KendaraanModel


class KendaraanController:

    def __init__(self):
        self.model = KendaraanModel()

    def daftar(self):
        return self.model.get_all_kendaraan()

    def tambah(self, jenis, merek, nomor_polisi, tarif_harian):
        return self.model.create_kendaraan(
            jenis, merek, nomor_polisi, tarif_harian
        )

    def ubah_status(self, kendaraan_id, status):
        return self.model.update_status(kendaraan_id, status)

    def hapus(self, kendaraan_id):
        return self.model.delete_kendaraan(kendaraan_id)