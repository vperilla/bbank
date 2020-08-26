from trytond.wsgi import app
from trytond.protocols.wrappers import with_pool, with_transaction, \
    user_application


libra_application = user_application('libra')


@app.route('/<database_name>/libra/parties', methods=['GET'])
@with_pool
@with_transaction()
@libra_application
def get_parties(request, pool):
    result = []
    Party = pool.get('party.party')
    for party in Party.search([('accounts', '!=', None)]):
        result.append({
            'id': party.id,
            'name': party.name,
            'account': party.accounts and party.accounts[0].address or '',
        })
    return result


@app.route('/<database_name>/libra/account/<int:account_id>', methods=['GET'])
@with_pool
@with_transaction()
@libra_application
def get_account(request, pool, account_id):
    Account = pool.get('libra.account')
    accounts = Account.search([
        ('id', '=', account_id)
    ])
    if accounts:
        account = accounts[0]
        return {
            'id': account.id,
            'party': account.party.name,
            'balance': account.balance,
        }
