.. highlight:: sh

Installation
============

.. important:: The `ligo.skymap` package requires `Python`_ 3.10 or later.
    See our :ref:`python-version-policy` for more details.

On the Linux or macOS operating systems and on x86_64 or aarch64/arm64 systems,
we recommend installing `ligo.skymap` using `pip`_ or `conda`_, either of which
will automatically install all of the additional
:ref:`Python dependencies <python-dependencies>`.

On other operating systems and architectures, you can :doc:`install from
source <../develop>`.

ligo.skymap does not support Windows. If you need to install ligo.skymap on
Windows, we suggest using a Linux virtual machine such as
`Windows Subsystem for Linux (WSL)`_.

Option 1: pip
-------------

To install `ligo.skymap` using `pip`_, you will need pip 19.3 or later. You can
check what version of pip you have by running this command::

    $ pip --version
    pip 20.0.2 from /usr/local/lib/python3.10/site-packages/pip (python 3.10)

If your version of pip is too old, then you can update pip to the most recent
version by running this command::

    $ pip install --upgrade pip

Then, just run this command::

    $ pip install ligo.skymap

You are now ready to get started using `ligo.skymap`.

Option 2: conda
---------------

If you are using the Anaconda Python distribution or the lightweight Miniconda
version, you can install `ligo.skymap` using `conda`_. First, enable the
`conda-forge`_ repository by running these commands::

    $ conda config --add channels conda-forge
    $ conda config --set channel_priority strict

Then, run this command::

    $ conda install ligo.skymap

You are now ready to get started using `ligo.skymap`.

.. _Python: https://www.python.org
.. _`pip`: https://pip.pypa.io
.. _`Python package index`: https://pypi.org/project/ligo.skymap/
.. _`conda`: https://conda.io
.. _`Windows Subsystem for Linux (WSL)`: https://learn.microsoft.com/en-us/windows/wsl/
.. _`conda-forge`: https://conda-forge.org

.. _python-dependencies:
.. note:: When you use pip to install `ligo.skymap` with pip or conda, it will
          automatically install the following required Python packages:

          *  `Astroplan <http://astroplan.readthedocs.io>`_ ≥ 0.7
          *  `Astropy`_ ≥ 6.0
          *  `astropy-healpix <https://astropy-healpix.readthedocs.io>`_ ≥ 0.3
          *  `Healpy <http://healpy.readthedocs.io>`_
          *  `h5py <https://www.h5py.org>`_
          *  `igwn-ligolw <https://pypi.org/project/igwn-ligolw/>`_
          *  `igwn-segments <https://pypi.org/project/igwn-segments/>`_
          *  `LALSuite <https://pypi.python.org/pypi/lalsuite>`_ ≥ 7.26
          *  `ligo-gracedb <https://pypi.org/project/ligo-gracedb/>`_ ≥ 2.0.1
          *  `Matplotlib <https://matplotlib.org>`_ ≥ 3.9.1
          *  `NetworkX <https://networkx.github.io>`_
          *  `Numpy <http://www.numpy.org>`_ ≥ 2.0.0
          *  `Pillow <http://pillow.readthedocs.io>`_ ≥ 2.5.0
          *  `ptemcee <https://github.com/willvousden/ptemcee>`_
          *  `Reproject <https://reproject.readthedocs.io>`_ ≥ 0.3.2
          *  `Scipy <https://www.scipy.org>`_ ≥ 1.10.1
          *  `Shapely <https://shapely.readthedocs.io/>`_ ≥ 2.0.0
          *  `tqdm <https://tqdm.github.io>`_ ≥ 4.27.0
          *  `pytz <http://pytz.sourceforge.net>`_

          The following packages are optional for specific features.

          For using DPGMM density estimation:
          *  `FIGARO <https://figaro.readthedocs.io>` ≥ 1.7.8

          For running the test suite:

          *  `astroquery <https://astroquery.readthedocs.io/>`_
          *  `pytest-astropy <https://github.com/astropy/pytest-astropy>`_
          *  `pytest-benchmark <https://pytest-benchmark.readthedocs.io/en/latest/>`_
          *  `pytest-mpl <https://pytest-mpl.readthedocs.io/>`_
          *  `pytest-rerunfailures <https://pytest-rerunfailures.readthedocs.io/>`_

          For building the documentation:

          *  `Sphinx <https://www.sphinx-doc.org/>`_ ≥ 4.0
          *  `sphinx-argparse <https://sphinx-argparse.readthedocs.org/>`_ ≥ 0.3.0
          *  `sphinx-astropy <https://github.com/astropy/sphinx-astropy>`_
          *  `sphinxcontrib-mermaid <https://github.com/mgaitan/sphinxcontrib-mermaid>`_ ≥ 0.7.1
          *  `tomli <https://github.com/hukkin/tomli>`_ ≥ 1.1.0

Optional LALSimulation Data
---------------------------

The following instructions are only relevant if you are installing ligo.skymap
for the purpose of generating localizations with BAYESTAR (e.g., for analysis
of LIGO/Virgo/KAGRA data or for simulations).

Some gravitational waveform approximants in LALSuite (notably, reduced order
models) rely on `LALSuite extra waveform files <lalsuite-waveform-data>`_ that
you must download and install separately. You can download the entire
collection of waveform files by following the `instructions in LALSuite's
README file <lalsuite-waveform-data>`_, or you can run the following command
to download just the one file needed by ligo.skymap::

    $ curl --create-dirs --output-dir ~/lalsuite-waveform-data -OL https://zenodo.org/records/14999310/files/SEOBNRv4ROM_v3.0.hdf5

Then, add the following line to your shell profile script (``~/.profile``,
``~/.bashrc``, or similar)::

    export LAL_DATA_PATH=$HOME/lalsuite-waveform-data

Then log out and log back in.

.. _`lalsuite-waveform-data`: https://git.ligo.org/lscsoft/lalsuite#lalsuite-extra-waveform-files
