Toxic Release Incidents Explorer
================================
Requires Python 2.7

Author: Percy Wegmann

Installation:

The zip archive requires everything needed to run.

Syntax:

python triexplore.py [port]

For example:

python triexplore.py 9000

This program provides a web-based interface preset county-level information about releases of toxic substances as
reported by the EPAs Toxic Release Inventory Program for the years 2000 - 2009.  The dataset consist of approximately
900,000 such incidents.

The web interface is found at the root on the specified port, for example:

http://localhost:9000/

Architecture
------------
Back-end: Python with CherryPy web server.  All data stored in memory, and parsed on each startup.  The data is stored
in something resembling a star schema, which is to say that aggregates are pre-computed (rather than storing all
line-items and computing aggregates on the fly).  This limits the number of dimensions on which we can report, but
improves performance considerably.

Front-end: HTML 5 with jQuery and various JavaScript utilities 

Features
--------
I aimed to make the UI self-explanatory, so I won't explain what it can do here.

Testing
-------
I manually tested that the data loads and spot tested the UI to make sure that filters and calculations work for normal
and extreme data values.

Areas for Additional Work
-------------------------
More work is required to verify the calculations themselves.

An interesting future exercise would be to correlate older chemical release incidents with
recent cancer incidence rates.

Acknowledgments
---------------
The visualization technique was adapted from this article:

  http://flowingdata.com/2009/11/12/how-to-make-a-us-county-thematic-map-using-free-tools/

The incident reports came from the EPA:

  http://www.epa.gov/tri/tridata/data/basic/index.html

Per-capita figures are based on population estimates from the Census Bureau:

  http://www.census.gov/popest/data/counties/totals/2009/files/CO-EST2009-ALLDATA.csv

Counties are correlated to a map of the United States using FIPS codes provided by:

  http://www.xtremelocator.com/xlocatordocs.html?task=file&file=2

Web server functionality is provided by CheeryPy 3.2.2:

  http://www.cherrypy.org/

with usage guidance from StackOverflow:

  http://stackoverflow.com/questions/3641007/cherrypy-how-to-respond-with-json

The UI makes heavy use of jQuery 1.7.2:

  http://jquery.com/

and also jQueryUI's autocomplete functionality:

  http://jqueryui.com/demos/autocomplete/combobox.html

with usage advice from:

  http://stackoverflow.com/questions/8401734/jquery-ui-autocomplete-have-the-menu-open-when-user-clicks-in-the-text-box

Tooltips are provided by qTip2:

  http://craigsworks.com/projects/qtip2/

Numbers are humanized with the help of the Humanize JavaScript library:

  http://javascript.so/index.php/javascript-library-to-humanize-numbers/

Loading indicators are provided by:

  http://code.google.com/p/jquery-loadmask/