# DFS Lite 🚀

A Distributed File Storage system built with FastAPI and PostgreSQL featuring replication, integrity verification, self-healing, node management, and background repair.

---

## 🔥 Features Implemented

### 📦 1. File Upload with Chunking
- Files are split into 1MB chunks
- Each chunk is stored independently
- Metadata stored in PostgreSQL

### 🔁 2. Replication
- Configurable replication factor
- Chunks are distributed across multiple storage nodes
- Dynamic node selection from database

### 🔐 3. Integrity Verification
- SHA-256 hashing for every chunk
- Hash stored in DB
- Verified on every download

### 🩺 4. Self-Healing (Read Repair)
- During download:
  - If one replica is corrupted → system auto-recovers using healthy copy
  - Corrupted replica is repaired automatically
- If all replicas corrupted → file marked as DEAD

### 🔄 5. Background Repair Daemon
- Runs continuously in background
- Periodically scans all chunks
- Repairs corrupted replicas automatically
- Updates file health status

### 🟢 6. File Health States
Files can be:
- `HEALTHY`
- `DEGRADED`
- `DEAD`

Health updates automatically during:
- Download
- Background repair scans

### 🗂 7. Node Management
- Nodes stored in database
- Nodes can be:
  - Online
  - Offline
- Upload only uses online nodes
- Simulated node failure supported

### 📊 8. Health API
- List files
- File metadata endpoint
- List nodes
- Node status tracking

---

## 🏗 Architecture

FastAPI + SQLAlchemy  
PostgreSQL  
Local filesystem storage nodes  
Background repair daemon (threaded)

---

## 🧪 How to Run

### 1. Clone
```bash
git clone git@github.com:ffsfarhan/dfs-lite.git
cd dfs-lite

