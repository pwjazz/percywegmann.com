# Copyright 2012, Percy Wegmann

# Requires Python 2.5 or greater

# To run:
#
# python triexplore.py [port]
#
# for example:
#
# python triexplore.py 9000
#
# See READM.txt for information 

import sys
import web

if __name__ == '__main__':
    if sys.version < '2.5':
        sys.exit('This program requires Python 2.5 or greater')

    if (len(sys.argv) < 2):
        sys.exit('Please specify a port on which to listen for http connections.  For example: python triexplore.py 9000')

    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit('Please specify an integer port on which to listen for http connections.  For example: python triexplore.py 9000')

    web.run(port)
