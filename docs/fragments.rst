.. _fragments: 

Entity fragmentation
======================

Generating graph data is a difficult process. The size of the datasets we want to process
using `followthemoney` (FtM) makes it impossible to incrementally build nodes and egdes in
memory like you would in `NetworkX`_. Instead, we use a stream-based solution
for constructing graph entities. That is why the toolkit supports *entity fragments*
and *aggregation*.

.. _NetworkX: https://networkx.org/

An example
------------

To illustrate this problem, imagine a table with millions of rows that describes a set of
people and the companies they control. Every company can have multiple directors, while
each director might control multiple companies:

========= ======================= ============ ============ ============
CompanyID CompanyName             DirectorName DirectorIdNo DirectorDoB
========= ======================= ============ ============ ============
A123      Brilliant Amazing Ltd.  John Smith   PP827817     1979-02-16
...       ...                     ...          ...          ...
A71882    Goldfish Ltd.           John Smith   PP827817     NULL
...       ...                     ...          ...          ...
A123      Brilliant Amazing Ltd.  Jane Doe     PP1988299    1983-06-24
...       ...                     ...          ...          ...
========= ======================= ============ ============ ============

Database humpty-dumpty
-----------------------

When :ref:`turning this data into FtM <mappings>`, we'd create three entities for
each row: a :ref:`schema-Company`, a :ref:`schema-Person` and a
:ref:`schema-Directorship` that connects the two.

If we do this row by row, we'd eventually generate three :ref:`schema-Company`
entities to represent two actual companies, and three :ref:`schema-Person` entities
for two distinct people. Of course, we could write these to an ElasticSearch index
sequentially - the later entities overwriting the earlier ones with the same ID.

That works only as long as each version of each entity contains the same data.
In our example, the first mention of `John Smith` includes his birth date, while
the second does not. If we don't wish to lose that detail, we need to merge these
`fragments`. While it's possible to perform such merges at index time, this has proven
to be impractically slow because it requires fetching each entity before it is
updated.

A better solution is to sort all generated fragments before indexing them. With this
approach, all the entities generated from the source table would be written to disk or
to a database, and then sorted using their ID. In the resulting entity set, all instances
of each company and person are grouped and can be merged as they are read.

In practice 
-------------

In the FtM toolchain, there are two tools for doing entity aggregation: from the command-line
`ftm aggregate` will merge fragments in memory. Alternately the add-on library `followthemoney-store`
will perform the same operation in a SQLite or PostgreSQL database.

.. code-block:: bash

    # Generate entities from a CSV file and a mapping:
    cat company-registry.csv | ftm map-csv mapping_file.yml >fragments.ijson
    # Write the fragments to a table `company_registry`:
    cat fragments.ijson | ftm store write -d company_registry
    # List the tables in the store:
    ftm store list 
    # Output merged entities:
    ftm store iterate -d company_registry

The same functionality can also be used as a Python library:

.. code-block:: python

    import os
    from ftmstore import get_dataset
    # Assume a function that will emit fragments:
    from myapp.data import generate_fragments

    # If no `database_uri` is given, ftmstore will read connection from 
    # $FTM_STORE_URI, or create a file called `followthemoney.sqlite` in
    # the current directory.
    database_uri = os.environ.get('DATABASE_URI')
    dataset = get_dataset('myapp_dataset', database_uri=database_uri)
    bulk = dataset.bulk()
    for idx, proxy in enumerate(generate_fragments()):
        bulk.put(proxy, fragment=idx)
    bulk.flush()

    # This will print the number of combined entities (ie. DISTINCT id):
    print(len(dataset)) 

    # This will return combined entities:
    for entity in dataset.iterate():
        print(entity.caption)

    # You could also iterate the underlying fragments:
    for proxy in dataset.partials():
        print(proxy)

    # Note: `dataset.partials()` returns `EntityProxy` objects. The method
    # `dataset.fragments()` would return raw Python dictionaries instead.

    # All three methods also support the `entity_id` filter, which can also be
    # shortened to `get`:
    entity = dataset.get(entity_id)

Fragment origins
-----------------

`followthemoney-store` is used across the tools built on FtM to capture and aggregate
entity fragments. In Aleph, fragments for one entity might be written by different
processes: the API, document ingestors, document NER analyzers or a translation 
backend. It is convenient to be able to flush all entity fragments from a 
particular origin, while leaving the other fragments intact. For example,
this can be used to delete all data uploaded via the bulk API, while leaving
document-based data in the same dataset intact.

To support this, `ftm-store` has the notion of an `origin` for each fragment. If
specified, this can be used to later delete or overwrite subsets of fragments.

.. code-block:: bash

    cat us_ofac.ijson | ftm store write -d sanctions -o us_ofac
    cat eu_eeas.ijson | ftm store write -d sanctions -o eu_eeas

    # Will now have entities from both source files:
    ftm store iterate -d sanctions | wc -l

    # Delete all fragments from the second file:
    ftm store delete -d sanctions -o eu_eeas

    # Only one source file is left:
    ftm store iterate -d sanctions | wc -l

