from trytond.pool import PoolMeta


class UserApplication(metaclass=PoolMeta):
    __name__ = 'res.user.application'

    @classmethod
    def __setup__(cls):
        super(UserApplication, cls).__setup__()
        cls.application.selection.append(('libra', 'Libra Accounts'))
