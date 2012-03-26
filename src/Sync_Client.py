#!/usr/bin/env python
#
# Copyright (c) 2011-2012 Wiktor Starzyk, Faisal Z. Qureshi
#
# This file is part of the Virtual Vision Simulator.
#
# The Virtual Vision Simulator is free software: you can 
# redistribute it and/or modify it under the terms 
# of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
#
# The Virtual Vision Simulator is distributed in the hope 
# that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Virtual Vision Simulator.  
# If not, see <http://www.gnu.org/licenses/>.
#


import sys
import getopt
import logging

from sync_client.sync_client import SyncClient

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["debug"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    debug = False
    for o, a in opts:

        if o in ("--debug"):
            debug = True

    format_str = '%(levelname)s: %(message)s'
    if debug:
        logging.basicConfig(format=format_str, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format_str, level=logging.INFO)

    server_list = []
    servers = args
    for server in servers:
        ip, port = server.split(":")
        server_list.append((ip, int(port)))

    sync = SyncClient(server_list)
    sync.run()


if __name__ == "__main__":
    main()
