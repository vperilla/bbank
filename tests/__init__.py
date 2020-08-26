# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

try:
    from trytond.modules.bbank.tests.test_bbank import suite  # noqa: E501
except ImportError:
    from .test_bbank import suite

__all__ = ['suite']
