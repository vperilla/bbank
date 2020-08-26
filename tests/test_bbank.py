# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import unittest
import doctest


from trytond.tests.test_tryton import ModuleTestCase, doctest_teardown, \
    doctest_checker
from trytond.tests.test_tryton import suite as test_suite


class BbankTestCase(ModuleTestCase):
    'Test Bbank module'
    module = 'bbank'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            BbankTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_bbank.rst',
            tearDown=doctest_teardown, encoding='UTF-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            checker=doctest_checker))
    return suite
