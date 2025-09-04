"""Cache operations for PyTorch compilation artifacts.

This module provides functions for loading and saving PyTorch compilation cache
to/from b10fs shared storage using atomic operations and space monitoring.
"""

import logging
import tempfile
from pathlib import Path

from .logging_utils import get_b10_logger

from .environment import get_cache_filename
from .cleanup import cooperative_cleanup_b10fs
from .utils import (
    timed_fn,
    critical_section_b10fs_file_lock,
    safe_execute,
    temp_file_cleanup,
    cache_operation,
    safe_unlink,
)
from .space_monitor import (
    CacheSpaceMonitor,
    CacheOperationInterrupted,
    run_monitored_process,
    worker_process,
)
from .constants import (
    TORCH_CACHE_DIR,
    B10FS_CACHE_DIR,
    LOCAL_WORK_DIR,
    MAX_CACHE_SIZE_MB,
    REQUIRED_B10FS_SPACE_MB,
    MIN_LOCAL_SPACE_MB,
    CACHE_FILE_EXTENSION,
    CACHE_LATEST_SUFFIX,
    CACHE_INCOMPLETE_SUFFIX,
    OperationStatus,
)
from .core import transfer

logger = get_b10_logger(__name__)


"""
FIXME(SRAY):
What about the case in @b10-transfer/ where a single pod finishes an inference request,
and then the client calls save_compile_cache. And while we are creating the local archive,
another inference call on the same pod is kicked off, which then modifies the torch cache.
How would this be handled? Maybe just accept that the cache will be recompiled/overwritten?
Otherwise you'd need application level coordination to ensure that the cache is not modified
while we are creating the archive, but this doesn't really seem like a good idea in terms of adoption.

FIXME(SR):
More things to consider:
- [possible] What if b10fs dies *during* an op? right now we check for b10fs availability in the beginning of the op... Add some constants instead of just False for load().
- [possible, and really bad if it happens] potential memory exhaustion during compression if the cache is super super large. very very edge case. higher compression levels also have high memory usage.
"""


def _setup_cache_paths():
    """Common setup for cache operations - returns paths and performs cleanup."""
    # Cooperative cleanup of stale shared resources
    cooperative_cleanup_b10fs()

    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)
    work_dir = Path(LOCAL_WORK_DIR)

    return b10fs_dir, torch_dir, work_dir


def _get_cache_file_paths(cache_filename: str, b10fs_dir: Path):
    """Generate cache file paths for a given cache filename."""
    final_file = (
        b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
    )
    temp_file = (
        b10fs_dir / f"{cache_filename}{CACHE_INCOMPLETE_SUFFIX}{CACHE_FILE_EXTENSION}"
    )
    return final_file, temp_file


def _run_with_space_monitoring(
    space_threshold_mb: float,
    monitor_dir: Path,
    operation_name: str,
    worker_func,
    worker_args: tuple,
    cleanup_func=None,
):
    """Helper to run an operation with space monitoring."""
    space_monitor = CacheSpaceMonitor(space_threshold_mb, monitor_dir)
    space_monitor.start()

    try:
        logger.info(
            f"[MONITORING] Starting {operation_name} with space monitoring: {' -> '.join(str(arg) for arg in worker_args[:2])}"
        )
        run_monitored_process(
            worker_func,
            worker_args,
            space_monitor,
            operation_name,
            cleanup_func=cleanup_func,
        )
    finally:
        space_monitor.stop()


def _transfer_with_b10fs_lock(
    source: str, dest: str, lock_type: str, cleanup_on_failure=True
):
    """Transfer a file with b10fs file locking and error handling."""

    @critical_section_b10fs_file_lock(lock_type)
    def _locked_transfer():
        # Get file size for logging
        source_path = Path(source)
        source_size_mb = (
            source_path.stat().st_size / (1024 * 1024) if source_path.exists() else 0
        )
        logger.info(
            f"[TRANSFER] Starting locked transfer: {source} -> {dest} (size: {source_size_mb:.2f} MB, lock: {lock_type})"
        )

        result = transfer(source, dest)
        if result != OperationStatus.SUCCESS:
            logger.error(f"[TRANSFER] Transfer failed with status: {result}")
            if cleanup_on_failure:
                logger.info(
                    f"[TRANSFER] Cleaning up failed transfer destination: {dest}"
                )
                safe_unlink(
                    Path(dest), f"Failed to cleanup after failed transfer {dest}"
                )
            raise Exception(f"Failed to transfer {source} -> {dest}")

        logger.info(f"[TRANSFER] Transfer completed successfully: {source} -> {dest}")

    _locked_transfer()


