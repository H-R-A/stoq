# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2011 Async Open Source <http://www.async.com.br>
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
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##
""" Stoq startup routines"""

import logging
import optparse
import os
import platform
import sys

# To avoid kiwi dependency at startup
log = logging.getLogger(__name__)


def get_shell(args):
    log.info('parsing command line arguments: %s ' % (args, ))
    from stoq.lib.options import get_option_parser
    parser = get_option_parser()

    group = optparse.OptionGroup(parser, 'Stoq')
    group.add_option('', '--quiet',
                     action="store_true",
                     dest="quiet",
                     help='Be quiet about warnings')
    group.add_option('', '--fatal-warnings',
                     action="store_false",
                     dest="non_fatal_warnings",
                     default=True,
                     help='Make all warnings fatal')
    group.add_option('', '--login-username',
                     action="store",
                     dest="login_username",
                     default=None,
                     help='Username to login to stoq with')
    group.add_option('', '--no-splash-screen',
                     action="store_false",
                     dest="splashscreen",
                     default=True,
                     help='Disable the splash screen')
    group.add_option('', '--version',
                     action="store_true",
                     dest="version",
                     help='Show the application version')
    group.add_option('', '--wizard',
                     action="store_true",
                     dest="wizard",
                     default=None,
                     help='Run the wizard')
    parser.add_option_group(group)

    options, args = parser.parse_args(args)

    if options.version:
        import stoq
        print(stoq.version)
        raise SystemExit()

    from stoq.gui.shell.bootstrap import boot_shell
    shell = boot_shell(options)

    return args, shell


def _windows_fixes():  # pragma: no cover
    executable = os.path.realpath(os.path.abspath(sys.executable))
    root = os.path.dirname(executable)

    # Indicate the cert.pem location so requests can use it on verify
    # From: http://stackoverflow.com/a/33334042
    import requests
    from raven.conf import defaults
    from raven.transport.http import HTTPTransport
    requests.utils.DEFAULT_CA_BUNDLE_PATH = os.path.join(root, 'cacert.pem')
    defaults.CA_BUNDLE = os.path.join(root, 'cacert.pem')

    # We need to monkeypatch the default values of the constructor, since the value is
    # 'hardcoded' once the class is first imported.
    _defs = list(HTTPTransport.__init__.__defaults__)
    _defs[-1] = defaults.CA_BUNDLE
    HTTPTransport.__init__.__defaults__ = tuple(_defs)
    print('XXX', defaults.CA_BUNDLE)


def main(args):
    if platform.system() == 'Windows':  # pragma: no cover
        _windows_fixes()

    args, shell = get_shell(args)

    action_name = None
    if len(args) < 2:
        appname = None
    else:
        appname = args[1].strip()
        if appname.endswith('/'):
            appname = appname[:-1]

        from stoq.lib.applist import get_application_names
        apps = get_application_names()

        if not appname in apps:
            raise SystemExit("'%s' is not an application. "
                             "Valid applications are: %s" % (appname, apps))

        if len(args) > 2:
            action_name = args[2]

    shell.main(appname, action_name)
