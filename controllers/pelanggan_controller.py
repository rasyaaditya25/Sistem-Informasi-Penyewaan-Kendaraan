from models.pelangganModel import PelangganModel


class PelangganController:

    def __init__(self):
        self.model = PelangganModel()

    def daftar(self):
        return self.model.get_all_pelanggan()

    def tambah(self, nama, no_identitas, no_telepon):
        return self.model.create_pelanggan(nama, no_identitas, no_telepon)