@timed_fn(logger=logger, name="Loading compile cache")
@safe_execute("Load failed", False)
def load_compile_cache() -> OperationStatus:
    """Load PyTorch compilation cache from b10fs to local torch cache directory.

    This function implements a lock-free pattern to safely load cached PyTorch
    compilation artifacts from the b10fs shared filesystem to the local torch
    cache directory. It validates b10fs availability, checks for existing cache,
    and extracts the archive if needed.

    The function monitors local disk space during both the copy from b10fs and
    extraction phases, interrupting operations if space falls below MIN_LOCAL_SPACE_MB.

    Returns:
        OperationStatus:
              OperationStatus.SUCCESS if cache was successfully loaded
              OperationStatus.SKIPPED if already exists
              OperationStatus.ERROR if b10fs is unavailable, local disk space is insufficient, or loading failed.
              OperationStatus.DOES_NOT_EXIST if no cache file was found.

    Raises:
        CacheValidationError: If b10fs is not enabled (caught and returns OperationStatus.ERROR).
        CacheOperationInterrupted: If operations interrupted due to insufficient
                                  local disk space (caught and returns OperationStatus.ERROR).
        Exception: Any other errors during loading (caught and returns OperationStatus.ERROR).
    """
    with cache_operation("Load"):
        b10fs_dir, torch_dir, work_dir = _setup_cache_paths()

        cache_filename = get_cache_filename()
        final_file, _ = _get_cache_file_paths(cache_filename, b10fs_dir)
        logger.info(f"[LOADING] Searching for cache file: {final_file}")

        if not final_file.exists():
            logger.info(f"[LOADING] No cache file found in b10fs at: {final_file}")
            return OperationStatus.DOES_NOT_EXIST

        # Skip if already loaded
        if torch_dir.exists() and any(torch_dir.iterdir()):
            size_mb = sum(
                f.stat().st_size for f in torch_dir.rglob("*") if f.is_file()
            ) / (1024 * 1024)
            logger.info(
                f"[LOADING] Torch cache already exists at {torch_dir}, skipping extraction (size: {size_mb:.2f} MB)"
            )
            return OperationStatus.SKIPPED

        # Create temp local copy
        with tempfile.NamedTemporaryFile(
            suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
        ) as f:
            temp_path = Path(f.name)
        logger.info(f"[LOADING] Created temporary file for cache download: {temp_path}")

        try:
            with temp_file_cleanup(temp_path):
                # Phase 1: Copy from b10fs to local temp file
                logger.info(
                    f"[LOADING] Phase 1: Copying cache from b10fs to local temp file ({final_file} -> {temp_path})"
                )
                _transfer_with_b10fs_lock(
                    str(final_file),
                    str(temp_path),
                    "copy_out",
                    cleanup_on_failure=False,
                )

                # Phase 2: Extract archive with space monitoring
                logger.info(
                    f"[LOADING] Phase 2: Extracting cache archive to torch directory ({temp_path} -> {torch_dir})"
                )
                _run_with_space_monitoring(
                    MIN_LOCAL_SPACE_MB,
                    work_dir,
                    "archive extraction",
                    _cache_extract_worker,
                    (str(temp_path), str(torch_dir)),
                    cleanup_func=lambda: _cleanup_torch_dir(torch_dir),
                )

            # Calculate final cache size for logging
            final_size_mb = (
                sum(f.stat().st_size for f in torch_dir.rglob("*") if f.is_file())
                / (1024 * 1024)
                if torch_dir.exists()
                else 0
            )
            logger.info(
                f"[LOADING] Cache load completed successfully (final size: {final_size_mb:.2f} MB)"
            )
            return OperationStatus.SUCCESS

        except CacheOperationInterrupted as e:
            logger.warning(
                f"[LOADING] Cache load interrupted due to insufficient disk space: {e}"
            )
            return OperationStatus.ERROR


