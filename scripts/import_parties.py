from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from proteus import config, Model
from faker import Faker


def import_parties(database, config_file):
    config.set_trytond(database, config_file=config_file)
    Party = Model.get('party.party')
    fake = Faker()

    to_save = []
    for i in range(1000):
        party = Party()
        party.name = fake.name()
        to_save.append(party)
    Party.save(to_save)


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--database', dest='database', required=True,
        help='database')
    parser.add_argument('--config-file', dest='config_file', required=True,
        help='trytond config file')
    options = parser.parse_args()
    import_parties(options.database, options.config_file)
