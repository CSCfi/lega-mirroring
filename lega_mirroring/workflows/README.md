# Luigi Workflow
The scripts in this module can be run using [luigi](https://github.com/spotify/luigi) workflow. Start the workflows by first starting a local luigi server by typing `luigid` in command prompt window. You can then view the workflows at your [local visualiser](http://localhost:8082) (example below).


![Luigi Workflow Example](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/luigi_example.png)

[Here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/luigi_example.png) is an example of what luigi visualizer looks like when running ProcessMaster.py (several TransferProcessing.py:s). The pipeline is read from bottom to top. The process tree is launched with the top command "Launch". Green tasks are done, yellow ones are pending and blue task is currently being worked on. This example picture shows the data processing of 20 files, each file will be taken through 6 steps as described below.

## Workflow 1: TransferTracking
Workflow 1 is used to periodically run the `monitor` script. See [/scripts](https://github.com/CSCfi/lega-mirroring/tree/master/lega_mirroring/scripts) for operating principles.

Workflow 1 can be run from command line (*cwd: lega-mirroring*) by typing:

`luigi --module lega_mirroring.workflows.TransferTracking CheckFilesInDirectory --branches <int> --branch <int> --config config.ini`

For example:

`luigi --module lega_mirroring.workflows.TransferTracking CheckFilesInDirectory --branches 4 --branch 1 --config config.ini` would run the process, checking
25% of the files in data/incoming/gridftp-endpoint/. Branches tell the fraction and branch is the starting index, for example, this setup
would check files 1,5,9,13,17....branch+4\*n. This syntax is used to set up parallel processes. To check all files in one process, use
values `--branches 1 --branch 1`.

## Workflow 2: TransferProcessing
Workflow 2 is used to run all the other steps as described in [the overview picture](https://github.com/CSCfi/lega-mirroring/blob/master/lega_visualised.png).

Workflow 2 can be run from command line (*cwd: lega-mirroring*) by typing:

`luigi --module lega_mirroring.workflows.TransferProcessing ArchiveFile --file /data/incoming/processing/examplegenomefile.bam.cip --config config.ini`



The given file is carried out through the following processes: 
* (1) decryption, 
* (2) after-decryption md5 checksum, 
* (3) encryption, 
* (4) after-encryption md5 hash generation, 
* (5) moving file to destination end storage location. 
* (6) update file details in database

## ProcessMaster: Workflow 2 Automator
This luigi script is used to start parallel TransferProcessing.py luigi workflows. `TransferProcessing.py` takes a single file as input,
and as such can only be used manually. `ProcessMaster.py` generates a list of files for `TransferProcessing.py` to work on, and thus
automates the process.

ProcessMaster can be started from command line (*cwd: lega-mirroring*) by typing:

`luigi --module lega_mirroring.workflows.ProcessMaster Launch --branches <int> --branch <int> --config config.ini`

For example:

`luigi --module lega_mirroring.workflows.ProcessMaster Launch --branches 4 --branch 1 --config config.ini` would run the process,
allocating 25% of the `processing` directory for machine number `1`. (as in Workflow 1: TransferTracking) To process the whole directory
on one machine (single process) use values `--branches 1 --branch 1`.