@timed_fn(logger=logger, name="Saving compile cache")
@safe_execute("Save failed", False)
def save_compile_cache() -> OperationStatus:
    """Save local PyTorch compilation cache to b10fs using atomic journal pattern.

    This function creates an archive of the local torch cache directory and
    atomically saves it to b10fs using a journal pattern (write to temp file,
    then rename). This ensures concurrent saves don't corrupt each other.

    The function validates b10fs availability, checks if cache already exists
    (early exit), performs initial space checks using pre-calculated requirements
    for concurrent saves, starts background space monitoring, then runs compression
    and copy operations in separate worker processes that can be terminated if disk
    space becomes insufficient, finally performing an atomic rename to the final cache file.

    Returns:
        OperationStatus:
              OperationStatus.SUCCESS if cache was successfully saved or already exists
              OperationStatus.ERROR if b10fs is unavailable, insufficient disk space caused interruption,
                no cache exists to save, or saving failed.
              OperationStatus.SKIPPED if no cache exists to save or cache already exists in b10fs

    Raises:
        CacheValidationError: If b10fs is not enabled (caught and returns OperationStatus.ERROR).
        CacheOperationInterrupted: If operations interrupted due to insufficient
                                  disk space (caught and returns OperationStatus.ERROR).
        ArchiveError: If archive creation fails (caught and returns OperationStatus.ERROR).
        Exception: Any other errors during saving (caught and returns OperationStatus.ERROR).
    """
    with cache_operation("Save"):
        b10fs_dir, torch_dir, work_dir = _setup_cache_paths()

        # Check if anything to save
        if not torch_dir.exists() or not any(torch_dir.iterdir()):
            logger.info(f"[SAVING] No torch cache found at {torch_dir} to save")
            return OperationStatus.SKIPPED

        cache_filename = get_cache_filename()
        final_file, temp_file = _get_cache_file_paths(cache_filename, b10fs_dir)

        # Check for existing cache first (early exit)
        if final_file.exists():
            file_size_mb = final_file.stat().st_size / (1024 * 1024)
            logger.info(
                f"[SAVING] Cache already exists in b10fs at {final_file} (size: {file_size_mb:.2f} MB), skipping save"
            )
            return OperationStatus.SKIPPED

        with tempfile.NamedTemporaryFile(
            suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
        ) as f:
            local_temp = Path(f.name)
        # Calculate source cache size for logging
        source_size_mb = sum(
            f.stat().st_size for f in torch_dir.rglob("*") if f.is_file()
        ) / (1024 * 1024)
        logger.info(
            f"[SAVING] Created local temp file for archive: {local_temp} (source cache size: {source_size_mb:.2f} MB)"
        )

        try:
            with temp_file_cleanup(local_temp):
                # Phase 1: Compression with space monitoring
                logger.info(
                    f"[SAVING] Phase 1: Compressing torch cache directory ({torch_dir} -> {local_temp}, max size: {MAX_CACHE_SIZE_MB} MB)"
                )
                _run_with_space_monitoring(
                    REQUIRED_B10FS_SPACE_MB,
                    b10fs_dir,
                    "compression",
                    _cache_compression_worker,
                    (str(torch_dir), str(local_temp), MAX_CACHE_SIZE_MB),
                )

                # Phase 2: Copy to b10fs with locking
                compressed_size_mb = local_temp.stat().st_size / (1024 * 1024)
                logger.info(
                    f"[SAVING] Phase 2: Copying compressed archive to b10fs ({local_temp} -> {temp_file}, size: {compressed_size_mb:.2f} MB)"
                )
                _transfer_with_b10fs_lock(
                    str(local_temp), str(temp_file), "copy_in", cleanup_on_failure=True
                )

                # Phase 3: Atomic rename (fast, don't interrupt)
                logger.info(
                    f"[SAVING] Phase 3: Atomically renaming temp file to final cache file: {temp_file} -> {final_file}"
                )
                temp_file.rename(final_file)

            final_file_size_mb = final_file.stat().st_size / (1024 * 1024)
            logger.info(
                f"[SAVING] Cache save completed successfully (final file: {final_file}, size: {final_file_size_mb:.2f} MB)"
            )
            return OperationStatus.SUCCESS

        except CacheOperationInterrupted as e:
            logger.warning(
                f"[SAVING] Cache save interrupted due to insufficient disk space: {e}"
            )
            return OperationStatus.ERROR


