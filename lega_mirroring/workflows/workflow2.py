import luigi
import lega_mirroring.scripts.md5_checksum
import lega_mirroring.scripts.res
#import lega_mirroring.scripts.encrypt_request #stage 4
import lega_mirroring.scripts.create_md5
import lega_mirroring.scripts.copy_file
#import lega_mirroring.scripts.db_loc #stage 7

class VerifyIntegrityOfTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 1/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def run(self):
        md5 = lega_mirroring.scripts.md5_checksum.main([self.file, self.config])
        if not md5:
            raise Exception('md5 mismatch')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return
    
    def output(self):
        return luigi.LocalTarget('output/1.txt')


class DecryptTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 2/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return VerifyIntegrityOfTransferredFile(file=self.file, config=self.config)

    def run(self):
        # Add / in front of filename for linux
        lega_mirroring.scripts.res.main(['decrypt', ('/' + self.file), self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/2.txt')
    

class VerifyIntegrityOfDecryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 3/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return DecryptTransferredFile(file=self.file, config=self.config)

    def run(self):
        # remove .cip extension from filename
        filename_decr = self.file.replace('.cip', '.txt')
        md5 = lega_mirroring.scripts.md5_checksum.main([filename_decr, self.config])
        if not md5:
            raise Exception('md5 mismatch')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/3.txt')

''' pseudocode: to do

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
