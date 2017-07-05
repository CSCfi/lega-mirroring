import luigi
import lega_mirroring.scripts.cf_dir

class CheckFilesInDirectory(luigi.Task):
    # Luigi class for WORKFLOW 1

    directory = luigi.Parameter()
    config = luigi.Parameter()

    '''
    Has no requires() method
      * independent script
    Has no output() method
      * cf_dir utilizes it's own db-tracking
    '''

    def run(self):
        ''' This function starts the file transfer checking process
        as described in lega_mirroring/scripts/cf_dir.py '''
        lega_mirroring.scripts.cf_dir.main([self.directory, self.config])
        return