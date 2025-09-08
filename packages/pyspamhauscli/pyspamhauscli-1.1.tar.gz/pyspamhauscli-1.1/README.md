pyspamhauscli
=============

Description
-----------
A simple Python script to interact with Spamhaus APIs from cli.


Usage
-----
```
$ python3 pyspamhauscli.py -h
usage: pyspamhauscli.py [-h] [-k API_KEY] [-a {submit,get_threats_types,get_subs_list,get_subs_counter}] [-i INPUT_FILE] [-r REASON]

version: 1.1

options:
  -h, --help            show this help message and exit

common parameters:
  -k, --api-key API_KEY
                        API key (could either be provided in the "SECRET_SPAMHAUS_API_KEY" env var)
  -a, --action {submit,get_threats_types,get_subs_list,get_subs_counter}
                        Action to do on Spamhaus (default 'submit')

'submit' action parameters:
  -i, --input-file INPUT_FILE
                        Input file (list of newline-separated FQDN or URL or IP or email address)
  -r, --reason REASON   Reason to use (max length 255 characters)
```
  

Changelog
---------
* version 1.1 - 2025-09-07: Publication on pypi.org

Copyright and license
---------------------

pyspamhauscli is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

pyspamhauscli is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License along with pyspamhauscli. 
If not, see http://www.gnu.org/licenses/.

Contact
-------
* Thomas Debize < tdebize at mail d0t com >