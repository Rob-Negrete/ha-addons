import base64
import io
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image

# Qdrant vector database (required)
from qdrant_adapter import get_qdrant_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

logger.info("✅ Qdrant adapter available")

# Configuración de rutas (con soporte para variables de entorno para testing)
BASE_PATH = os.environ.get(
    "FACE_REKON_BASE_PATH", "/config/face-rekon/faces"
)  # noqa: E501
UNKNOWN_PATH = os.environ.get(
    "FACE_REKON_UNKNOWN_PATH", "/config/face-rekon/unknowns"
)  # noqa: E501
THUMBNAIL_PATH = os.environ.get(
    "FACE_REKON_THUMBNAIL_PATH", "/config/face-rekon/thumbnails"
)  # noqa: E501

# Storage optimization configuration
USE_OPTIMIZED_STORAGE = (
    os.environ.get("FACE_REKON_USE_OPTIMIZED_STORAGE", "true").lower() == "true"
)

# Qdrant is now the only storage backend

THUMBNAIL_SIZE = (160, 160)

# Face quality thresholds
MIN_FACE_SIZE = int(
    os.environ.get("FACE_REKON_MIN_FACE_SIZE", "50")
)  # Minimum face width/height in pixels
MIN_BLUR_THRESHOLD = float(
    os.environ.get("FACE_REKON_MIN_BLUR_THRESHOLD", "50.0")
)  # Laplacian variance threshold
MIN_DETECTION_CONFIDENCE = float(
    os.environ.get("FACE_REKON_MIN_DETECTION_CONFIDENCE", "0.5")
)  # InsightFace confidence
MIN_QUALITY_SCORE = float(
    os.environ.get("FACE_REKON_MIN_QUALITY_SCORE", "0.3")
)  # Overall quality threshold (0.0-1.0)

# Face recognition similarity threshold (lower = more permissive matching)
FACE_SIMILARITY_THRESHOLD = float(
    os.environ.get("FACE_REKON_SIMILARITY_THRESHOLD", "0.35")
)  # Distance threshold for face matching (0.0-1.0, default: 0.35)

# Time-based deduplication window (seconds)
DEDUPLICATION_WINDOW = int(
    os.environ.get("FACE_REKON_DEDUPLICATION_WINDOW", "60")
)  # Skip saving faces detected within this window

# Enhanced thumbnail generation configuration
USE_SUPER_RESOLUTION = (
    os.environ.get("FACE_REKON_USE_SUPER_RESOLUTION", "false").lower() == "true"
)  # Enable super-resolution for small faces
SR_THRESHOLD = int(
    os.environ.get("FACE_REKON_SR_THRESHOLD", "100")
)  # Apply SR to faces smaller than this
ADAPTIVE_INTERPOLATION = (
    os.environ.get("FACE_REKON_ADAPTIVE_INTERPOLATION", "true").lower() == "true"
)  # Use adaptive interpolation (always recommended)

# Borderline match threshold for smart grouping suggestions
BORDERLINE_THRESHOLD = float(
    os.environ.get("FACE_REKON_BORDERLINE_THRESHOLD", "0.50")
)  # Suggest grouping between SIMILARITY and BORDERLINE thresholds

# Inicializar InsightFace
logger.info("🚀 Initializing InsightFace...")
try:
    app = FaceAnalysis(allowed_modules=["detection", "recognition"])
    app.prepare(ctx_id=0, det_size=(640, 640))  # Use CPU, set detection size
    logger.info("✅ FaceAnalysis instance created")
    logger.info("✅ InsightFace prepared successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize InsightFace: {e}")
    raise

# Lazy initialization for Qdrant adapter
_qdrant_adapter = None


def get_qdrant_adapter_instance():
    """Get Qdrant adapter instance with lazy initialization."""
    global _qdrant_adapter
    if _qdrant_adapter is None:
        logger.info("🚀 Initializing Qdrant vector database")
        try:
            _qdrant_adapter = get_qdrant_adapter()
            logger.info("✅ Qdrant adapter initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant: {e}")
            raise
    return _qdrant_adapter


