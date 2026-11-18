from views.shared.komponen import TabelView, rupiah


def buat_tab_kendaraan(parent, kendaraan_controller):
    return TabelView(
        parent,
        "Data Kendaraan",
        [
            ("id", "ID", 50),
            ("jenis", "Jenis", 90),
            ("merek", "Merek", 220, "w"),
            ("nopol", "No. Polisi", 140),
            ("tarif", "Tarif / Hari", 140),
            ("status", "Status", 110),
        ],
        kendaraan_controller.daftar,
        lambda k: (
            k["id"], k["jenis"], k["merek"], k["nomor_polisi"],
            rupiah(k["tarif_harian"]), k["status"]
        ),
        subjudul="Hanya kendaraan berstatus Tersedia yang dapat disewa.",
        tag_fn=lambda k: k["status"]
    )
