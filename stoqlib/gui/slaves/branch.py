# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005, 2006 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s): Bruno Rafael Garcia         <brg@async.com.br>
##
##
""" General slaves for branch management"""

from stoqlib.gui.base.editors import BaseEditorSlave
from stoqlib.domain.interfaces import IBranch


class BranchDetailsSlave(BaseEditorSlave):
    gladefile = 'BranchDetailsSlave'
    model_iface = IBranch
    proxy_widgets = ('active_check',
                     'manager')

    def setup_proxies(self):
        self.proxy = self.add_proxy(self.model,
                                    BranchDetailsSlave.proxy_widgets)
