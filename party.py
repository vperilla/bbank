from trytond.model import fields
from trytond.pool import PoolMeta


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    accounts = fields.One2Many('libra.account', 'party', 'Accounts')
