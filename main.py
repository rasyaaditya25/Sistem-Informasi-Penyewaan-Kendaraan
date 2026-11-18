"""Titik masuk aplikasi GoRent.  Jalankan:  python main.py"""

from views.shared.aset import set_id_aplikasi_windows
from controllers.auth_controller import AuthController


def main():
    set_id_aplikasi_windows()      # ikon GoRent di taskbar Windows
    AuthController().run()


if __name__ == "__main__":
    main()
