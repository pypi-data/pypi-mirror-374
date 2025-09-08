pynetcraftcli
=============

Description
-----------
A simple Python script to interact with Netcraft APIs from CLI.


Usage
-----
```
$ python3 pynetcraftcli.py -h
usage: pynetcraftcli.py [-h] [-k API_KEY] [-a {submit,check}] -i INPUT_FILE [-w WORKERS] [-o OUTPUT] [-oc OUTPUT_CREDITED]

version: 1.1

options:
  -h, --help            show this help message and exit

common parameters:
  -k, --api-key API_KEY
                        API key (could either be provided in the "SECRET_NETCRAFT_API_KEY" env var)
  -a, --action {submit,check}
                        Action to do on Netcraft (default 'submit')
  -i, --input-file INPUT_FILE
                        Input file (either list of newline-separated FQDN or URL (for reporting) || submission UUID (for checking
                        reports)

'check' action parameters:
  -w, --workers WORKERS
                        Number of multithread workers (default 8)
  -o, --output OUTPUT   Output file for all malicious findings (default: ./output_malicious.txt)
  -oc, --output-credited OUTPUT_CREDITED
                        Output file for credited malicious findings only (default: ./output_malicious_credited.txt)
```
  

Changelog
---------
* version 1.1 - 2025-09-07: Publication on pypi.org


Copyright and license
---------------------

pynetcraftcli is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

pynetcraftcli is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with pynetcraftcli. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >