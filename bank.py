from decimal import Decimal
from datetime import datetime
from collections import defaultdict

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.tools import grouped_slice, reduce_ids

from libra_client import Client, WalletLibrary


client = Client()
_digits = (16, 6)


class LibraAccount(ModelSQL, ModelView):
    'Libra Bank Account'
    __name__ = 'libra.account'
    _history = True

    address = fields.Binary('Addresss', states={'readonly': True})
    hex_address = fields.Char('Hex Address', states={'readonly': True})
    auth_key_prefix = fields.Binary('Key prefix', states={'readonly': True})
    party = fields.Many2One('party.party', 'Party', required=True)
    balance = fields.Function(
        fields.Numeric('Balance', digits=_digits), 'on_change_with_balance')
    wallet_file = fields.Binary('Wallet file', store_prefix='wallet')
    wallet_mnemonic = fields.Text('mnemonic', states={'readonly': True})
    events = fields.Function(
        fields.One2Many('libra.account.event', None, 'Events'), 'get_events')

    @classmethod
    def __setup__(cls):
        super(LibraAccount, cls).__setup__()
        cls._buttons.update({
            'create_libra_account': {
                'icon': 'tryton-ok',
            },
            'mint_libra_account': {
                'icon': 'tryton-ok',
            },
            'transfer_libra_account': {
                'icon': 'tryton-ok',
            },
        })

    @fields.depends('hex_address')
    def on_change_with_balance(self, name=None):
        balance = Decimal('0.0')
        if self.hex_address:
            balance = client.get_balance(self.hex_address)
        return Decimal(str(balance)).quantize(Decimal('10') ** _digits[1])

    def get_rec_name(self, name):
        return f'{self.party.name} - {self.hex_address}'

    @classmethod
    @ModelView.button
    def create_libra_account(cls, accounts):
        for account in accounts:
            wallet = WalletLibrary.new()
            libra_account = wallet.new_account()
            account.wallet_mnemonic = wallet.mnemonic
            account.address = fields.Binary.cast(libra_account.address)
            account.hex_address = libra_account.address.hex()
            account.auth_key_prefix = fields.Binary.cast(
                libra_account.auth_key_prefix)
            wallet.write_recovery('/tmp/wallet.wallet')
            with open('/tmp/wallet.wallet', 'rb') as fp:
                account.wallet_file = fp.read()
        cls.save(accounts)

    @classmethod
    @ModelView.button_action('bbank.wizard_mint_account')
    def mint_libra_account(cls, accounts):
        pass

    @classmethod
    @ModelView.button_action('bbank.wizard_transfer_account')
    def transfer_libra_account(cls, accounts):
        pass

    @classmethod
    def get_events(cls, accounts, names):
        pool = Pool()
        account = cls.__table__()
        Event = pool.get('libra.account.event')
        event = Event.__table__()
        result = defaultdict(lambda: [])
        cursor = Transaction().connection.cursor()
        ids = [acc.id for acc in accounts]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(account.id, sub_ids)
            query = account.join(event,
                condition=(
                    (event.to_account == account.id) |
                    (event.from_account == account.id))
            ).select(
                account.id,
                event.id,
                where=red_sql
            )
            cursor.execute(*query)
            for acc, event in cursor.fetchall():
                result[acc].append(event)
        return {
            'events': result
        }


class LibraAccountEvent(ModelSQL, ModelView):
    'Libra Bank Account Transfer'
    __name__ = 'libra.account.event'
    _history = True

    number = fields.Integer('Sequence Number')
    amount = fields.Numeric('Amount', digits=_digits)
    to_account = fields.Many2One('libra.account', 'Destiny')
    from_account = fields.Many2One('libra.account', 'Origin')
    effective_date = fields.DateTime('Effective Date')


class LibraAccountMintForm(ModelView):
    'Libra Account Mint Form'
    __name__ = 'libra.account.mint'
    amount = fields.Numeric('Amount', digits=_digits)

    @staticmethod
    def default_amount():
        return Decimal('0.0')


class LibraAccountMint(Wizard):
    'Mint Account'
    __name__ = 'libra.account.mint.wizard'
    start_state = 'ask'
    ask = StateView('libra.account.mint',
        'bbank.mint_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'handle', 'tryton-ok', default=True),
        ])
    handle = StateTransition()

    def transition_handle(self):
        pool = Pool()
        try:
            Event = pool.get('libra.account.event')
            account = self.record
            client.mint_coins(
                account.address, account.auth_key_prefix, self.ask.amount)
            event_ = client.get_events_received(
                account.address, start_sequence_number=0, limit=100)[-1]
            event = Event()
            event.number = event_.sequence_number
            event.to_account = account
            event.amount = event_.data.amount.amount
            event.effective_date = datetime.now()
            event.save()
        except Exception:
            pass
        return 'end'


class LibraAccountTransferForm(ModelView):
    'Libra Account Transfer Form'
    __name__ = 'libra.account.transfer'
    amount = fields.Numeric('Amount', digits=_digits)
    from_account = fields.Many2One('libra.account', 'Origin', required=True,
        states={
            'invisible': True,
        })
    to_account = fields.Many2One('libra.account', 'Destiny', required=True,
        domain=[
            ('id', '!=', Eval('from_account')),
        ], depends=['from_account'])

    @staticmethod
    def default_amount():
        return Decimal('0.0')


class LibraAccountTransfer(Wizard):
    'Mint Account'
    __name__ = 'libra.account.transfer.wizard'
    start_state = 'ask'
    ask = StateView('libra.account.transfer',
        'bbank.transfer_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'handle', 'tryton-ok', default=True),
        ])
    handle = StateTransition()

    def default_ask(self, fields):
        return {
            'from_account': self.record.id
        }

    def transition_handle(self):
        pool = Pool()
        Event = pool.get('libra.account.event')
        filename = f'/tmp/wallet_{self.record.id}'
        with open(filename, 'wb') as fp:
            fp.write(self.record.wallet_file)
        wallet = WalletLibrary.recover(filename)
        acc = wallet.accounts[0]
        _ = client.transfer_coin(acc, self.ask.to_account.hex_address,
            int(self.ask.amount), gas_unit_price=1)
        event = Event()
        event.number = 0
        event.from_account = self.record
        event.to_account = self.ask.to_account
        event.amount = self.ask.amount
        event.effective_date = datetime.now()
        event.save()
        return 'end'
