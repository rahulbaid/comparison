# MongoDB vs DocumentDB

## Single Sentence Description
*From ChatGPT,*

MongoDB is a NoSQL, document-oriented database that provides high performance, scalability, and flexibility by storing data in JSON-like BSON (Binary JSON) documents, offering dynamic schema, and supporting a rich set of query capabilities.

Amazon DocumentDB is a fully managed NoSQL database service that is compatible with MongoDB, providing developers with a highly scalable, reliable, and performance-optimized solution for storing and querying JSON-like documents.


## DB Showdown

> System: M3 MacBook Pro 2023, 16GB RAM
> OS: MacOS Sonoma 14.3
> Python: 3.11.7
> Script: scripts/docdb.py
> MongoDB: 4.2.23 Community, t3a.small, 2vCPUs, 2G Memory, up to 2,085 EBS burst bandwidth (Mbps), Up to 5Gbps N/w
> DocumentDB: 5.0.0 Community, db.t4g.medium, 2vCPUs, 4G Memory, up to 2,085 EBS burst bandwidth (Mbps), Up to 5Gbps N/w

Here, we are **only testing the write performance** of the 2 databases. All the tests were run over 3 iterations and the average was taken. `retryWrites` has been set to `false` for DocumentDB client. Unless otherwise mentioned, all other settings of the `pymongo` driver are kept as default. The results have been shared below.

Truncating the collection before each test iteration (`insert_many` operations with `collection.drop()`) -
 
| Number of documents | Write latency in seconds - DocumentDB | Insertion rate (num docs/second) - DocumentDB | Write latency in seconds - MongoDB | Insertion rate (num docs/second) - MongoDB |
|------------------:|------------------------:|---------------------------------:|------------------------:|---------------------------------:|
|               100 |                    0.05 |                          1968.29 |                    0.05 |                          2051.42 |
|              1000 |                    0.33 |                          3037.50 |                    0.26 |                          3909.24 |
|             10000 |                    6.28 |                          1591.05 |                    2.94 |                          3403.25 |
|            100000 |                   29.24 |                          3419.51 |                   28.39 |                          3522.66 |
|           1000000 |                  269.85 |                          3705.70 |                  208.47 |                          4796.75 |


Appending data to the collection before each test iteration (`insert_many` operations) -

| Number of documents | Write latency in seconds - DocumentDB | Insertion rate (num docs/second) - DocumentDB | Write latency in seconds - MongoDB | Insertion rate (num docs/second) - MongoDB |
|------------------:|-------------------------------------:|--------------------------------------------:|----------------------------------:|-----------------------------------------:|
|               100 |                                 0.04 |                                     2302.07 |                              0.03 |                                  3014.31 |
|              1000 |                                 0.49 |                                     2015.58 |                              0.51 |                                  1963.18 |
|             10000 |                                 5.00 |                                     1997.40 |                              3.45 |                                  2897.75 |
|            100000 |                                35.45 |                                     2820.76 |                             29.71 |                                  3365.54 |


Specifying the `_id` field for each document before each test iteration (`bulk_write` operations) -

| Number of documents | Write latency in seconds - DocumentDB | Insertion rate (num docs/second) - DocumentDB | Write latency in seconds - MongoDB | Insertion rate (num docs/second) - MongoDB |
|------------------:|-------------------------------------:|--------------------------------------------:|----------------------------------:|-----------------------------------------:|
|               100 |                                 0.43 |                                     230.06 |                              0.04 |                                  2064.23 |
|              1000 |                                 3.50 |                                     285.58 |                              0.46 |                                  2177.43 |
|             10000 |                                31.19 |                                     320.58 |                              7.91 |                                  1264.15 |
|            100000 |                               274.55 |                                     364.22 |                             42.94 |                                  2328.46 |


## Conclusion

We can see that while the performance of the databases is comparable (though MongoDB is a bit faster) for insert operations without specifying the `_id` field, DocumentDB is significantly slower than MongoDB when the `_id` field is specified. 

Other settings can be tweaked to improve write performance such as `ordered`, `write_concern`, `bypass_document_validation`. However, I have not tested them yet.
