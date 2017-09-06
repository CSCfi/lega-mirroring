# Local EGA: Data Mirroring
This git repository contains scripts for Local EGA data mirroring project. Local EGA data mirroring is part of the [ELIXIR](https://www.elixir-europe.org/about-us) [EXCELERATE](https://www.elixir-europe.org/excelerate) [biobank node](http://www.elixir-finland.org/) development project in EU. This work package is developed by [CSC - IT Center for Science Ltd](https://www.csc.fi/csc) in Finland in co-operation with Nordic [Tryggve](https://neic.no/tryggve/) partners.

The scripts in this repository will be run in a [luigi](https://github.com/spotify/luigi) workflow according to [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png).

# Local EGA Process Overview
Here is an overview picture of how this module handles files.

Genomic datasets are received in gridftp-endpoint that is supervised by TransferTracking.py (luigi workflow that is running monitor.py).
When TransferTracking.py has determined that a file has finished downloading, it will move them to processing. The processing directory
is supervised by ProcessMaster.py (luigi workflow that generates child workflows). ProcessMaster.py launches a number of TransferProcessing.py workflows (luigi workflow that is running md5.py, res.py, move.py and update.py). This workflow handles the files
as presented in the picture. Processed files are moved to final-archive.
![Picture](https://github.com/CSCfi/lega-mirroring/blob/master/lega_visualized.png)

Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_visualized.png?raw=true) to open full picture.

##### Local EGA Demo Video
Here is a short (1 minute) animation visualizing the process. (NOTE: animation is outdated; .md5 files are no longer utilized, the process looks the same however. The only difference is that md5 hashes are fetched from a database).
![Local EGA Demo](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/local_ega_demo.gif)

Click [here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/local_ega_demo.gif) to restart the video in a new window.

## Contents

##### lega_mirroring/scripts/
This directory contains the actual scripts, a separate readme-file in the directory explains the scripts. [Go to scripts](https://github.com/CSCfi/lega-mirroring/tree/master/lega_mirroring/scripts)

##### lega_mirroring/workflows/
This directory contain the luigi workflows that run the scripts in tasks. [Go to workflows](https://github.com/CSCfi/lega-mirroring/tree/master/lega_mirroring/workflows)

##### testingscripts/
This directory contains scripts and instructions on how to run end-to-end test with this module. [Go to testingscripts](https://github.com/CSCfi/lega-mirroring/tree/master/testingscripts)

##### other/
This directory contains other related files, for example, the database creation script. [Go to other](https://github.com/CSCfi/lega-mirroring/tree/master/other)


## How to install
Clone a copy of this repository using ```git clone https://github.com/CSCfi/lega-mirroring```. Then run the setup in command prompt
with ```sudo python3 setup.py install``` (use python 3.4). The scripts are now installed. Install dependencies by typing `sudo pip3.4 install -r requirements.txt` to install required python libraries. Next you must configure the scripts before they are ready to be used.
You can change certain variable values in [config.ini](https://github.com/CSCfi/lega-mirroring/blob/master/config.ini), which will be used by the scripts. You may need to edit `PYTHONPATH` for the luigi workflows to work, e.g. `PYTHONPATH='.'`.
