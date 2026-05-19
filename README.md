# DFS Lite — Distributed File Storage System

## Overview

DFS Lite is a distributed file storage and monitoring system built using FastAPI, React, Docker, and Jenkins. The system simulates a fault-tolerant distributed storage cluster with chunk replication, integrity verification, automated repair mechanisms, and real-time monitoring capabilities.

The project demonstrates core distributed systems concepts including replication, redundancy, node failure handling, integrity validation, and self-healing storage recovery, while also integrating modern DevOps workflows using Docker containerization and Jenkins CI pipelines.

---

## Architecture

The project consists of:

- Frontend: React + Vite monitoring dashboard
- Backend: FastAPI REST API server
- Database: SQLite metadata storage
- Storage Layer: Multi-node distributed storage simulation
- Containerization: Docker and Docker Compose
- CI/CD: Jenkins pipeline integration

---

## Core Features

### Distributed File Storage
- Chunk-based file storage architecture
- File replication across multiple storage nodes
- Distributed node simulation

### Fault Tolerance
- Replica redundancy for file recovery
- Node online/offline simulation
- Cluster degradation detection

### Integrity Verification
- SHA-256 checksum validation
- Corruption detection mechanisms
- Integrity-aware retrieval system

### Self-Healing Storage
- Background repair daemon
- Continuous integrity scanning
- Automatic replica restoration from healthy nodes

### Monitoring Dashboard
- Real-time cluster monitoring
- Node health visualization
- File health tracking
- Upload, download, and deletion operations
- Dynamic cluster status computation

### REST API
- File upload API
- File download API
- File deletion API
- Cluster health API
- Node management API

### DevOps Integration
- Dockerized frontend and backend services
- Docker Compose orchestration
- Jenkins CI pipeline
- Automated Docker image builds

---

## Technology Stack

### Backend
- FastAPI
- Python
- SQLAlchemy
- SQLite

### Frontend
- React
- Vite
- CSS

### DevOps
- Docker
- Docker Compose
- Jenkins
- GitHub

---

## Project Structure

```text
dfs-project/
│
├── dfs-lite/                 # FastAPI backend
│   ├── app/
│   ├── storage/
│   ├── Dockerfile
│   └── requirements.txt
│
├── dfs-frontend/             # React frontend
│   ├── src/
│   ├── public/
│   └── Dockerfile
│
├── Jenkinsfile               # Jenkins CI pipeline
├── docker-compose.yml
└── README.md
```

---

## Running the Project

### Prerequisites

- Docker
- Docker Compose
- Git

---

## Clone Repository

```bash
git clone https://github.com/ffsfarhan/dfs-lite.git
cd dfs-lite
```

---

## Run Using Docker Compose

```bash
docker compose up
```

---

## Access Application

### Frontend
http://localhost:5173

### Backend API
http://localhost:8000

### Swagger Documentation
http://localhost:8000/docs

### Jenkins
http://localhost:8080

---

## Jenkins CI Pipeline

The Jenkins pipeline performs:

1. Repository cloning from GitHub
2. Backend Docker image build
3. Frontend Docker image build
4. CI pipeline validation

Pipeline configuration is defined in:

```text
Jenkinsfile
```

---

## Demonstrating Fault Tolerance and Self-Healing

### Simulate Node Failure

Delete storage contents from one node:

```bash
rm -rf storage/node2/*
```

The repair daemon will:
- Detect missing replicas
- Restore lost chunks automatically
- Recover cluster redundancy

### Verify Recovery

```bash
find storage
```

---

## API Endpoints

### Cluster Health

```http
GET /cluster/health
```

### List Files

```http
GET /files
```

### List Nodes

```http
GET /nodes
```

### Upload File

```http
POST /upload
```

### Delete File

```http
DELETE /delete/{file_id}
```

---

## Educational Concepts Demonstrated

- Distributed Storage Systems
- Fault Tolerance
- Replication
- Data Integrity Verification
- Self-Healing Architectures
- REST API Design
- Containerization
- CI/CD Pipelines
- Monitoring Systems

---

## Future Improvements

- Kubernetes deployment
- Distributed consensus implementation
- Load balancing
- Object storage abstraction
- Authentication and authorization
- Persistent distributed databases
- Real-time websocket monitoring

---

## Author

Farhan

GitHub: https://github.com/ffsfarhan
