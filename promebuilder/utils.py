# -*- coding: utf-8 -*-
import setuptools
import os
import re
import time
import sys
import warnings
from setuptools.extern.packaging.version import Version, InvalidVersion

VERSIONFILE = 'version'
BRANCHFILE = 'branch'
REQUIREMENTSFILE = 'requirements.txt'
BUILDNUMFILES = ['buildnum', 'build_trigger_number']
CHANNELFILE = 'channel'
VALIDVER = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')
COVERAGEFILE = "htmlcov/index.html"
DYNBUILDNUM = int(time.time() - 1514764800)
LONGDESCFILE = "README.md"

FORKED = 'forked'
RESERVED = ('master', 'support', 'hotfix', 'release', FORKED, 'develop', 'backporting', 'feature', 'test')


def echo(msg):
    print("[{}]".format(msg))


def btype2index(btype):
    orderer = [''] + list(reversed(RESERVED))
    try:
        return orderer.index(btype)
    except ValueError:
        return 0


def discover_git_branch():
    headfilename = '.git/HEAD'
    if not os.path.isfile(headfilename):
        echo("Not a GIT repo")
        return
    with open(headfilename) as hfile:
        lines = hfile.readlines()
    if not lines or not lines[0]:
        echo("Invalid GIT repo")
        return
    try:
        refs = lines[0].split(':', 1)[1].strip().split('/')
    except IndexError:
        echo("Not a GIT branch")
        return
    for mustbe in ('refs', 'heads'):
        if refs.pop(0) != mustbe:
            echo ("Invalid GIT HEAD config")
            return
    branch = '/'.join(refs)
    echo("Discovered branch {}".format(branch))
    return branch


def gen_ver_build(rawversion, branch, build, masterlabel='main', masterbuild=0):
    """Returns <version>, <buildnum>, <channel>"""
    def calc():
        if not VALIDVER.match(rawversion):
            return rawversion, build, ''
        if not branch:
            return rawversion + 'a0', DYNBUILDNUM, ''
        if branch == 'develop':
            return "{}a{}".format(rawversion, btype2index(branch)), build or DYNBUILDNUM, branch
        try:
            if branch.startswith('develop_'):
                btype = FORKED
                bname = branch.split('_', 1)[1]
            else:
                btype, bname = branch.split("/")
        except ValueError:
            btype, bname = '', ''
        assert bname not in RESERVED
        if branch == 'master' or btype == 'support':
            return rawversion, masterbuild, masterlabel
        if build and btype in ('release', 'hotfix'):
            return '{}rc{}'.format(rawversion, build), masterbuild, btype
        bindex = btype2index(btype)
        if btype == FORKED:
            return (
                '{}a{}+{}'.format(rawversion, bindex, bname),
                build or DYNBUILDNUM,
                bname
            )
        return (
            '{}a{}'.format(rawversion, bindex),
            build or DYNBUILDNUM,
            btype if bindex else ''
        )

    tver, tbuild, tlab = calc()
    # Version normalization
    try:
        parsedver = Version(tver)
        tver = str(parsedver)
    except InvalidVersion:
        warnings.warn("Invalid version %s" % tver)
    return tver, tbuild, tlab


def _readfiles(names, default=None):
    if not isinstance(names, list):
        names = [names]
    for name in names:
        try:
            with open(name) as thefile:
                data = thefile.read().strip()
                if data:
                    return data
        except IOError:
            echo("not found file %s" % name)
    if default is None:
        raise IOError("Missing or empty all of the files " + ', '.join(names))
    else:
        echo("returning default '%s'" % default)
    return default


def read_version():
    return _readfiles(VERSIONFILE)


def has_coverage_report():
    hascoverage = os.path.isfile(COVERAGEFILE)
    if hascoverage:
        echo("found a coverage report in %s" % COVERAGEFILE)
    else:
        echo("no coverage was calculated")
    return hascoverage


def gen_metadata(name, description, email, url="http://www.prometeia.com", keywords=None, packages=None,
                 entry_points=None, package_data=None, data_files=None, zip_safe=False,
                 masterlabel='main', masterbuild=0, author="Prometeia", addpythonver=True):
    branch = _readfiles(BRANCHFILE, '')
    if not branch:
        branch = discover_git_branch() or ''
    version, buildnum, channel = gen_ver_build(read_version(), branch, int(_readfiles(BUILDNUMFILES, '0')),
                                               masterlabel, masterbuild)
    echo('Building version "%s" build "%d" from branch "%s" for channel "%s"' % (
        version, buildnum, branch, channel or ''))
    with open(CHANNELFILE, 'w') as channelfile:
        echo("Writing channel '%s' on %s" % (channel, os.path.abspath(CHANNELFILE)))
        channelfile.write(channel)

    if 'bdist_conda' in sys.argv:
        echo("bdist_conda mode: requirements from file become setup requires")
        requires = _readfiles(REQUIREMENTSFILE, default="").splitlines()
        if addpythonver:
            pythominver = 'python=={}.*'.format('.'.join(str(x) for x in sys.version_info[:2]))
            echo("Adding current python version constraint: {}".format(pythominver))
            requires.insert(0, pythominver)
    else:
        # Quando si installa in sviluppo, tanto al setup quanto all'esecuzione del wrapper viene verificato
        # che i package indicati siano effettivamente presenti. I package sono però gli effettivi moduli,
        # mentre nel requirements.txt ci sono i nomi dei pacchetti!
        # Qui andrebbero elencati tutti i moduli indispensabili davvero voluti, non i pacchetti, che a loro volta
        # dovrebbero avere analogamente ordinati install_requires. Qui un sottoinsieme solo di verifica.
        requires = []

    metadata = dict(
        name=name,
        description=description,
        url=url,
        author=author,
        author_email=email,
        maintainer=author,
        maintainer_email=email,
        keywords=keywords or [],
        packages=sorted(packages or set(setuptools.find_packages()) - {'tests'}),
        license="Proprietary",
        include_package_data=True,
        zip_safe=zip_safe,
        classifiers=['License :: Other/Proprietary License', 'Framework :: Pytest',
                     'Intended Audience :: Financial and Insurance Industry',
                     'Operating System :: Microsoft :: Windows', 'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python :: 2.7'],
        platforms=['Microsoft Windows, Linux'],
        install_requires=requires or [],
        package_data=package_data or {},
        entry_points=entry_points or {},
        version=version,
        data_files=data_files or []
    )

    try:
        with open(LONGDESCFILE, "r") as fh:
            long_description = fh.read()
        metadata['long_description'] = long_description
        metadata['long_description_content_type'] = "text/markdown"
    except OSError:
        metadata['long_description'] = description
        metadata['long_description_content_type'] = "text/plain"

    try:
        import distutils.command.bdist_conda
        echo("Conda distribution")
        docondatests = has_coverage_report()
        if not docondatests:
            echo("skipping conda tests")
        metadata.update(dict(
            distclass=distutils.command.bdist_conda.CondaDistribution,
            conda_import_tests=docondatests,
            conda_command_tests=docondatests,
            conda_buildnum=buildnum
        ))
    except ImportError:
        echo("Standard distribution")

    return metadata


def setup(metadata):
    try:
        from conda import CondaError
    except ImportError:
        setuptools.setup(**metadata)
    else:
        tnum = 3
        while tnum:
            tnum -= 1
            try:
                setuptools.setup(**metadata)
            except CondaError as cerr:
                if not tnum:
                    echo("-- TOO MANY CONDA ERROR--")
                    raise
                echo("-- CONDA ERROR --")
                echo(str(cerr))
                echo("-- RETRY --")
            else:
                break
