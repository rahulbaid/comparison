import argparse
from datetime import datetime
import logging
import pandas as pd
import pymongo
import sys


parser = argparse.ArgumentParser(description="MongoDB Write Performance Test")
parser.add_argument(
    "--num_docs",
    type=int,
    default=1000,
    help="Number of documents to insert (default: 1000)",
)
parser.add_argument(
    "--iter",
    type=int,
    default=3,
    help="Frequency of insertion (default: 3)",
)
parser.add_argument(
    "--truncate",
    action="store_true",
    help="Truncate collection before insertion (default: True)",
)
parser.add_argument(
    "--specify-id",
    action="store_true",
    help="Specify the _id field (default: False)",
)

args = parser.parse_args()
num_documents = args.num_docs

# Set up logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

if num_documents < 1:
    logging.error("Number of documents must be positive")
    sys.exit(1)

df = pd.DataFrame()

logging.info("Loading data...Please wait")

try:
    # Load data into Pandas DataFrame
    for year in range(2017, 2024):
        for month in range(1, 13):
            url = f"https://s3.amazonaws.com/tripdata/{year}{month:02d}-citibike-tripdata.csv.zip"
            df = pd.concat([df, pd.read_csv(url, compression="zip", header=0)])
            if len(df) > num_documents:
                break
        if len(df) > num_documents:
            break

    # Sample data to be inserted
    sample_data = df.sample(n=num_documents, random_state=1)
    sample_data = sample_data.to_dict(orient="records")

    # Delete original DataFrame to save memory
    if args.truncate:
        del df

    logging.info("Data loaded into memory successfully")

except Exception as e:
    logging.error("Data loading failed: %s", e)
    sys.exit(1)

# MongoDB connection details
mongo_uri = "change-mongo-uri"
mongo_client = pymongo.MongoClient(mongo_uri)
if mongo_client.admin.command("hello"):
    logging.info("MongoDB connection: Success")
else:
    logging.error("MongoDB connection: Failed")
    sys.exit(1)

# DocDB connection details
docdb_uri = "change-docdb-uri"
docdb_client = pymongo.MongoClient(docdb_uri)
if docdb_client.admin.command("hello"):
    logging.info("DocDB connection: Success")
else:
    logging.error("DocDB connection: Failed")
    sys.exit(1)

clients = {"MongoDB": mongo_client, "DocDB": docdb_client}

# Specify the database and collection name and the number of documents to insert
database_name = "change-your-database"
collection_name = "loadtest"

logging.info("Starting write operations...")

try:
    # Iterate over the clients and perform the write operation
    for name, client in clients.items():
        # Connect to the specified database and collection
        db = client.get_database(database_name)

        # Create the collection if it does not exist
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

        collection = db.get_collection(collection_name)

        elapsed_times = []

        for frequency in range(args.iter):

            # Perform write operation and measure the time
            start_time = datetime.now()

            # Insert the sample data into the collection
            if args.specify_id:
                collection.bulk_write([
                pymongo.UpdateOne(
                    {"_id": row["Bike ID"]},
                    {"$set": row},
                    upsert=True,
                ) for row in sample_data
            ])
            else:
                collection.insert_many(sample_data)
            
            # Calculate the elapsed time
            elapsed_time = datetime.now() - start_time
            elapsed_times.append(elapsed_time.total_seconds())

            # Drop the collection
            if args.truncate:
                collection.drop()
            else:
                # shuffling the data to avoid duplicate key error
                sample_data = df.sample(n=num_documents).to_dict(orient="records")

        # Calculate the average elapsed time
        avg_elapsed_time = sum(elapsed_times) / len(elapsed_times)

        logging.info(
            "Database: %s\nNumber of documents inserted: %d\nElapsed time: %f seconds\nInsertion rate: %f documents per second",
            name,
            num_documents,
            avg_elapsed_time,
            num_documents / avg_elapsed_time,
        )

        # Clean up - drop the collection
        if collection_name in db.list_collection_names():
            collection.drop()

        # Close the client connection
        client.close()

    logging.info("Write operations completed successfully")

except Exception as e:
    logging.error("Write operations failed: %s", e)
