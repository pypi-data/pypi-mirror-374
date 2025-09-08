redflagdomains_scraper
=============

Description
-----------
A simple Python script to scrape data from red.flag.domains.


Usage
-----
```
$ python3 redflagdomains_scraper.py -h
usage: red.flag.domains_scraper.py [-h] [-i INPUT_URL | -d {today,yesterday} | -a | -f INPUT_FILE] [-o OUTPUT_DIR]

version: 1.2

options:
  -h, --help            show this help message and exit
  -i, --input-url INPUT_URL
                        Input a single red.flag.domains URL
  -d, --date {today,yesterday}
                        Get a specific date of red.flag.domains publication
  -a, --all             Get all red.flag.domains publications ever
  -f, --input-file INPUT_FILE
                        Input file as a list of newline-separated red.flag.domains URL
  -o, --output-dir OUTPUT_DIR
                        Output directory (default: current working directory)
```
  

Changelog
---------
* version 1.2 - 2025-09-07: Publication on pypi.org

Copyright and license
---------------------

redflagdomains_scraper is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

redflagdomains_scraper is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with redflagdomains_scraper. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >