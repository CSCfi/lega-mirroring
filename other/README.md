##### getmetadata.py
This utility script is used to fetch dataset metadata from the EGA API and to insert the received information to dev_ega_downloader.file,
filedataset and dataset_log. The script's syntax goes as follows: `python3 getmetadata.py <dataset_id> <config_file>`.

Example:

`python3 getmetadata.py EGAD000010014288 config.ini`

Remember to configure `[api]` section in `config.ini`.

- - - -
##### dsin.py
This utility script is used to insert dataset metadata to dev_ega_downloader.file, filedataset and dataset_log from sources other
than EGA API. The script's syntax goes as follows: `python3 dsin.py <metafile> <config_file>`

Example:

`python3 dsin.py manifest.txt config.ini`

The `manifest.txt` must be in format `filename\tmd5\n`.

Short example:

```
file1.bam    bc41ac2
file2.bam    acbb221
file3.bam    bbcc77d
```
