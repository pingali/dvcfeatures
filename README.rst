===================================
Automated ML Feature Storage in DVC
===================================


.. image:: https://img.shields.io/pypi/v/dvcfeatures.svg
        :target: https://pypi.python.org/pypi/dvcfeatures

.. image:: https://img.shields.io/travis/pingali/dvcfeatures.svg
        :target: https://travis-ci.org/pingali/dvcfeatures

.. image:: https://readthedocs.org/projects/dvcfeatures/badge/?version=latest
        :target: https://dvcfeatures.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


A Python package to store computed features in DVC. It is a wrapper
around dvc commands to allow discovery and automated commit of the
freshly generated datasets.

* Free software: MIT license
* Documentation: https://dvcfeatures.readthedocs.io.

Description
-----------

Note: This repo is under development.

Feature engineering is the process of generating neat model-ready
input files. It is time consuming and operations heavy process, and
deals with messy inputs, changing feature definitions. The outputs are
typically large tables - final and intermediate - that are generated
at regular intervals, e.g., a day. They could be generated for various
scopes as well such as a region or age group or feature cluster. There
are dozens of these datasets, each of which may have hundreds or
thousands of tables, in a typical environment. There are many
downstream systems that consume feature engineering output in various
forms including blob-store backed SQL (e.g., athena), a database
(e.g., cassandra or Redshift), a key-value pair store (e.g., redis),
and finally flat files.

Typical structure has many external directories depending on the
process that is generating the feature sets::

    ├── ...external1..
    │   └── v1
    │       └── 11.2.1
    │           ├── data.csv
    │           ├── README.txt
    ├── ...external2.. (different complicated path)
    │   └── v3.2
    │       ├── 2019-08-02
    │       │   ├── log.txt
    │       │   ├── metadata.json
    │       ├── 2019-08-04
    │       │   ├── customer_summary.csv
    │       │   ├── log.txt
    │       │   ├── metadata.json
    ├── ...external3... (different complicated path)
    │   └── v192.1.1.2
    │       ├── 2-3-Butane
    │       │   ├── dataset.gz
    ...     ...
         

Challenge: Putting all the datasets in a versioned system adds
complexity of ingesting the data into downstream systems. On the other
hand, the datasets need to be versioned because we dont know when the
downstream systems will ingest, and when the feature engineering
processes overwrite the files, the consumed dataset may be 'lost'.

Approach
--------

1. Keep the external data directory simple and as they are so that the
   consumption process is not disturbed.
2. Create a NEW DVC repository that points to the output directory.
3. When the dataset is generated/updated in the external data
   directory, we run dvc commands to create and push a new version to
   the remote.
4. Clean the cache to make sure we dont change the disk management
   process.

The feature store git repository looks like this::
  
    ├── datasets.json
    ├── local.datasets.json (not committed to git)
    ├── datasets
    │   └── targets
    │       ├── 2019-08-25.dvc
    │       ├── 2019-09-04.dvc
    │       ├── 2019-10-01.dvc
    │       └── data -> ...external2... (symbolic link)
    │   └── compounds
    │       ├── 2-3-Butane.dvc
    │       └── data -> ...external3... (symbolic link)
    ...
    
Installation
------------

For now this package is only installable via the git repository::

    $ pip install git+https://github.com/pingali/dvcfeatures 

Create an empty repo and setup the DVC as usual::

    $ git clone git@github.com:.../webdatasets.git
    $ dvc init

    # Add a dvc s3 repo
    $ dvc remote add demo s3://...webdatasets/versioned/data

Create a dvcfeatures configuration file `datasets.json`::

    $ cd webdatasets
    $ ls .
    ./datasets.local.json
    ./datasets.json

    # 
    $ cat datasets.json
    {
        "params": {
            "targetset_version": "v3",
            "root": "scribble-demodata/versioned"
         },
        "datasets": {
            "targets": {
                "remote": "%(root)s/%(dataset)s",
                "root": "$SCRIBBLE_DATA/shared/datasets/experiment/targetset/%(targetset_version)s"
             }
        }
    }

    # Override the default settings with a local settings that is
    # not commited to the git repo. This will allow flexible management
    # of the data.
    $ cat local.datasets.json
    {
        "datasets": {
            "targets": {
                "root": "/home/alpha/experiment/data"
            }
        }
    }
  

Usage
-----

The cli is minimal::
      
    $ dvcfeatures 
    Usage: dvcfeatures [OPTIONS] COMMAND [ARGS]...
    
      Manage feature datasets in DVC

    Options:
      --help  Show this message and exit.

    Commands:
      init    Initialize the directories but dont commit
      list    List configured datasets
      show    Show dataset details
      update  Update repo with given unit of dataset


Now initialize and use the dvcfeatures::

    # Bootstrap the directory structure
    $  dvcfeatures init
    ✓ [.gitignore] Checked
    ✓ [dataset] targets

    # See what datasets have been configured    
    $ dvcfeatures list
    targets
       Root: /home/pingali/Data/enrich/data/shared/datasets/experiment/targetset/v3

    # See what can be added to the dvc features repo
    $ dvcfeatures show targets
    targets :
       Root: /home/pingali/Data/enrich/data/shared/datasets/experiment/targetset/v3
       Units:
             2019-10-25
             2019-09-27
             2019-11-07
             2019-09-30
             2019-09-19
             2019-09-10
             2019-08-27
             2019-08-25 ✓ Versioned
             2019-08-24
             2019-09-13
             2019-08-28
             2019-08-20
             2019-10-02
             2019-09-04
             2019-08-23
             2019-09-23
             2019-08-22
             2019-08-21
             2019-10-13

    # Update repository with one run/unit of the dataset
    $ dvcfeatures update targets 2019-09-04 
    Working dir /work/pingali/Code/plpdatasets/datasets/targets
    [run] dvc add data/2019-09-04
    Stage is cached, skipping.
    
    [run] git add datasets
    [run] git commit -a -m Automated commit of the dataset update
    [master 0e15775] Automated commit of the dataset update
     1 file changed, 1 insertion(+), 1 deletion(-)
    
    [run] dvc push -r demo
    [run] git push origin
    To git@github.com:pingali/webdatasets.git
       f5e84de..0e15775  master -> master
    

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
