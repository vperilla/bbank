from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from proteus import config, Model


def import_parties(database, config_file):
    config.set_trytond(database, config_file=config_file)
    Party = Model.get('party.party')
    Account = Model.get('libra.account')

    for party in Party.find([]):
        account = Account()
        account.party = party
        account.save()
        account.click('create_libra_account')


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--database', dest='database', required=True,
        help='database')
    parser.add_argument('--config-file', dest='config_file', required=True,
        help='trytond config file')
    options = parser.parse_args()
    import_parties(options.database, options.config_file)
