import os
from setuptools import setup, find_packages

def scripts_list():
    """ Return list of command line tools from package scripts """
    scripts = []
    for modulename in os.listdir('lega_mirroring'):
        if modulename == '__init__.py':
            continue
        if not modulename.endswith('.py'):
            continue
        modulename = modulename.replace('.py', '')
        scriptname = modulename.replace('_', '-')
        scripts.append('%s = lega_mirroring.%s:main' % (scriptname, modulename))
        print(scripts)
        return scripts


def main():
    """ Install lega """
    setup(name='lega',
          version='dev',
          packages=['lega_mirroring'],
          entry_points={'console_scripts': scripts_list()})

if __name__ == '__main__':
    main()
