import luigi
import lega_mirroring.scripts.md5_checksum
import lega_mirroring.scripts.res
import lega_mirroring.scripts.create_md5
import lega_mirroring.scripts.move
#import lega_mirroring.scripts.storeloc #stage 7, script not yet created

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
        lega_mirroring.scripts.res.main(['decrypt', self.file, self.config])
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
        filename_decr = self.file.replace('.cip', '')
        md5 = lega_mirroring.scripts.md5_checksum.main([filename_decr, self.config])
        if not md5:
            raise Exception('md5 mismatch')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/3.txt')


class EncryptVerifiedFile(luigi.Task):
    # WORKFLOW 2 STAGE 4/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return VerifyIntegrityOfDecryptedFile(file=self.file, config=self.config)

    def run(self):
        filename_decr = self.file.replace('.cip', '')
        lega_mirroring.scripts.res.main(['encrypt', filename_decr, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/4.txt')


class CreateHashForEncryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 5/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return EncryptVerifiedFile(file=self.file, config=self.config)

    def run(self):
        filename_encr = self.file.replace('.cip', '.cip.csc')
        lega_mirroring.scripts.create_md5.main([filename_encr, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/5.txt')


class ArchiveFile(luigi.Task):
    # WORKFLOW 2 STAGE 6/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return CreateHashForEncryptedFile(file=self.file, config=self.config)

    def run(self):
        cscfile = self.file + '.csc'
        cscmd5 = cscfile + '.md5'
        lega_mirroring.scripts.move.main([cscfile, cscmd5, self.config])
        with self.output().open('w') as fd:
            fd.write(str(cscfile + '\n' + cscmd5))
        return

    def output(self):
        return luigi.LocalTarget('output/6.txt')

'''
class StoreFileLocationToDB(luigi.Task):
    # WORKFLOW 2 STAGE 7/7

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return ArchiveFile(file=self.file, config=self.config)

    def run(self):
        # Make a script that fills this table
        # https://github.com/elixir-europe/ega-data-api-v3-downloader/blob/master/src/main/resources/File.sql
        lega_mirroring.scripts.storeloc.main('...')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/7.txt')
'''
