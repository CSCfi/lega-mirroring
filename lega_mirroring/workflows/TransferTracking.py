import luigi
import lega_mirroring.scripts.monitor


class CheckFilesInDirectory(luigi.Task):
    # Luigi class for WORKFLOW 1

    branches = luigi.Parameter()
    branch = luigi.Parameter()
    config = luigi.Parameter()

    def run(self):
        ''' This function starts the file transfer checking process
        as described in lega_mirroring/scripts/monitor.py '''
        lega_mirroring.scripts.monitor.main([self.branches,
                                             self.branch,
                                             self.config])
        return
