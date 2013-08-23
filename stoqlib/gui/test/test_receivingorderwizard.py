# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

from decimal import Decimal

import gtk
from kiwi.python import Settable
import mock

from stoqlib.api import api
from stoqlib.domain.purchase import PurchaseOrder
from stoqlib.domain.receiving import ReceivingOrder
from stoqlib.gui.dialogs.labeldialog import SkipLabelsEditor
from stoqlib.gui.test.uitestutils import GUITest
from stoqlib.gui.wizards.receivingwizard import ReceivingOrderWizard
from stoqlib.lib.dateutils import localdatetime


class TestReceivingOrderWizard(GUITest):
    @mock.patch('stoqlib.gui.utils.printing.warning')
    @mock.patch('stoqlib.gui.wizards.receivingwizard.run_dialog')
    @mock.patch('stoqlib.gui.wizards.receivingwizard.yesno')
    def test_complete_receiving(self, yesno, run_dialog, warning):
        yesno.return_value = True
        run_dialog.return_value = Settable(skip=Decimal('0'))
        branch = api.get_current_branch(self.store)

        order = self.create_purchase_order(branch=branch)
        order.identifier = 65432
        order.open_date = localdatetime(2012, 10, 9)
        order.expected_receival_date = localdatetime(2012, 9, 25)
        sellable = self.create_sellable()
        order.add_item(sellable, 1)
        order.status = PurchaseOrder.ORDER_PENDING
        order.confirm()
        wizard = ReceivingOrderWizard(self.store)

        step = wizard.get_current_step()
        self.assertNotSensitive(wizard, ['next_button'])
        self.click(step.search.search_button)
        order_view = step.search.results[0]
        step.search.results.select(order_view)
        self.assertSensitive(wizard, ['next_button'])
        self.check_wizard(wizard, 'purchase-selection-step')
        self.click(wizard.next_button)

        step = wizard.get_current_step()
        self.assertSensitive(wizard, ['next_button'])
        self.check_wizard(wizard, 'receiving-order-product-step')
        self.click(wizard.next_button)

        step = wizard.get_current_step()
        self.assertNotSensitive(wizard, ['next_button'])
        step.invoice_slave.invoice_number.update(1)
        self.assertSensitive(wizard, ['next_button'])
        self.check_wizard(wizard, 'receiving-invoice-step')
        module = 'stoqlib.gui.events.ReceivingOrderWizardFinishEvent.emit'
        with mock.patch(module) as emit:
            with mock.patch.object(wizard.model, 'confirm') as confirm:
                api.sysparam(self.store).LABEL_TEMPLATE_PATH.path = u''
                self.assertEqual(confirm.call_count, 0)
                self.click(wizard.next_button)
                self.assertEqual(confirm.call_count, 1)
                self.assertEquals(emit.call_count, 1)
                args, kwargs = emit.call_args
                self.assertTrue(isinstance(args[0], ReceivingOrder))
                self.assertEqual(yesno.call_count, 0)
                api.sysparam(self.store).LABEL_TEMPLATE_PATH.path = ur'C:\nppdf32Log\debuglog.txt'
                emit.reset_mock()
                confirm.reset_mock()
                self.click(wizard.next_button)
                self.assertEqual(emit.call_count, 1)
                self.assertEqual(confirm.call_count, 1)
                args, kwargs = emit.call_args
                self.assertTrue(isinstance(args[0], ReceivingOrder))
                yesno.assert_called_once_with('Do you want to print the labels for '
                                              'the received products?',
                                              gtk.RESPONSE_YES, 'Print labels',
                                              "Don't print")
                run_dialog.assert_called_once_with(SkipLabelsEditor, wizard,
                                                   self.store)
                warning.assert_called_once_with('It was not possible to print the '
                                                'labels. The template file was '
                                                'not found.')
