import pyarrow.parquet as pq
import pandas as pd
from neo4j import GraphDatabase
import time


class DataLoader:
    def __init__(self, uri, user, password):
        """Connect to the Neo4j database"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.driver.verify_connectivity()

    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()

    def _create_constraints(self):
        """Ensure unique Location(name) constraint"""
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT location_name IF NOT EXISTS
                FOR (l:Location)
                REQUIRE l.name IS UNIQUE
            """)

    def load_transform_file(self, file_path):
        """Load Parquet → CSV → Neo4j"""
        # --- Read and filter parquet ---
        trips = pq.read_table(file_path).to_pandas()
        trips = trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime',
                       'PULocationID', 'DOLocationID',
                       'trip_distance', 'fare_amount']]

        bronx = [3, 18, 20, 31, 32, 46, 47, 51, 58, 59, 60, 69, 78, 81, 94,
                 119, 126, 136, 147, 159, 167, 168, 169, 174, 182, 183, 184,
                 185, 199, 200, 208, 212, 213, 220, 235, 240, 241, 242, 247,
                 248, 250, 254, 259]
        trips = trips[
            trips.iloc[:, 2].isin(bronx) & trips.iloc[:, 3].isin(bronx)
        ]
        trips = trips[trips['trip_distance'] > 0.1]
        trips = trips[trips['fare_amount'] > 2.5]

        # --- Convert date/time to string form ---
        trips['tpep_pickup_datetime'] = trips['tpep_pickup_datetime'].astype(str)
        trips['tpep_dropoff_datetime'] = trips['tpep_dropoff_datetime'].astype(str)

        # --- Write CSV into Neo4j import dir ---
        csv_name = "yellow_tripdata_2022-03.csv"
        save_loc = f"/var/lib/neo4j/import/{csv_name}"
        trips.to_csv(save_loc, index=False)

        self._create_constraints()

        csv_url = f"file:///{csv_name}"

        # --- Cypher for Neo4j 5 (CALL {...} IN TRANSACTIONS) ---
        cypher = """
        CALL {
            LOAD CSV WITH HEADERS FROM $csv AS row
             WITH row
             WHERE row.PULocationID IS NOT NULL AND row.DOLocationID IS NOT NULL
             MERGE (start:Location {name: toInteger(row.PULocationID)})
            MERGE (end:Location {name: toInteger(row.DOLocationID)})
            CREATE (start)-[:TRIP {
                pickup_dt: datetime(replace(row.tpep_pickup_datetime, " ", "T")),
                dropoff_dt: datetime(replace(row.tpep_dropoff_datetime, " ", "T")),
                distance: toFloat(row.trip_distance),
                fare: toFloat(row.fare_amount)
            }]->(end)
        } IN TRANSACTIONS OF 1000 ROWS;
        """

        with self.driver.session() as session:
            result = session.run(cypher, csv=csv_url)
            print("Data successfully imported into Neo4j.")



def main():
    total_attempts = 10
    attempt = 0

    while attempt < total_attempts:
        try:
            loader = DataLoader("neo4j://localhost:7687", "neo4j", "graphprocessing")
            loader.load_transform_file("yellow_tripdata_2022-03.parquet")
            loader.close()
            break
        except Exception as e:
            print(f"(Attempt {attempt+1}/{total_attempts}) Error: ", e)
            attempt += 1
            time.sleep(10)


if __name__ == "__main__":
    main()
