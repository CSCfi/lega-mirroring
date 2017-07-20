# Local EGA: Data Mirroring
This git repository contains scripts for Local EGA data mirroring project. Local EGA data mirroring is part of the [ELIXIR](https://www.elixir-europe.org/about-us) [EXCELERATE](https://www.elixir-europe.org/excelerate) [biobank node](http://www.elixir-finland.org/) development project in EU. This work package is developed by [CSC - IT Center for Science Ltd](https://www.csc.fi/csc) in Finland in co-operation with Nordic [Tryggve](https://neic.no/tryggve/) partners.

The scripts in this repository will be run in a [luigi](https://github.com/spotify/luigi) workflow according to [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png). Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/README.md) to see how.

## Scripts
##### cf_dir.py
```cf_dir.py``` can be used to track file transmission. The name cf_dir stands for *Check Files in DIRectory*.
This script can be run from command line by typing ```cf-dir <path/config.ini>```. ```cf-dir``` recursively checks all files
in the set directory (config.ini) of a certain filetype and keeps track of them with a MySQL database table. A configuration file must be given.

##### Operating principle

```cf-dir``` inspects file(s) *size* in bytes and *time* of last modification. If a file's size hasn't changed in
some time, the script assumes that file transmission is complete and gives the file a pass mark on the database
table. Files that have accumulated enough of passes are excluded from the checking process.

NOTES:
* cf-dir operations are logged to file cf_log.log in the working directory
* default config.ini can be found from lega_mirroring/scripts/
- - - -
##### move.py
```move.py``` moves a file to a directory. This script can be run from command line by typing ```move <path/file> <destination_directory>```.  ```move``` is an atomic operation if destination directory is within the same disk partition as file.

NOTES:
* move operations are logged to file move_log.log in the working directory
- - - -
##### res.py
`res.py` is a multifunctional script utilizing ELIXIR's RES microservice. It can be used to either encrypt or decrypt a given file.
This script can be run from command line by typing `res <method> <path/file> <path/config.ini>`.

Example encryption:

`res encrypt file.bam config.ini`. The encrypted contents are saved to `file.bam.cip` in the working directory.

Example decryption:

`res decrypt file.bam.cip config.ini`. The decrypted contents are saved to `file.bam` in the working directory.

NOTES:
* res operations are logged to file res_log.log in the working directory
* Read more about RES microservice [here](https://github.com/elixir-europe/ega-data-api-v3-res_mvc)
* `[func_conf] res_url=<url>` in `config.ini` must be configured with the url of an active RES microservice.
- - - -
##### md5_checksum.py
```md5_checksum.py``` verifies file integrity using md5 checksums. This function is used to verify the integrity of decrypted
files and should not be confused with the built-in md5-function inside cf_dir.py. This script can be run from command line by
typing ```md5-checksum <path/file> <path/config.ini>```. The script will calculate an md5 checksum for given file and attempt to read the hash inside ```file.type.md5``` and compare these values.

NOTES:
* md5-checksum operations are logged to file md5checksum_log.log in the working directory
- - - -
##### create_md5.py
```create_md5.py``` generates an md5 hash for a given file and saves it to an .md5 file. This script can be run from command line
by typing ```create-md5 <path/file> <path/config.ini>```.

NOTES:
* create-md5 operations are logged to file create_md5_log.log in the working directory
- - - -
##### find_errors.py
```find_errors.py``` can be run to query the database tracking table for files' ```passes``` and ```verified``` statuses. If
a file has remained unchanged for a considerable amount of time and hasn't been verified, an error will be logged to file. This
script can be run from command line by typing ```find-errors <path/config.ini>```.

NOTES:
* file-errors operations are logged to file errors.log in the working directory
- - - -
## Other

```db_script.txt``` contains the creation script of the database table used by ```cf_dir.py``` to track file transmission and verification.

##### Dependencies (required python libraries)
* `MySQLdb, os, time, datetime, calendar, sys, argparse, logging, configparser, collections, hashlib, ntpath, requests, luigi`

## How to install
Clone a copy of this repository using ```git clone https://github.com/CSCfi/lega-mirroring```. Then run the setup in command prompt
with ```python setup.py install``` (use python 3.4). The scripts are now installed. Next you must configure the scripts before they are ready to be used.
You can change certain variable values in config.ini, which will be used by the scripts.

```
[database]
host=<localhost or url to your mysql server>
user=<login username to database>
passwd=<login password to database>
db=<working database directory>
```
Example:
```
[database]
host=localhost
user=root
passwd=root
db=lega
```
Other config.ini variables:
```
[func_conf]
chunk_size=<int value>  #chunk size in bytes used in hashing
age_limit=<int value>  #number of seconds until cf-dir starts to accumulate passes
pass_limit=<int value>  #number of passes until cf-dir attempts to verify file
age_error_threshold=<int_value>  #number of seconds the file must stay unchanged for an error to be logged
res_url=<url>  #url to an active res microservice
[workspaces]
receiving=<path>  #path to gridftp endpoint (receiving directory, workflow1)
processing=<path>  #path to processing directory (workflow2)
end_storage=<path>  #path to final file archive
```
Example: values are already set in ```lega_mirroring/scripts/config.ini```
