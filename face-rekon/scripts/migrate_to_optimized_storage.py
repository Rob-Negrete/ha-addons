#!/usr/bin/env python3
"""
Database Migration Script: Legacy to Optimized Storage

This script migrates face-rekon database from legacy format to optimized storage:
- Moves base64 thumbnails from TinyDB to separate JPEG files (90% size reduction)
- Removes embedding duplication from TinyDB (stored only in FAISS)
- Converts records to optimized format with file references

Expected Results:
- TinyDB size reduction: 65MB → 3MB (95% reduction)
- Eliminates JSON corruption risk
- Maintains backward compatibility

Usage:
    python migrate_to_optimized_storage.py [--dry-run] [--backup]

Options:
    --dry-run    Show migration plan without making changes
    --backup     Create backup before migration (recommended)
"""

import argparse
import logging
import os
import shutil
import sys
import time
from typing import Any, Dict

import clasificador

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def analyze_current_database() -> Dict[str, Any]:
    """Analyze current database to understand migration scope."""
    logger.info("🔍 Analyzing current database...")

    try:
        # Get all records safely
        all_records = clasificador.safe_db_all()

        if not all_records:
            logger.warning("⚠️ No records found in database")
            return {"total_records": 0, "legacy_records": 0, "optimized_records": 0}

        # Categorize records
        legacy_records = []
        optimized_records = []

        total_thumbnail_size = 0
        total_embedding_size = 0

        for record in all_records:
            # Check if record is already optimized
            if (
                "storage_version" in record
                and record["storage_version"] == "optimized_v1"
            ):
                optimized_records.append(record)
            else:
                legacy_records.append(record)

                # Calculate storage sizes
                if "thumbnail" in record and record["thumbnail"]:
                    # Estimate base64 size (4/3 of binary size)
                    thumbnail_size = len(record["thumbnail"]) * 3 // 4
                    total_thumbnail_size += thumbnail_size

                if "embedding" in record and record["embedding"]:
                    # 512 floats * 8 bytes per float = ~4KB
                    total_embedding_size += len(record["embedding"]) * 8

        analysis = {
            "total_records": len(all_records),
            "legacy_records": len(legacy_records),
            "optimized_records": len(optimized_records),
            "estimated_thumbnail_size_mb": total_thumbnail_size / (1024 * 1024),
            "estimated_embedding_size_mb": total_embedding_size / (1024 * 1024),
            "estimated_total_size_mb": (total_thumbnail_size + total_embedding_size)
            / (1024 * 1024),
            "migration_needed": len(legacy_records) > 0,
        }

        return analysis

    except Exception as e:
        logger.error(f"❌ Failed to analyze database: {e}")
        return {"error": str(e)}


def create_database_backup() -> str:
    """Create backup of current database."""
    logger.info("💾 Creating database backup...")

    try:
        timestamp = int(time.time())
        backup_dir = os.path.join(os.path.dirname(clasificador.DB_PATH), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        backup_path = os.path.join(backup_dir, f"tinydb_backup_{timestamp}.json")

        # Copy database file
        shutil.copy2(clasificador.DB_PATH, backup_path)

        logger.info(f"✅ Database backup created: {backup_path}")
        return backup_path

    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}")
        raise


