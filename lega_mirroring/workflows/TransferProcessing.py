import luigi
import os
from configparser import ConfigParser
from collections import namedtuple
import lega_mirroring.scripts.res
import lega_mirroring.scripts.md5
import lega_mirroring.scripts.move
import lega_mirroring.scripts.update


def get_conf(path_to_config):
    """ 
    This function reads configuration variables from an external file
    and returns the configuration variables as a class object 
    
    :path_to_config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'extensions': config.get('func_conf', 'extensions'),
            'path_receiving': config.get('workspaces', 'receiving'),
            'path_processing': config.get('workspaces', 'processing'),
            'path_archive': config.get('workspaces', 'end_storage')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named

class DecryptTransferredFile(luigi.Task):
    # WORKFLOW 2 STAGE 1/6

    file = luigi.Parameter()
    config = luigi.Parameter()
    
    def run(self):
        conf = get_conf(self.config)
        ext = tuple(conf.extensions.split(','))
        if self.file.endswith(ext):  # if file is encrypted, decrypt it
            lega_mirroring.scripts.res.main(['decrypt', self.file, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/1.txt')
    

class VerifyIntegrityOfDecryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 2/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return DecryptTransferredFile(file=self.file, config=self.config)

    def run(self):
        conf = get_conf(self.config)
        ext = tuple(conf.extensions.split(','))
        filename_decr = self.file  # .bam
        # remove crypt extension from filename
        if self.file.endswith(ext):
            filename_decr, extension = os.path.splitext(self.file)
        md5 = lega_mirroring.scripts.md5.main(['check', filename_decr, self.config])
        if not md5:
            raise Exception('md5 mismatch')
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/2.txt')


class EncryptVerifiedFile(luigi.Task):
    # WORKFLOW 2 STAGE 3/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return VerifyIntegrityOfDecryptedFile(file=self.file, config=self.config)

    def run(self):
        conf = get_conf(self.config)
        ext = tuple(conf.extensions.split(','))
        filename_decr = self.file  # .bam
        # remove crypt extension from filename
        if self.file.endswith(ext):
            filename_decr, extension = os.path.splitext(self.file)
        lega_mirroring.scripts.res.main(['encrypt', filename_decr, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/3.txt')


class CreateHashForEncryptedFile(luigi.Task):
    # WORKFLOW 2 STAGE 4/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return EncryptVerifiedFile(file=self.file, config=self.config)

    def run(self):
        # self.file = .bam or .bam.cip
        base, exte = os.path.splitext(self.file)  # .bam.cip -> .bam or .bam -> ''
        base, exte = os.path.splitext(base)  # .bam -> '' (precaution)
        filename = base + '.bam'  # put it back to be sure it's .bam
        lega_mirroring.scripts.md5.main(['hash', filename, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/4.txt')


class ArchiveFile(luigi.Task):
    # WORKFLOW 2 STAGE 5/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return CreateHashForEncryptedFile(file=self.file, config=self.config)

    def run(self):
        conf = get_conf(self.config)
        # Create new directory to end storage location
        relpath = self.file.replace(conf.path_processing, '')  # remove /root/path
        if os.path.dirname(relpath):
            if not os.path.exists(os.path.join(conf.path_archive, os.path.dirname(relpath))):
                os.mkdir(os.path.join(conf.path_archive, os.path.dirname(relpath)))
        ext = tuple(conf.extensions.split(','))
        if self.file.endswith(ext):
            base, extension =  os.path.splitext(self.file)  # remove extension
            cscfile = base + '.cip.csc'
            cscmd5 = base + '.cip.csc.md5'
        else:  # .bam
            cscfile = self.file + '.cip.csc'
            cscmd5 = self.file + '.cip.csc.md5'
        lega_mirroring.scripts.move.main([cscfile, cscmd5, self.config])
        with self.output().open('w') as fd:
            fd.write(str(cscfile + '\n' + cscmd5))
        return

    def output(self):
        return luigi.LocalTarget('output/5.txt')


class UpdateFileStatus(luigi.Task):
    # WORKFLOW 2 STAGE 6/6

    file = luigi.Parameter()
    config = luigi.Parameter()

    def requires(self):
        return ArchiveFile(file=self.file, config=self.config)

    def run(self):
        conf = get_conf(self.config)
        ext = tuple(conf.extensions.split(','))
        basefile = self.file  # .bam
        if self.file.endswith(ext):
            basefile, extension = os.path.splitext(self.file)  # remove extension
        basefile = basefile.replace(conf.path_processing, '')  # remove /root/path
        lega_mirroring.scripts.update.main([basefile, self.config])
        with self.output().open('w') as fd:
            fd.write(str(self.file))
        return

    def output(self):
        return luigi.LocalTarget('output/6.txt')
