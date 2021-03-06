# -*- coding: utf-8 -*-
from shutil import copyfile
from promebuilder import gen_metadata, setup
from promebuilder.utils import REQUIREMENTSFILE

BUILREQFILE = 'build-requirements.txt'

print("Duplicating {} into {}".format(BUILREQFILE, REQUIREMENTSFILE))
copyfile(BUILREQFILE, REQUIREMENTSFILE)

METADATA = gen_metadata(
    name="promebuilder",
    description="Prometeia Package Builder",
    email="pytho_support@prometeia.com",
    url="https://github.com/prometeia/promebuilder",
    keywords="setup build pipeline ci",
    entry_points={
        'console_scripts': [
            'promescanner = promebuilder.scanner:scan_here',
            'activatenrt = promebuilder.activatenrt:activate_nrt'
        ]
    }
)


if __name__ == '__main__':
    setup(METADATA)
