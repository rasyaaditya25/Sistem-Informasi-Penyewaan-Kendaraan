from controllers.akses import (
    Session, wajib_role, ADMIN, PELANGGAN, PEMILIK
)
from models.pengembalianModel import PengembalianModel


class PengembalianController:

    def __init__(self):
        self.model = PengembalianModel()

    # UTILITAS: hitung denda (tanpa akses data, aman dipakai view)
    def hitung_denda(self, tarif_harian, tanggal_rencana, tanggal_kembali):
        """Mengembalikan (denda, hari_terlambat, tarif_harian)."""
        return self.model.hitung_denda(
            tarif_harian, tanggal_rencana, tanggal_kembali
        )

    # READ: seluruh riwayat (admin & pemilik)
    @wajib_role(ADMIN, PEMILIK)
    def daftar(self):
        return self.model.get_all_pengembalian()

    # READ: riwayat pengembalian milik pelanggan login
    @wajib_role(PELANGGAN)
    def daftar_saya(self):
        return self.model.get_all_pengembalian(Session.id_user())

    # READ: pengajuan pelanggan yang menunggu konfirmasi (admin)
    @wajib_role(ADMIN)
    def daftar_pengajuan(self):
        return [
            p for p in self.model.get_penyewaan_berjalan()
            if p.get("status_pengembalian") == "Diajukan"
        ]

    # READ: penyewaan berjalan milik pelanggan login
    @wajib_role(PELANGGAN)
    def daftar_penyewaan_berjalan_saya(self):
        return self.model.get_penyewaan_berjalan(Session.id_user())

    # ADMIN: mengonfirmasi pengajuan (tanggal boleh dikoreksi)
    @wajib_role(ADMIN)
    def proses(self, penyewaan_id, tanggal_kembali):
        return self.model.process_pengembalian(
            penyewaan_id,
            tanggal_kembali
        )

    # ADMIN: menolak pengajuan
    @wajib_role(ADMIN)
    def tolak(self, penyewaan_id):
        return self.model.tolak_pengajuan(penyewaan_id)

    # PELANGGAN: mengajukan pengembalian pada tanggal pilihannya
    @wajib_role(PELANGGAN)
    def ajukan(self, penyewaan_id, tanggal_kembali):
        return self.model.ajukan_pengembalian(
            penyewaan_id,
            Session.id_user(),
            tanggal_kembali
        )
