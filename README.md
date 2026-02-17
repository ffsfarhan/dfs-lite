# DFS-Lite

Distributed File Storage System with Chunking, Replication, Integrity Verification, and Self-Healing.

## Features

- File chunking with configurable chunk size
- Multi-node replication
- SHA-256 integrity verification
- Read repair (self-healing)
- REST API using FastAPI
- PostgreSQL metadata storage

## Architecture

- FastAPI backend
- PostgreSQL for metadata
- Local simulated storage nodes
- SHA-256 hashing for integrity validation

## Endpoints

POST /upload
GET /download/{file_id}
GET /files
GET /files/{file_id}

## Run Locally

Create virtual environment:

    python -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Run server:

    uvicorn app.main:app --reload
