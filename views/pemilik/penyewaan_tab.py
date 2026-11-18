from views.shared.komponen import TabelView, rupiah, tgl


def buat_tab_penyewaan(parent, controller):
    return TabelView(
        parent,
        "Data Peminjaman",
        [
            ("id", "ID", 45),
            ("pelanggan", "Pelanggan", 140, "w"),
            ("kendaraan", "Kendaraan", 210, "w"),
            ("mulai", "Mulai", 100),
            ("rencana", "Rencana Kembali", 120),
            ("total", "Total Biaya", 120),
            ("status", "Status", 90),
        ],
        controller.daftar,
        lambda p: (
            p["id"], p["username"],
            f'{p["merek"]} ({p["nomor_polisi"]})',
            tgl(p["tanggal_mulai"]), tgl(p["tanggal_rencana_kembali"]),
            rupiah(p["total_biaya"]), p["status"]
        ),
        subjudul="Seluruh transaksi peminjaman (hanya-baca).",
        tag_fn=lambda p: p["status"]
    )
