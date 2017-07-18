import luigi
import lega_mirroring.scripts.cf_dir

class CheckFilesInDirectory(luigi.Task):
    # Luigi class for WORKFLOW 1

    branches = luigi.Parameter()
    branch = luigi.Parameter()
    config = luigi.Parameter()

    def run(self):
        ''' This function starts the file transfer checking process
        as described in lega_mirroring/scripts/cf_dir.py '''
        lega_mirroring.scripts.cf_dir.main([self.branches, self.branch, self.config])
        return
