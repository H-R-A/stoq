# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005 Async Open Source <http://www.async.com.br>
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
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s):       Evandro Vale Miquelito      <evandro@async.com.br>
##
"""
stoq/gui/receivable/receivable.py:

    Implementation of receivable application.
"""

import gtk
import gettext
import datetime

from kiwi.datatypes import currency
from kiwi.ui.widgets.list import Column, SummaryLabel
from stoqlib.lib.defaults import ALL_ITEMS_INDEX

from stoqlib.domain.payment.base import Payment
from stoqlib.lib.validators import get_price_format_str
from stoq.gui.application import SearchableAppWindow

_ = gettext.gettext

class ReceivableApp(SearchableAppWindow):

    app_name = _('Receivable')
    app_icon_name = 'stoq-bills'
    gladefile = 'receivable'
    searchbar_table = Payment
    searchbar_use_dates = True
    searchbar_result_strings = (_('payment'), _('payments'))
    searchbar_labels = (_('matching:'),)
    filter_slave_label = _('Show payments with status')
    klist_selection_mode = gtk.SELECTION_MULTIPLE
    klist_name = 'receivables'

    def __init__(self, app):
        SearchableAppWindow.__init__(self, app)
        self._setup_widgets()
        self._update_widgets()

    def _setup_widgets(self):
        value_format = '<b>%s</b>' % get_price_format_str()
        self.summary_label = SummaryLabel(klist=self.receivables,
                                          column='value',
                                          label='<b>Total:</b>',
                                          value_format=value_format)
        self.summary_label.show()
        self.list_vbox.pack_start(self.summary_label, False)

    def _update_widgets(self, *args):
        has_sales = len(self.receivables) > 0
        widgets = [self.cancel_button, self.details_button,
                   self.edit_button, self.add_button]
        for widget in widgets:
            widget.set_sensitive(has_sales)
        self._update_total_label()

    def _update_total_label(self):
        self.summary_label.update_total()

    def on_searchbar_activate(self, slave, objs):
        SearchableAppWindow.on_searchbar_activate(self, slave, objs)
        self._update_widgets()

    def get_filter_slave_items(self):
        items = [(value, key) for key, value in Payment.statuses.items()]
        items.append((_('Any'), ALL_ITEMS_INDEX))
        return items

    def _get_payment_id(self, value):
        if not value:
            return
        return '%03d' % value

    #
    # SearchBar hooks
    #

    def get_columns(self):
        return [Column('payment_id', title=_('Number'), width=100, 
                       data_type=str, sorted=True,
                       format_func=self._get_payment_id),
                Column('description', title=_('Description'), width=220, 
                       data_type=str),
                Column('thirdparty_name', title=_('Drawee'), data_type=str,
                       width=170),
                Column('due_date', title=_('Due Date'),
                       data_type=datetime.date, width=90),
                Column('status_str', title=_('Status'), width=80, 
                       data_type=str), 
                Column('value', title=_('Value'), data_type=currency)]

    def get_extra_query(self):
        status = self.filter_slave.get_selected_status()
        if status == ALL_ITEMS_INDEX:
            return
        return Payment.q.status == status

    #
    # Kiwi callbacks
    #

    def _on_conference_action_clicked(self, *args):
        pass

    def _on_bills_action_clicked(self, *args):
        pass
