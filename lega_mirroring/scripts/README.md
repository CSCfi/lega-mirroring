# Scripts
This directory contains the scripts that are run in luigi workflow. The scripts can also be run individually.

##### monitor.py
```monitor.py``` can be used to track file transmission.
This script can be run from command line by typing ```monitor <path/config.ini>```. ```monitor``` recursively checks all files
in the set directory (config.ini) of a certain filetype and keeps track of them with a MySQL database table. A configuration file must be given.

##### Operating principle

```monitor``` inspects file(s) *size* in bytes and *time* of last modification. If a file's size hasn't changed in
some time, the script assumes that file transmission is complete and gives the file a pass mark on the database
table. Files that have accumulated enough of passes are excluded from the checking process.

NOTES:
* monitor operations are logged to file monitor_log.log in the working directory
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

`res encrypt file.bam config.ini`. The encrypted contents are saved to `file.bam.cip.csc` in the working directory.

Example decryption:

`res decrypt file.bam.cip config.ini`. The decrypted contents are saved to `file.bam` in the working directory.

NOTES:
* res operations are logged to file res_log.log in the working directory
* Read more about RES microservice [here](https://github.com/elixir-europe/ega-data-api-v3-res_mvc)
* `[func_conf] res_url=<url>` in `config.ini` must be configured with the url of an active RES microservice.
- - - -
##### md5.py
`md5.py` is a multifunctional script capable of generating md5 hashes and writing them to file as well as performing checksum operations. This function is used to verify the integrity of transferred and decrypted files as well as generating md5 hashes for
encrypted files. This script can be run from command line by typing `md5 <method> <path/file> <path/config.ini>`.

Example hash generation:

`md5 hash file.bam.cip.csc config.ini`. Generates `file.bam.cip.csc.md5` in the working directory.

Example checksumming:

`md5 check file.bam.cip.csc config.ini`. Reads `file_md5` from database to determine if hashed value is equal to read value.
- - - -
##### update.py
`update.py` is used to update file status and path in `dev_ega_downloader.file`. This script can be run from command line by typing
`update <file_basename_in_db> <path/config.ini>` for example `update file.bam config.ini`. The script updates file.bam's status from pending
to available, and fixes the path from `receiving` to `end-storage`

- - - -
##### datasetlogger.py
This script is embedded within other scripts and is used to add timestamps to database table dataset_log on key process points: (1) dataset requested, (2) download started, (3) download ended (processing started), (4) processing ended.
