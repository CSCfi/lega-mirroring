import luigi
import ntpath
import lega_mirroring.scripts.res
import lega_mirroring.scripts.md5
import lega_mirroring.scripts.move
import lega_mirroring.scripts.update

class DecryptTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 1/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def run(self):
        lega_mirroring.scripts.res.main(['decrypt', self.file, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/2.txt')
    

class VerifyIntegrityOfDecryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 2/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return DecryptTransferredFile(file=self.file, config=self.config)

    def run(self):
        # remove .cip extension from filename
        filename_decr = self.file.replace('.cip', '')
        md5 = lega_mirroring.scripts.md5.main(['check', filename_decr, self.config])
        if not md5:
            raise Exception('md5 mismatch')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/3.txt')


class EncryptVerifiedFile(luigi.Task):
    # WORKFLOW 2 STAGE 3/6

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
    # WORKFLOW 2 STAGE 4/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return EncryptVerifiedFile(file=self.file, config=self.config)

    def run(self):
        filename_encr = self.file.replace('.cip', '.cip.csc')
        lega_mirroring.scripts.md5.main(['hash', filename_encr, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/5.txt')


class ArchiveFile(luigi.Task):
    # WORKFLOW 2 STAGE 5/6

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


class UpdateFileStatus(luigi.Task):
    # WORKFLOW 2 STAGE 6/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return ArchiveFile(file=self.file, config=self.config)

    def run(self):
        # cut path and send only file.bam
        basefile = ntpath.basename(self.file)
        basefile = basefile.replace('.cip', '')
        lega_mirroring.scripts.update.main([basefile, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/7.txt')
