# Luigi Workflow
This module can be run using [luigi](https://github.com/spotify/luigi) workflow. Start the workflows by first starting a local luigi
server by typing `luigid` in command prompt window. You can then view the workflows at your [local visualiser](http://localhost:8082).

[Here](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/luigi_example.png) is an example of what luigi visualizer looks like when running workflow2.py. The pipeline is read from bottom to top.

## Workflow 1: Tracking file transfer process
Workflow 1 is used to periodically run the `cf-dir` script. See [README](https://github.com/CSCfi/lega-mirroring/blob/master/README.md)
for operating principles.

Workflow 1 can be run from command line by typing:

`luigi --module workflow1 CheckFilesInDirectory --directory C:\..\targetdir --config C:\..\config.ini`

## Workflow 2: Everything else
Workflow 2 is used to run all the other steps as described in [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png).

Workflow 2 in it's current state (f0a1ba7 @ 10.7.) can be run from command line by typing:

`luigi --module workflow2 ArchiveFile --file C:\..\file.txt --destination C:\..\destination --config C:\..\config.ini`

The given file is carried out through the following processes: 
* (1) after-transfer md5 checksum, 
* (2) decryption, 
* (3) after-decryption md5 checksum, 
* (4) encryption, 
* (5) after-encryption md5 hash generation, 
* (6) moving file to destination end storage location. 

(to do: step (7) save end storage location to tracking table)
