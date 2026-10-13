from models.pengembalianModel import PengembalianModel


class PengembalianController:

    def __init__(self):
        self.model = PengembalianModel()

    def daftar(self):
        return self.model.get_all_pengembalian()

    def proses(self, penyewaan_id, tanggal_kembali):
        return self.model.process_pengembalian(penyewaan_id, tanggal_kembali)