def db_save_face(face_data: Dict[str, Any], embedding: np.ndarray) -> str:
    """Save face with metadata and embedding using Qdrant."""
    return get_qdrant_adapter_instance().save_face(face_data, embedding)


def db_search_similar(
    embedding: np.ndarray, limit: int = 1
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search for similar faces using Qdrant."""
    return get_qdrant_adapter_instance().search_similar_faces(embedding, limit)


def db_get_face(face_id: str) -> Optional[Dict[str, Any]]:
    """Get face metadata by ID using Qdrant."""
    return get_qdrant_adapter_instance().get_face(face_id)


def db_update_face(face_id: str, updates: Dict[str, Any]) -> bool:
    """Update face metadata using Qdrant."""
    return get_qdrant_adapter_instance().update_face(face_id, updates)


def db_get_unclassified_faces() -> List[Dict[str, Any]]:
    """Get unclassified faces using Qdrant."""
    return get_qdrant_adapter_instance().get_unclassified_faces()


def db_check_recent_detection(event_id: str) -> bool:
    """Check for recent detections using Qdrant."""
    return get_qdrant_adapter_instance().check_recent_detection(event_id)


def extract_face_embedding(image_path: str) -> Optional[np.ndarray]:
    """Extract face embedding from image using InsightFace.

    Args:
        image_path: Path to the image file

    Returns:
        Face embedding as numpy array, or None if no face found
    """
    try:
        logger.info(f"🔍 Extracting embedding from: {image_path}")

        # Read image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"❌ Could not read image: {image_path}")
            return None

        # Detect faces
        faces = app.get(img)
        if not faces:
            logger.warning(f"⚠️ No faces detected in: {image_path}")
            return None

        # Return embedding of first/best face
        face = faces[0]  # Take the first detected face
        embedding = face.embedding
        logger.info(f"✅ Extracted {len(embedding)}-dimensional embedding")

        return embedding

    except Exception as e:
        logger.error(f"❌ Error extracting embedding: {e}")
        return None


def calculate_face_quality_metrics(face_crop: np.ndarray) -> Dict[str, float]:
    """Calculate comprehensive face quality metrics.

    Args:
        face_crop: Cropped face image as numpy array

    Returns:
        Dictionary with quality metrics
    """
    try:
        # Convert to grayscale for analysis
        if len(face_crop.shape) == 3:
            gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_crop

        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 2. Face size (area)
        face_area = face_crop.shape[0] * face_crop.shape[1]

        # 3. Brightness (mean intensity)
        brightness = np.mean(gray)

        # 4. Contrast (standard deviation)
        contrast = np.std(gray)

        # 5. Overall quality score (normalized combination)
        # Normalize metrics to 0-1 range
        sharpness_score = min(laplacian_var / 100.0, 1.0)  # Cap at 100
        size_score = min(face_area / 10000.0, 1.0)  # Cap at 100x100 pixels
        brightness_score = 1.0 - abs(brightness - 128) / 128.0  # Optimal around 128
        contrast_score = min(contrast / 64.0, 1.0)  # Cap at 64

        # Weighted combination
        quality_score = (
            sharpness_score * 0.4
            + size_score * 0.2
            + brightness_score * 0.2
            + contrast_score * 0.2
        )

        return {
            "sharpness": float(laplacian_var),
            "face_area": float(face_area),
            "brightness": float(brightness),
            "contrast": float(contrast),
            "quality_score": float(quality_score),
        }

    except Exception as e:
        logger.error(f"❌ Error calculating quality metrics: {e}")
        return {
            "sharpness": 0.0,
            "face_area": 0.0,
            "brightness": 0.0,
            "contrast": 0.0,
            "quality_score": 0.0,
        }


# ============================================================================
# ENHANCED THUMBNAIL GENERATION - Hybrid Approach for Small Face Recognition
# ============================================================================


def apply_unsharp_mask(
    image: np.ndarray, amount: float = 0.7, radius: float = 1.0
) -> np.ndarray:
    """
    Apply unsharp mask to enhance edges and details.

    Unsharp masking formula: sharpened = original + amount * (original - blurred)

    Args:
        image: Input image as numpy array
        amount: Sharpening strength (0.0-2.0, recommended: 0.5-1.0)
        radius: Gaussian blur radius (recommended: 1.0-2.0)

    Returns:
        Sharpened image
    """
    try:
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(image, (0, 0), radius)

        # Unsharp mask: original + amount * (original - blurred)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)

        # Clip values to valid range [0, 255]
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

        return sharpened

    except Exception as e:
        logger.error(f"❌ Error applying unsharp mask: {e}")
        return image  # Return original on error


def apply_super_resolution(face_crop: np.ndarray, scale: int = 2) -> np.ndarray:
    """
    Apply super-resolution to upscale small faces.

    Uses Real-ESRGAN model for high-quality upscaling.
    This function is only called when USE_SUPER_RESOLUTION=true.

    Args:
        face_crop: Input face crop as numpy array
        scale: Upscaling factor (2 or 4)

    Returns:
        Super-resolved image
    """
    try:
        # Lazy import - only load when SR is enabled
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        # Initialize model (cached globally after first use)
        if not hasattr(apply_super_resolution, "model"):
            logger.info("🚀 Initializing Real-ESRGAN model...")

            # Use lightweight x2 model for faces
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=2,
            )

            model_path = os.environ.get(
                "FACE_REKON_SR_MODEL_PATH",
                "/app/models/RealESRGAN_x2plus.pth",
            )

            upsampler = RealESRGANer(
                scale=2,
                model_path=model_path,
                model=model,
                tile=0,  # No tiling for small faces
                tile_pad=10,
                pre_pad=0,
                half=False,  # Use FP32 for CPU
            )

            apply_super_resolution.model = upsampler
            logger.info("✅ Real-ESRGAN model loaded")

        # Apply super-resolution
        output, _ = apply_super_resolution.model.enhance(face_crop, outscale=scale)

        return output

    except ImportError:
        logger.warning(
            "⚠️ Real-ESRGAN not installed. Install with: "
            "pip install realesrgan basicsr"
        )
        return face_crop
    except Exception as e:
        logger.error(f"❌ Error in super-resolution: {e}")
        return face_crop  # Fallback to original


def create_enhanced_thumbnail_adaptive(
    face_crop: np.ndarray, target_size: Tuple[int, int] = (160, 160)
) -> np.ndarray:
    """
    Create enhanced thumbnail with adaptive interpolation for small faces.

    Strategy (EMPIRICALLY TESTED - based on actual sharpness retention):
    - Extreme upscaling (<100px, >1.6x scale): NEAREST + unsharp (retains ~116%)
    - Moderate upscaling (100-160px): CUBIC + unsharp (retains ~80%)
    - Light upscaling (160-300px): CUBIC + light unsharp (retains ~90%)
    - Downscaling (>300px): AREA (current method, retains ~100%)

    This dramatically improves quality for distant/small faces while
    maintaining quality for normal-sized faces.

    Args:
        face_crop: Source face crop as numpy array
        target_size: Target thumbnail size (default: 160x160)

    Returns:
        Enhanced thumbnail as numpy array
    """
    try:
        h, w = face_crop.shape[:2]
        max_dim = max(h, w)
        scale_factor = target_size[0] / max_dim

        # Determine interpolation method based on upscaling factor
        if max_dim < 100 and scale_factor > 1.6:
            # Extreme upscaling - NEAREST is surprisingly best!
            # For 57px → 160px (2.8x), NEAREST+unsharp retains 116% sharpness
            interpolation = cv2.INTER_NEAREST
            sharpen_amount = 0.7  # Moderate sharpening
            sharpen_radius = 1.0
            needs_sharpening = True
            logger.debug(
                f"🔍 Extreme upscaling ({max_dim}px, {scale_factor:.1f}x) - "
                f"using NEAREST + unsharp"
            )

        elif max_dim < target_size[0]:
            # Moderate upscaling - CUBIC works well
            interpolation = cv2.INTER_CUBIC
            sharpen_amount = 0.6
            sharpen_radius = 1.0
            needs_sharpening = True
            logger.debug(
                f"📏 Moderate upscaling ({max_dim}px, {scale_factor:.1f}x) - "
                f"using CUBIC + unsharp"
            )

        elif max_dim < target_size[0] * 2:
            # Light upscaling/resizing - CUBIC + light sharpening
            interpolation = cv2.INTER_CUBIC
            sharpen_amount = 0.4
            sharpen_radius = 0.8
            needs_sharpening = True
            logger.debug(
                f"📐 Light upscaling ({max_dim}px, {scale_factor:.1f}x) - "
                f"using CUBIC + light unsharp"
            )

        else:
            # Downscaling - AREA is best (current method)
            interpolation = cv2.INTER_AREA
            needs_sharpening = False
            logger.debug(
                f"📊 Downscaling ({max_dim}px, {scale_factor:.1f}x) - " f"using AREA"
            )

        # Resize to target size
        thumbnail = cv2.resize(face_crop, target_size, interpolation=interpolation)

        # Apply unsharp mask for upscaled images
        if needs_sharpening:
            thumbnail = apply_unsharp_mask(thumbnail, sharpen_amount, sharpen_radius)

        return thumbnail

    except Exception as e:
        logger.error(f"❌ Error in adaptive thumbnail creation: {e}")
        # Fallback to current method
        return cv2.resize(face_crop, target_size, interpolation=cv2.INTER_AREA)


def create_enhanced_thumbnail_hybrid(
    face_crop: np.ndarray, target_size: Tuple[int, int] = (160, 160)
) -> np.ndarray:
    """
    Hybrid thumbnail generation: Adaptive interpolation + optional super-resolution.

    Decision tree:
    1. IF USE_SUPER_RESOLUTION=true AND face < SR_THRESHOLD:
         Apply super-resolution (2x upscale) → then adaptive resize
    2. ELSE:
         Apply adaptive interpolation only

    This provides the best of both worlds:
    - Fast, high-quality enhancement for most cases (adaptive)
    - ML-powered restoration for critical tiny faces (SR)

    Args:
        face_crop: Source face crop as numpy array
        target_size: Target thumbnail size (default: 160x160)

    Returns:
        Enhanced thumbnail as numpy array
    """
    try:
        h, w = face_crop.shape[:2]
        max_dim = max(h, w)

        # Step 1: Check if super-resolution is needed and enabled
        if USE_SUPER_RESOLUTION and max_dim < SR_THRESHOLD:
            logger.info(
                f"🎯 Applying super-resolution to tiny face "
                f"({max_dim}px < {SR_THRESHOLD}px threshold)"
            )

            # Upscale 2x with SR
            face_crop = apply_super_resolution(face_crop, scale=2)

            # Log new size after SR
            h_new, w_new = face_crop.shape[:2]
            logger.info(
                f"✨ Super-resolution complete: {max_dim}px → {max(h_new, w_new)}px"
            )

        # Step 2: Apply adaptive interpolation (always, even after SR)
        if ADAPTIVE_INTERPOLATION:
            thumbnail = create_enhanced_thumbnail_adaptive(face_crop, target_size)
        else:
            # Fallback to current method if adaptive is disabled
            thumbnail = cv2.resize(face_crop, target_size, interpolation=cv2.INTER_AREA)

        return thumbnail

    except Exception as e:
        logger.error(f"❌ Error in hybrid thumbnail creation: {e}")
        # Ultimate fallback to current method
        return cv2.resize(face_crop, target_size, interpolation=cv2.INTER_AREA)


# ============================================================================
# END: Enhanced Thumbnail Generation
# ============================================================================


def create_face_thumbnail(face_crop: np.ndarray) -> str:
    """Create base64-encoded thumbnail from face crop.

    Uses hybrid enhancement: adaptive interpolation + optional super-resolution.

    Args:
        face_crop: Face crop as numpy array

    Returns:
        Base64-encoded JPEG thumbnail
    """
    try:
        # Use enhanced hybrid thumbnail generation
        thumbnail = create_enhanced_thumbnail_hybrid(face_crop, THUMBNAIL_SIZE)

        # Convert to PIL Image and save as JPEG in memory
        if len(thumbnail.shape) == 3:
            # Convert BGR to RGB for PIL
            thumbnail_rgb = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(thumbnail_rgb)
        else:
            pil_image = Image.fromarray(thumbnail)

        # Save to bytes buffer
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)

        # Encode as base64
        thumbnail_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return thumbnail_b64

    except Exception as e:
        logger.error(f"❌ Error creating thumbnail: {e}")
        return ""


def extract_faces_with_crops(image_path: str) -> List[Dict[str, Any]]:
    """Extract all faces from image with crops and quality metrics.

    Args:
        image_path: Path to the image file

    Returns:
        List of face data dictionaries with embeddings, crops, and metrics
    """
    try:
        logger.info(f"🔍 Extracting faces from: {image_path}")

        # Read image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"❌ Could not read image: {image_path}")
            return []

        # Detect faces with InsightFace
        faces = app.get(img)
        if not faces:
            logger.info(f"ℹ️ No faces detected in: {image_path}")
            return []

        face_data_list = []

        for i, face in enumerate(faces):
            try:
                # Extract face bounding box
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox

                # Crop face with some padding
                padding = 20
                x1_padded = max(0, x1 - padding)
                y1_padded = max(0, y1 - padding)
                x2_padded = min(img.shape[1], x2 + padding)
                y2_padded = min(img.shape[0], y2 + padding)

                face_crop = img[y1_padded:y2_padded, x1_padded:x2_padded]

                # Skip if face is too small
                if (
                    face_crop.shape[0] < MIN_FACE_SIZE
                    or face_crop.shape[1] < MIN_FACE_SIZE
                ):
                    logger.info(f"⏭️ Skipping small face {i+1}: {face_crop.shape}")
                    continue

                # Calculate quality metrics
                quality_metrics = calculate_face_quality_metrics(face_crop)

                # Skip low quality faces
                if quality_metrics["quality_score"] < MIN_QUALITY_SCORE:
                    logger.info(
                        f"⏭️ Skipping low quality face {i+1}: "
                        f"{quality_metrics['quality_score']:.3f}"
                    )
                    continue

                if quality_metrics["sharpness"] < MIN_BLUR_THRESHOLD:
                    logger.info(
                        f"⏭️ Skipping blurry face {i+1}: "
                        f"{quality_metrics['sharpness']:.1f}"
                    )
                    continue

                # Generate face ID
                face_id = str(uuid.uuid4())

                # Save thumbnail directly to file (no base64 step)
                thumbnail_path = save_face_crop_to_file(face_crop, face_id)

                # Prepare face data
                face_data = {
                    "face_id": face_id,
                    "embedding": face.embedding,
                    "detection_confidence": float(face.det_score),
                    "face_bbox": [int(x) for x in bbox],
                    "quality_metrics": quality_metrics,
                    "thumbnail_path": thumbnail_path,
                    "face_index": i,
                }

                face_data_list.append(face_data)
                logger.info(
                    f"✅ Extracted face {i+1}: "
                    f"quality={quality_metrics['quality_score']:.3f}, "
                    f"confidence={face.det_score:.3f}"
                )

            except Exception as e:
                logger.error(f"❌ Error processing face {i+1}: {e}")
                continue

        logger.info(
            f"🎉 Successfully extracted {len(face_data_list)} faces "
            f"from {len(faces)} detected"
        )
        return face_data_list

    except Exception as e:
        logger.error(f"❌ Error extracting faces: {e}")
        return []


def save_multiple_faces_optimized(image_path: str, event_id: str) -> List[str]:
    """Save multiple faces with optimized storage.

    Args:
        image_path: Path to the source image
        event_id: Event identifier for grouping

    Returns:
        List of saved face IDs
    """
    try:
        logger.info(f"💾 Saving faces (optimized) from: {image_path}")

        # Check for recent detections from same event
        if db_check_recent_detection(event_id):
            logger.info(f"⏭️ Skipping duplicate detection for event {event_id}")
            return []

        # Extract faces with crops
        faces_data = extract_faces_with_crops(image_path)
        if not faces_data:
            logger.info("ℹ️ No valid faces to save")
            return []

        saved_face_ids = []

        for face_data in faces_data:
            try:
                # Prepare metadata for storage
                metadata = {
                    "face_id": face_data["face_id"],
                    "name": "unknown",  # Will be classified later
                    "event_id": event_id,
                    "timestamp": int(time.time() * 1000),
                    "thumbnail_path": face_data["thumbnail_path"],
                    "confidence": face_data["detection_confidence"],
                    "quality_metrics": face_data["quality_metrics"],
                    "face_bbox": face_data["face_bbox"],
                    "notes": "",
                }

                # Save to Qdrant
                face_id = db_save_face(metadata, face_data["embedding"])
                saved_face_ids.append(face_id)

                logger.info(f"✅ Saved face {face_id} with optimized storage")

            except Exception as e:
                logger.error(f"❌ Error saving face {face_data['face_id']}: {e}")
                continue

        logger.info(
            f"🎉 Optimized save complete: {len(saved_face_ids)} faces "
            f"for event {event_id}"
        )
        return saved_face_ids

    except Exception as e:
        logger.error(f"❌ Error in optimized face saving: {e}")
        return []


def save_multiple_faces(image_path: str, event_id: str) -> List[str]:
    """Save multiple faces (legacy compatibility function).

    This now just calls the optimized version since we only use Qdrant.

    Args:
        image_path: Path to the source image
        event_id: Event identifier for grouping

    Returns:
        List of saved face IDs
    """
    return save_multiple_faces_optimized(image_path, event_id)


def identify_all_faces(image_path: str) -> List[Dict[str, Any]]:
    """Identify all faces in an image and return recognition results.

    Args:
        image_path: Path to the image file

    Returns:
        List of face recognition results with status and metadata
    """
    try:
        logger.info(f"🎯 Starting face identification: {image_path}")

        # Extract all faces with embeddings
        faces_data = extract_faces_with_crops(image_path)
        if not faces_data:
            logger.info("ℹ️ No faces detected for identification")
            return []

        results = []

        for face_data in faces_data:
            try:
                # Search for similar faces in database
                similar_faces = db_search_similar(face_data["embedding"], limit=3)

                face_result = {
                    "face_id": face_data["face_id"],
                    "confidence": face_data["detection_confidence"],
                    "quality_score": face_data["quality_metrics"]["quality_score"],
                    "face_bbox": face_data["face_bbox"],
                }

                if similar_faces:
                    best_match = similar_faces[0]
                    distance = best_match[1]
                    match_metadata = best_match[2]

                    if distance <= FACE_SIMILARITY_THRESHOLD:
                        # Definite match
                        face_result.update(
                            {
                                "status": "identified",
                                "name": match_metadata.get("name", "unknown"),
                                "match_confidence": 1.0 - distance,
                                "distance": distance,
                                "matched_face_id": match_metadata.get("face_id"),
                            }
                        )
                        logger.info(
                            f"✅ Identified: {match_metadata.get('name')} "
                            f"(distance: {distance:.3f})"
                        )

                    elif distance <= BORDERLINE_THRESHOLD:
                        # Possible match - suggest for review
                        face_result.update(
                            {
                                "status": "suggestion",
                                "suggested_name": match_metadata.get("name", "unknown"),
                                "match_confidence": 1.0 - distance,
                                "distance": distance,
                                "suggested_face_id": match_metadata.get("face_id"),
                                "message": (
                                    f"Possible match with {match_metadata.get('name')} "
                                    f"(confidence: {(1.0-distance)*100:.1f}%)"
                                ),
                            }
                        )
                        logger.info(
                            f"🤔 Suggestion: {match_metadata.get('name')} "
                            f"(distance: {distance:.3f})"
                        )

                    else:
                        # No match
                        face_result.update(
                            {
                                "status": "unknown",
                                "name": "unknown",
                                "message": "No matching face found",
                            }
                        )
                        logger.info(
                            f"❓ Unknown face (closest distance: {distance:.3f})"
                        )
                else:
                    # No faces in database
                    face_result.update(
                        {
                            "status": "unknown",
                            "name": "unknown",
                            "message": "No faces in database",
                        }
                    )
                    logger.info("❓ Unknown face (empty database)")

                results.append(face_result)

            except Exception as e:
                logger.error(f"❌ Error identifying face {face_data['face_id']}: {e}")
                # Add error result
                results.append(
                    {
                        "face_id": face_data["face_id"],
                        "status": "error",
                        "message": f"Identification error: {str(e)}",
                        "confidence": face_data["detection_confidence"],
                        "face_bbox": face_data["face_bbox"],
                    }
                )
                continue

        logger.info(f"🎉 Face identification complete: {len(results)} faces processed")
        return results

    except Exception as e:
        logger.error(f"❌ Error in face identification: {e}")
        return []


def get_unclassified_faces() -> List[Dict[str, Any]]:
    """Get all unclassified faces from the database with file paths.

    Returns:
        List of unclassified face dictionaries with thumbnail_path for direct access
    """
    try:
        logger.info("📋 Retrieving unclassified faces")
        unclassified = db_get_unclassified_faces()
        logger.info(f"📊 Found {len(unclassified)} unclassified faces")
        return unclassified
    except Exception as e:
        logger.error(f"❌ Error retrieving unclassified faces: {e}")
        return []


def update_face(face_id: str, data: Dict[str, str]) -> None:
    """Update face information in the database.

    Args:
        face_id: Unique face identifier
        data: Dictionary with update data (name, notes, etc.)
    """
    try:
        logger.info(f"📝 Updating face {face_id}")
        success = db_update_face(face_id, data)
        if success:
            logger.info(f"✅ Successfully updated face {face_id}")
        else:
            logger.error(f"❌ Failed to update face {face_id}")
    except Exception as e:
        logger.error(f"❌ Error updating face {face_id}: {e}")
        raise


def get_face(face_id: str) -> Optional[Dict[str, Any]]:
    """Get face metadata by ID."""
    return db_get_face(face_id)


def save_face_crop_to_file(face_crop: np.ndarray, face_id: str) -> str:
    """Save face crop directly as JPEG file without base64 conversion.

    Args:
        face_crop: Face crop image as numpy array
        face_id: Unique face identifier

    Returns:
        Path to saved thumbnail file
    """
    # Determine thumbnail directory
    thumbnail_dir = THUMBNAIL_PATH

    # Ensure thumbnail directory exists
    try:
        os.makedirs(thumbnail_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        logger.warning(f"⚠️ Could not create thumbnail directory {thumbnail_dir}: {e}")
        # Fallback to temp directory for testing environments
        thumbnail_dir = os.path.join("/tmp", "face_rekon_thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        logger.info(f"📁 Using fallback thumbnail path: {thumbnail_dir}")

    # Create thumbnail file path
    thumbnail_file = f"{face_id}.jpg"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_file)

    try:
        # Use enhanced hybrid thumbnail generation
        thumbnail = create_enhanced_thumbnail_hybrid(face_crop, THUMBNAIL_SIZE)

        # Convert BGR to RGB if needed
        if len(thumbnail.shape) == 3:
            # OpenCV uses BGR, convert to RGB for PIL
            thumbnail_rgb = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(thumbnail_rgb)
        else:
            pil_image = Image.fromarray(thumbnail)

        # Save directly as JPEG
        pil_image.save(thumbnail_path, "JPEG", quality=85, optimize=True)

        logger.info(f"💾 Saved thumbnail: {thumbnail_path}")
        return thumbnail_path

    except Exception as e:
        logger.error(f"❌ Failed to save thumbnail {face_id}: {e}")
        return ""


def get_face_with_thumbnail(face_id: str) -> Optional[Dict[str, Any]]:
    """Get face metadata with thumbnail_path (no base64 conversion).

    Args:
        face_id: Face identifier

    Returns:
        Face metadata with thumbnail_path, or None if not found
    """
    face = db_get_face(face_id)
    return face
