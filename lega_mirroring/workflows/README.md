# Luigi Workflow
This module can be run using [luigi](https://github.com/spotify/luigi) workflow. Start the workflows by first starting a local luigi
server by typing `luigid` in command prompt window. You can then view the workflows at your [local visualiser](http://localhost:8082) (example below).


![Luigi Workflow Example](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/luigi_example.png)

[Here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/luigi_example.png) is an example of what luigi visualizer looks like when running TransferProcessing.py. The pipeline is read from bottom to top.

## Workflow 1: TransferTracking
Workflow 1 is used to periodically run the `monitor` script. See [README](https://github.com/CSCfi/lega-mirroring/blob/master/README.md)
for operating principles.

Workflow 1 can be run from command line (*cwd: lega-mirroring*) by typing:

`luigi --module lega_mirroring.workflows.TransferTracking CheckFilesInDirectory --branches <int> --branch <int> --config config.ini`

For example:

`luigi --module lega_mirroring.workflows.TransferTracking CheckFilesInDirectory --branches 4 --branch 1 --config config.ini` would run the process, checking
25% of the files in data/incoming/gridftp-endpoint/. Branches tell the fraction and branch is the starting index, for example, this setup
would check files 1,5,9,13,17....branch+4\*n. This syntax is used to set up parallel processes. To check all files in one process, use
values `--branches 1 --branch 1`.

## Workflow 2: TransferProcessing
Workflow 2 is used to run all the other steps as described in [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png).

Workflow 2 can be run from command line (*cwd: lega-mirroring*) by typing:

`luigi --module lega_mirroring.workflows.TransferProcessing ArchiveFile --file /data/incoming/processing/examplegenomefile.bam.cip --config config.ini`



The given file is carried out through the following processes: 
* (1) after-transfer md5 checksum, 
* (2) decryption, 
* (3) after-decryption md5 checksum, 
* (4) encryption, 
* (5) after-encryption md5 hash generation, 
* (6) moving file to destination end storage location. 

(to do: step (7) save end storage location to tracking table)

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
