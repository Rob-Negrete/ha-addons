# TinyDB Storage Analysis & Optimization Recommendations

## 🔍 Current Storage Issues Identified

### **Data Stored Per Face Record:**

1. **Base64 JPEG Thumbnail** (160x160px, quality=85): ~15-25KB each
2. **512-dimensional Embedding Array**: ~2KB each (512 floats)
3. **Metadata**: Face ID, event ID, timestamps, bounding boxes, quality metrics: ~0.5KB

**Total per face: ~17-27KB**

### **Volume Calculation:**

- With 2,500 faces → 42-67MB (explains the 65MB corrupted file!)
- High event volume = frequent writes to single JSON file
- TinyDB loads entire JSON into memory for each operation

## 📊 Storage Inefficiency Analysis

### 1. **Unnecessary Base64 Storage in TinyDB** ❌

- **Current**: Storing 15-25KB base64 thumbnails directly in JSON
- **Problem**: Makes JSON files massive and slow to parse
- **Solution**: Store thumbnails as separate JPEG files, reference by path

### 2. **Duplicate Embedding Storage** ❌

- **Current**: Embeddings stored in both TinyDB AND FAISS index
- **Problem**: 2KB per face duplicated across systems
- **Solution**: Store embeddings only in FAISS, reference by index

### 3. **Single JSON File Bottleneck** ❌

- **Current**: All data in one JSON file with no concurrent access protection
- **Problem**: Corruption risk during high-volume writes
- **Solution**: Migrate to proper database with transaction support

### 4. **No Data Partitioning** ❌

- **Current**: All historical faces in one file
- **Problem**: File size grows indefinitely
- **Solution**: Implement data archiving/partitioning strategies

## 🎯 Optimization Strategies

### **Immediate Wins (No DB Migration)**

#### 1. **File-Based Thumbnail Storage**

```python
# Instead of storing base64 in TinyDB:
"thumbnail": "/config/face-rekon/thumbnails/{face_id}.jpg"

# Reduces TinyDB record size by 90%+
```

#### 2. **Remove Embedding Duplication**

```python
# Remove from TinyDB record:
# "embedding": face_data["embedding"].tolist(),  # DELETE THIS

# Keep only FAISS index + mapping
# Reduces record size by additional 2KB per face
```

#### 3. **Optimized TinyDB Records**

```python
# Minimal record (metadata only):
{
    "face_id": "uuid",
    "event_id": "event_123",
    "timestamp": 1234567890,
    "name": "Person Name",
    "thumbnail_path": "/thumbnails/{face_id}.jpg",
    "faiss_index": 42,  # Position in FAISS index
    "face_bbox": [x1, y1, x2, y2],
    "quality_score": 0.85
}
# Size: ~0.5KB vs current ~20KB = 97% reduction!
```

### **Database Migration Options**

#### **Option 1: SQLite** 🌟 (Recommended for HA)

```sql
-- Face metadata table
CREATE TABLE faces (
    face_id TEXT PRIMARY KEY,
    event_id TEXT,
    timestamp INTEGER,
    name TEXT,
    thumbnail_path TEXT,
    faiss_index INTEGER,
    bbox_x1 INTEGER, bbox_y1 INTEGER,
    bbox_x2 INTEGER, bbox_y2 INTEGER,
    quality_score REAL
);

-- Separate embeddings table (if needed)
CREATE TABLE embeddings (
    face_id TEXT PRIMARY KEY,
    embedding BLOB  -- Store as binary instead of JSON
);
```

**Benefits:**

- ✅ ACID transactions (no corruption)
- ✅ Concurrent access support
- ✅ 100x faster than TinyDB for large datasets
- ✅ Built into Python (no dependencies)
- ✅ Perfect for Home Assistant environment

#### **Option 2: MongoDB** 🔥 (For Advanced Setups)

```javascript
{
  _id: ObjectId,
  face_id: "uuid",
  event_id: "event_123",
  timestamp: ISODate,
  name: "Person Name",
  thumbnail_path: "/thumbnails/{face_id}.jpg",
  faiss_index: 42,
  face_bbox: [x1, y1, x2, y2],
  quality_metrics: { overall: 0.85, blur: 0.9 }
}

// Vector search support with MongoDB Atlas
db.faces.createIndex({
  "embedding": "vectorSearch"
})
```

**Benefits:**

- ✅ Native JSON document support
- ✅ Vector search capabilities (can replace FAISS)
- ✅ Horizontal scaling
- ✅ Rich querying capabilities
- ❌ Heavier deployment footprint

#### **Option 3: PostgreSQL + pgvector** 🚀 (Enterprise Grade)

```sql
CREATE EXTENSION vector;

CREATE TABLE faces (
    face_id UUID PRIMARY KEY,
    event_id TEXT,
    timestamp TIMESTAMPTZ,
    name TEXT,
    thumbnail_path TEXT,
    embedding vector(512),  -- Native vector type!
    face_bbox BOX,
    quality_score REAL
);

-- Vector similarity index
CREATE INDEX faces_embedding_idx
ON faces USING ivfflat (embedding vector_cosine_ops);

-- Query similar faces
SELECT face_id, name, 1 - (embedding <=> $1) AS similarity
FROM faces
ORDER BY embedding <=> $1
LIMIT 10;
```

**Benefits:**

- ✅ Native vector operations (replaces FAISS)
- ✅ ACID compliance + concurrency
- ✅ Advanced SQL querying
- ✅ Excellent performance at scale
- ❌ More complex deployment

## 🎯 **Recommended Migration Path**

### **Phase 1: Immediate Optimization (This Week)**

1. ✅ Keep TinyDB for metadata only
2. ✅ Move thumbnails to separate JPEG files
3. ✅ Remove embedding duplication from TinyDB
4. ✅ Implement data cleanup/archiving

**Expected Result:** 95% reduction in TinyDB file size (65MB → 3MB)

### **Phase 2: SQLite Migration (Next Sprint)**

1. ✅ Migrate to SQLite for metadata
2. ✅ Keep FAISS for vector search
3. ✅ Add proper indexing and queries
4. ✅ Implement database migration script

**Expected Result:** Eliminate corruption risk, 10x performance improvement

### **Phase 3: Advanced Features (Future)**

1. ⭐ Consider PostgreSQL + pgvector for advanced deployments
2. ⭐ Implement face clustering and analytics
3. ⭐ Add real-time face recognition dashboards

## 💡 **Implementation Priority**

| Priority  | Change                       | Impact                   | Effort |
| --------- | ---------------------------- | ------------------------ | ------ |
| 🔥 HIGH   | File-based thumbnails        | 90% size reduction       | Low    |
| 🔥 HIGH   | Remove embedding duplication | Additional 10% reduction | Low    |
| 🚀 MEDIUM | SQLite migration             | Eliminate corruption     | Medium |
| ⭐ LOW    | PostgreSQL/MongoDB           | Advanced features        | High   |

## 📝 **Next Steps**

1. Implement file-based thumbnail storage
2. Create database migration utilities
3. Add data archiving for old records
4. Monitor performance improvements

Would you like me to implement the immediate optimizations first?
