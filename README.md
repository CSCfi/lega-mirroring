# Local EGA: Data Mirroring
This git repository contains scripts for Local EGA data mirroring project. Local EGA data mirroring is part of the [ELIXIR](https://www.elixir-europe.org/about-us) [EXCELERATE](https://www.elixir-europe.org/excelerate) [biobank node](http://www.elixir-finland.org/) development project in EU. This work package is developed by [CSC - IT Center for Science Ltd](https://www.csc.fi/csc) in Finland in co-operation with Nordic [Tryggve](https://neic.no/tryggve/) partners.

## Scripts
##### cf_dir.py
```cf_dir.py``` can be used to track file transmission. The name cf_dir stands for *Check Files in DIRectory*.
This script can be run from command line by typing ```cf-dir <directory>```. ```cf-dir``` recursively checks all files
in the current directory of a certain filetype and keeps track of them with a MySQL database table.

##### Operating principle

```cf-dir``` inspects file(s) *size* in bytes and *time* of last modification. If a file's size hasn't changed in
some time, the script assumes that file transmission is complete and gives the file a pass mark on the database
table. Upon accumulating enough of passes, the script calculates an md5 checksum for the file and reads a checksum
from a corresponding ```file.type.md5``` and compares these hashes. If the checksums match, the script marks
the file as verified in the database table. The verified file is henceforth excluded from the checking process.

NOTES:
* cf-dir operations are logged to file cf_log.log in the working directory

##### copy_file.py
```copy_file.py``` copies a file to a directory. This script can be run from command line by typing ```copy-file <path/file> <destination_directory>```. The function is able to copy large files with a built-in buffer size of 16 kB. ```copy-file```
also copies metadata.

NOTES:
* copy-file operations are logged to file copy_log.log in the working directory *(target or destination directory?)*

##### decrypt_request.py
```decrypt_request.py``` decrypts a file using ELIXIR's RES decryption microservice. This script can be run from command line
by typing ```decrypt-request <host_url> <path/file>```. The decrypted file contents are saved to a plain .txt file in the working
directory.

NOTES:
* decrypt-request operations are logged to file decrypt_log.log in the working directory
* Read more about RES microservice [here](https://github.com/elixir-europe/ega-data-api-v3-res_mvc)

##### md5_checksum.py
```md5_checksum.py``` verifies file integrity using md5 checksums. This function is used to verify the integrity of decrypted
files and should not be confused with the built-in md5-function inside cf_dir.py. This script can be run from command line by
typing ```md5-checksum <path/file>```. The script will calculate an md5 checksum for given file and attempt to read the hash
inside ```file.type.md5``` and compare these values.

NOTES:
* md5-checksum operations are logged to file md5checksum_log.log in the working directory

## Other

```db_script.txt``` contains the creation script of the database table used by ```cf_dir.py``` to track file transmission and verification.

##### Dependencies
* ```decrypt_request.py``` contains import of python [requests](https://github.com/requests/requests) library

## How to install
Clone a copy of this repository using ```git clone https://github.com/CSCfi/lega-mirroring```. Then run the setup in command prompt
with ```python setup.py install```. The scripts are now installed. Next you must configure the scripts before they are ready to be used.
You can change certain variable values in config.ini, which will be used by the scripts.

Mainly, you need to define variables in section ```[database]```, as variables have been pre-defined for section ```[func_conf]```.
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
```
Example: values are already set in ```lega_mirroring/scripts/config.ini```
