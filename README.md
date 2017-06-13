This README is a WIP

# Local EGA: Data Mirroring
*Introduction to local ega*

## Modules (scripts)
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
* At this moment the script will fail if ```.md5``` file is not found
* Should file extension be given as a parameter, e.g. ```cf-dir cip %cd%```, or be hard coded into the script?
* cf-dir operations are logged to file cf_log.log in the working directory


```copy_file.py``` copies a file to a directory. This script can be run from command line by typing ```copy-file <path/file> <destination_directory>```. The function is able to copy large files with a built-in buffer size of 16 kB. ```copy-file```
also copies metadata.

NOTES:
* copy-file operations are logged to file copy_log.log in the working directory *(target or destination directory?)*

```decrypt_request.py``` decrypts a file using ELIXIR's RES decryption microservice. This script can be run from command line
by typing ```decrypt-request <host_url> <path/file>```. The decrypted file contents are saved to a plain .txt file in the working
directory.

NOTES:
* decrypt-request operations are logged to file decrypt_log.log in the working directory
* Current buffer size is 1 kB. Should this be defined as a parameter as well, giving the user some freedom of
memory control?
* Read more about RES microservice <here> <-- put link here

```md5_checksum.py``` verifies file integrity using md5 checksums. This function is used to verify the integrity of decrypted
files and should not be confused with the built-in md5-function inside cf_dir.py. This script can be run from command line by
typing ```md5-checksum <path/file>```. The script will calculate an md5 checksum for given file and attempt to read the hash
inside ```file.type.md5``` and compare these values.

NOTES:
* md5-checksum operations are logged to file md5checksum_log.log in the working directory

## Other

```db_script.txt``` contains the creation script of the database table used by ```cf_dir.py``` to track file transmission and verification.

## How to install
todo: python setup.py install, db connect config.ini
