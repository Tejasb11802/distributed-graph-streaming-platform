#  Distributed Graph Streaming Platform

**Tejas Bhanushali** | ASU MS Data Science, Analytics & Engineering | May 2026

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-Streaming-black)](https://kafka.apache.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-green)](https://neo4j.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-blue)](https://kubernetes.io)

---

## What is this?

A distributed real-time data streaming pipeline that ingests NYC taxicab trip data through Apache Kafka, stores and queries it as a graph in Neo4j, and orchestrates the entire infrastructure on Kubernetes.

Built as a group course project for ASU's optimization and distributed systems curriculum.

---

## Architecture

NYC Taxicab Parquet Dataset (54MB, March 2022)
|
data_producer.py
(Kafka Producer - streams
trip records every 250ms)
|
Apache Kafka (Topic: nyc_taxicab_data)
Running on Kubernetes via Zookeeper
|
Kafka-Neo4j Connector
(Streams messages into graph database)
|
Neo4j Graph DB
(Trip nodes, location relationships,
fare and distance properties)
|
interface.py
(Query and interact with the graph)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Message streaming | Apache Kafka |
| Stream coordination | Apache Zookeeper |
| Graph database | Neo4j |
| Container orchestration | Kubernetes |
| Data format | Apache Parquet (PyArrow) |
| Language | Python 3.10+ |
| Infrastructure config | YAML (Kubernetes manifests) |
| Testing | Custom rubric-based test suite |

---

## Dataset

NYC Yellow Taxi Trip Data - March 2022

Filtered to Bronx borough trips only:
- Trip distance greater than 0.1 miles
- Fare amount greater than $2.50
- Fields: pickup/dropoff datetime, pickup/dropoff location ID, trip distance, fare amount

---

## Project Structure

| File | Description |
|---|---|
| `data_producer.py` | Kafka producer — streams trip records from Parquet file to Kafka topic |
| `data_loader.py` | Loads and preprocesses the Parquet dataset |
| `interface.py` | Query interface for interacting with Neo4j graph |
| `tester.py` | Comprehensive test suite — validates Kafka, Neo4j, and connector (100 point rubric) |
| `neo4j-service.yaml` | Kubernetes service manifest for Neo4j deployment |
| `Dockerfile` | Container definition for pipeline components |

---

## Infrastructure Components

**Step 1 — Kubernetes Infrastructure**
- Zookeeper deployment and service
- Kafka deployment and service
- Kafka connectivity verification

**Step 2 — Neo4j Graph Database**
- Neo4j deployment on Kubernetes
- Bolt protocol connectivity on port 7687
- HTTP interface on port 7474

**Step 3 — Kafka-Neo4j Connector**
- Streams Kafka topic messages directly into Neo4j graph nodes
- Automatic relationship creation between pickup and dropoff locations

**Step 4 — Data Production**
- Reads NYC taxicab Parquet file
- Filters Bronx trips
- Streams each trip as a JSON message to Kafka every 250ms

**Step 5 — End-to-End Validation**
- Verifies messages in Kafka topic
- Verifies graph nodes created in Neo4j

---

## How to Run

**Prerequisites:**
- Kubernetes cluster (Minikube or cloud)
- kubectl configured
- Python 3.10+

**Install dependencies:**
```bash
pip install confluent-kafka pyarrow pandas neo4j
```

**Deploy infrastructure:**
```bash
kubectl apply -f neo4j-service.yaml
```

**Run the producer:**
```bash
python data_producer.py
```

**Run the test suite:**
```bash
python tester.py
```

---

## Key Concepts Demonstrated

- **Event-driven architecture** — Kafka decouples data production from consumption
- **Graph data modeling** — NYC trip locations modeled as nodes, trips as relationships
- **Container orchestration** — full infrastructure defined as Kubernetes manifests
- **Real-time streaming** — 250ms producer interval simulates live sensor/event data
- **Distributed systems** — Zookeeper coordinates Kafka broker state

---

## About

Group project for ASU distributed systems and optimization coursework.

**Tejas Bhanushali**
MS Data Science, Analytics & Engineering — Arizona State University (GPA 3.80)
Graduating May 2026 | Tempe, AZ

[LinkedIn](https://linkedin.com/in/tejas-b-6a28aa263/) · [GitHub](https://github.com/Tejasb11802)
