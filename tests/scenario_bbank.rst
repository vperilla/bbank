=================
Purchase Scenario
=================

Imports::

    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules

Activate modules::

    >>> config = activate_modules('bbank')

Create parties::

    >>> Party = Model.get('party.party')
    >>> party_1 = Party(name='Jhon Doe')
    >>> party_1.save()

    >>> party_2 = Party(name='Diego Abad')
    >>> party_2.save()

Create accounts::
    >>> Account = Model.get('libra.account')
    >>> account_1 = Account(party=party_1)
    >>> account_1.click('create_libra_account')
    >>> account_1.save()

    >>> account_2 = Account(party=party_2)
    >>> account_2.click('create_libra_account')
    >>> account_2.save()

Mint accounts::
    >>> mint_1 = Wizard('libra.account.mint.wizard', [account_1])
    >>> mint_1.form.amount = Decimal('10.0')
    >>> mint_1.execute('handle')
    >>> account_1.reload()

    >>> mint_2 = Wizard('libra.account.mint.wizard', [account_2])
    >>> mint_2.form.amount = Decimal('20.0')
    >>> mint_2.execute('handle')
    >>> account_2.reload()

Mint accounts with negative amount::
    >>> mint_negative = Wizard('libra.account.mint.wizard', [account_1])
    >>> mint_negative.form.amount = Decimal('-10.0')
    >>> mint_negative.execute('handle')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    UserError: ...
