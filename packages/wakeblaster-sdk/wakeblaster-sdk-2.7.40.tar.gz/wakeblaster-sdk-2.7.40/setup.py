from setuptools import setup, find_packages
from codecs import open
from os import path
from subprocess import check_output

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'wakeblastersdk', '__version__.py')) as fp:
    exec(fp.read())

readme = path.join(here, 'README.md')
if path.isfile(readme):
    # Get the long description from the README file
    with open(readme, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ''

setup(
    name='wakeblaster-sdk',
    description='The WakeBlaster SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='http://www.wakeblaster.net',
    
    version=__version__,

    # Author details
    author='ProPlanEn GmbH',
    author_email='wakeblaster@proplanen.net',

    # Choose your license
    # license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Physics',

        # Pick your license as you wish (should match "license" above)
        # 'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='wakeblaster windfarm modelling simulation',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[
        'wakeblastersdk', 'wakeblastersdk.emd', 'wakeblasterexamples', 'energytoolbox'
    ],
    
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # include_package_data=True,
    package_data={'wakeblasterexamples': ['examples/*']},

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests==2.*', 'numpy', 'matplotlib', 'pandas', 'h5py'],

    python_requires='==3.*',
    
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'wakeblaster-example-simulation=wakeblasterexamples.example:main',
        ],
    },
)