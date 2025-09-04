import zipfile
import rarfile
import subprocess
import os  # Add import for os.scandir
from pathlib import Path
from typing import Optional, Callable

CONVERTED_EXTENSIONS = ('.cbz', '.cbr', '.pdf')


def extract_rar_archive(
    rar_path: Path,
    extract_path: Path,
    progress_callback: Optional[Callable[[int], None]] = None,
    start_progress: int = 0,
    end_progress: int = 100
):
    """
    Extract a RAR archive to a specified directory with optional progress tracking.

    Args:
        rar_path (Path): Path to the RAR file to extract.
        extract_path (Path): Directory to extract files into.
        progress_callback (Optional[Callable[[int], None]]): Callback for progress updates.
        start_progress (int): Starting progress value.
        end_progress (int): Ending progress value.

    Raises:
        RuntimeError: If extraction fails.
    """
    try:
        with rarfile.RarFile(str(rar_path), 'r') as rar_file:
            file_list = rar_file.namelist()
            total_files = len(file_list)
            for i, file_name in enumerate(file_list):
                rar_file.extract(file_name, str(extract_path))
                if progress_callback and total_files > 0:
                    progress_callback(i + 1, total_files)
    except Exception as e:
        raise RuntimeError(f"Failed to extract RAR archive: {str(e)}")
    

def extract_zip_archive(
    zip_path: Path,
    extract_path: Path,
    progress_callback: Optional[Callable[[int], None]] = None,
    start_progress: int = 0,
    end_progress: int = 100
):
    """
    Extract a ZIP archive to a specified directory with optional progress tracking.

    Args:
        zip_path (Path): Path to the ZIP file to extract.
        extract_path (Path): Directory to extract files into.
        progress_callback (Optional[Callable[[int], None]]): Callback for progress updates.
        start_progress (int): Starting progress value.
        end_progress (int): Ending progress value.

    Raises:
        RuntimeError: If extraction fails.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            total_files = len(file_list)
            for i, file_name in enumerate(file_list):
                zip_file.extract(file_name, extract_path)
                if progress_callback and total_files > 0:
                    progress_callback(i + 1, total_files)
    except Exception as e:
        raise RuntimeError(f"Failed to extract ZIP archive: {str(e)}")
    

def create_zip_archive(
    source_path: Path,
    zip_path: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    start_progress: int = 0,
    end_progress: int = 100
):
    """
    Create a ZIP archive from a source directory with optional progress tracking.

    Args:
        source_path (Path): Directory to archive.
        zip_path (Path): Path for the output ZIP file.
        progress_callback (Optional[Callable[[int, int], None]]): Callback for progress updates.
        start_progress (int): Starting progress value.
        end_progress (int): Ending progress value.

    Raises:
        RuntimeError: If archive creation fails.
    """
    if not source_path.exists() or not source_path.is_dir():
        raise RuntimeError(f"Source directory does not exist: {source_path}")
    try:
        # Use os.scandir for faster traversal
        all_files = []
        for root, dirs, files in os.walk(source_path):
            for file in files:
                all_files.append(Path(root) / file)
        files_to_archive = all_files
        total_files = len(files_to_archive)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, file_path in enumerate(files_to_archive):
                relative_path = file_path.relative_to(source_path)
                zip_file.write(file_path, relative_path)
                if progress_callback and total_files > 0:
                    current_progress = start_progress + (
                        ((i + 1) / total_files) * (end_progress - start_progress)
                    )
                    progress_callback(int(current_progress), total_files)
    except Exception as e:
        raise RuntimeError(f"Failed to create ZIP archive: {str(e)}")
    

def create_rar_archive(
    source_path: Path,
    rar_path: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    start_progress: int = 0,
    end_progress: int = 100
):
    """
    Create a RAR archive from a source directory with optional progress tracking.

    Args:
        source_path (Path): Directory to archive.
        rar_path (Path): Path for the output RAR file.
        progress_callback (Optional[Callable[[int, int], None]]): Callback for progress updates.
        start_progress (int): Starting progress value.
        end_progress (int): Ending progress value.

    Raises:
        RuntimeError: If archive creation fails or RAR tool is not found.
    """
    try:
        try:
            subprocess.run(['rar'], capture_output=True, check=False)
        except FileNotFoundError:
            raise RuntimeError(
                "RAR command-line tool not found. Install Rarfile or rar package to create CBR files."
            )

        # Use os.scandir for faster traversal
        all_files = []
        for root, dirs, files in os.walk(source_path):
            for file in files:
                all_files.append(Path(root) / file)
        files_to_archive = all_files
        total_files = len(files_to_archive)

        if progress_callback:
            progress_callback(start_progress + 10, total_files)

        cmd = [
            'rar', 'a', '-r', '-ep1',
            str(rar_path),
            str(source_path / '*')
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"RAR creation failed: {result.stderr}")

        if progress_callback:
            progress_callback(end_progress, total_files)
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to create RAR archive: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to create RAR archive: {str(e)}")


def create_per_file_progress_callback(
    progress_callback: Optional[Callable[[int, int], None]],
    file_index: int,
    total_files: int,
    is_last_file: bool = False
) -> Callable[[int, int], None]:
    """
    Create a per-file progress callback that shows 0-100% for each file.
    Ensures the bar resets for each file and emits final 100% only for the last file.

    Args:
        progress_callback: The base progress callback to emit to.
        file_index: Index of the current file (0-based).
        total_files: Total number of files.
        is_last_file: True if this is the last file, to emit final 100%.

    Returns:
        A callback function for per-file progress updates.
    """
    def callback(current: int, total: int):
        if progress_callback:
            if total > 0:
                percent = min(100, max(0, int((current / total) * 100)))
            else:
                percent = 0
            # For non-last files, cap at 99% to avoid multiple 100%
            if not is_last_file and percent == 100:
                percent = 99
            progress_callback(percent, 100)
    return callback
