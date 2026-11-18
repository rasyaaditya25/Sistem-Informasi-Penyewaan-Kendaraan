from views.shared.komponen import TabelView, rupiah, tgl, status_sewa


def buat_tab_riwayat(parent, penyewaan_controller):
    return TabelView(
        parent,
        "Riwayat Peminjaman",
        [
            ("id", "ID", 45),
            ("kendaraan", "Kendaraan", 190, "w"),
            ("mulai", "Mulai", 95),
            ("rencana", "Rencana Kembali", 120),
            ("kembali", "Dikembalikan", 100),
            ("total", "Total Biaya", 110),
            ("denda", "Denda", 100),
            ("status", "Status", 140),
        ],
        penyewaan_controller.daftar_saya,
        lambda p: (
            p["id"],
            f'{p["merek"]} ({p["nomor_polisi"]})',
            tgl(p["tanggal_mulai"]),
            tgl(p["tanggal_rencana_kembali"]),
            tgl(p["tanggal_kembali"]),
            rupiah(p["total_biaya"]),
            rupiah(p["denda"]) if p["denda"] is not None else "-",
            status_sewa(p),
        ),
        subjudul="Seluruh penyewaan yang pernah Anda lakukan.",
        tag_fn=status_sewa
    )
