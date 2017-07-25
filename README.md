# Local EGA: Data Mirroring
This git repository contains scripts for Local EGA data mirroring project. Local EGA data mirroring is part of the [ELIXIR](https://www.elixir-europe.org/about-us) [EXCELERATE](https://www.elixir-europe.org/excelerate) [biobank node](http://www.elixir-finland.org/) development project in EU. This work package is developed by [CSC - IT Center for Science Ltd](https://www.csc.fi/csc) in Finland in co-operation with Nordic [Tryggve](https://neic.no/tryggve/) partners.

The scripts in this repository will be run in a [luigi](https://github.com/spotify/luigi) workflow according to [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png). Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/README.md) to see how.

##### Local EGA Demo Video

![Local EGA Demo](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/local_ega_demo.gif)

Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/local_ega_demo.gif) to restart the video in a new window.

## Scripts
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

`res encrypt file.bam config.ini`. The encrypted contents are saved to `file.bam.cip` in the working directory.

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

`md5 hash file.txt config.ini`. Generates `file.txt.md5` in the working directory.

Example checksumming:

`md5 check file.txt config.ini`. Reads `file.txt.md5` in the working directory to determine if hashed value is equal to read value.

NOTES:
* md5 operations are logged to file md5_log.log in the working directory
- - - -
## Other

```db_script.txt``` contains the creation script of the database table used by ```monitor.py``` to track file transmission.

## How to install
Clone a copy of this repository using ```git clone https://github.com/CSCfi/lega-mirroring```. Then run the setup in command prompt
with ```sudo python3 setup.py install``` (use python 3.4). The scripts are now installed. Install dependencies by typing `sudo pip3.4 install -r requirements.txt` to install required python libraries. Next you must configure the scripts before they are ready to be used.
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
age_limit=<int value>  #number of seconds until monitor starts to accumulate passes
pass_limit=<int value>  #number of passes until monitor attempts to verify file
res_url=<url>  #url to an active res microservice
[workspaces]
receiving=<path>  #path to gridftp endpoint (receiving directory, workflow1)
processing=<path>  #path to processing directory (workflow2)
end_storage=<path>  #path to final file archive
```
Example: values are already set in [config.ini](https://github.com/CSCfi/lega-mirroring/blob/master/config.ini)


# Local EGA Process Overview
![Picture](https://github.com/CSCfi/lega-mirroring/blob/master/lega_visualized.png)

Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_visualized.png?raw=true) to open full picture.
