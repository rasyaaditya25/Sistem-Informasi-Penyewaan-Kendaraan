from views.shared.komponen import TabelView, rupiah, tgl


def _status(p):
    return (
        "Menunggu Konfirmasi" if p["status"] == "Diajukan"
        else "Dikonfirmasi"
    )


def buat_tab_pengembalian(parent, controller):
    return TabelView(
        parent,
        "Data Pengembalian",
        [
            ("id", "ID", 45),
            ("sewa", "ID Sewa", 70),
            ("pelanggan", "Pelanggan", 140, "w"),
            ("kendaraan", "Kendaraan", 210, "w"),
            ("tanggal", "Tgl Kembali", 110),
            ("denda", "Denda", 110),
            ("status", "Status", 140),
        ],
        controller.daftar,
        lambda p: (
            p["id"], p["penyewaan_id"], p["username"],
            f'{p["merek"]} ({p["nomor_polisi"]})',
            tgl(p["tanggal_kembali"]), rupiah(p["denda"]), _status(p)
        ),
        subjudul="Seluruh data pengembalian kendaraan (hanya-baca).",
        tag_fn=_status
    )
