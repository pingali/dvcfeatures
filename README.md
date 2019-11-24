Features in DVC
===============

Note: This repo is under development.

Feature engineering is the process of generating neat model-ready
input files. It is time consuming and operations heavy process, and
deals with messy inputs, changing feature definitions. The outputs are
typically large tables - final and intermediate - that are generated
at regular intervals, e.g., a day. There are dozens of these datasets,
each of which has hundreds of tables, in a typical environment. There
are many downstream systems that consume feature engineering output in
various forms including blob-store backed SQL (e.g., athena), a
database (e.g., cassandra or Redshift), a key-value pair store (e.g.,
redis), and finally flat files.

Challenge: Putting all the datasets in a versioned system adds
complexity of ingesting the data into downstream systems. On the other
hand, the datasets need to be versioned because we dont know when the
downstream systems will ingest, and when we overwrite the files, the
consumed dataset is 'lost'.

Approach: 

1. Keep the output directory simple and as they are so that the
   consumption process is not disturbed.
2. Create a separate DVC repository that points to the output
   directory.
3. When the dataset is generated/updated, we run dvc commands to
   create and push a new version to the remote. 
4. Clean the cache to make sure we dont change the disk management
   process.

