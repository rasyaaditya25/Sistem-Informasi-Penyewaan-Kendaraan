from datetime import date

from controllers.akses import wajib_role, ADMIN, PEMILIK
from models.laporanModel import LaporanModel


class LaporanController:

    def __init__(self):
        self.model = LaporanModel()

    @wajib_role(PEMILIK, ADMIN)
    def ringkasan(self, dari, sampai):
        if date.fromisoformat(sampai) < date.fromisoformat(dari):
            raise ValueError(
                "Tanggal akhir tidak boleh sebelum tanggal awal."
            )

        return self.model.ringkasan(dari, sampai)
