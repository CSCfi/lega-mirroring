# Luigi Workflow
This module can be run using [luigi](https://github.com/spotify/luigi) workflow. Start the workflows by first starting a local luigi
server by typing `luigid` in command prompt window. You can then view the workflows at your [local visualiser](http://localhost:8082).

## Workflow 1: Tracking file transfer process
Workflow 1 is used to periodically run the `cf-dir` script. See [README](https://github.com/CSCfi/lega-mirroring/blob/master/README.md)
for operating principles.

Workflow 1 can be run from command line by typing:

`luigi --module workflow1 CheckFilesInDirectory --directory C:\..\targetdir --config C:\..\config.ini`

## Workflow 2: Everything else
Workflow 2 is used to run all the other steps as described in [this diagram](https://github.com/CSCfi/lega-mirroring/blob/master/lega_mirroring/workflows/workflow.png).

To be written: how to run workflow 2
