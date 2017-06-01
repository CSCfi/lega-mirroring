import requests

file_path = '/data/NA12878.mapped.ILLUMINA.bwa.CEU.high_coverage_pcr_free.20130906.bam'


def decrypt(file_path):
    """ This function decrypts file type file.txt.cip
    and saves the decrypted file to file.txt.txt """
    params = {'filePath': file_path,
              'sourceFormat': 'aes128',
              'sourceKey': 'aeskey',
              'destinationFormat': 'plain'}
    r = requests.get('http://86.50.169.120:9090/file/', params, stream=True)
    with open('decrypted_file.txt', 'wb+') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return