@safe_execute("Clear failed", False)
def clear_local_cache() -> bool:
    """Clear the local PyTorch compilation cache directory.

    This function removes the entire local torch cache directory and all its
    contents. This is useful for cleaning up disk space or forcing recompilation.

    Returns:
        bool: True if cache was successfully cleared or didn't exist, False if
              clearing failed due to permissions or other filesystem errors.

    Raises:
        Exception: Any errors during directory removal (caught and returns False).
    """
    torch_dir = Path(TORCH_CACHE_DIR)
    if not torch_dir.exists():
        logger.info(
            f"[CLEARING] No torch cache directory found at {torch_dir}, nothing to clear"
        )
        return True

    # Calculate size before clearing for logging
    size_mb = sum(f.stat().st_size for f in torch_dir.rglob("*") if f.is_file()) / (
        1024 * 1024
    )
    logger.info(
        f"[CLEARING] Removing torch cache directory: {torch_dir} (size: {size_mb:.2f} MB)"
    )

    import shutil

    shutil.rmtree(torch_dir)
    logger.info(f"[CLEARING] Successfully cleared torch cache directory: {torch_dir}")
    return True


@worker_process("Compression was cancelled before starting")
def _cache_compression_worker(
    torch_dir_str: str, local_temp_str: str, max_size_mb: int
) -> None:
    """Worker process that handles cache compression.

    This function runs in a separate process to compress the torch cache directory
    into an archive. It can be terminated externally if disk space becomes insufficient.

    Args:
        torch_dir_str: String path to the torch cache directory to compress.
        local_temp_str: String path where the compressed archive will be created.
        max_size_mb: Maximum allowed archive size in megabytes.
    """
    torch_dir = Path(torch_dir_str)
    local_temp = Path(local_temp_str)

    # Import here to avoid issues with multiprocessing
    from .archive import create_archive

    # Note: We can't use the main logger here due to multiprocessing
    # The create_archive function should handle its own logging
    create_archive(torch_dir, local_temp, max_size_mb)


def _cleanup_torch_dir(torch_dir: Path) -> None:
    """Helper function to safely cleanup torch directory during interrupted extraction."""
    try:
        if torch_dir.exists():
            import shutil

            shutil.rmtree(torch_dir)
            logger.info(
                f"[CLEANUP] Successfully cleaned up torch directory: {torch_dir}"
            )
    except Exception as e:
        logger.error(f"[CLEANUP] Failed to cleanup torch directory {torch_dir}: {e}")


@worker_process("Extraction was cancelled before starting")
def _cache_extract_worker(archive_path_str: str, dest_dir_str: str) -> None:
    """Worker process that handles archive extraction.

    This function runs in a separate process to extract the cache archive to
    the torch cache directory. It can be terminated externally if local disk space becomes insufficient.

    Args:
        archive_path_str: String path to the archive file to extract.
        dest_dir_str: String path to the directory where archive will be extracted.
    """
    archive_path = Path(archive_path_str)
    dest_dir = Path(dest_dir_str)

    # Import here to avoid issues with multiprocessing
    from .archive import extract_archive

    # Note: We can't use the main logger here due to multiprocessing
    # The extract_archive function should handle its own logging
    extract_archive(archive_path, dest_dir)
