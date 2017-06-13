This README is a WIP

# Local EGA
*Introduction to local ega*

## Modules (scripts)
##### cf_dir.py
```cf_dir.py``` can be used to track file transmission. The name cf_dir stands for *Check Files in DIRectory*.
This script can be run from command line by typing ```cf-dir %cd%```. ```cf-dir``` recursively checks all files
in the current directory of a certain filetype and keeps track of them with a MySQL database table.

Operating principle

```cf-dir``` inspects file(s) *size* in bytes and *time* of last modification. If a file's size hasn't changed in
some time, the script assumes that file transmission is complete and gives the file a pass mark on the database
table. Upon accumulating enough of passes, the script calculates an md5 checksum for the file and reads a checksum
from a corresponding ```file.type.md5``` and compares these hashes. If the checksums match, the script marks
the file as verified in the database table. The verified file is henceforth excluded from the checking process.

NOTES:
* At this moment the script will fail if ```.md5``` file is not found
* Should file extension be given as a parameter, e.g. ```cf-dir cip %cd%```, or be hard coded into the script?
* cf-dir operations are logged to file cf_log.log in the working directory

```copy_file.py``` copies a file to a 

```decrypt_request.py```

```md5_checksum.py```

## How to install
todo: python setup.py install, db connect config.ini