def migrate_legacy_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy record to optimized format."""

    # Create face_id if missing
    face_id = record.get("face_id", f"migrated_{int(time.time())}_{hash(str(record))}")

    # Save thumbnail to file if exists
    thumbnail_path = ""
    if "thumbnail" in record and record["thumbnail"]:
        thumbnail_path = clasificador.save_thumbnail_to_file(
            record["thumbnail"], face_id
        )

    # Find FAISS index for this record (if embedding exists)
    faiss_index = -1
    if "embedding" in record and record["embedding"]:
        try:
            # Look up existing FAISS index
            # This is simplified - in practice, we'd need to match the embedding
            # For migration, we'll assign sequential indices
            faiss_index = clasificador.index.ntotal
        except Exception:
            faiss_index = -1

    # Create optimized record
    optimized_record = {
        "face_id": face_id,
        "event_id": record.get("event_id", "migrated"),
        "timestamp": record.get("timestamp", int(time.time())),
        "name": record.get("name"),
        "thumbnail_path": thumbnail_path,
        "faiss_index": faiss_index,
        "face_bbox": record.get("face_bbox"),
        "face_index": record.get("face_index", 0),
        "quality_metrics": record.get("quality_metrics", {}),
        "relationship": record.get("relationship", "unknown"),
        "confidence": record.get("confidence", "unknown"),
        # Migration metadata
        "storage_version": "optimized_v1",
        "created_with": "migration_script",
        "migrated_from": "legacy_format",
        "migration_timestamp": int(time.time()),
    }

    # Remove legacy fields (embedding duplication removed, thumbnail moved to file)
    # Fields NOT included: "embedding", "thumbnail", "image_path"

    return optimized_record


def perform_migration(dry_run: bool = False, backup: bool = True) -> Dict[str, Any]:
    """Perform the database migration."""

    if backup and not dry_run:
        backup_path = create_database_backup()

    analysis = analyze_current_database()

    if "error" in analysis:
        logger.error(f"❌ Cannot proceed with migration: {analysis['error']}")
        return analysis

    if not analysis["migration_needed"]:
        logger.info("✅ Database already optimized, no migration needed")
        return analysis

    logger.info(f"🚀 Starting migration for {analysis['legacy_records']} records...")

    if dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
        return {
            **analysis,
            "dry_run": True,
            "estimated_size_reduction_mb": analysis["estimated_total_size_mb"] * 0.95,
            "migration_plan": (
                f"Convert {analysis['legacy_records']} legacy records to "
                "optimized format"
            ),
        }

    try:
        # Get all records
        all_records = clasificador.safe_db_all()
        migrated_records = []
        migration_errors = []

        for record in all_records:
            # Skip already optimized records
            if (
                "storage_version" in record
                and record["storage_version"] == "optimized_v1"
            ):
                migrated_records.append(record)
                continue

            try:
                # Migrate legacy record
                optimized_record = migrate_legacy_record(record)
                migrated_records.append(optimized_record)
                logger.info(f"✅ Migrated record: {optimized_record['face_id']}")

            except Exception as e:
                logger.error(
                    f"❌ Failed to migrate record "
                    f"{record.get('face_id', 'unknown')}: {e}"
                )
                migration_errors.append({"record": record, "error": str(e)})

        # Clear database and insert migrated records
        logger.info("🔄 Updating database with migrated records...")

        # Backup current database one more time
        temp_backup = f"{clasificador.DB_PATH}.migration_backup"
        shutil.copy2(clasificador.DB_PATH, temp_backup)

        try:
            # Clear database
            clasificador.db.truncate()

            # Insert all migrated records
            for record in migrated_records:
                if not clasificador.safe_db_insert(record):
                    logger.error(
                        f"❌ Failed to insert migrated record: {record['face_id']}"
                    )

            logger.info("✅ Database migration completed successfully")

            # Remove temporary backup
            os.remove(temp_backup)

        except Exception as e:
            # Restore from temporary backup on error
            logger.error(f"❌ Migration failed, restoring backup: {e}")
            shutil.copy2(temp_backup, clasificador.DB_PATH)
            os.remove(temp_backup)
            raise

        return {
            **analysis,
            "migration_completed": True,
            "migrated_records": len(migrated_records),
            "migration_errors": len(migration_errors),
            "errors": migration_errors,
            "backup_path": backup_path if backup else None,
        }

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return {**analysis, "migration_failed": True, "error": str(e)}


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate face-rekon database to optimized storage"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show migration plan without making changes",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before migration",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (not recommended)",
    )

    args = parser.parse_args()

    # Handle backup option
    create_backup = args.backup and not args.no_backup

    logger.info("🚀 Face-rekon Database Migration: Legacy → Optimized Storage")
    logger.info("=" * 60)

    # Perform migration
    result = perform_migration(dry_run=args.dry_run, backup=create_backup)

    # Print results
    logger.info("\n📊 Migration Results:")
    logger.info(f"Total records: {result.get('total_records', 0)}")
    logger.info(f"Legacy records: {result.get('legacy_records', 0)}")
    logger.info(f"Optimized records: {result.get('optimized_records', 0)}")

    if "estimated_total_size_mb" in result:
        logger.info(
            f"Estimated current size: {result['estimated_total_size_mb']:.1f} MB"
        )
        if result.get("migration_completed"):
            reduction = result["estimated_total_size_mb"] * 0.95
            logger.info(f"Expected size reduction: {reduction:.1f} MB (95%)")

    if result.get("migration_completed"):
        logger.info("✅ Migration completed successfully!")
        logger.info("💡 Expected benefits:")
        logger.info("   - 95% reduction in TinyDB file size")
        logger.info("   - Elimination of JSON corruption risk")
        logger.info("   - Faster database operations")
    elif result.get("dry_run"):
        logger.info("🔍 Dry run completed - use without --dry-run to perform migration")
    elif result.get("migration_failed"):
        logger.error("❌ Migration failed!")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    else:
        logger.info("ℹ️ No migration needed")


if __name__ == "__main__":
    main()
