import luigi
import os
from configparser import ConfigParser
from collections import namedtuple
import lega_mirroring.scripts.monitor
from lega_mirroring.workflows.TransferProcessing import ArchiveFile

# functions for luigi class 'Launch'

def get_conf(path_to_config):
    """ 
    This function reads configuration variables from an external file
    and returns the configuration variables as a class object 
    
    :path_to_config: full path to config.ini (or just config.ini if
                     cwd: lega-mirroring)
    """
    config = ConfigParser()
    config.read(path_to_config)
    conf = {'path_processing': config.get('workspaces', 'processing')}
    conf_named = namedtuple("Config", conf.keys())(*conf.values())
    return conf_named

def par(directory, branches, branch):
    """
    This function reads a directory and generates a list
    of files to be checked by a single parallel process
    
    :directory:  target directory to be sorted
    :branches:  number of branches to be run
    :branch:  id of branch
    """
    complete_set = os.listdir(directory)
    selected_set = []  # to be appended
    i = 0
    while i <= len(complete_set):
        index = int(branch)+i*int(branches)
        if index <= len(complete_set):
            selected_set.append(complete_set[index-1])
        i += 1
    return selected_set

# luigi starts from here

class Launch(luigi.Task):
    # Luigi class for starting TransferProcessing WORKFLOW

    branches = luigi.Parameter()
    branch = luigi.Parameter()
    config = luigi.Parameter()
    
    def requires(self):
        conf = get_conf(self.config)
        path = conf.path_processing
        selected_set = par(path, self.branches, self.branch)
        for filename in selected_set:
            if filename.endswith('.cip'):
                filepath = os.path.join(path, filename)
                yield ArchiveFile(file=filepath, config=self.config)
