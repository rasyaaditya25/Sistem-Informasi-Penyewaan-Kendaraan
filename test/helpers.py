"""Alat bantu test: user palsu, session, dan koneksi database MagicMock."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from controllers.akses import Session, ADMIN, PELANGGAN, PEMILIK

USER = {
    ADMIN: {"id_user": 1, "username": "admin", "role": ADMIN},
    PELANGGAN: {"id_user": 7, "username": "budi", "role": PELANGGAN},
    PEMILIK: {"id_user": 9, "username": "owner", "role": PEMILIK},
}


def login_sebagai(role):
    Session.login(USER[role])


def logout():
    Session.logout()


@contextmanager
def database_palsu(nama_modul):
    """
    Mengganti Database di models.<nama_modul> dengan MagicMock.
    Menghasilkan (conn, cursor) agar test bisa mengatur fetchone/fetchall
    dan memeriksa query yang dijalankan.
    """
    with patch(f"models.{nama_modul}.Database") as kelas_db:
        conn = MagicMock(name="conn")
        cursor = MagicMock(name="cursor")
        conn.cursor.return_value = cursor
        kelas_db.return_value.get_connection.return_value = conn
        yield conn, cursor


def sql_dijalankan(cursor):
    """Daftar teks SQL (ringkas, huruf besar) yang dieksekusi cursor."""
    return [
        " ".join(c.args[0].split()).upper()
        for c in cursor.execute.call_args_list
    ]
