# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import bank
from . import party
from . import user
from . import routes

__all__ = ['register', 'routes']


def register():
    Pool.register(
        bank.LibraAccount,
        bank.LibraAccountEvent,
        bank.LibraAccountMintForm,
        bank.LibraAccountTransferForm,
        party.Party,
        user.UserApplication,
        module='bbank', type_='model')
    Pool.register(
        bank.LibraAccountMint,
        bank.LibraAccountTransfer,
        module='bbank', type_='wizard')
    Pool.register(
        module='bbank', type_='report')
