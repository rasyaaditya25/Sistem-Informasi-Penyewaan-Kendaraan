from models.penyewaanModel import PenyewaanModel


class PenyewaanController:

    def __init__(self):
        self.model = PenyewaanModel()

    def daftar(self):
        return self.model.get_all_penyewaan()

    def buat(self, pelanggan_id, kendaraan_id, tanggal_mulai, tanggal_kembali):
        return self.model.create_penyewaan(
            pelanggan_id, kendaraan_id, tanggal_mulai, tanggal_kembali
        )