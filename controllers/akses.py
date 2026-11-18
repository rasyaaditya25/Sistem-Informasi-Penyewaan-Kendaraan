import functools

ADMIN = "Admin"
PELANGGAN = "Pelanggan"
PEMILIK = "Pemilik Rental"


class Session:
    """Menyimpan user yang sedang login."""

    user = None

    @classmethod
    def login(cls, user):
        cls.user = user

    @classmethod
    def logout(cls):
        cls.user = None

    @classmethod
    def role(cls):
        return cls.user["role"] if cls.user else None

    @classmethod
    def id_user(cls):
        return cls.user["id_user"] if cls.user else None


def wajib_role(*roles):
    """
    Decorator untuk method controller. Method hanya bisa dipakai
    oleh role yang diizinkan, jadi pembatasan akses tidak hanya
    bergantung pada tab yang ditampilkan di view.
    """

    def dekorator(fungsi):
        @functools.wraps(fungsi)
        def pembungkus(*args, **kwargs):
            if Session.user is None:
                raise PermissionError("Silakan login terlebih dahulu.")

            if Session.role() not in roles:
                raise PermissionError(
                    "Anda tidak memiliki akses untuk fitur ini."
                )

            return fungsi(*args, **kwargs)

        return pembungkus

    return dekorator
