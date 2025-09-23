"""
Qdrant Vector Database Adapter for Face Recognition

This module provides a unified interface to Qdrant vector database,
replacing both TinyDB and FAISS for face embedding storage and search.

Key Features:
- Unified storage for face metadata and embeddings
- Built-in similarity search with filtering
- Automatic collection management
- Backward compatibility with existing API
- Configurable distance thresholds
"""

import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)

# Configuration from environment variables
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_PATH = os.environ.get("QDRANT_PATH", "/config/face-rekon/qdrant")
USE_EMBEDDED_QDRANT = (
    os.environ.get("FACE_REKON_USE_EMBEDDED_QDRANT", "true").lower() == "true"
)
COLLECTION_NAME = "faces"
EMBEDDING_SIZE = 512  # InsightFace embedding dimension

# Face recognition thresholds
FACE_SIMILARITY_THRESHOLD = float(
    os.environ.get("FACE_REKON_SIMILARITY_THRESHOLD", "0.35")
)
BORDERLINE_THRESHOLD = float(os.environ.get("FACE_REKON_BORDERLINE_THRESHOLD", "0.50"))
DEDUPLICATION_WINDOW = int(os.environ.get("FACE_REKON_DEDUPLICATION_WINDOW", "60"))


class QdrantAdapter:
    """
    Qdrant vector database adapter for face recognition.

    Replaces TinyDB + FAISS with a single vector database that handles
    both metadata storage and similarity search.
    """

    def __init__(self):
        """Initialize Qdrant client and create collection if needed."""
        self.client = None
        self._connect_with_retry()
        self._ensure_collection()

    def _connect_with_retry(self, max_retries: int = 5):
        """Connect to Qdrant with retry logic."""
        if USE_EMBEDDED_QDRANT:
            try:
                # Use embedded mode - no server needed
                os.makedirs(QDRANT_PATH, exist_ok=True)
                self.client = QdrantClient(path=QDRANT_PATH)
                logger.info(f"✅ Connected to embedded Qdrant at {QDRANT_PATH}")
                return
            except Exception as e:
                # Check if it's a storage lock conflict (common during Flask reloads)
                if "already accessed by another instance" in str(e):
                    logger.warning(
                        f"⚠️ Qdrant storage locked (likely Flask reload): {e}"
                    )
                    logger.info(
                        "🔄 This is normal during development - falling back to FAISS"
                    )
                else:
                    logger.error(f"❌ Failed to initialize embedded Qdrant: {e}")
                raise
        else:
            # Use remote server mode (original behavior)
            for attempt in range(max_retries):
                try:
                    self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                    # Test connection
                    self.client.get_collections()
                    logger.info(
                        f"✅ Connected to Qdrant server at {QDRANT_HOST}:{QDRANT_PORT}"
                    )
                    return
                except Exception as e:
                    logger.warning(
                        f"⚠️ Qdrant connection attempt {attempt + 1}/{max_retries} "
                        f"failed: {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(2**attempt)  # Exponential backoff
                    else:
                        logger.error(
                            "❌ Failed to connect to Qdrant server after all retries"
                        )
                        raise

    def _ensure_collection(self):
        """Create the faces collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if COLLECTION_NAME not in collection_names:
                logger.info(f"🔧 Creating Qdrant collection: {COLLECTION_NAME}")
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=EMBEDDING_SIZE, distance=models.Distance.COSINE
                    ),
                )
                logger.info(f"✅ Created collection {COLLECTION_NAME}")
            else:
                logger.info(f"✅ Collection {COLLECTION_NAME} already exists")

        except Exception as e:
            logger.error(f"❌ Failed to ensure collection: {e}")
            raise

    def save_face(self, face_data: Dict[str, Any], embedding: np.ndarray) -> str:
        """
        Save a face with metadata and embedding to Qdrant.

        Args:
            face_data: Face metadata (name, event_id, timestamp, etc.)
            embedding: Face embedding vector

        Returns:
            face_id: Unique identifier for the saved face
        """
        try:
            face_id = face_data.get("face_id", str(uuid.uuid4()))

            # Prepare payload (metadata)
            payload = {
                "face_id": face_id,
                "name": face_data.get("name", "unknown"),
                "event_id": face_data.get("event_id", "unknown"),
                "timestamp": face_data.get("timestamp", int(time.time())),
                "image_path": face_data.get("image_path"),
                "thumbnail": face_data.get("thumbnail"),
                "thumbnail_path": face_data.get("thumbnail_path"),
                "notes": face_data.get("notes", ""),
                "confidence": face_data.get("confidence", 0.0),
                "quality_metrics": face_data.get("quality_metrics", {}),
                "face_bbox": face_data.get("face_bbox", []),
                "created_at": int(time.time()),
            }

            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            # Insert point with embedding and metadata
            # Convert face_id to valid UUID string for Qdrant
            try:
                point_id = (
                    str(uuid.UUID(face_id)) if "-" in face_id else str(uuid.uuid4())
                )
            except ValueError:
                point_id = str(uuid.uuid4())

            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=point_id, vector=embedding.tolist(), payload=payload
                    )
                ],
            )

            logger.info(f"💾 Saved face {face_id} to Qdrant")
            return face_id

        except Exception as e:
            logger.error(f"❌ Failed to save face to Qdrant: {e}")
            raise

    def search_similar_faces(
        self, embedding: np.ndarray, limit: int = 1, score_threshold: float = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar faces using vector similarity.

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of (face_id, similarity_score, metadata) tuples
        """
        try:
            if score_threshold is None:
                score_threshold = (
                    1.0 - BORDERLINE_THRESHOLD
                )  # Convert distance to score

            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=embedding.tolist(),
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )

            matches = []
            for result in results:
                similarity_score = result.score
                distance = 1.0 - similarity_score  # Convert score back to distance
                face_id = result.payload["face_id"]
                metadata = result.payload

                matches.append((face_id, distance, metadata))

            logger.info(f"🔍 Found {len(matches)} similar faces")
            return matches

        except Exception as e:
            logger.error(f"❌ Failed to search similar faces: {e}")
            return []

    def get_face(self, face_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a face by ID.

        Args:
            face_id: Face identifier

        Returns:
            Face metadata dict or None if not found
        """
        try:
            # Since we may not have a direct UUID mapping, we need to search by face_id
            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="face_id", match=models.MatchValue(value=face_id)
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
            )

            if results[0]:
                return results[0][0].payload
            return None

        except Exception as e:
            logger.error(f"❌ Failed to get face {face_id}: {e}")
            return None

    def update_face(self, face_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update face metadata.

        Args:
            face_id: Face identifier
            updates: Fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current face data and point ID
            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="face_id", match=models.MatchValue(value=face_id)
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
            )

            if not results[0]:
                logger.warning(f"⚠️ Face {face_id} not found for update")
                return False

            point = results[0][0]
            current = point.payload
            point_id = point.id

            # Merge updates
            current.update(updates)
            current["updated_at"] = int(time.time())

            # Update payload (keep existing vector)
            self.client.set_payload(
                collection_name=COLLECTION_NAME, points=[point_id], payload=current
            )

            logger.info(f"✅ Updated face {face_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update face {face_id}: {e}")
            return False

    def get_unclassified_faces(self) -> List[Dict[str, Any]]:
        """
        Get all faces with name="unknown".

        Returns:
            List of unclassified face metadata
        """
        try:
            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="name", match=models.MatchValue(value="unknown")
                        )
                    ]
                ),
                with_payload=True,
                limit=1000,  # Adjust based on expected volume
            )

            faces = [point.payload for point in results[0]]
            logger.info(f"📋 Found {len(faces)} unclassified faces")
            return faces

        except Exception as e:
            logger.error(f"❌ Failed to get unclassified faces: {e}")
            return []

    def delete_face(self, face_id: str) -> bool:
        """
        Delete a face from the database.

        Args:
            face_id: Face identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the point ID for this face_id
            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="face_id", match=models.MatchValue(value=face_id)
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
            )

            if not results[0]:
                logger.warning(f"⚠️ Face {face_id} not found for deletion")
                return False

            point_id = results[0][0].id

            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.PointIdsList(points=[point_id]),
            )

            logger.info(f"🗑️ Deleted face {face_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete face {face_id}: {e}")
            return False

    def check_recent_detection(self, event_id: str) -> bool:
        """
        Check if there are recent detections from the same event.

        Args:
            event_id: Event identifier

        Returns:
            True if recent detection found, False otherwise
        """
        if not DEDUPLICATION_WINDOW or DEDUPLICATION_WINDOW <= 0:
            return False

        try:
            current_time = int(time.time())
            cutoff_time = current_time - DEDUPLICATION_WINDOW

            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="event_id", match=models.MatchValue(value=event_id)
                        ),
                        models.FieldCondition(
                            key="timestamp", range=models.Range(gte=cutoff_time)
                        ),
                    ]
                ),
                limit=1,
            )

            has_recent = len(results[0]) > 0
            if has_recent:
                logger.info(
                    f"🚫 Found recent detection for event {event_id} "
                    f"within {DEDUPLICATION_WINDOW}s"
                )

            return has_recent

        except Exception as e:
            logger.error(f"❌ Failed to check recent detection: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Statistics dict
        """
        try:
            collection_info = self.client.get_collection(COLLECTION_NAME)

            return {
                "total_faces": collection_info.points_count,
                "status": "healthy",
                "collection_name": COLLECTION_NAME,
                "embedding_size": EMBEDDING_SIZE,
                "similarity_threshold": FACE_SIMILARITY_THRESHOLD,
                "borderline_threshold": BORDERLINE_THRESHOLD,
                "deduplication_window": DEDUPLICATION_WINDOW,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {"status": "error", "error": str(e)}


# Global adapter instance
qdrant_adapter = None


def get_qdrant_adapter() -> QdrantAdapter:
    """Get or create the global Qdrant adapter instance."""
    global qdrant_adapter
    if qdrant_adapter is None:
        qdrant_adapter = QdrantAdapter()
    return qdrant_adapter
