# End-to-End Testing
This directory contains scripts that can be used to run end-to-end tests for this lega-mirroring module.

##### CreateTestFiles.py
Generate `n` test files filled with lorem ipsum. The files are created in `receiving` as noted in `config.ini`.
The script can be run by typing `python3 CreateTestFiles.py n` where `n` is the amount of test files you wish to create, for example
`python3 CreateTestFiles.py 10000` would create 10k test `.bam.cip` test files. And a random number of `.json` files to `metadata` 
directory. The `.bam` files are associated with random EGAD dataset IDs and are given individual random EGAF file IDs. This `.json` file
simulates EBI EGA REST API.

##### FileCount.py
This script is used to quickly see the amount of files in each directory. The script can be run by typing `python3 FileCount.py`.

##### RequestDatasets.py
Reads the `.json` files generated in `metadata` by `CreateTestFiles.py` and inserts the contents into database. This simulates the 
EBI EGA REST API.

##### TrackItems.py
This script is used to verify that all files have been archived. The script has three methods; `start`, `end` and `compare`. It can be
run by typing `python3 TrackItems.py method` for example `python3 TrackItems.py start`. `start`-method creates a .txt file listing the
files in `receiving`. `end`-method creates a .txt file listing the files in `end-storage`. `compare`-method compares the two previously
generated lists and creates a .txt file containing the differences of these lists. If the end-to-end test was succesful, this file should
be empty (all files were moved from beginning to end).
