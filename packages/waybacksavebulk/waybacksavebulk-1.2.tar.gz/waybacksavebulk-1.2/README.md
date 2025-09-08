waybacksavebulk
===============

Description
-----------
A simple script to bulk save URLs to the archive.org Wayback Machine.


Usage
-----
```
$ python3 -Wall waybacksavebulk.py -h
usage: waybacksavebulk.py [-h] -i INPUT_FILE [-s OUTPUT_SUCCESS] [-f OUTPUT_FAILED] [-q]

version: 1.2

options:
  -h, --help            show this help message and exit
  -i, --input-file INPUT_FILE
                        Input file as list of newline-separated FQDN
  -s, --output-success OUTPUT_SUCCESS
                        Output file to write successfully saved URL
  -f, --output-failed OUTPUT_FAILED
                        Output file to write failed attempts to save URL
  -q, --quiet           Quiet, no output displayed
```
  

Changelog
---------
* version 1.3 - 2025-09-07: Publication on pypi.org

Copyright and license
---------------------

waybacksavebulk is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

waybacksavebulk is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with waybacksavebulk. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >