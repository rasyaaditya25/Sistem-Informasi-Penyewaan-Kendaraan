from controllers.akses import Session, wajib_role, ADMIN
from models.user_model import UserModel


class UserController:

    def __init__(self):
        self.model = UserModel()

    # LOGIN (menyimpan user yang login ke Session)
    def login(self, username, password):
        user = self.model.autentikasi(username, password)

        if user:
            Session.login(user)

        return user

    # LOGOUT
    def logout(self):
        Session.logout()

    # REGISTER (dipakai RegisterView, belum perlu login)
    def register(self, username, password, no_identitas,
                 no_telepon, role):
        return self.model.register_user(
            username,
            password,
            no_identitas,
            no_telepon,
            role
        )

    # READ
    @wajib_role(ADMIN)
    def daftar_pelanggan(self):
        return self.model.get_all_pelanggan()

    # UPDATE
    @wajib_role(ADMIN)
    def ubah_pelanggan(
        self, id_user, username, no_identitas, no_telepon
    ):
        return self.model.update_pelanggan(
            id_user,
            username,
            no_identitas,
            no_telepon
        )

    # DELETE
    @wajib_role(ADMIN)
    def hapus_pelanggan(self, id_user):
        return self.model.delete_pelanggan(id_user)
