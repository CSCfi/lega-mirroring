import luigi
import lega_mirroring.scripts.md5_checksum
import lega_mirroring.scripts.decrypt_request
#import lega_mirroring.scripts.encrypt_request #stage 4
import lega_mirroring.scripts.create_md5
import lega_mirroring.scripts.copy_file
#import lega_mirroring.scripts.db_loc #stage 7

class VerifyIntegrityOfTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 1/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def run(self):
        lega_mirroring.scripts.md5_checksum.main([self.file, self.config])
        return
    
    '''
    def output(self):
        return
    '''

class DecryptTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 2/7

    host = luigi.Parameter()
    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return VerifyIntegrityOfTransferredFile(file=self.file, config=self.config)

    def run(self):
        lega_mirroring.scripts.decrypt_request.main([self.host, self.file, self.config])
        return

    '''
    def output():
        return
    '''

''' pseudocode: to do

class VerifyIntegrityOfDecryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 3/7

    def requires():
        return DecryptTransferredFile()

    def run():
        # md5_checksum.py
        return

    def output():
        return


class EncryptVerifiedFile(luigi.Task):
    # WORKFLOW 2 STAGE 4/7

    def requires():
        return VerifyIntegrityOfDecryptedFile()

    def run():
        # --encrypt_request.py--
        return

    def output():
        return


class CreateHashForEncryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 5/7

    def requires():
        return EncryptVerifiedFile()

    def run():
        # create_md5.py
        return

    def output():
        return


class ArchiveFile(luigi.Task):
    # WORKFLOW 2 STAGE 6/7

    def requires():
        return CreateHashForEncryptedFile()

    def run():
        # copy_file.py
        return

    def output():
        return


class StoreFileLocationToDB(luigi.Task):
    # WORKFLOW 2 STAGE 7/7

    def requires():
        return ArchiveFile()

    def run():
        # --store_location.py--
        return

    def output():
        return
'''
