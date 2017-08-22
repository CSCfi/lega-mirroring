CREATE DATABASE dev_ega_downloader;
USE dev_ega_downloader;

# For TransferTracking.py
CREATE TABLE trackingtable (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL,
    size VARCHAR(32) NOT NULL,
    age VARCHAR(32) NOT NULL,
    passes INT NOT NULL,
    PRIMARY KEY (id)
);

# For TransferProcessing.py
CREATE TABLE file (
    file_id VARCHAR(128) NULL,
    file_name VARCHAR(128) NULL,
    file_size INT8 NULL,
    file_md5 VARCHAR(32) NULL,
    status VARCHAR(13) NULL
);

CREATE UNIQUE INDEX file_id_idx ON dev_ega_downloader.file (file_id);

CREATE TABLE filedataset (
    dataset_id VARCHAR(128) NULL,
    file_id VARCHAR(128) NULL
);

CREATE UNIQUE INDEX dataset_id_idx ON dev_ega_downloader.filedataset (dataset_id, file_id);
CREATE UNIQUE INDEX file_id_idx ON dev_ega_downloader.filedataset (file_id, dataset_id);

# Dataset logger
CREATE TABLE dataset_log (
    dataset_id VARCHAR(128),
    n_files INT,
    n_bytes INT,
    date_requested TIMESTAMP NULL,
    date_download_start TIMESTAMP NULL,
    date_download_end TIMESTAMP NULL,
    date_processing_end TIMESTAMP NULL
);

CREATE UNIQUE INDEX dataset_id_idx ON dev_ega_downloader.dataset_log (dataset_id);