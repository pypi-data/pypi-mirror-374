import os
import sys
import time
import json
import yaml
import logging
import argparse
import shutil
import glob
import fnmatch
import zipfile
import csv
import platform
import subprocess
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Try to import adls_server modules
try:
    from tlpytools.adls_server import adls_tables, adls_util

    ADLS_AVAILABLE = True
except ImportError:
    ADLS_AVAILABLE = False
    adls_tables = None
    adls_util = None

# Try to import psutil for system monitoring (optional)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Get the absolute path to the current script's directory
ORCA_DIR = os.path.dirname(os.path.abspath(__file__))


# For backward compatibility and path resolution
def ensure_python_path():
    """Ensure the current directory and ORCA_DIR are in Python path."""
    paths_to_add = [
        os.getcwd(),  # Current working directory
        ORCA_DIR,  # tlpytools directory
    ]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)


# Initialize path on module import
ensure_python_path()


class OrcaLogger:
    """
    Centralized logger class for ORCA orchestrator and related utilities.

    This class provides a singleton-like behavior to ensure all orchestrator-related
    logging goes to the same log file with consistent formatting.
    """

    _instance = None
    _logger = None
    _log_file_path = None
    _initialized = False

    def __new__(cls, log_file_path: Optional[str] = None):
        """Create or return the singleton logger instance."""
        if cls._instance is None:
            cls._instance = super(OrcaLogger, cls).__new__(cls)
        # If a new log file path is provided and it's different from current, reinitialize
        elif log_file_path and log_file_path != cls._instance._log_file_path:
            cls._instance.close()
            cls._instance = super(OrcaLogger, cls).__new__(cls)
            cls._initialized = False
        return cls._instance

    def __init__(self, log_file_path: Optional[str] = None):
        """
        Initialize the ORCA logger.

        Args:
            log_file_path (str, optional): Path to the log file. If None, uses default.
        """
        if self._initialized:
            return

        # Set default log file path if none provided
        if log_file_path is None:
            # Check if we're running from within a databank directory
            current_dir = os.getcwd()

            # Look for databank indicators (config files that suggest we're in a databank)
            databank_indicators = ["orca_model_config.yaml", "orca_model_state.json"]
            is_databank = any(
                os.path.exists(os.path.join(current_dir, indicator))
                for indicator in databank_indicators
            )

            if is_databank:
                # Create log file in the current (databank) directory
                log_dir = current_dir
                log_file_name = "orca_orchestrator.log"
            else:
                # Create logs directory if it doesn't exist (legacy behavior)
                log_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "logs"
                )
                os.makedirs(log_dir, exist_ok=True)

                # Create timestamped log file name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file_name = f"orca_orchestrator_{timestamp}.log"

            log_file_path = os.path.join(log_dir, log_file_name)

        self._log_file_path = log_file_path
        self._setup_logger()
        self._initialized = True

    def _setup_logger(self):
        """Set up the logger with consistent formatting and handlers."""
        # Create logger
        self._logger = logging.getLogger("orca_orchestrator")
        self._logger.setLevel(logging.INFO)

        # Remove any existing handlers to avoid duplicates
        if self._logger.handlers:
            self._logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler
        file_handler = logging.FileHandler(
            self._log_file_path, mode="a", encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        # Console handler (optional - can be disabled for production)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # Suppress verbose Azure SDK logging
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
            logging.WARNING
        )
        logging.getLogger("azure.storage").setLevel(logging.WARNING)
        logging.getLogger("azure.identity").setLevel(logging.WARNING)
        logging.getLogger("azure.core").setLevel(logging.WARNING)

        # Log the initialization
        self._logger.info("=" * 80)
        self._logger.info("ORCA Orchestrator Logger Initialized")
        self._logger.info("Log file: %s", self._log_file_path)

        # Collect and log detailed system information
        self._log_system_info()

        self._logger.info("=" * 80)

    def _log_system_info(self):
        """
        Log detailed system information.
        """
        try:
            # Basic platform information
            self._logger.info("System Information:")
            self._logger.info("=" * 40)
            self._logger.info("  Hostname: %s", platform.node())
            self._logger.info("  Platform: %s", platform.platform())
            self._logger.info("  Processor: %s", platform.processor())
            self._logger.info("  Machine Type: %s", platform.machine())
            self._logger.info("  Python Version: %s", platform.python_version())
            self._logger.info("  Python Executable: %s", sys.executable)

            # Current working directory
            self._logger.info("  Current Working Directory: %s", os.getcwd())

            # System-specific commands for disk and directory information
            # By default, disable disk and directory information from being reported since it is messy in logs
            REPORT_DISK_INFO = False
            if REPORT_DISK_INFO:
                if platform.system() == "Windows":
                    # Windows commands
                    self._run_system_command(
                        "wmic logicaldisk get size,freespace,caption",
                        "Disk Usage Information",
                    )
                    self._run_system_command("dir", "Current Directory Listing")
                    self._run_system_command(
                        'systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"',
                        "Memory Information",
                    )
                else:
                    # Linux/Unix commands
                    self._run_system_command("uname -a", "System Information")
                    self._run_system_command(
                        "lsblk -o NAME,HCTL,SIZE,MOUNTPOINT", "Block Device Information"
                    )
                    self._run_system_command("df -h", "Disk Usage Information")
                    self._run_system_command("ls -lahn", "Current Directory Listing")
                    self._run_system_command("free -h", "Memory Information")

            self._logger.info("=" * 40)
            self._logger.info("Finished collecting system information:")

        except Exception as e:
            self._logger.error("Error collecting system information: %s", str(e))

    def _run_system_command(self, command: str, description: str):
        """
        Run a system command and log its output.

        Args:
            command: The command to run
            description: Description of what the command does
        """
        try:
            self._logger.info("%s (%s):", description, command)

            # Run the command
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                # Log the output, limiting length if too long
                output = result.stdout.strip()
                if len(output) > 1500:  # Limit output length for log readability
                    output = output[:1500] + "\n... (output truncated)"
                self._logger.info("%s", output)
            else:
                self._logger.warning(
                    "Command failed with return code %d: %s",
                    result.returncode,
                    result.stderr.strip(),
                )

        except subprocess.TimeoutExpired:
            self._logger.warning("Command timed out: %s", command)
        except Exception as e:
            self._logger.error("Error running command '%s': %s", command, str(e))

    @property
    def logger(self):
        """Get the logger instance."""
        return self._logger

    @property
    def log_file_path(self):
        """Get the current log file path."""
        return self._log_file_path

    def get_child_logger(self, name: str):
        """Get a child logger with the specified name."""
        child_logger = self._logger.getChild(name)
        child_logger.setLevel(logging.INFO)
        return child_logger

    def close(self):
        """Close all handlers and clean up."""
        if self._logger:
            self._logger.info("Closing ORCA orchestrator logger")
            self._logger.info("=" * 80)

            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)
                handler.close()


def get_orca_logger(name: Optional[str] = None, log_file_path: Optional[str] = None):
    """Get the ORCA orchestrator logger or a child logger."""
    orca_logger = OrcaLogger(log_file_path)

    if name:
        return orca_logger.get_child_logger(name)
    else:
        return orca_logger.logger


# Logger will be initialized after databank path is known
logger = None


class OrcaPerformanceMonitor:
    """
    Performance monitoring class that tracks runtime and system resource usage
    for ORCA model commands in a separate thread.
    """

    def __init__(
        self,
        poll_interval: float = 1.0,
        track_memory: bool = True,
        track_cpu: bool = True,
    ):
        """
        Initialize the performance monitor.

        Args:
            poll_interval: Interval in seconds between metric collections
            track_memory: Whether to track memory usage
            track_cpu: Whether to track CPU usage
        """
        self.poll_interval = poll_interval
        self.track_memory = track_memory and PSUTIL_AVAILABLE
        self.track_cpu = track_cpu and PSUTIL_AVAILABLE
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_data = []
        self.start_time = None
        self.end_time = None
        self.process = None

        # Warning about missing psutil
        if (track_memory or track_cpu) and not PSUTIL_AVAILABLE:
            print(
                "Warning: psutil not available. Memory/CPU tracking disabled. Install with: pip install psutil"
            )

    def start_monitoring(self, process_pid: Optional[int] = None):
        """
        Start monitoring system metrics in a separate thread.

        Args:
            process_pid: Optional PID of specific process to monitor
        """
        if not PSUTIL_AVAILABLE and (self.track_memory or self.track_cpu):
            return

        self.monitoring = True
        self.start_time = time.time()
        self.metrics_data = []

        # Get process object if PID provided
        if process_pid:
            try:
                self.process = psutil.Process(process_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.process = None

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring and return collected metrics."""
        self.monitoring = False
        self.end_time = time.time()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)

        return self._get_summary()

    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        while self.monitoring:
            timestamp = time.time()
            metrics = {"timestamp": timestamp}

            try:
                if self.track_memory:
                    # System memory
                    sys_memory = psutil.virtual_memory()
                    metrics.update(
                        {
                            "system_memory_total_gb": round(
                                sys_memory.total / (1024**3), 2
                            ),
                            "system_memory_used_gb": round(
                                sys_memory.used / (1024**3), 2
                            ),
                            "system_memory_available_gb": round(
                                sys_memory.available / (1024**3), 2
                            ),
                            "system_memory_percent": round(sys_memory.percent, 1),
                        }
                    )

                    # Process-specific memory if available
                    if self.process:
                        try:
                            proc_memory = self.process.memory_info()
                            metrics.update(
                                {
                                    "process_memory_rss_gb": round(
                                        proc_memory.rss / (1024**3), 3
                                    ),
                                    "process_memory_vms_gb": round(
                                        proc_memory.vms / (1024**3), 3
                                    ),
                                }
                            )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            self.process = None

                if self.track_cpu:
                    # System CPU
                    cpu_percent = psutil.cpu_percent(interval=None)
                    metrics["system_cpu_percent"] = round(cpu_percent, 1)

                    # Process-specific CPU if available
                    if self.process:
                        try:
                            proc_cpu = self.process.cpu_percent()
                            metrics["process_cpu_percent"] = round(proc_cpu, 1)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            self.process = None

                self.metrics_data.append(metrics)

            except Exception as e:
                # Continue monitoring even if individual metric collection fails
                metrics["error"] = str(e)
                self.metrics_data.append(metrics)

            time.sleep(self.poll_interval)

    def _get_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from collected metrics."""
        if not self.metrics_data:
            return {
                "runtime_seconds": (
                    self.end_time - self.start_time
                    if (self.start_time and self.end_time)
                    else 0
                ),
                "samples_collected": 0,
                "monitoring_enabled": False,
            }

        runtime = (
            self.end_time - self.start_time
            if (self.start_time and self.end_time)
            else 0
        )

        summary = {
            "runtime_seconds": round(runtime, 2),
            "samples_collected": len(self.metrics_data),
            "poll_interval": self.poll_interval,
            "monitoring_enabled": True,
        }

        # Calculate memory statistics
        if self.track_memory and any(
            "system_memory_used_gb" in m for m in self.metrics_data
        ):
            memory_values = [
                m.get("system_memory_used_gb", 0)
                for m in self.metrics_data
                if "system_memory_used_gb" in m
            ]
            if memory_values:
                summary.update(
                    {
                        "memory_used_min_gb": round(min(memory_values), 2),
                        "memory_used_max_gb": round(max(memory_values), 2),
                        "memory_used_avg_gb": round(
                            sum(memory_values) / len(memory_values), 2
                        ),
                    }
                )

            # Process memory if available
            proc_memory_values = [
                m.get("process_memory_rss_gb", 0)
                for m in self.metrics_data
                if "process_memory_rss_gb" in m
            ]
            if proc_memory_values:
                summary.update(
                    {
                        "process_memory_min_gb": round(min(proc_memory_values), 3),
                        "process_memory_max_gb": round(max(proc_memory_values), 3),
                        "process_memory_avg_gb": round(
                            sum(proc_memory_values) / len(proc_memory_values), 3
                        ),
                    }
                )

        # Calculate CPU statistics
        if self.track_cpu and any("system_cpu_percent" in m for m in self.metrics_data):
            cpu_values = [
                m.get("system_cpu_percent", 0)
                for m in self.metrics_data
                if "system_cpu_percent" in m
            ]
            if cpu_values:
                summary.update(
                    {
                        "cpu_usage_min_percent": round(min(cpu_values), 1),
                        "cpu_usage_max_percent": round(max(cpu_values), 1),
                        "cpu_usage_avg_percent": round(
                            sum(cpu_values) / len(cpu_values), 1
                        ),
                    }
                )

        return summary

    def export_detailed_data(self, file_path: str) -> bool:
        """
        Export detailed monitoring data to CSV file.

        Args:
            file_path: Path to save the CSV file

        Returns:
            True if export successful, False otherwise
        """
        if not self.metrics_data:
            return False

        try:
            # Determine all possible fieldnames from the data
            all_fields = set()
            for metrics in self.metrics_data:
                all_fields.update(metrics.keys())

            # Sort fieldnames for consistent output
            fieldnames = sorted(all_fields)

            # Ensure timestamp is first if present
            if "timestamp" in fieldnames:
                fieldnames.remove("timestamp")
                fieldnames.insert(0, "timestamp")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for metrics in self.metrics_data:
                    # Convert timestamp to readable format
                    if "timestamp" in metrics:
                        readable_metrics = metrics.copy()
                        readable_metrics["timestamp"] = datetime.fromtimestamp(
                            metrics["timestamp"]
                        ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        writer.writerow(readable_metrics)
                    else:
                        writer.writerow(metrics)

            return True
        except Exception as e:
            if logger:
                logger.error(
                    "Failed to export performance monitoring data to %s: %s",
                    file_path,
                    e,
                )
            return False


class OrcaFileSync:
    """
    Handles all cloud file synchronization operations with Azure Data Lake Storage (ADLS).
    Manages uploads, downloads, and file listing operations for ORCA databanks.

    Key behaviors:
    - Sub-component folders are zipped before upload, extracted after download
    - Config files (yaml, json, log) are uploaded individually with conflict handling
    - Files in outputs/ folder are synced individually (never overwritten)
    - Cloud conflict files go to .cloud_sync_conflict/ folder
    - Local databank determination: empty (download all) vs non-empty (outputs only)
    """

    def __init__(self, sync_logger: logging.Logger):
        """
        Initialize the file sync manager.

        Args:
            sync_logger: Logger instance for sync operations
        """
        self.logger = sync_logger

    def get_adls_uri(self, adls_file: str, adls_dir: str, adls_url: str) -> str:
        """
        Construct ADLS URI from components.

        Args:
            adls_file: File path within ADLS
            adls_dir: Directory within ADLS container
            adls_url: Base ADLS account URL

        Returns:
            Complete ADLS URI
        """
        # Remove leading slash from adls_file if present
        if adls_file.startswith("/"):
            adls_file = adls_file[1:]

        # Construct the full URI
        return f"{adls_url}/{adls_dir}/{adls_file}"

    def _get_adls_connection_with_timeout(
        self, adls_url, adls_container, adls_path, timeout=300
    ):
        """
        Get ADLS connection with timeout to prevent hanging tests.

        Args:
            adls_url: ADLS account URL
            adls_container: ADLS container name
            adls_path: ADLS path
            timeout: Timeout in seconds (default 300)

        Returns:
            Tuple of (az_fs, directory) objects

        Raises:
            RuntimeError: If connection fails or times out
        """

        def _connect():
            return adls_util.get_fs_directory_object(
                account_url=adls_url,
                file_system_name=adls_container,
                directory_name=adls_path,
                credential=adls_util.get_azure_credential(),
            )

        # Use ThreadPoolExecutor with timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_connect)
            try:
                return future.result(timeout=timeout)
            except FutureTimeoutError:
                raise RuntimeError(f"ADLS connection timed out after {timeout} seconds")
            except Exception as e:
                raise RuntimeError(f"ADLS connection failed: {str(e)}")

    def download_from_adls(
        self,
        adls_file: str,
        local_path: str,
        adls_url: str = "https://tlebtsprd01dail06lk01.dfs.core.windows.net",
        adls_container: str = "raw",
        adls_folder: str = "orca_cloud_model_runs",
        export_log: bool = True,
    ) -> Optional[str]:
        """Downloads a file from Azure Data Lake Storage (ADLS) to a local path."""
        time_start = time.time()

        # Prepare operation info
        if adls_folder:
            adls_uri = f"{adls_url}/{adls_container}/{adls_folder}/{adls_file}"
        else:
            adls_uri = f"{adls_url}/{adls_container}/{adls_file}"

        file_name = os.path.basename(adls_file)
        local_file_path = os.path.join(local_path, file_name)

        operation_info = {
            "source_uri": adls_uri,
            "target_file": local_file_path,
            "status": "failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation_type": "download",
            "file_size_bytes": 0,  # Will be updated if successful
        }

        try:
            # Check if ADLS is available
            if not ADLS_AVAILABLE or adls_tables is None:
                self.logger.error(
                    "ADLS functionality not available - missing dependencies"
                )
                return None

            # Create the local directory if it doesn't exist
            os.makedirs(local_path, exist_ok=True)

            # Download the file
            self.logger.info("Downloading from ADLS: %s", adls_uri)
            bytes_io = adls_tables.get_table_by_name(uri=adls_uri)

            if not bytes_io:
                self.logger.error("Failed to download file from ADLS: %s", adls_uri)

                # Log the failed operation
                if export_log:
                    operation_info["error_message"] = (
                        "Failed to download file (no data received)"
                    )
                    self._log_file_operations(
                        operations=[operation_info],
                        log_dir=local_path,
                        operation_type="download",
                        export_log=export_log,
                    )

                return None

            # Write the file to the local path
            with open(local_file_path, "wb") as file:
                if hasattr(bytes_io, "getbuffer"):
                    # If it's a BytesIO object
                    buffer = bytes_io.getbuffer()
                    file.write(buffer)
                    operation_info["file_size_bytes"] = len(buffer)
                else:
                    # If it's raw bytes or a mock
                    if isinstance(bytes_io, bytes):
                        file.write(bytes_io)
                        operation_info["file_size_bytes"] = len(bytes_io)
                    else:
                        # Handle mock objects or other types
                        try:
                            content = bytes(bytes_io)
                            file.write(content)
                            operation_info["file_size_bytes"] = len(content)
                        except (TypeError, ValueError):
                            # Last resort - convert to string and encode
                            content = str(bytes_io).encode("utf-8")
                            file.write(content)
                            operation_info["file_size_bytes"] = len(content)

            time_end = time.time()
            duration = round(time_end - time_start, 1)
            self.logger.info(
                "Successfully downloaded %s in %s seconds", file_name, duration
            )

            # Update operation info
            operation_info["status"] = "success"
            operation_info["duration_seconds"] = duration

            # Log the operation
            if export_log:
                self._log_file_operations(
                    operations=[operation_info],
                    log_dir=local_path,
                    operation_type="download",
                    export_log=export_log,
                )

            return local_file_path

        except Exception as e:
            self.logger.error("Error downloading from ADLS: %s", e)

            # Update operation info with error
            operation_info["error_message"] = str(e)

            # Log the failed operation
            if export_log:
                self._log_file_operations(
                    operations=[operation_info],
                    log_dir=local_path,
                    operation_type="download",
                    export_log=export_log,
                )

            return None

    def download_from_adls_by_pattern(
        self,
        adls_pattern: str,
        local_path: str,
        adls_url: str = "https://tlebtsprd01dail06lk01.dfs.core.windows.net",
        adls_container: str = "raw",
        adls_folder: str = "orca_cloud_model_runs",
        export_log: bool = True,
        list_only: bool = False,
        exclude_log_files: bool = True,
        exclude_error_dumps: bool = True,
        allow_overwrite: bool = True,
        databank_name: str = None,
    ) -> List[str]:
        """
        Downloads multiple files from ADLS matching a pattern.

        Args:
            adls_pattern: Pattern to match files in ADLS
            local_path: Local directory to download files to
            adls_url: ADLS account URL
            adls_container: ADLS container name
            adls_folder: ADLS folder path
            export_log: Whether to export operation logs
            list_only: If True, only return file list without downloading
            exclude_log_files: If True, exclude .log files and files in /logs/ directories
            exclude_error_dumps: If True, exclude files in .error_dump directories
            allow_overwrite: If True, overwrite existing files; if False, skip conflicts
            databank_name: Name of databank for conflict handling

        Returns:
            List of downloaded file paths or file names (if list_only=True)
        """

        operations = []
        matching_files = []
        sync_timestamp = time.strftime("%Y%m%d_%H%M%S")

        try:
            if "**" in adls_pattern:
                # Extract base directory from pattern (everything before /**)
                pattern_base_dir = adls_pattern.split("/**")[0]

                # Build the full ADLS path: adls_folder/pattern_base_dir
                if adls_folder:
                    adls_path = f"{adls_folder}/{pattern_base_dir}"
                else:
                    adls_path = pattern_base_dir

                self.logger.info(
                    "Connecting to ADLS: account=%s, adls_container=%s, path=%s",
                    adls_url,
                    adls_container,
                    adls_path,
                )

                az_fs, _ = self._get_adls_connection_with_timeout(
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_path=adls_path,
                    timeout=300,
                )

                # List files in the directory recursively
                file_list = []
                paths = az_fs.get_paths(path=adls_path, recursive=True)
                for path_item in paths:
                    # Extract relative path from the full path
                    relative_path = path_item.name.replace(f"{adls_path}/", "", 1)
                    if relative_path and not relative_path.endswith(
                        "/"
                    ):  # Skip directories
                        file_list.append(relative_path)

                # Filter out log files if requested
                if exclude_log_files:
                    file_list = [
                        f
                        for f in file_list
                        if not (f.endswith(".log") or "/logs/" in f)
                    ]

                # Filter out cloud conflict files
                cloud_conflict_pattern = ".cloud_sync_conflict/"
                file_list = [
                    f for f in file_list if not f.startswith(cloud_conflict_pattern)
                ]

                # Filter out .error_dump files if requested
                if exclude_error_dumps:
                    error_dump_pattern = ".error_dump/"
                    file_list = [
                        f for f in file_list if not f.startswith(error_dump_pattern)
                    ]

                # Return the list of files if list_only is True
                if list_only:
                    return [f"{pattern_base_dir}/{file}" for file in file_list]

                matching_files = [f"{pattern_base_dir}/{file}" for file in file_list]

            elif "*" in adls_pattern:
                # Extract directory and filename pattern
                dir_path = os.path.dirname(adls_pattern)
                filename_pattern = os.path.basename(adls_pattern)

                # Build the full ADLS path: adls_folder/dir_path
                if adls_folder:
                    adls_path = f"{adls_folder}/{dir_path}"
                else:
                    adls_path = dir_path

                self.logger.info(
                    "Connecting to ADLS: account=%s, adls_container=%s, path=%s",
                    adls_url,
                    adls_container,
                    adls_path,
                )

                az_fs, _ = self._get_adls_connection_with_timeout(
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_path=adls_path,
                    timeout=300,
                )

                # List files in the directory non-recursively
                file_list = []
                paths = az_fs.get_paths(path=adls_path, recursive=False)
                for path_item in paths:
                    # Extract the file name from the full path
                    file_name = os.path.basename(path_item.name)
                    if not path_item.is_directory:  # Skip directories
                        file_list.append(file_name)

                # Filter files based on pattern
                matching_file_names = [
                    f for f in file_list if fnmatch.fnmatch(f, filename_pattern)
                ]
                matching_files = [f"{dir_path}/{file}" for file in matching_file_names]

                # Filter out log files if requested
                if exclude_log_files:
                    matching_files = [
                        f
                        for f in matching_files
                        if not (f.endswith(".log") or "/logs/" in f)
                    ]

                # Filter out .error_dump files if requested
                if exclude_error_dumps:
                    matching_files = [
                        f for f in matching_files if not "/.error_dump/" in f
                    ]

                # Return the list of matching files if list_only is True
                if list_only:
                    return matching_files
            else:
                # If no wildcard, just use the specific file
                matching_files = [adls_pattern]

                # Filter out log files if requested and not doing list_only
                if exclude_log_files and not list_only:
                    matching_files = [
                        f
                        for f in matching_files
                        if not (f.endswith(".log") or "/logs/" in f)
                    ]

                # Filter out .error_dump files if requested and not doing list_only
                if exclude_error_dumps and not list_only:
                    matching_files = [
                        f for f in matching_files if not "/.error_dump/" in f
                    ]

                # Return the file path if list_only is True
                if list_only:
                    return matching_files

            # If list_only, we've already returned the results above
            if list_only:
                return matching_files

            # If not list_only, download each matching file
            downloaded_files = []
            for adls_file in matching_files:
                # Create local directory structure if needed
                file_dir = os.path.dirname(adls_file)
                local_file_dir = os.path.join(local_path, file_dir)
                os.makedirs(local_file_dir, exist_ok=True)

                # Check for local file conflicts and handle appropriately
                file_name = os.path.basename(adls_file)
                local_file_path = os.path.join(local_file_dir, file_name)

                if os.path.exists(local_file_path) and not allow_overwrite:
                    # Skip downloading files that exist both locally and in cloud
                    self.logger.info(
                        "File exists both locally and in cloud, skipping download: %s",
                        local_file_path,
                    )
                    continue
                elif (
                    os.path.exists(local_file_path)
                    and allow_overwrite
                    and databank_name
                ):
                    # Move local conflict file to conflict directory
                    rel_path = os.path.relpath(local_file_path, local_path)
                    base_name, ext = os.path.splitext(rel_path)
                    conflict_file_name = (
                        f"{os.path.basename(base_name)}_{sync_timestamp}_bak{ext}"
                    )
                    conflict_rel_path = os.path.join(
                        os.path.dirname(rel_path), conflict_file_name
                    )
                    conflict_path = os.path.join(
                        local_path, ".cloud_sync_conflict", conflict_rel_path
                    )

                    os.makedirs(os.path.dirname(conflict_path), exist_ok=True)
                    self.logger.info(
                        "Local conflict detected. Moving local file from %s to %s",
                        local_file_path,
                        conflict_path,
                    )
                    shutil.move(local_file_path, conflict_path)

                # Download the file
                local_file = self.download_from_adls(
                    adls_file=adls_file,
                    local_path=local_file_dir,
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_folder=adls_folder,
                    export_log=False,  # We'll log the batch operation
                )

                if local_file:
                    downloaded_files.append(local_file)

                    # Add to operations for logging
                    operation_info = {
                        "source_uri": (
                            f"{adls_url}/{adls_container}/{adls_folder}/{adls_file}"
                            if adls_folder
                            else f"{adls_url}/{adls_container}/{adls_file}"
                        ),
                        "target_file": local_file,
                        "status": "success",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "operation_type": "batch_download",
                        "file_size_bytes": os.path.getsize(local_file),
                    }
                    operations.append(operation_info)

            # Log batch operation
            if export_log and operations:
                self._log_file_operations(
                    operations=operations,
                    log_dir=local_path,
                    operation_type="batch_download",
                    export_log=export_log,
                )

            return downloaded_files

        except Exception as e:
            self.logger.error("Error in download_from_adls_by_pattern: %s", str(e))

            # Log the error
            if export_log:
                error_info = {
                    "source_uri": adls_pattern,
                    "target_path": local_path,
                    "status": "failed",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "operation_type": "batch_download",
                    "error_message": str(e),
                }
                self._log_file_operations(
                    operations=[error_info],
                    log_dir=local_path,
                    operation_type="batch_download",
                    export_log=export_log,
                )

            return []

    def upload_to_adls(
        self,
        local_file_path: str,
        adls_file: str,
        adls_url: str = "https://tlebtsprd01dail06lk01.dfs.core.windows.net",
        adls_container: str = "raw",
        adls_folder: str = "orca_cloud_model_runs",
        export_log: bool = True,
    ) -> bool:
        """Uploads a file to Azure Data Lake Storage (ADLS)."""
        time_start = time.time()
        log_dir = os.path.dirname(local_file_path)
        operation_info = {
            "source_file": local_file_path,
            "target_uri": "",  # Will be updated with full URI
            "status": "failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation_type": "upload",
            "file_size_bytes": (
                0
                if not os.path.exists(local_file_path)
                else os.path.getsize(local_file_path)
            ),
        }

        try:

            if not os.path.exists(local_file_path):
                self.logger.error("Local file does not exist: %s", local_file_path)
                return False

            # Check if ADLS is available
            if not ADLS_AVAILABLE or adls_tables is None:
                self.logger.error(
                    "ADLS functionality not available - missing dependencies"
                )
                return False

            # Construct the ADLS URI
            adls_uri = f"{adls_url}/{adls_container}/{adls_folder}/{adls_file}"
            operation_info["target_uri"] = adls_uri

            # Upload the file
            self.logger.info("Uploading to ADLS: %s", adls_uri)
            adls_tables.write_table_by_name(
                uri=adls_uri,
                local_path=os.path.dirname(local_file_path),
                file_name=os.path.basename(local_file_path),
            )

            time_end = time.time()
            duration = round(time_end - time_start, 1)
            self.logger.info(
                "Successfully uploaded %s in %s seconds",
                os.path.basename(local_file_path),
                duration,
            )

            # Update operation info
            operation_info["status"] = "success"
            operation_info["duration_seconds"] = duration

            # Log the operation
            if export_log:
                self._log_file_operations(
                    operations=[operation_info],
                    log_dir=log_dir,
                    operation_type="upload",
                    export_log=export_log,
                )

            return True

        except Exception as e:
            self.logger.error("Error uploading to ADLS: %s", e)

            # Update operation info with error
            operation_info["error_message"] = str(e)

            # Log the failed operation
            if export_log:
                self._log_file_operations(
                    operations=[operation_info],
                    log_dir=log_dir,
                    operation_type="upload",
                    export_log=export_log,
                )

            return False

    def _log_file_operations(
        self,
        operations: List[Dict[str, Any]],
        log_dir: str,
        operation_type: str,
        export_log: bool = True,
    ) -> str:
        """Log file operations to a CSV file."""
        if not operations or not export_log:
            return ""

        # Count operations by status
        operation_counts = {}
        for op in operations:
            status = op.get("status", "unknown")
            operation_counts[status] = operation_counts.get(status, 0) + 1

        # Log summary
        total_ops = len(operations)
        self.logger.info(
            "%s operations summary - Total: %d, By status: %s",
            operation_type.capitalize(),
            total_ops,
            ", ".join([f"{k}: {v}" for k, v in operation_counts.items()]),
        )

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create CSV file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"{operation_type}_log_{timestamp}.csv")

        # Determine the fieldnames based on the keys in the first operation
        if operations:
            fieldnames = list(operations[0].keys())
        else:
            fieldnames = ["source", "target", "status", "timestamp"]

        # Write to CSV
        with open(log_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for operation in operations:
                writer.writerow(operation)

        self.logger.info(
            "%s operations log exported to: %s",
            operation_type.capitalize(),
            log_filename,
        )
        return log_filename


class OrcaDatabank:
    """
    Manages data initialization, movement between steps, and local file operations.
    Handles file management, directory structure, and data archiving.
    Note: Cloud sync operations are now handled by OrcaFileSync class.
    """

    def __init__(self, databank_path: str, databank_logger: logging.Logger):
        """Initialize the databank manager."""
        self.databank_path = databank_path
        self.logger = databank_logger

    def log_file_operations(
        self,
        operations: List[Dict[str, Any]],
        log_dir: str,
        operation_type: str,
        export_log: bool = True,
    ) -> str:
        """Log file operations to a CSV file."""
        if not operations or not export_log:
            return ""

        # Count operations by status
        operation_counts = {}
        for op in operations:
            status = op.get("status", "unknown")
            operation_counts[status] = operation_counts.get(status, 0) + 1

        # Log summary
        total_ops = len(operations)
        self.logger.info(
            "%s operations summary - Total: %d, By status: %s",
            operation_type.capitalize(),
            total_ops,
            ", ".join([f"{k}: {v}" for k, v in operation_counts.items()]),
        )

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create CSV file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"{operation_type}_log_{timestamp}.csv")

        # Determine the fieldnames based on the keys in the first operation
        if operations:
            fieldnames = list(operations[0].keys())
        else:
            fieldnames = ["source", "target", "status", "timestamp"]

        # Write to CSV
        with open(log_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for operation in operations:
                writer.writerow(operation)

        self.logger.info(
            "%s operations log exported to: %s",
            operation_type.capitalize(),
            log_filename,
        )
        return log_filename

    def get_adls_uri(self, adls_file: str, adls_dir: str, adls_url: str) -> str:
        """
        Construct ADLS URI from components.

        Args:
            adls_file: File path within ADLS
            adls_dir: Directory within ADLS container
            adls_url: Base ADLS account URL

        Returns:
            Complete ADLS URI
        """
        # Remove leading slash from adls_file if present
        if adls_file.startswith("/"):
            adls_file = adls_file[1:]

        # Construct the full URI
        return f"{adls_url}/{adls_dir}/{adls_file}"

    def zip_files(self, file_paths: List[str], zip_path: str) -> bool:
        """
        Create a zip file from a list of file paths.

        Args:
            file_paths: List of absolute file paths to include
            zip_path: Path where zip file should be created

        Returns:
            True if successful, False otherwise
        """
        if not file_paths:
            self.logger.warning("No files provided for zipping")
            return False

        try:
            # Create the directory for the zip file if it doesn't exist
            zip_dir = os.path.dirname(zip_path)
            if zip_dir and not os.path.exists(zip_dir):
                os.makedirs(zip_dir, exist_ok=True)

            self.logger.info(f"Creating zip file: {zip_path}")
            file_count = 0

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        # Get the filename to use as archive name
                        arcname = os.path.basename(file_path)
                        zf.write(file_path, arcname)
                        file_count += 1
                    else:
                        self.logger.warning(f"  File not found: {file_path}")

            self.logger.info(
                f"Successfully created zip file: {zip_path}, total file count: {file_count}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error creating zip file: {e}")
            # Clean up partially created zip file
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass
            return False

    def unpack_zip_file(
        self,
        zip_file_path: str,
        output_dir: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        export_log: bool = True,
    ) -> bool:
        """
        Unpack a zip file to a directory with optional pattern filtering.

        Args:
            zip_file_path: Path to the zip file to extract
            output_dir: Directory to extract files to
            include_patterns: Patterns for files to include (None = include all)
            exclude_patterns: Patterns for files to exclude (None = exclude none)
            export_log: Whether to export operation log

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(zip_file_path):
            self.logger.error(f"Zip file not found: {zip_file_path}")
            return False

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            self.logger.info(f"Unpacking zip file: {zip_file_path} to {output_dir}")

            operations = []
            file_count = 0

            with zipfile.ZipFile(zip_file_path, "r") as zip_file:
                # Get list of files to extract
                files_to_extract = []

                for file_info in zip_file.filelist:
                    filename = file_info.filename

                    # Skip directory entries
                    if filename.endswith("/"):
                        continue

                    # Check include patterns
                    if include_patterns:
                        if not any(
                            fnmatch.fnmatch(filename, pattern)
                            for pattern in include_patterns
                        ):
                            continue

                    # Check exclude patterns
                    if exclude_patterns:
                        if any(
                            fnmatch.fnmatch(filename, pattern)
                            for pattern in exclude_patterns
                        ):
                            continue

                    files_to_extract.append(file_info)

                # Extract the selected files
                for file_info in files_to_extract:
                    filename = file_info.filename
                    target_path = os.path.join(output_dir, filename)

                    operation_info = {
                        "source": filename,
                        "target": target_path,
                        "operation_type": "extract",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "pending",
                    }

                    try:
                        # Create directory if needed
                        target_dir = os.path.dirname(target_path)
                        if target_dir and not os.path.exists(target_dir):
                            os.makedirs(target_dir, exist_ok=True)

                        # Extract the file
                        zip_file.extract(file_info, output_dir)
                        operation_info["status"] = "success"
                        file_count += 1

                    except Exception as e:
                        self.logger.warning(f"  Failed to extract {filename}: {e}")
                        operation_info["status"] = "failed"
                        operation_info["error_message"] = str(e)

                    operations.append(operation_info)

            # Log extraction operations
            if export_log and operations:
                self.log_file_operations(
                    operations=operations,
                    log_dir=output_dir,
                    operation_type="extract",
                    export_log=export_log,
                )

            self.logger.info(
                f"Successfully unpacked zip file: {zip_file_path}, total file count: {file_count}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error unpacking zip file: {e}")
            return False

    def unpack_landuse_zip(
        self,
        zip_file_path: str,
        output_dir: str,
        model_year: str,
        export_log: bool = True,
    ) -> bool:
        """
        Unpack landuse zip files with model year filtering.

        Args:
            zip_file_path: Path to the landuse zip file
            output_dir: Directory to extract files to
            model_year: Model year to filter files by
            export_log: Whether to export operation log

        Returns:
            True if successful, False otherwise
        """
        # Define patterns for landuse files
        landuse_patterns = [
            f"*land_use_{model_year}.csv",
            f"*info_{model_year}.txt",
            f"households_{model_year}.csv",
            f"persons_{model_year}.csv",
        ]

        # Extract files matching the landuse patterns
        self.unpack_zip_file(
            zip_file_path=zip_file_path,
            output_dir=output_dir,
            include_patterns=landuse_patterns,
            export_log=export_log,
        )

        # renames extracted files
        lusp_spec = {
            f"households_{model_year}.csv": "households.csv",
            f"persons_{model_year}.csv": "persons.csv",
            f"taz1709_land_use_{model_year}.csv": "land_use.csv",
            f"taz1709_land_use_metadata_{model_year}.csv": "land_use_metadata.csv",
            f"info_{model_year}.txt": "info.txt",
        }
        for src, target in lusp_spec.items():
            src_path = os.path.join(output_dir, src)
            target_path = os.path.join(output_dir, target)
            if os.path.exists(src_path):
                os.rename(src_path, target_path)

        return True

    def zip_directory(
        self,
        dir_path: str,
        zip_path: str,
        skip_patterns: Optional[List[str]] = None,
        include_empty_dirs: bool = False,
    ) -> bool:
        """Zips all files and subdirectories within a given directory."""
        if not os.path.isdir(dir_path):
            self.logger.error(f"Directory not found: {dir_path}")
            return False

        if skip_patterns is None:
            skip_patterns = []

        # Separate regular skip patterns from negation patterns
        regular_skip_patterns = []
        negation_patterns = []

        for pattern in skip_patterns:
            if pattern.startswith("!"):
                # Remove the '!' prefix for negation patterns
                negation_patterns.append(pattern[1:])
            else:
                regular_skip_patterns.append(pattern)

        if not zip_path.lower().endswith(".zip"):
            zip_path += ".zip"
            self.logger.warning(f"Added .zip extension to output file: '{zip_path}'")

        # Create parent directory for the zip file if it doesn't exist
        zip_parent_dir = os.path.dirname(zip_path)
        if zip_parent_dir and not os.path.exists(zip_parent_dir):
            self.logger.info(
                f"Creating parent directory for zip file: {zip_parent_dir}"
            )
            os.makedirs(zip_parent_dir, exist_ok=True)

        self.logger.info(f"Creating zip file: {zip_path}")
        self.logger.info(f"Source directory: {dir_path}")
        if skip_patterns:
            self.logger.info(f"Skip patterns: {regular_skip_patterns}")
            if negation_patterns:
                self.logger.info(f"Negation patterns (include): {negation_patterns}")

        def should_include_path(path_basename: str, path_relative: str) -> bool:
            """Determines if a path should be included based on skip and negation patterns."""
            # First check if it matches any negation patterns (these take precedence)
            if negation_patterns:
                include_by_basename = any(
                    fnmatch.fnmatch(path_basename, pattern)
                    for pattern in negation_patterns
                )
                include_by_relative = any(
                    fnmatch.fnmatch(path_relative, pattern)
                    for pattern in negation_patterns
                )
                if include_by_basename or include_by_relative:
                    return True

            # Then check if it matches any regular skip patterns
            skip_by_basename = any(
                fnmatch.fnmatch(path_basename, pattern)
                for pattern in regular_skip_patterns
            )
            skip_by_relative = any(
                fnmatch.fnmatch(path_relative, pattern)
                for pattern in regular_skip_patterns
            )
            should_skip = skip_by_basename or skip_by_relative

            # If no patterns matched, include the path
            return not should_skip

        def should_traverse_directory(dir_basename: str, dir_relative: str) -> bool:
            """Determines if a directory should be traversed based on patterns."""
            # If there are negation patterns, we need to check if this directory
            # or any of its potential contents could match them
            if negation_patterns:
                # Check if this directory itself matches any negation patterns
                include_by_basename = any(
                    fnmatch.fnmatch(dir_basename, pattern)
                    for pattern in negation_patterns
                )
                include_by_relative = any(
                    fnmatch.fnmatch(dir_relative, pattern)
                    for pattern in negation_patterns
                )

                # Check if any negation pattern could match contents within this directory
                could_match_contents = any(
                    pattern.startswith(dir_relative + "/")
                    or pattern.startswith(dir_basename + "/")
                    or pattern.endswith("/**")
                    and (
                        fnmatch.fnmatch(dir_relative, pattern[:-3])
                        or fnmatch.fnmatch(dir_basename, pattern[:-3])
                    )
                    for pattern in negation_patterns
                )

                if include_by_basename or include_by_relative or could_match_contents:
                    return True

            # Use the regular inclusion logic
            return should_include_path(dir_basename, dir_relative)

        try:
            file_count = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(dir_path, topdown=True):
                    # Filter directories for traversal
                    dirs_to_remove = set()
                    for d in dirs:
                        # Calculate relative path for the directory
                        relative_dir_path = os.path.normpath(
                            os.path.join(os.path.relpath(root, dir_path), d)
                        )
                        if relative_dir_path == ".":
                            relative_dir_path = d  # for top-level dirs

                        # Use the helper function to determine if directory should be traversed
                        if not should_traverse_directory(d, relative_dir_path):
                            dirs_to_remove.add(d)
                            self.logger.info(
                                f"  Not traversing directory: {relative_dir_path}"
                            )

                    dirs[:] = [d for d in dirs if d not in dirs_to_remove]

                    # Add files, skipping based on patterns
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        relative_file_path = os.path.relpath(file_path, dir_path)

                        # Use the helper function to determine if file should be included
                        if should_include_path(file_name, relative_file_path):
                            arcname = relative_file_path  # Path inside the zip file
                            zf.write(file_path, arcname)
                            file_count += 1
                        else:
                            self.logger.info(f"  Skipping file: {relative_file_path}")

                    # Add empty directories if requested
                    if include_empty_dirs:
                        if not files and not dirs:
                            current_dir_rel_path = os.path.relpath(root, dir_path)
                            if current_dir_rel_path != ".":
                                current_dir_basename = os.path.basename(root)

                                # Use the helper function to determine if empty directory should be included
                                if should_include_path(
                                    current_dir_basename, current_dir_rel_path
                                ):
                                    self.logger.info(
                                        f"  Adding empty directory: {current_dir_rel_path}/"
                                    )
                                    dir_arcname = current_dir_rel_path + "/"
                                    zinfo = zipfile.ZipInfo(dir_arcname)
                                    zinfo.external_attr = (
                                        0o40755 << 16
                                    )  # Directory permissions
                                    zf.writestr(zinfo, "")

            self.logger.info(
                f"Successfully created zip file: {zip_path}, total file count: {file_count}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error creating zip file: {e}")
            # Clean up partially created zip file
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return False

    def cleanup_files_by_patterns(
        self, base_dir: str, patterns: List[str], export_log: bool = True
    ) -> List[str]:
        """Removes files matching the specified patterns from the given directory."""
        deleted_files = []
        operations = []

        try:
            self.logger.info(
                "Cleaning up files in %s matching patterns: %s", base_dir, patterns
            )

            for pattern in patterns:
                # Handle both absolute and relative patterns
                if os.path.isabs(pattern):
                    full_pattern = pattern
                else:
                    full_pattern = os.path.join(base_dir, pattern)

                # Find all files matching the pattern
                matching_files = glob.glob(full_pattern, recursive=True)

                # Delete each file
                for file_path in matching_files:
                    if os.path.isfile(file_path):
                        # Prepare operation info
                        operation_info = {
                            "file_path": file_path,
                            "pattern": pattern,
                            "status": "pending",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "operation_type": "delete",
                            "file_size_bytes": os.path.getsize(file_path),
                        }

                        try:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            self.logger.info("Deleted file: %s", file_path)

                            # Update operation info
                            operation_info["status"] = "success"
                        except Exception as e:
                            self.logger.warning(
                                "Could not delete file %s: %s", file_path, e
                            )

                            # Update operation info
                            operation_info["status"] = "failed"
                            operation_info["error_message"] = str(e)

                        operations.append(operation_info)

            # Log deletion operations
            if export_log and operations:
                self.log_file_operations(
                    operations=operations,
                    log_dir=base_dir,
                    operation_type="delete",
                    export_log=export_log,
                )

            return deleted_files

        except Exception as e:
            self.logger.error("Error cleaning up files: %s", e)

            # Log the failed operations
            if export_log and operations:
                # Mark remaining operations as failed
                for op in operations:
                    if op["status"] == "pending":
                        op["status"] = "failed"
                        op["error_message"] = str(e)

                self.log_file_operations(
                    operations=operations,
                    log_dir=base_dir,
                    operation_type="delete",
                    export_log=export_log,
                )

            return deleted_files

    def copy_template_directory(
        self,
        source_dir: str,
        target_dir: str,
        overwrite: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        export_copy_log: bool = True,
    ) -> bool:
        """Copies a template directory to a target location."""
        try:
            # Ensure source directory exists
            if not os.path.exists(source_dir):
                self.logger.error("Source directory does not exist: %s", source_dir)
                return False

            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)

            self.logger.info("Copying template from %s to %s", source_dir, target_dir)

            # Keep track of file operations
            file_operations = []
            skipped_files = 0
            copied_files = 0
            conflict_files = 0

            # Walk through the source directory and copy files
            for root, _, files in os.walk(source_dir):
                # Calculate the relative path to maintain directory structure
                rel_path = os.path.relpath(root, source_dir)
                target_subdir = os.path.join(target_dir, rel_path)

                # Create the target subdirectory if it doesn't exist
                os.makedirs(target_subdir, exist_ok=True)

                # Copy files
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_subdir, file)

                    # Apply include/exclude patterns if provided
                    if include_patterns and not any(
                        fnmatch.fnmatch(file, pattern) for pattern in include_patterns
                    ):
                        skipped_files += 1
                        continue
                    if exclude_patterns and any(
                        fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns
                    ):
                        skipped_files += 1
                        continue

                    # Skip if file exists and overwrite is False
                    if os.path.exists(target_file) and not overwrite:
                        file_operations.append(
                            {
                                "source_file": source_file,
                                "target_file": target_file,
                                "status": "skipped (file exists)",
                                "time_copied": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )
                        conflict_files += 1
                        continue

                    # Copy the file and record timestamp immediately after
                    shutil.copy2(source_file, target_file)
                    copy_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    copied_files += 1

                    file_operations.append(
                        {
                            "source_file": source_file,
                            "target_file": target_file,
                            "status": "copied",
                            "time_copied": copy_time,
                        }
                    )

            # Log summary with more detailed information
            if conflict_files > 0:
                self.logger.info(
                    "Some files were not copied because they already exist in the target directory and overwrite=False"
                )

            self.logger.info(
                "Template copy results from %s to %s: Files copied: %d, Files skipped due to patterns: %d, Files skipped due to conflicts: %d",
                source_dir,
                target_dir,
                copied_files,
                skipped_files,
                conflict_files,
            )

            # Export the list of file operations if requested
            if export_copy_log and file_operations:
                self.log_file_operations(
                    operations=file_operations,
                    log_dir=target_dir,
                    operation_type="copy",
                    export_log=export_copy_log,
                )

            return True

        except Exception as e:
            self.logger.error("Error copying template directory: %s", e)
            return False

    def copy_template_file(
        self,
        source_file: str,
        target_file: str,
        overwrite: bool = False,
        export_log: bool = True,
    ) -> bool:
        """Copies a template file to a target location."""
        operation_info = {
            "source_file": source_file,
            "target_file": target_file,
            "status": "pending",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation_type": "copy_file",
            "file_size_bytes": (
                os.path.getsize(source_file) if os.path.exists(source_file) else 0
            ),
        }

        target_dir = os.path.dirname(target_file)

        try:
            # Ensure source file exists
            if not os.path.exists(source_file):
                self.logger.error("Source file does not exist: %s", source_file)

                # Update operation info
                operation_info["status"] = "failed"
                operation_info["error_message"] = "Source file does not exist"

                # Log the failed operation
                if export_log:
                    self.log_file_operations(
                        operations=[operation_info],
                        log_dir=(
                            target_dir if os.path.isdir(target_dir) else os.getcwd()
                        ),
                        operation_type="copy_file",
                        export_log=export_log,
                    )

                return False

            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)

            # Check if target file exists and handle overwrite flag
            if os.path.exists(target_file) and not overwrite:
                self.logger.info(
                    "Target file exists and overwrite=False, skipping: %s", target_file
                )

                # Update operation info
                operation_info["status"] = "skipped"

                # Log the skipped operation
                if export_log:
                    self.log_file_operations(
                        operations=[operation_info],
                        log_dir=target_dir,
                        operation_type="copy_file",
                        export_log=export_log,
                    )

                return True

            # Copy the file
            shutil.copy2(source_file, target_file)
            self.logger.info("Copied: %s -> %s", source_file, target_file)

            # Update operation info
            operation_info["status"] = "success"
            operation_info["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            operation_info["file_size_bytes"] = os.path.getsize(target_file)

            # Log the successful operation
            if export_log:
                self.log_file_operations(
                    operations=[operation_info],
                    log_dir=target_dir,
                    operation_type="copy_file",
                    export_log=export_log,
                )

            return True

        except Exception as e:
            self.logger.error("Error copying template file: %s", e)

            # Update operation info
            operation_info["status"] = "failed"
            operation_info["error_message"] = str(e)

            # Log the failed operation
            if export_log:
                self.log_file_operations(
                    operations=[operation_info],
                    log_dir=target_dir if os.path.isdir(target_dir) else os.getcwd(),
                    operation_type="copy_file",
                    export_log=export_log,
                )

            return False

    def create_error_dump(
        self,
        step_name: str,
        iteration: int,
        error_message: str,
        include_all_databank: bool = False,
        export_log: bool = True,
    ) -> bool:
        """
        Create an error dump when a model execution fails.

        This method creates a comprehensive error dump containing:
        - All data from the failed step directory
        - Configuration files (yaml, json)
        - Log files
        - State information
        - Optionally, the entire databank content

        Args:
            step_name: Name of the step that failed
            iteration: Current iteration number
            error_message: Error message describing the failure
            include_all_databank: If True, includes entire databank in error dump
            export_log: Whether to export operation log

        Returns:
            bool: True if error dump was created successfully, False otherwise
        """
        try:
            # Create error dump directory structure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_dump_base = os.path.join(self.databank_path, ".error_dump")
            error_dump_dir = os.path.join(
                error_dump_base, f"error_{step_name}_iter{iteration}_{timestamp}"
            )

            os.makedirs(error_dump_dir, exist_ok=True)

            self.logger.info("Creating error dump in: %s", error_dump_dir)

            # Create error info file
            error_info = {
                "timestamp": timestamp,
                "step_name": step_name,
                "iteration": iteration,
                "error_message": error_message,
                "databank_path": self.databank_path,
                "dump_contents": [],
            }

            operations = []

            # 1. Copy the failed step directory if it exists
            step_dir = os.path.join(self.databank_path, step_name)
            if os.path.exists(step_dir):
                step_dump_dir = os.path.join(error_dump_dir, f"{step_name}")
                self.logger.info("Copying failed step directory: %s", step_dir)

                success = self.copy_template_directory(
                    source_dir=step_dir,
                    target_dir=step_dump_dir,
                    overwrite=True,
                    export_copy_log=False,  # We'll log everything together
                )

                if success:
                    error_info["dump_contents"].append(f"{step_name}/")
                    operations.append(
                        {
                            "source": step_dir,
                            "target": step_dump_dir,
                            "type": "directory_copy",
                            "status": "success",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                else:
                    operations.append(
                        {
                            "source": step_dir,
                            "target": step_dump_dir,
                            "type": "directory_copy",
                            "status": "failed",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "error": "Failed to copy step directory",
                        }
                    )

            # 2. Copy configuration files
            config_files = [
                "orca_model_config.yaml",
                "orca_model_config_default.yaml",
                "orca_model_state.json",
            ]

            config_dump_dir = os.path.join(error_dump_dir, "config")
            os.makedirs(config_dump_dir, exist_ok=True)

            for config_file in config_files:
                config_path = os.path.join(self.databank_path, config_file)
                if os.path.exists(config_path):
                    target_path = os.path.join(config_dump_dir, config_file)
                    try:
                        shutil.copy2(config_path, target_path)
                        error_info["dump_contents"].append(f"config/{config_file}")
                        operations.append(
                            {
                                "source": config_path,
                                "target": target_path,
                                "type": "file_copy",
                                "status": "success",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )
                    except Exception as e:
                        operations.append(
                            {
                                "source": config_path,
                                "target": target_path,
                                "type": "file_copy",
                                "status": "failed",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "error": str(e),
                            }
                        )

            # 3. Copy log files
            log_files = glob.glob(os.path.join(self.databank_path, "*.log"))
            if log_files:
                logs_dump_dir = os.path.join(error_dump_dir, "logs")
                os.makedirs(logs_dump_dir, exist_ok=True)

                for log_file in log_files:
                    log_name = os.path.basename(log_file)
                    target_path = os.path.join(logs_dump_dir, log_name)
                    try:
                        shutil.copy2(log_file, target_path)
                        error_info["dump_contents"].append(f"logs/{log_name}")
                        operations.append(
                            {
                                "source": log_file,
                                "target": target_path,
                                "type": "file_copy",
                                "status": "success",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )
                    except Exception as e:
                        operations.append(
                            {
                                "source": log_file,
                                "target": target_path,
                                "type": "file_copy",
                                "status": "failed",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "error": str(e),
                            }
                        )

            # 4. Copy outputs directory if it exists
            outputs_dir = os.path.join(self.databank_path, "outputs")
            if os.path.exists(outputs_dir):
                outputs_dump_dir = os.path.join(error_dump_dir, "outputs")
                self.logger.info("Copying outputs directory for error analysis")

                success = self.copy_template_directory(
                    source_dir=outputs_dir,
                    target_dir=outputs_dump_dir,
                    overwrite=True,
                    export_copy_log=False,
                )

                if success:
                    error_info["dump_contents"].append("outputs/")
                    operations.append(
                        {
                            "source": outputs_dir,
                            "target": outputs_dump_dir,
                            "type": "directory_copy",
                            "status": "success",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                else:
                    operations.append(
                        {
                            "source": outputs_dir,
                            "target": outputs_dump_dir,
                            "type": "directory_copy",
                            "status": "failed",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "error": "Failed to copy outputs directory",
                        }
                    )

            # 5. Optionally copy entire databank (excluding the error dump itself)
            if include_all_databank:
                self.logger.info("Including full databank content in error dump")
                full_dump_dir = os.path.join(error_dump_dir, "full_databank")

                success = self.copy_template_directory(
                    source_dir=self.databank_path,
                    target_dir=full_dump_dir,
                    overwrite=True,
                    exclude_patterns=[".error_dump/**"],  # Exclude error dump directory
                    export_copy_log=False,
                )

                if success:
                    error_info["dump_contents"].append("full_databank/")
                    operations.append(
                        {
                            "source": self.databank_path,
                            "target": full_dump_dir,
                            "type": "full_databank_copy",
                            "status": "success",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                else:
                    operations.append(
                        {
                            "source": self.databank_path,
                            "target": full_dump_dir,
                            "type": "full_databank_copy",
                            "status": "failed",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "error": "Failed to copy full databank",
                        }
                    )

            # 6. Save error information
            error_info_file = os.path.join(error_dump_dir, "error_info.json")
            with open(error_info_file, "w", encoding="utf-8") as f:
                json.dump(error_info, f, indent=2, ensure_ascii=False)

            error_info["dump_contents"].append("error_info.json")

            # 7. Create a zip archive of the error dump
            zip_name = f"error_dump_{step_name}_iter{iteration}_{timestamp}.zip"
            zip_path = os.path.join(error_dump_base, zip_name)

            zip_success = self.zip_directory(
                dir_path=error_dump_dir, zip_path=zip_path, include_empty_dirs=True
            )

            if zip_success:
                self.logger.info("Error dump archive created: %s", zip_path)
                # Remove the unzipped directory to save space
                shutil.rmtree(error_dump_dir)
                error_info["archive_path"] = zip_path
            else:
                self.logger.warning(
                    "Failed to create error dump archive, keeping directory: %s",
                    error_dump_dir,
                )

            # 8. Log all operations
            if export_log and operations:
                self.log_file_operations(
                    operations=operations,
                    log_dir=error_dump_base,
                    operation_type="error_dump",
                    export_log=export_log,
                )

            # Summary logging
            self.logger.info("Error dump completed successfully")
            self.logger.info(
                "Error dump location: %s", zip_path if zip_success else error_dump_dir
            )
            self.logger.info(
                "Error dump contents: %s", ", ".join(error_info["dump_contents"])
            )

            return True

        except Exception as e:
            self.logger.error("Failed to create error dump: %s", e)
            return False


class OrcaState:
    """
    Manages the state of the ORCA model run.
    Handles reading from and writing to the state file, tracking iterations and steps.
    """

    def __init__(self, state_file_path: str, state_logger: logging.Logger):
        """
        Initialize the state manager.

        Args:
            state_file_path: Path to the state file
            state_logger: Logger instance
        """
        self.state_file_path = state_file_path
        self.logger = state_logger
        self.state = self._initialize_state()

    def _initialize_state(self) -> Dict:
        """Initialize the state, either by reading from existing file or creating default."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error("Error reading state file: %s", e)
                state = self._create_default_state()
                self._save_state(state)
                return state
        else:
            state = self._create_default_state()
            self._save_state(state)
            return state

    def _create_default_state(self) -> Dict:
        """Create a default state structure."""
        return {
            "start_at": 1,
            "total_iterations": 0,
            "current_iteration": 1,  # Track current iteration separately
            "steps": [],
            "completed_steps": [],
            "total_steps_completed": 0,  # Track total across all iterations
            "current_step_index": 0,
            "status": "not_started",
            "start_time": None,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": None,
        }

    def save(self) -> None:
        """Save the current state to the state file."""
        self.state["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_state(self.state)
        self.logger.info("State saved to %s", self.state_file_path)

    def _save_state(self, state: Dict) -> None:
        """Helper method to save state to file."""
        # Create directory if it doesn't exist
        state_dir = os.path.dirname(self.state_file_path)
        if state_dir and not os.path.exists(state_dir):
            os.makedirs(state_dir, exist_ok=True)

        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def update(self, **kwargs) -> None:
        """Update the state with the provided values."""
        for key, value in kwargs.items():
            self.state[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return self.state.get(key) if key in self.state else default

    def mark_step_complete(self, step_name: str) -> None:
        """Mark a step as completed."""
        # Only add if not already in current iteration's completed steps
        if step_name not in self.state["completed_steps"]:
            self.state["completed_steps"].append(step_name)
            self.logger.info("Step marked as complete: %s", step_name)

        # Always increment total steps completed (across all iterations)
        total_completed = self.state.get("total_steps_completed", 0)
        self.state["total_steps_completed"] = total_completed + 1

        # Increment the current step index to move to the next step
        old_step_index = self.state.get("current_step_index", 0)
        self.state["current_step_index"] = old_step_index + 1

        self.logger.debug(
            "Step index incremented from %d to %d",
            old_step_index,
            self.state["current_step_index"],
        )
        self.logger.debug(
            "Total steps completed: %d", self.state["total_steps_completed"]
        )

        self.save()

    def is_step_completed(self, step_name: str) -> bool:
        """Check if a step has been completed."""
        return step_name in self.state["completed_steps"]

    def get_next_step(self) -> Optional[str]:
        """Get the next step to execute."""
        if not self.state["steps"]:
            self.logger.debug("No steps defined in state")
            return None

        current_step_index = self.state["current_step_index"]
        total_steps = len(self.state["steps"])

        self.logger.debug(
            "Current step index: %d, Total steps: %d", current_step_index, total_steps
        )

        # Check if we're at the end of all steps in the current iteration
        if current_step_index >= total_steps:
            self.logger.debug("Reached end of steps for current iteration")
            return None

        next_step = self.state["steps"][current_step_index]
        self.logger.debug("Next step to execute: %s", next_step)
        return next_step

    def increment_iteration(self) -> int:
        """Reset step tracking and move to the next iteration."""
        self.state["current_step_index"] = 0
        self.state["completed_steps"] = []
        # Increment the current iteration counter
        current_iteration = self.state.get("current_iteration", 1)
        self.state["current_iteration"] = current_iteration + 1
        self.save()
        return self.get_display_iteration()

    def get_display_iteration(self) -> int:
        """Get the display iteration number."""
        return self.state.get("current_iteration", 1)

    def is_all_iterations_complete(self) -> bool:
        """Check if all iterations have been completed."""
        # If no steps defined, consider complete
        steps = self.state.get("steps", [])
        if not steps:
            return True

        total_iterations = self.state.get("total_iterations", 0)
        total_steps_completed = self.state.get("total_steps_completed", 0)
        steps_per_iteration = len(steps)

        # Calculate how many total steps need to be completed across all iterations
        total_steps_required = total_iterations * steps_per_iteration

        # We're complete if we've completed at least the required number of steps
        return total_steps_completed >= total_steps_required


class OrcaOrchestrator:
    """
    Main orchestrator class for the ORCA model.
    Manages the execution of model steps and iterations.
    """

    def __init__(
        self,
        databank_name: str,
        config_file: str = "orca_model_config.yaml",
        state_file: str = "orca_model_state.json",
        mode: str = "local_testing",
        project_folder: Optional[str] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            databank_name: Name of the data bank (scenario)
            config_file: Name of the configuration file (used for initialization only)
            state_file: Name of the state file
            mode: Execution mode - 'local_testing' or 'cloud_production'
            project_folder: Optional override for the ADLS project folder path
        """
        self.databank_name = databank_name
        self.databank_path = os.path.abspath(databank_name)
        # Store the initialization config file name for initial setup
        self.init_config_file = config_file
        # Always use standard config file name in databank after initialization
        self.config_file = os.path.join(self.databank_path, "orca_model_config.yaml")
        self.state_file = os.path.join(self.databank_path, state_file)
        self.mode = mode
        self.project_folder_override = project_folder

        # Create data bank directory if it doesn't exist
        os.makedirs(self.databank_path, exist_ok=True)

        # Initialize logger with databank-specific log file
        log_file_path = os.path.join(self.databank_path, "orca_orchestrator.log")
        orca_logger = get_orca_logger("orchestrator", log_file_path=log_file_path)

        # Set the global logger for backward compatibility
        global logger
        logger = orca_logger

        # Log project folder override if provided
        if self.project_folder_override:
            logger.info(
                "Project folder override specified: %s", self.project_folder_override
            )

        # Initialize databank manager
        self.databank = OrcaDatabank(self.databank_path, orca_logger)

        # Initialize file sync manager for cloud operations
        self.file_sync = OrcaFileSync(orca_logger)

        # Initialize databank based on mode
        if self.mode == "local_testing":
            # For local mode, simply initialize databank in local folder
            if not os.path.exists(self.state_file):
                self._initialize_databank()
            else:
                # Load configuration for existing databank
                self.config = self._load_configuration()
        elif self.mode == "cloud_production":
            # For cloud mode, check if cloud has valid databank first
            if not os.path.exists(self.config_file):
                # No local config - create template first
                self._create_template_config()

            self.config = self._load_configuration()

            # Check cloud databank and initialize appropriately
            if not self._initialize_cloud_databank():
                logger.error("Failed to initialize cloud databank")
                raise RuntimeError("Cloud databank initialization failed")
        else:
            logger.error("Invalid mode: %s", self.mode)
            raise ValueError(f"Invalid mode: {self.mode}")

        # Initialize state
        self.state = OrcaState(self.state_file, orca_logger)

        # Validate environment
        self._validate_environment()

        # Update state with configuration if it's a new run
        if self.state.get("status") == "not_started":
            self._initialize_state_from_config()

    def _load_configuration(self) -> Dict:
        """
        Load the configuration from the YAML file.

        Returns:
            Dict: The configuration
        """
        try:
            if not os.path.exists(self.config_file):
                self._create_template_config()
                logger.info(
                    "Configuration loaded from default config, %s is missing",
                    self.config_file,
                )

            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info("Configuration loaded from %s", self.config_file)

            return config
        except yaml.YAMLError as e:
            logger.error("Error loading configuration: %s", e)
            sys.exit(1)
        except Exception as e:
            logger.error("Error loading configuration: %s", e)
            sys.exit(1)

    def _initialize_databank(self) -> None:
        """
        Initialize a new data bank by creating directory structure and copying template files.
        """
        logger.info("Initializing new data bank: %s", self.databank_name)

        # Create main data bank directory
        os.makedirs(self.databank_path, exist_ok=True)

        # Create output directory
        os.makedirs(os.path.join(self.databank_path, "outputs"), exist_ok=True)

        # Create a template configuration file if it doesn't exist
        if not os.path.exists(self.config_file):
            self._create_template_config()
            logger.info(
                "Init Databank - Configuration loaded from default config, %s is missing",
                self.config_file,
            )

        # Load configuration to get sub-component information
        self.config = self._load_configuration()

        # Copy shared input data
        self._copy_input_data()

        # Copy all sub-component template directories during initialization
        self._copy_all_sub_component_templates()

        logger.info("Data bank initialized at %s", self.databank_path)

    def _copy_all_sub_component_templates(self) -> None:
        """
        Copy all sub-component template directories during databank initialization.
        """
        if "sub_components" not in self.config:
            logger.warning("No sub-components defined in configuration")
            return

        logger.info("Copying sub-component templates...")

        for step_name, step_config in self.config["sub_components"].items():
            # Create the sub-component directory if it doesn't exist
            step_dir = os.path.join(self.databank_path, step_name)
            os.makedirs(step_dir, exist_ok=True)

            # Check if we need to copy template files
            if "source_template" in step_config:
                source_templates = step_config["source_template"]
                if not isinstance(source_templates, list):
                    source_templates = [source_templates]

                for source_template in source_templates:
                    source_path = os.path.join(
                        os.path.dirname(self.databank_path), source_template
                    )
                    if os.path.exists(source_path):
                        logger.info(
                            "Copying template from %s to %s", source_path, step_dir
                        )

                        if os.path.isdir(source_path):
                            # Copy directory
                            self.databank.copy_template_directory(
                                source_dir=source_path,
                                target_dir=step_dir,
                                overwrite=False,
                            )
                        else:
                            # Copy file
                            self.databank.copy_template_file(
                                source_file=source_path,
                                target_file=os.path.join(
                                    step_dir, os.path.basename(source_path)
                                ),
                                overwrite=False,
                            )
                    else:
                        logger.warning("Template source not found: %s", source_path)

        logger.info("Sub-component templates copied successfully")

    def _copy_input_data(self) -> None:
        """
        Copy shared input data across multiple sub-components.
        """
        if "input_data" not in self.config:
            logger.debug("No input_data section defined in configuration")
            return

        logger.info("Copying shared input data...")

        # Create input_data directory in databank
        input_data_dir = os.path.join(self.databank_path, "inputs")
        os.makedirs(input_data_dir, exist_ok=True)

        for data_category, sources in self.config["input_data"].items():
            # Create category subdirectory
            category_dir = os.path.join(input_data_dir, data_category)
            os.makedirs(category_dir, exist_ok=True)

            # Process dict format and unfold to list
            if isinstance(sources, dict):
                sources = sources["sources"]

            for source_path in sources:
                if not isinstance(source_path, str):
                    logger.warning("Invalid source entry format: %s", source_path)
                    continue

                # Resolve source path relative to databank parent directory
                full_source_path = os.path.join(
                    os.path.dirname(self.databank_path), source_path
                )

                if os.path.exists(full_source_path):
                    logger.info(
                        "Copying input data from %s to %s",
                        full_source_path,
                        category_dir,
                    )

                    if os.path.isdir(full_source_path):
                        # Copy directory
                        self.databank.copy_template_directory(
                            source_dir=full_source_path,
                            target_dir=category_dir,
                            overwrite=False,
                        )
                    else:
                        # Copy file
                        self.databank.copy_template_file(
                            source_file=full_source_path,
                            target_file=os.path.join(
                                category_dir, os.path.basename(full_source_path)
                            ),
                            overwrite=False,
                        )
                else:
                    # Handle glob patterns
                    import glob

                    matching_files = glob.glob(full_source_path)
                    if matching_files:
                        for file_path in matching_files:
                            logger.info(
                                "Copying input data from %s to %s",
                                file_path,
                                category_dir,
                            )
                            self.databank.copy_template_file(
                                source_file=file_path,
                                target_file=os.path.join(
                                    category_dir, os.path.basename(file_path)
                                ),
                                overwrite=False,
                            )
                    else:
                        logger.warning(
                            "Input data source not found: %s", full_source_path
                        )

        logger.info("Shared input data copied successfully")

    def _create_template_config(self) -> None:
        """
        Create a template configuration file by copying from the default template.
        If an initialization config file was specified and exists, use that instead.
        """
        # Check if a custom initialization config file was specified and exists
        if self.init_config_file != "orca_model_config.yaml":
            # Try to find the initialization config file in various locations
            possible_paths = [
                # Absolute path
                self.init_config_file,
                # Relative to current working directory
                os.path.abspath(self.init_config_file),
                # Relative to orchestrator script directory
                os.path.join(os.path.dirname(__file__), self.init_config_file),
                # Relative to databank parent directory
                os.path.join(
                    os.path.dirname(self.databank_path), self.init_config_file
                ),
            ]

            init_config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    init_config_path = path
                    break

            if init_config_path:
                logger.info("Using initialization config file: %s", init_config_path)
                try:
                    self.databank.copy_template_file(
                        source_file=init_config_path,
                        target_file=self.config_file,
                        overwrite=False,
                    )
                    return
                except Exception as e:
                    logger.warning(
                        "Failed to copy initialization config file: %s. Falling back to default.",
                        e,
                    )

        # Fall back to default config template - try multiple locations
        default_config_locations = [
            # In the same directory as this script (tlpytools package)
            os.path.join(os.path.dirname(__file__), "orca_model_config_default.yaml"),
            # In the current working directory
            os.path.join(os.getcwd(), "orca_model_config_default.yaml"),
            # In the orca folder of the working directory
            os.path.join(os.getcwd(), "orca", "orca_model_config_default.yaml"),
            # In the parent directory of databank
            os.path.join(
                os.path.dirname(self.databank_path), "orca_model_config_default.yaml"
            ),
        ]

        default_config_path = None
        for path in default_config_locations:
            if os.path.exists(path):
                default_config_path = path
                break

        if not default_config_path:
            logger.error(
                "Default configuration template not found in any of these locations: %s",
                default_config_locations,
            )
            raise FileNotFoundError(
                f"Default configuration template not found. Searched: {default_config_locations}"
            )

        # Copy the default config file using our utility function
        logger.info("Copying default config from %s", default_config_path)
        try:
            self.databank.copy_template_file(
                source_file=default_config_path,
                target_file=self.config_file,
                overwrite=False,
            )
        except Exception as e:
            logger.error("Error copying template configuration: %s", e)
            raise

    def _initialize_state_from_config(self) -> None:
        """
        Initialize the state from the configuration file.
        """
        # Set up the steps from the configuration
        steps = self.config.get("model_steps", [])
        iterations_config = self.config.get("iterations", {})
        total_iterations = iterations_config.get("total", 1)
        start_at = iterations_config.get("start_at", 1)

        # Update the state
        self.state.update(
            steps=steps,
            total_iterations=total_iterations,
            start_at=start_at,
            current_iteration=start_at,  # Initialize current iteration to start_at
            current_step_index=0,
            completed_steps=[],
            status="initialized",
            start_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        logger.info("State initialized from configuration")

    def _validate_environment(self) -> None:
        """
        Validate that all required environments for sub-components are available.
        """
        if "sub_components" not in self.config:
            logger.warning("No sub-components defined in configuration")
            return

        # Validate performance monitoring configuration
        perf_config = self.config.get("performance_monitoring", {})
        if perf_config.get("enabled", False):
            if not PSUTIL_AVAILABLE and (
                perf_config.get("track_memory", True)
                or perf_config.get("track_cpu", True)
            ):
                logger.warning(
                    "Performance monitoring enabled but psutil not available. "
                    "Memory/CPU tracking will be disabled. Install with: pip install psutil"
                )
            else:
                logger.info("Performance monitoring enabled with psutil support")
                poll_interval = perf_config.get("poll_interval", 1.0)
                logger.info(
                    "Performance monitoring poll interval: %.1f seconds", poll_interval
                )

                if perf_config.get("track_memory", True):
                    logger.info("Memory tracking: enabled")
                if perf_config.get("track_cpu", True):
                    logger.info("CPU tracking: enabled")
                if perf_config.get("export_detailed_logs", True):
                    logger.info("Detailed performance logs: enabled")
        else:
            logger.info("Performance monitoring: disabled")

        # Check each sub-component's environment
        for step_name, step_config in self.config["sub_components"].items():
            if "environment" in step_config:
                env_config = step_config["environment"]
                env_var = env_config.get("env_var")
                default_env = env_config.get("default")

                # Check if environment variable is set
                if env_var and env_var in os.environ:
                    logger.info(
                        "Environment for %s: %s=%s",
                        step_name,
                        env_var,
                        os.environ[env_var],
                    )
                else:
                    if default_env:
                        logger.info(
                            "Using default environment for %s: %s",
                            step_name,
                            default_env,
                        )
                    else:
                        logger.warning("No environment configured for %s", step_name)

    def _execute_step(self, step_name: str) -> bool:
        """
        Execute a single sub-component step.

        Args:
            step_name: The name of the step to execute

        Returns:
            bool: True if the step was executed successfully, False otherwise
        """
        logger.info("Executing step: %s", step_name)

        # Get the step configuration
        step_config = self.config["sub_components"].get(step_name)
        if not step_config:
            logger.error("Step %s not found in configuration", step_name)
            return False

        # Get the current iteration information
        display_iteration = self.state.get_display_iteration()
        total_iterations = self.state.get("total_iterations")
        start_at = self.state.get("start_at", 1)

        # Determine if this is the first or last iteration
        is_first_iteration = display_iteration == start_at
        is_last_iteration = display_iteration == (start_at + total_iterations - 1)

        # Execute the commands for this step
        success = True
        if "commands" in step_config:
            for cmd_config in step_config["commands"]:
                # Check if the command should run in this iteration
                iterations = cmd_config.get("iterations", "all")
                should_run = False

                if iterations == "all":
                    should_run = True
                elif iterations == "first":
                    should_run = is_first_iteration
                elif iterations == "last":
                    should_run = is_last_iteration
                elif isinstance(iterations, list) and display_iteration in iterations:
                    should_run = True

                if should_run:
                    # Get the environment for this command
                    env_config = step_config.get("environment", {})
                    env_var = env_config.get("env_var")
                    default_env = env_config.get("default")

                    # Determine the Python executable to use
                    python_cmd = (
                        os.environ.get(env_var, default_env) if env_var else default_env
                    )
                    if not python_cmd:
                        python_cmd = "python"

                    # Format the command with the Python environment
                    command = cmd_config["command"].format(python=python_cmd)

                    # Execute the command
                    cmd_description = cmd_config.get("description", "Running command")
                    logger.info("%s: %s", cmd_description, command)

                    # Change to the step directory
                    original_dir = os.getcwd()
                    step_directory = os.path.join(self.databank_path, step_name)

                    # Ensure step directory exists
                    if not os.path.exists(step_directory):
                        logger.warning(
                            "Step directory does not exist: %s. Creating it.",
                            step_directory,
                        )
                        os.makedirs(step_directory, exist_ok=True)

                    os.chdir(step_directory)

                    # Ensure Python path includes necessary directories
                    ensure_python_path()

                    # Create a platform-specific command to set the PYTHONPATH
                    if os.name == "nt":  # Windows
                        # On Windows, use SET command
                        pythonpath_cmd = (
                            f"set PYTHONPATH={ORCA_DIR};{os.getcwd()};%PYTHONPATH% && "
                        )
                    else:  # Unix/Linux/Mac
                        # On Unix-like systems, use export command
                        pythonpath_cmd = f"export PYTHONPATH={ORCA_DIR}:{os.getcwd()}:$PYTHONPATH && "

                    # Modify the command to ensure environment can be found
                    modified_command = f"{pythonpath_cmd}{command}"

                    # Initialize performance monitoring if enabled
                    perf_config = self.config.get("performance_monitoring", {})
                    perf_enabled = perf_config.get("enabled", False)
                    perf_monitor = None

                    if perf_enabled:
                        poll_interval = perf_config.get("poll_interval", 1.0)
                        track_memory = perf_config.get("track_memory", True)
                        track_cpu = perf_config.get("track_cpu", True)

                        perf_monitor = OrcaPerformanceMonitor(
                            poll_interval=poll_interval,
                            track_memory=track_memory,
                            track_cpu=track_cpu,
                        )
                        perf_monitor.start_monitoring()
                        logger.info(
                            "Performance monitoring started for command: %s", command
                        )

                    # Execute the modified command
                    logger.info(
                        "Executing with environment setup: %s", modified_command
                    )
                    result = os.system(modified_command)

                    # Stop performance monitoring and collect results
                    performance_summary = None
                    if perf_monitor:
                        performance_summary = perf_monitor.stop_monitoring()
                        logger.info(
                            "Performance monitoring completed for command: %s", command
                        )

                        # Log performance summary
                        if performance_summary.get("monitoring_enabled", False):
                            logger.info(
                                "Performance Summary - Runtime: %.2fs, Samples: %d",
                                performance_summary.get("runtime_seconds", 0),
                                performance_summary.get("samples_collected", 0),
                            )

                            if "memory_used_max_gb" in performance_summary:
                                logger.info(
                                    "Memory Usage - Min: %.2fGB, Max: %.2fGB, Avg: %.2fGB",
                                    performance_summary.get("memory_used_min_gb", 0),
                                    performance_summary.get("memory_used_max_gb", 0),
                                    performance_summary.get("memory_used_avg_gb", 0),
                                )

                            if "cpu_usage_avg_percent" in performance_summary:
                                logger.info(
                                    "CPU Usage - Min: %.1f%%, Max: %.1f%%, Avg: %.1f%%",
                                    performance_summary.get("cpu_usage_min_percent", 0),
                                    performance_summary.get("cpu_usage_max_percent", 0),
                                    performance_summary.get("cpu_usage_avg_percent", 0),
                                )

                        # Export detailed performance data if enabled
                        export_detailed = perf_config.get("export_detailed_logs", True)
                        if export_detailed:
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            perf_filename = f"performance_{step_name}_iter{display_iteration}_cmd{len([c for c in step_config.get('commands', []) if c == cmd_config]) + 1}_{timestamp}.csv"
                            perf_filepath = os.path.join(
                                self.databank_path, "outputs", perf_filename
                            )

                            # Ensure outputs directory exists
                            os.makedirs(os.path.dirname(perf_filepath), exist_ok=True)

                            if perf_monitor.export_detailed_data(perf_filepath):
                                logger.info(
                                    "Detailed performance data exported to: %s",
                                    perf_filepath,
                                )
                            else:
                                logger.warning(
                                    "Failed to export detailed performance data"
                                )

                        # Add performance summary to a consolidated log
                        self._log_performance_summary(
                            step_name,
                            display_iteration,
                            cmd_description,
                            command,
                            performance_summary,
                        )

                    # Change back to original directory
                    os.chdir(original_dir)

                    if result != 0:
                        error_msg = f"Command failed with exit code {result}: {command}"
                        logger.error(error_msg)

                        # Check if error dump creation is enabled
                        error_config = self.config.get("error_handling", {})
                        create_dump = error_config.get("create_error_dump", True)
                        include_full_databank = error_config.get(
                            "include_full_databank_in_dump", False
                        )

                        if create_dump:
                            # Create error dump when command fails
                            logger.info(
                                "Creating error dump for failed step: %s", step_name
                            )
                            dump_success = self.databank.create_error_dump(
                                step_name=step_name,
                                iteration=display_iteration,
                                error_message=error_msg,
                                include_all_databank=include_full_databank,
                                export_log=True,
                            )

                            if dump_success:
                                logger.info(
                                    "Error dump created successfully for step: %s",
                                    step_name,
                                )

                                # Upload error dump to cloud if in cloud_production mode
                                if (
                                    self.mode == "cloud_production"
                                    and error_config.get(
                                        "upload_error_dumps_to_cloud", True
                                    )
                                ):
                                    logger.info("Uploading error dump to cloud storage")
                                    try:
                                        self._upload_error_dumps_to_cloud()
                                    except Exception as e:
                                        logger.warning(
                                            "Failed to upload error dump to cloud: %s",
                                            e,
                                        )
                            else:
                                logger.warning(
                                    "Failed to create error dump for step: %s",
                                    step_name,
                                )
                        else:
                            logger.info(
                                "Error dump creation is disabled in configuration"
                            )

                        success = False
                        break
                    else:
                        logger.info("Command completed successfully: %s", command)

        # Archive outputs and clean up if needed
        if success:
            # Clean up files first, then archive if successful
            self._cleanup_files(step_name)
            self._archive_outputs(step_name)
        else:
            # If there was an error, archive without cleaning up
            logger.info(
                "Error encountered in step: %s - Archiving outputs without cleanup",
                step_name,
            )
            self._archive_outputs(step_name)

        return success

    def _archive_outputs(self, step_name: str) -> None:
        """
        Archive the outputs of a step using the output_archives structure.

        Args:
            step_name: The name of the step
        """
        step_config = self.config["sub_components"].get(step_name)

        if not step_config or "output_archives" not in step_config:
            return

        output_archives = step_config["output_archives"]
        if not output_archives:
            return

        logger.info("Archiving outputs for step: %s", step_name)
        step_dir = os.path.join(self.databank_path, step_name)
        display_iteration = self.state.get_display_iteration()

        for archive_config in output_archives:
            if isinstance(archive_config, dict) and "archive_name" in archive_config:
                archive_name = archive_config["archive_name"]
                patterns = archive_config.get("patterns", [])

                if not patterns:
                    logger.warning(
                        "No patterns specified for archive: %s", archive_name
                    )
                    continue

                # Create archive with new naming convention
                zip_filename = f"{step_name}_{archive_name}_iter{display_iteration}.zip"
                archive_path = os.path.join(self.databank_path, "outputs", zip_filename)

                logger.info("Creating archive: %s", zip_filename)

                # Use the zip_directory utility function to create the archive
                self.databank.zip_directory(
                    dir_path=step_dir,
                    zip_path=archive_path,
                    # Skip everything except the specified patterns
                    skip_patterns=["*"] + [f"!{pattern}" for pattern in patterns],
                    include_empty_dirs=False,
                )
            else:
                logger.warning(
                    "Invalid archive configuration for step %s: %s",
                    step_name,
                    archive_config,
                )

    def _cleanup_files(self, step_name: str) -> None:
        """
        Clean up temporary files after a step is completed.

        Args:
            step_name: The name of the step
        """
        step_config = self.config["sub_components"].get(step_name)
        if not step_config or "cleanup_patterns" not in step_config:
            return

        cleanup_patterns = step_config["cleanup_patterns"]
        if not cleanup_patterns:
            return

        logger.info("Cleaning up temporary files for step: %s", step_name)
        step_dir = os.path.join(self.databank_path, step_name)

        # Use the cleanup_files_by_patterns utility function
        deleted_files = self.databank.cleanup_files_by_patterns(
            base_dir=step_dir, patterns=cleanup_patterns
        )

        logger.info("Cleaned up %d files for step: %s", len(deleted_files), step_name)

    def _log_performance_summary(
        self,
        step_name: str,
        iteration: int,
        cmd_description: str,
        command: str,
        performance_summary: Dict[str, Any],
    ) -> None:
        """
        Log performance summary to a consolidated CSV file.

        Args:
            step_name: Name of the model step
            iteration: Current iteration number
            cmd_description: Description of the command
            command: The actual command executed
            performance_summary: Dictionary containing performance metrics
        """
        if not performance_summary or not performance_summary.get(
            "monitoring_enabled", False
        ):
            return

        try:
            # Create performance log entry
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "step_name": step_name,
                "iteration": iteration,
                "command_description": cmd_description,
                "command": (
                    command[:100] + "..." if len(command) > 100 else command
                ),  # Truncate long commands
                "runtime_seconds": performance_summary.get("runtime_seconds", 0),
                "samples_collected": performance_summary.get("samples_collected", 0),
                "poll_interval": performance_summary.get("poll_interval", 0),
            }

            # Add memory metrics if available
            if "memory_used_max_gb" in performance_summary:
                log_entry.update(
                    {
                        "memory_min_gb": performance_summary.get(
                            "memory_used_min_gb", 0
                        ),
                        "memory_max_gb": performance_summary.get(
                            "memory_used_max_gb", 0
                        ),
                        "memory_avg_gb": performance_summary.get(
                            "memory_used_avg_gb", 0
                        ),
                    }
                )

            # Add process memory metrics if available
            if "process_memory_max_gb" in performance_summary:
                log_entry.update(
                    {
                        "process_memory_min_gb": performance_summary.get(
                            "process_memory_min_gb", 0
                        ),
                        "process_memory_max_gb": performance_summary.get(
                            "process_memory_max_gb", 0
                        ),
                        "process_memory_avg_gb": performance_summary.get(
                            "process_memory_avg_gb", 0
                        ),
                    }
                )

            # Add CPU metrics if available
            if "cpu_usage_avg_percent" in performance_summary:
                log_entry.update(
                    {
                        "cpu_min_percent": performance_summary.get(
                            "cpu_usage_min_percent", 0
                        ),
                        "cpu_max_percent": performance_summary.get(
                            "cpu_usage_max_percent", 0
                        ),
                        "cpu_avg_percent": performance_summary.get(
                            "cpu_usage_avg_percent", 0
                        ),
                    }
                )

            # Determine log file path
            log_filename = "performance_summary.csv"
            log_filepath = os.path.join(self.databank_path, "outputs", log_filename)

            # Ensure outputs directory exists
            os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(log_filepath)

            # Write to CSV file
            with open(log_filepath, "a", newline="", encoding="utf-8") as csvfile:
                if log_entry:
                    fieldnames = list(log_entry.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()

                    writer.writerow(log_entry)

            logger.info("Performance summary logged to: %s", log_filepath)

        except Exception as e:
            logger.warning("Failed to log performance summary: %s", e)

    def _get_adls_config(self):
        """
        Get ADLS configuration from config file.

        Returns:
            tuple: (adls_url, adls_container, adls_folder)
        """
        cloud_config = self.config["operational_mode"].get("cloud", {})

        adls_url = cloud_config.get(
            "adls_url", "https://tlebtsprd01dail06lk01.dfs.core.windows.net"
        )
        adls_container = cloud_config.get("adls_container", "raw")

        # Use project_folder override if provided, otherwise use config value
        if self.project_folder_override:
            adls_folder = self.project_folder_override
            logger.info("Using project folder override: %s", adls_folder)
        else:
            adls_folder = cloud_config.get("adls_folder", "orca_cloud_model_runs")

        return adls_url, adls_container, adls_folder

    def get_adls_config(self):
        """
        Get ADLS configuration from config file (public method).

        Returns:
            tuple: (adls_url, adls_container, adls_folder)
        """
        return self._get_adls_config()

    def _sync_with_cloud(self, direction: str) -> bool:
        """
        Sync data with the cloud storage according to requirements.

        Upload behavior:
        - Sub-component folders are zipped and uploaded individually
        - Config files are uploaded individually with conflict handling
        - Files in outputs/ are uploaded individually (only new files)

        Download behavior:
        - If local databank is empty: download and extract everything
        - If local databank exists: download only outputs/ files (only new files)
        - Files in .cloud_sync_conflict/ are always skipped

        Args:
            direction: 'download' or 'upload'

        Returns:
            bool: True if successful, False otherwise
        """
        if "operational_mode" not in self.config:
            logger.error("No operational_mode configuration found")
            return False

        adls_url, adls_container, adls_folder = self._get_adls_config()

        if direction == "download":
            return self._download_from_cloud(adls_url, adls_container, adls_folder)
        elif direction == "upload":
            return self._upload_to_cloud(adls_url, adls_container, adls_folder)
        else:
            logger.error("Invalid sync direction: %s", direction)
            return False

    def _download_from_cloud(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download files from cloud according to requirements.

        Logic:
        - If local databank is empty: download everything (zip archives + outputs)
        - If local databank exists: download only new files from outputs/
        - Skip files in .cloud_sync_conflict/
        - Never overwrite local files

        Args:
            adls_url: ADLS account URL
            adls_container: ADLS container name
            adls_folder: ADLS folder path

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting cloud download synchronization")

        try:
            # Determine if local databank is empty
            is_empty_databank = self._is_local_databank_empty()

            if is_empty_databank:
                logger.info(
                    "Local databank is empty - downloading all archives and files"
                )
                return self._download_all_from_cloud(
                    adls_url, adls_container, adls_folder
                )
            else:
                logger.info(
                    "Local databank exists - downloading only new outputs files"
                )
                return self._download_outputs_only(
                    adls_url, adls_container, adls_folder
                )

        except Exception as e:
            logger.error("Error during cloud download: %s", str(e))
            return False

    def _is_local_databank_empty(self) -> bool:
        """
        Check if local databank is considered empty.

        A databank is empty if it lacks key component directories or config files.
        """
        # Check for config files
        config_files = ["orca_model_state.json"]
        for config_file in config_files:
            if os.path.exists(os.path.join(self.databank_path, config_file)):
                return False

        # Check for sub-component directories
        if "sub_components" in self.config:
            for component_name in self.config["sub_components"].keys():
                component_path = os.path.join(self.databank_path, component_name)
                if os.path.exists(component_path) and os.path.isdir(component_path):
                    # Check if directory has actual content (not just empty)
                    try:
                        if any(os.scandir(component_path)):
                            return False
                    except OSError:
                        pass

        return True

    def _download_all_from_cloud(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download all files from cloud when local databank is empty.
        """
        logger.info("Downloading all files from cloud databank")

        try:
            # 1. Download and extract component zip files
            success = self._download_and_extract_components(
                adls_url, adls_container, adls_folder
            )
            if not success:
                logger.error("Failed to download component archives")

            # 2. Download config files
            success = self._download_config_files(adls_url, adls_container, adls_folder)
            if not success:
                logger.warning(
                    "Failed to download some config files, will use default (continuing)"
                )

            # 3. Download outputs files
            success = self._download_outputs_files(
                adls_url, adls_container, adls_folder
            )
            if not success:
                logger.warning(
                    "Failed to download outputs files, runs beyond iteration 1 will likely fail (continuing)"
                )

            logger.info("Successfully downloaded all files from cloud")
            return True

        except Exception as e:
            logger.error("Error downloading all files from cloud: %s", str(e))
            return False

    def _download_outputs_only(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download only new outputs files when local databank exists.
        """
        logger.info("Downloading only new outputs files from cloud")

        try:
            success = self._download_outputs_files(
                adls_url, adls_container, adls_folder
            )
            if success:
                logger.info("Successfully downloaded new outputs files")
            else:
                logger.warning("Failed to download outputs files")
            return success

        except Exception as e:
            logger.error("Error downloading outputs files: %s", str(e))
            return False

    def _download_and_extract_components(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download and extract component zip files.
        Always downloads from main folder (initialization versions), not from .cloud_model_archive.
        """
        logger.info("Downloading component zip archives from cloud")

        try:
            # List component zip files (exclude .cloud_model_archive, .error_dump, .cloud_sync_conflict and outputs)
            pattern = f"{self.databank_name}/*.zip"
            cloud_files = self.file_sync.download_from_adls_by_pattern(
                adls_pattern=pattern,
                local_path="",
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                list_only=True,
                export_log=False,
                exclude_log_files=True,
                databank_name=self.databank_name,
            )

            if not cloud_files:
                logger.info("No component zip files found in cloud")
                return True

            # Filter out outputs, config archives, .cloud_model_archive files, .error_dump files, and conflict files
            component_files = []
            for file_path in cloud_files:
                file_name = os.path.basename(file_path)

                # Skip conflict files
                if ".cloud_sync_conflict" in file_path:
                    continue

                # Skip .cloud_model_archive files
                if ".cloud_model_archive" in file_path:
                    continue

                # Skip .error_dump files
                if ".error_dump" in file_path:
                    continue

                # Skip outputs and config archives - we handle those separately
                if file_name.startswith("outputs_") or file_name.startswith("config_"):
                    continue

                # Skip backup files
                if "_bak." in file_name:
                    continue

                # Skip iteration-specific files (want only the main initialization versions)
                if "_iter" in file_name:
                    continue

                component_files.append(file_path)

            if not component_files:
                logger.info("No component archives found (after filtering)")
                return True

            # Create temp directory for downloads
            temp_dir = os.path.join(self.databank_path, ".temp_download")
            os.makedirs(temp_dir, exist_ok=True)

            try:
                # Download each component archive
                for file_path in component_files:
                    file_name = os.path.basename(file_path)
                    logger.info("Downloading component archive: %s", file_name)

                    local_file = self.file_sync.download_from_adls(
                        adls_file=file_path,
                        local_path=temp_dir,
                        adls_url=adls_url,
                        adls_container=adls_container,
                        adls_folder=adls_folder,
                        export_log=False,
                    )

                    if local_file:
                        # Extract to component directory
                        # Get component name from filename (zip archive file name with extension removed)
                        component_name = ".".join(file_name.split(".")[0:-1])
                        component_dir = os.path.join(self.databank_path, component_name)

                        # Remove existing component directory if it exists
                        if os.path.exists(component_dir):
                            shutil.rmtree(component_dir)

                        os.makedirs(component_dir, exist_ok=True)

                        # Extract the archive
                        success = self.databank.unpack_zip_file(
                            zip_file_path=local_file,
                            output_dir=component_dir,
                            export_log=False,
                        )

                        if success:
                            logger.info(
                                "Successfully extracted %s to %s",
                                file_name,
                                component_dir,
                            )
                        else:
                            logger.error("Failed to extract %s", file_name)
                    else:
                        logger.error("Failed to download %s", file_name)

                return True

            finally:
                # Clean up temp directory
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

        except Exception as e:
            logger.error("Error downloading component archives: %s", str(e))
            return False

    def _download_config_files(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download config files individually.
        """
        logger.info("Downloading config files from cloud")

        config_files = [
            "orca_model_config.yaml",
            "orca_model_state.json",
            "orca_orchestrator.log",
        ]

        success_count = 0
        for config_file in config_files:
            cloud_path = f"{self.databank_name}/{config_file}"
            local_path = os.path.join(self.databank_path, config_file)

            # If local file exist, overwrite all except log files
            if os.path.exists(local_path):
                if config_file == "orca_orchestrator.log":
                    logger.info("Local log file exists, skipping: %s", config_file)
                    continue
                logger.info("Local config file exists, overwriting: %s", config_file)
                os.remove(local_path)

            logger.info("Downloading config file: %s", config_file)

            downloaded_file = self.file_sync.download_from_adls(
                adls_file=cloud_path,
                local_path=self.databank_path,
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                export_log=False,
            )

            if downloaded_file:
                success_count += 1
                logger.info("Successfully downloaded %s", config_file)
            else:
                logger.warning(
                    "Failed to download %s (may not exist in cloud)", config_file
                )

        return success_count > 0

    def _download_outputs_files(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Download files from outputs/ directory (only new files).
        """
        logger.info("Downloading outputs files from cloud")

        try:
            # Create local outputs directory
            outputs_dir = os.path.join(self.databank_path, "outputs")
            os.makedirs(outputs_dir, exist_ok=True)

            # List outputs files in cloud
            pattern = f"{self.databank_name}/outputs/**"
            cloud_files = self.file_sync.download_from_adls_by_pattern(
                adls_pattern=pattern,
                local_path="",
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                list_only=True,
                export_log=False,
                exclude_log_files=True,
                databank_name=self.databank_name,
            )

            if not cloud_files:
                logger.info("No outputs files found in cloud")
                return True

            # Download only new files (that don't exist locally)
            downloaded_count = 0
            for cloud_file in cloud_files:
                # Skip conflict files
                if ".cloud_sync_conflict" in cloud_file:
                    continue

                # Skip .cloud_model_archive files
                if ".cloud_model_archive" in cloud_file:
                    continue

                # Skip .error_dump files
                if ".error_dump" in cloud_file:
                    continue

                file_name = os.path.basename(cloud_file)
                local_file_path = os.path.join(outputs_dir, file_name)

                # Skip if file already exists locally
                if os.path.exists(local_file_path):
                    logger.debug(
                        "Outputs file already exists locally, skipping: %s", file_name
                    )
                    continue

                logger.info("Downloading new outputs file: %s", file_name)

                downloaded_file = self.file_sync.download_from_adls(
                    adls_file=cloud_file,
                    local_path=outputs_dir,
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_folder=adls_folder,
                    export_log=False,
                )

                if downloaded_file:
                    downloaded_count += 1
                    logger.info("Successfully downloaded outputs file: %s", file_name)
                else:
                    logger.warning("Failed to download outputs file: %s", file_name)

            logger.info("Downloaded %d new outputs files", downloaded_count)
            return True

        except Exception as e:
            logger.error("Error downloading outputs files: %s", str(e))
            return False

    def _upload_to_cloud(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Upload files to cloud according to requirements.

        Logic:
        - Sub-component folders are zipped and uploaded
        - Config files are uploaded individually with conflict handling
        - Files in outputs/ are uploaded individually (only new files)
        - By default, upload all folders - sub component model folders, outputs, and config files
        - Check UPLOAD_OUTPUTS_ONLY environment variable, if True, upload only outputs and config files
        - Check model completion status, if completed, upload only config files

        Args:
            adls_url: ADLS account URL
            adls_container: ADLS container name
            adls_folder: ADLS folder path

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting cloud upload synchronization")

        try:
            success = True

            # Check if UPLOAD_OUTPUTS_ONLY environment variable is set
            upload_outputs_only = os.environ.get("UPLOAD_OUTPUTS_ONLY", "0") == "1"
            # On completion, upload only config, state and log files
            upload_config_only = (
                True if self.state.get("status") == "completed" else False
            )

            if upload_outputs_only:
                logger.info(
                    "UPLOAD_OUTPUTS_ONLY=1 detected - skipping sub component folders"
                )
            elif upload_config_only:
                logger.info(
                    "State status completion detected - skipping sub component folders"
                )
            else:
                # 1. Create and upload sub-component zip files
                if not self._upload_component_zips(
                    adls_url, adls_container, adls_folder
                ):
                    logger.error("Failed to upload component zip files")
                    success = False

            if upload_config_only:
                logger.info(
                    "State status completion detected - skipping uploading output files"
                )
            else:
                # 2. Upload new outputs files only
                if not self._upload_outputs_files(
                    adls_url, adls_container, adls_folder
                ):
                    logger.warning("Failed to upload outputs files")
                    success = False

            # 3. Upload config files with conflict handling
            if not self._upload_config_files(adls_url, adls_container, adls_folder):
                logger.warning("Failed to upload some config files")
                success = False

            if success:
                logger.info("Successfully uploaded all files to cloud")
            else:
                logger.warning("Upload completed with some errors")

            return success

        except Exception as e:
            logger.error("Error during cloud upload: %s", str(e))
            return False

    def _upload_component_zips(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Create zip files for sub-components and upload them.

        Upload behavior:
        - During databank initialization: upload to main folder as {component}.zip
        - After each step: upload to .cloud_model_archive/{component}_iter{iteration}.zip
        """
        logger.info("Creating and uploading component zip files")

        try:
            if "sub_components" not in self.config:
                logger.info("No sub-components defined, skipping component zips")
                return True

            # Create temp directory for zip files
            temp_dir = os.path.join(self.databank_path, ".temp_upload")
            os.makedirs(temp_dir, exist_ok=True)

            try:
                upload_success = True

                # Determine if this is databank initialization or step completion
                current_iteration = self.state.get_display_iteration()
                current_step_index = self.state.get("current_step_index", 0)
                step_name = self.state.get("steps")[current_step_index - 1]
                is_databank_init = current_iteration == 1 and current_step_index == 0

                for component_name in self.config["sub_components"].keys():
                    component_dir = os.path.join(self.databank_path, component_name)

                    if not os.path.exists(component_dir) or not os.path.isdir(
                        component_dir
                    ):
                        logger.info(
                            "Component directory not found, skipping: %s",
                            component_name,
                        )
                        continue

                    # Create zip file name based on context
                    if is_databank_init:
                        # During initialization: upload to main folder
                        zip_name = f"{component_name}.zip"
                        cloud_path = f"{self.databank_name}/{zip_name}"
                        logger.info(
                            "Creating zip for component initialization: %s",
                            component_name,
                        )
                    else:
                        # After step completion: upload to .cloud_model_archive for component matching step_name
                        zip_name = f"{component_name}_iter{current_iteration}.zip"
                        cloud_path = (
                            f"{self.databank_name}/.cloud_model_archive/{zip_name}"
                        )
                        logger.info(
                            "Creating zip for step completion: %s (iteration %d)",
                            component_name,
                            current_iteration,
                        )

                    zip_path = os.path.join(temp_dir, zip_name)
                    if (step_name == component_name) or is_databank_init:
                        # Only upload if step_name matches or during initialization
                        logger.info("Creating zip for %s", component_name)

                        # Create zip archive
                        success = self.databank.zip_directory(
                            dir_path=component_dir,
                            zip_path=zip_path,
                            skip_patterns=[
                                ".temp_*/**",
                            ],
                        )

                        if not success:
                            logger.error("Failed to create zip for %s", component_name)
                            upload_success = False
                            continue

                        # Upload zip using enhanced method with conflict handling
                        logger.info(
                            "Uploading component zip: %s to %s", zip_name, cloud_path
                        )
                        success = self._upload_file_with_conflict_handling(
                            local_file_path=zip_path,
                            cloud_file_path=cloud_path,
                            adls_url=adls_url,
                            adls_container=adls_container,
                            adls_folder=adls_folder,
                        )

                        if success:
                            logger.info(
                                "Successfully uploaded component zip: %s", zip_name
                            )
                        else:
                            logger.error("Failed to upload component zip: %s", zip_name)
                            upload_success = False

                    else:
                        logger.info(
                            "Skipping zip creation for %s (not matching step %s)",
                            component_name,
                            step_name,
                        )

                return upload_success

            finally:
                # Clean up temp directory
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

        except Exception as e:
            logger.error("Error creating/uploading component zips: %s", str(e))
            return False

    def _upload_config_files(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Upload config files individually with conflict handling.
        Config files refer to config, state and log files
        """
        logger.info("Uploading config files to cloud")

        config_files = [
            "orca_model_config.yaml",
            "orca_model_state.json",
            "orca_orchestrator.log",
        ]

        success_count = 0
        for config_file in config_files:
            local_path = os.path.join(self.databank_path, config_file)

            if not os.path.exists(local_path):
                logger.debug("Config file not found locally, skipping: %s", config_file)
                continue

            cloud_path = f"{self.databank_name}/{config_file}"

            logger.info("Uploading config file: %s", config_file)

            success = self._upload_file_with_conflict_handling(
                local_file_path=local_path,
                cloud_file_path=cloud_path,
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
            )

            if success:
                success_count += 1
                logger.info("Successfully uploaded config file: %s", config_file)
            else:
                logger.warning("Failed to upload config file: %s", config_file)

        return success_count > 0

    def _upload_outputs_files(
        self, adls_url: str, adls_container: str, adls_folder: str
    ) -> bool:
        """
        Upload files from outputs/ directory (only new files that don't exist in cloud).
        """
        logger.info("Uploading outputs files to cloud")

        try:
            outputs_dir = os.path.join(self.databank_path, "outputs")

            if not os.path.exists(outputs_dir) or not os.path.isdir(outputs_dir):
                logger.info("No outputs directory found, skipping outputs upload")
                return True

            # Get list of cloud outputs files to check for existing files
            pattern = f"{self.databank_name}/outputs/**"
            cloud_files = self.file_sync.download_from_adls_by_pattern(
                adls_pattern=pattern,
                local_path="",
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                list_only=True,
                export_log=False,
                exclude_log_files=True,
                databank_name=self.databank_name,
            )

            # Create set of existing cloud file names for quick lookup
            cloud_file_names = set()
            if cloud_files:
                for cloud_file in cloud_files:
                    # Skip conflict files
                    if ".cloud_sync_conflict" not in cloud_file:
                        cloud_file_names.add(os.path.basename(cloud_file))

            # Upload local files that don't exist in cloud
            uploaded_count = 0
            for root, dirs, files in os.walk(outputs_dir):
                for file_name in files:
                    local_file_path = os.path.join(root, file_name)

                    # Skip if file already exists in cloud
                    if file_name in cloud_file_names:
                        logger.debug(
                            "Outputs file already exists in cloud, skipping: %s",
                            file_name,
                        )
                        continue

                    # Create relative path for cloud upload
                    rel_path = os.path.relpath(local_file_path, self.databank_path)
                    cloud_path = f"{self.databank_name}/{rel_path}".replace("\\", "/")

                    logger.info("Uploading new outputs file: %s", file_name)

                    # Upload without conflict handling for outputs (they never conflict)
                    success = self.file_sync.upload_to_adls(
                        local_file_path=local_file_path,
                        adls_file=cloud_path,
                        adls_url=adls_url,
                        adls_container=adls_container,
                        adls_folder=adls_folder,
                        export_log=False,
                    )

                    if success:
                        uploaded_count += 1
                        logger.info("Successfully uploaded outputs file: %s", file_name)
                    else:
                        logger.warning("Failed to upload outputs file: %s", file_name)

            logger.info("Uploaded %d new outputs files", uploaded_count)
            return True

        except Exception as e:
            logger.error("Error uploading outputs files: %s", str(e))
            return False

    def _upload_file_with_conflict_handling(
        self,
        local_file_path: str,
        cloud_file_path: str,
        adls_url: str,
        adls_container: str,
        adls_folder: str,
    ) -> bool:
        """
        Upload a file with conflict handling using Azure Storage SDK.

        If the file exists in cloud, it will be moved to .cloud_sync_conflict/
        with a timestamp, then the local file will be uploaded.
        """
        try:
            # Parse the cloud path for Azure operations
            # cloud_file_path format: "databank_name/file.ext"
            adls_path_parts = cloud_file_path.split("/")
            if len(adls_path_parts) < 2:
                logger.error("Invalid cloud file path format: %s", cloud_file_path)
                return False

            databank_dir = adls_path_parts[0]
            file_path_in_databank = "/".join(adls_path_parts[1:])

            # Get Azure directory client
            full_adls_path = f"{adls_folder}/{databank_dir}"
            az_fs, az_dir = adls_util.get_fs_directory_object(
                account_url=adls_url,
                file_system_name=adls_container,
                directory_name=full_adls_path,
                credential=adls_util.get_azure_credential(),
            )

            # Check if file exists in cloud
            file_client = az_dir.get_file_client(file_path_in_databank)

            if adls_util.file_exists(file_client):
                logger.info(
                    "File exists in cloud, handling conflict: %s", file_path_in_databank
                )

                # Generate timestamp and backup filename
                timestamp = time.strftime("%Y%m%d%H%M", time.localtime())

                # Parse original filename to create backup name
                path_parts = file_path_in_databank.split(".")
                if len(path_parts) > 1:
                    base_name = ".".join(path_parts[:-1])
                    extension = path_parts[-1]
                    backup_name = f"{base_name}_{timestamp}_bak.{extension}"
                else:
                    backup_name = f"{file_path_in_databank}_{timestamp}_bak"

                # Create conflict directory path
                conflict_file_path = f".cloud_sync_conflict/{backup_name}"

                # Get conflict directory client
                conflict_dir_path = f"{adls_folder}/{databank_dir}/.cloud_sync_conflict"
                _, conflict_dir = adls_util.get_fs_directory_object(
                    account_url=adls_url,
                    file_system_name=adls_container,
                    directory_name=conflict_dir_path,
                    credential=adls_util.get_azure_credential(),
                )

                # Rename (move) the existing file to conflict directory
                logger.info(
                    "Moving existing cloud file to conflict directory: %s",
                    conflict_file_path,
                )

                try:
                    # Use Azure rename operation to move file to conflict directory
                    adls_util.rename_file(
                        directory_client=az_dir,
                        old_file_name=file_path_in_databank,
                        new_file_name=conflict_file_path,
                    )
                    logger.info(
                        "Successfully moved existing file to conflict directory"
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to move existing file to conflict directory: %s", str(e)
                    )
                    # Continue with upload anyway

            # Upload the local file (this will now succeed since conflict was resolved)
            logger.info("Uploading local file: %s", file_path_in_databank)

            success = self.file_sync.upload_to_adls(
                local_file_path=local_file_path,
                adls_file=cloud_file_path,
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                export_log=False,
            )

            if success:
                logger.info(
                    "Successfully uploaded file with conflict handling: %s",
                    file_path_in_databank,
                )
            else:
                logger.error("Failed to upload file: %s", file_path_in_databank)

            return success

        except Exception as e:
            logger.error("Error in upload with conflict handling: %s", str(e))
            return False

    def _initialize_cloud_databank(self) -> bool:
        """
        Initialize cloud databank by checking for existing files and downloading if available.

        For cloud mode initialization:
        - Check if cloud has valid databank files (config and component zips)
        - If valid files exist, download them based on local databank status
        - If no valid databank exists, initialize new databank and upload to cloud

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Initializing cloud databank")

        if "operational_mode" not in self.config:
            logger.error("No operational_mode configuration found")
            return False

        adls_url, adls_container, adls_folder = self._get_adls_config()

        try:
            # Check if files exist in cloud
            cloud_files = self.file_sync.download_from_adls_by_pattern(
                adls_pattern=f"{self.databank_name}/**",
                local_path="",  # Don't download, just list
                adls_url=adls_url,
                adls_container=adls_container,
                adls_folder=adls_folder,
                list_only=True,
                export_log=False,
                databank_name=self.databank_name,
            )

            if cloud_files is None:
                logger.error("Failed to list files in cloud databank")
                return False

            if len(cloud_files) == 0:
                logger.info(
                    "No existing files found in cloud - initializing new databank"
                )
                # Initialize new databank and upload if no cloud files found
                self._initialize_databank()

                # Initialize state after databank creation
                self.state = OrcaState(self.state_file, logger)
                if self.state.get("status") == "not_started":
                    self._initialize_state_from_config()

                # Upload to cloud (will be treated as databank initialization)
                if not self._sync_with_cloud(direction="upload"):
                    logger.error("Failed to upload initial databank to cloud")
                    return False
                return True

            # Filter out conflict files
            current_files = []
            config_files = []
            for cloud_file in cloud_files:
                file_name = os.path.basename(cloud_file)

                # Skip conflict files
                if ".cloud_sync_conflict" in cloud_file:
                    logger.debug("Skipping conflict file: %s", file_name)
                    continue

                # Skip .cloud_model_archive files when checking for valid databank
                if ".cloud_model_archive" in cloud_file:
                    logger.debug("Skipping archive file: %s", file_name)
                    continue

                # Skip .error_dump files when checking for valid databank
                if ".error_dump" in cloud_file:
                    logger.debug("Skipping error dump file: %s", file_name)
                    continue

                current_files.append(cloud_file)
                if file_name.endswith((".yaml", ".json")):
                    config_files.append(cloud_file)

            # Check if we have config files (required for valid databank)
            if len(config_files) == 0:
                logger.info(
                    "No config files found in cloud - initializing new databank"
                )
                # Initialize new databank and upload
                self._initialize_databank()

                # Initialize state after databank creation
                self.state = OrcaState(self.state_file, logger)
                if self.state.get("status") == "not_started":
                    self._initialize_state_from_config()

                # Upload to cloud (will be treated as databank initialization)
                if not self._sync_with_cloud(direction="upload"):
                    logger.error("Failed to upload initial databank to cloud")
                    return False
                return True

            logger.info(
                "Valid databank files found in cloud (%d files) - downloading",
                len(current_files),
            )

            # Download files based on local databank status
            success = self._sync_with_cloud(direction="download")
            if not success:
                logger.error("Failed to download existing databank from cloud")
                # Attempt recovery by initializing fresh databank
                logger.info("Attempting recovery by initializing fresh databank")
                self._initialize_databank()

                # Initialize state after databank creation for recovery
                self.state = OrcaState(self.state_file, logger)
                if self.state.get("status") == "not_started":
                    self._initialize_state_from_config()

                # Upload to cloud (will be treated as databank initialization)
                if not self._sync_with_cloud(direction="upload"):
                    logger.error("Recovery initialization also failed")
                    return False
                return True

            # Reload configuration and state from downloaded files
            if os.path.exists(self.config_file):
                logger.info("Reloading configuration from downloaded config file")
                try:
                    self.config = self._load_configuration()
                except Exception as e:
                    logger.error("Failed to reload config from cloud: %s", str(e))
                    logger.info("Continuing with local config")

            if os.path.exists(self.state_file):
                logger.info("Reloading state from downloaded state file")
                try:
                    self.state = OrcaState(self.state_file, logger)
                    logger.info("Successfully loaded existing state from cloud")
                except Exception as e:
                    logger.error("Failed to load state from cloud: %s", str(e))
                    logger.info("Reinitializing state")
                    self.state.update(status="initialized")

            return True

        except Exception as e:
            logger.error("Error during cloud databank initialization: %s", str(e))
            return False

    def _upload_error_dumps_to_cloud(self) -> bool:
        """
        Upload error dumps to cloud storage.

        This method uploads all error dump files from the .error_dump directory
        to the cloud storage with a special error_dumps/ prefix.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            error_dump_base = os.path.join(self.databank_path, ".error_dump")

            if not os.path.exists(error_dump_base):
                logger.info("No error dumps found to upload")
                return True

            # Get ADLS configuration
            adls_url, adls_container, adls_folder = self._get_adls_config()

            # Find all error dump files (zip files)
            error_dump_files = glob.glob(os.path.join(error_dump_base, "*.zip"))

            if not error_dump_files:
                logger.info("No error dump archives found to upload")
                return True

            logger.info("Found %d error dump files to upload", len(error_dump_files))

            success = True
            for dump_file in error_dump_files:
                dump_filename = os.path.basename(dump_file)

                # Upload to {databank_name}/.error_dump/ subfolder in cloud
                cloud_path = f"{self.databank_name}/.error_dump/{dump_filename}"

                logger.info("Uploading error dump: %s", dump_filename)

                upload_success = self.file_sync.upload_to_adls(
                    local_file_path=dump_file,
                    adls_file=cloud_path,
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_folder=adls_folder,
                    export_log=True,
                )

                if upload_success:
                    logger.info("Successfully uploaded error dump: %s", dump_filename)
                else:
                    logger.error("Failed to upload error dump: %s", dump_filename)
                    success = False

            if success:
                logger.info("All error dumps uploaded successfully")
            else:
                logger.warning("Some error dumps failed to upload")

            return success

        except Exception as e:
            logger.error("Error uploading error dumps to cloud: %s", e)
            return False

    def run_local_testing(self) -> bool:
        """
        Run the model in local testing mode - execute all steps for all iterations.

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Running in local_testing mode")

        # Update status
        self.state.update(status="running")

        # Add safety counter to prevent infinite loops
        max_steps = self.state.get("total_iterations", 1) * len(
            self.state.get("steps", [])
        )
        step_counter = 0

        # Run until all iterations are complete
        while not self.state.is_all_iterations_complete():
            # Safety check to prevent infinite loops
            step_counter += 1
            if step_counter > max_steps * 2:  # Allow some buffer
                logger.error(
                    "Infinite loop detected! Executed %d steps, expected max %d",
                    step_counter,
                    max_steps,
                )
                self.state.update(status="error", error="Infinite loop detected")
                return False

            # Get the next step to execute
            step_name = self.state.get_next_step()
            current_iter = self.state.get_display_iteration()
            current_step_idx = self.state.get("current_step_index", 0)

            logger.info(
                "Iteration %d, Step %d/%d: %s",
                current_iter,
                current_step_idx + 1,
                len(self.state.get("steps", [])),
                step_name,
            )

            if step_name is None:
                # No more steps in this iteration, start a new one
                next_iter = self.state.increment_iteration()
                logger.info("Starting iteration %d", next_iter)

                # Check if we've exceeded the total iterations
                if self.state.is_all_iterations_complete():
                    logger.info("All iterations completed")
                    break

                # Get the first step of the new iteration
                step_name = self.state.get_next_step()
                if step_name is None:
                    logger.warning("No steps available in new iteration")
                    break

            # Execute the step
            success = self._execute_step(step_name)

            if success:
                # Mark the step as completed
                self.state.mark_step_complete(step_name)
            else:
                # Update state to reflect the error
                self.state.update(
                    status="error", error=f"Error executing step: {step_name}"
                )
                logger.error("Error executing step: %s", step_name)
                return False

        # Update state to reflect completion
        self.state.update(status="completed")
        logger.info("Model run completed successfully")
        return True

    def run_cloud_production(self) -> bool:
        """
        Run the model in cloud production mode - execute all steps with cloud synchronization.

        Cloud mode sync behavior:
        - Databank initialized locally, or from cloud if databank directory available on ADLS
        - File sync occurs at the end of each step (upload with overwrite on)
        - Upload at the end of each iteration should happen along with the last step of that iteration

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Running in cloud_production mode")

        # Update status
        self.state.update(status="running")

        # Add safety counter to prevent infinite loops
        max_steps = self.state.get("total_iterations", 1) * len(
            self.state.get("steps", [])
        )
        step_counter = 0

        # Run until all iterations are complete
        while not self.state.is_all_iterations_complete():
            # Safety check to prevent infinite loops
            step_counter += 1
            if step_counter > max_steps * 2:  # Allow some buffer
                logger.error(
                    "Infinite loop detected! Executed %d steps, expected max %d",
                    step_counter,
                    max_steps,
                )
                self.state.update(status="error", error="Infinite loop detected")
                return False

            # Get the next step to execute
            step_name = self.state.get_next_step()
            current_iter = self.state.get_display_iteration()
            current_step_idx = self.state.get("current_step_index", 0)
            total_steps = len(self.state.get("steps", []))

            logger.info(
                "Cloud mode - Iteration %d, Step %d/%d: %s",
                current_iter,
                current_step_idx + 1,
                total_steps,
                step_name,
            )

            if step_name is None:
                # No more steps in this iteration, start a new one
                next_iter = self.state.increment_iteration()
                logger.info("Starting iteration %d", next_iter)

                # Check if we've exceeded the total iterations
                if self.state.is_all_iterations_complete():
                    logger.info("All iterations completed")
                    break

                # Get the first step of the new iteration
                step_name = self.state.get_next_step()
                if step_name is None:
                    logger.warning("No steps available in new iteration")
                    break

            # Execute the step
            success = self._execute_step(step_name)

            if success:
                # Mark the step as completed
                self.state.mark_step_complete(step_name)

                # Upload data to cloud after successful step completion
                logger.info("Syncing data to cloud after step completion")
                if not self._sync_with_cloud(direction="upload"):
                    logger.warning("Failed to sync data to cloud after step completion")
                    # Continue execution even if sync fails

                # Check if this is the last step of an iteration
                current_step_idx = self.state.get("current_step_index", 0)
                if current_step_idx >= total_steps:
                    logger.info("Completed iteration %d.", current_iter)
                    # The upload after the last step serves as the iteration-end upload
            else:
                # Update state to reflect the error
                self.state.update(
                    status="error", error=f"Error executing step: {step_name}"
                )
                logger.error("Error executing step: %s", step_name)

                return False

        # Update state to reflect completion
        self.state.update(status="completed")

        # Final sync to cloud after completion
        logger.info("Final state sync to cloud after model completion")
        if not self._sync_with_cloud(direction="upload"):
            logger.warning("Failed to perform final state sync to cloud")

        logger.info("Model run completed successfully")
        return True

    def run(self) -> bool:
        """
        Run the model based on the configured mode.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.mode == "local_testing":
            return self.run_local_testing()
        elif self.mode == "cloud_production":
            return self.run_cloud_production()
        else:
            logger.error("Invalid mode: %s", self.mode)
            return False

    def initialize_databank(self) -> bool:
        """
        Initialize a databank without running model steps.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Initializing databank: %s", self.databank_name)

            # The databank is already initialized in __init__, but we can
            # validate the setup and report what was created

            # Report what was created
            logger.info("Databank Summary:")
            logger.info("  Location: %s", self.databank_path)
            logger.info("  Configuration: %s", self.config_file)
            logger.info("  State file: %s", self.state_file)

            # List created directories
            if os.path.exists(self.databank_path):
                contents = os.listdir(self.databank_path)
                directories = [
                    item
                    for item in contents
                    if os.path.isdir(os.path.join(self.databank_path, item))
                ]
                files = [
                    item
                    for item in contents
                    if os.path.isfile(os.path.join(self.databank_path, item))
                ]

                if directories:
                    logger.info(
                        "  Sub-component directories: %s",
                        ", ".join(sorted(directories)),
                    )
                if files:
                    logger.info("  Configuration files: %s", ", ".join(sorted(files)))

            # Show configured model steps
            model_steps = self.config.get("model_steps", [])
            if model_steps:
                logger.info("  Configured model steps: %s", " → ".join(model_steps))

            total_iterations = self.config.get("iterations", {}).get("total", 1)
            logger.info("  Configured iterations: %d", total_iterations)

            logger.info("Databank is ready for model execution!")
            return True

        except Exception as e:
            logger.error("Error initializing databank: %s", e)
            return False

    def sync_with_adls(self, direction: str, **kwargs) -> bool:
        """
        Sync databank with Azure Data Lake Storage.

        Args:
            direction: 'upload', 'download', or 'list'
            **kwargs: Additional options

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if "operational_mode" not in self.config:
                logger.error("No operational_mode configuration found")
                return False

            adls_url, adls_container, adls_folder = self._get_adls_config()

            if direction == "list":
                # List files in ADLS
                files = self.file_sync.download_from_adls_by_pattern(
                    adls_pattern=f"{self.databank_name}/**",
                    local_path="",
                    adls_url=adls_url,
                    adls_container=adls_container,
                    adls_folder=adls_folder,
                    list_only=True,
                    export_log=False,
                    databank_name=self.databank_name,
                )

                if files:
                    logger.info(
                        "Files found in ADLS for databank '%s':",
                        self.databank_name,
                    )
                    # Separate current files from backup/conflict files
                    current_files = []
                    conflict_files = []
                    backup_files = []

                    for file_path in files:
                        file_name = os.path.basename(file_path)

                        if ".cloud_sync_conflict" in file_path:
                            conflict_files.append(file_path)
                        elif "_bak." in file_name:
                            backup_files.append(file_path)
                        else:
                            current_files.append(file_path)

                    if current_files:
                        logger.info("Current files:")
                        for file_path in sorted(current_files):
                            logger.info("  - %s", file_path)

                    if conflict_files:
                        logger.info("Conflict files:")
                        for file_path in sorted(conflict_files):
                            logger.info("  - %s", file_path)

                    if backup_files:
                        logger.info("Backup files:")
                        for file_path in sorted(backup_files):
                            logger.info("  - %s", file_path)

                    logger.info(
                        "Total files: %d (current: %d, conflicts: %d, backups: %d)",
                        len(files),
                        len(current_files),
                        len(conflict_files),
                        len(backup_files),
                    )
                else:
                    logger.info(
                        "No files found in ADLS for databank: %s",
                        self.databank_name,
                    )
                return True

            elif direction == "download":
                return self._sync_with_cloud(direction="download", **kwargs)

            elif direction == "upload":
                return self._sync_with_cloud(direction="upload", **kwargs)

            else:
                logger.error("Invalid sync direction: %s", direction)
                return False

        except Exception as e:
            logger.error("Error during ADLS sync: %s", e)
            return False


def check_databank_exists(databank_path):
    """
    Check if a databank already exists based on the presence of the state file.

    A databank is considered to exist if the state file (orca_model_state.json) exists,
    regardless of other files (including log files) that might be present.

    Returns:
        dict: Information about the existing databank
    """
    if not os.path.exists(databank_path):
        return {"exists": False}

    # Check specifically for the state file to determine if databank exists
    state_file_path = os.path.join(databank_path, "orca_model_state.json")

    if not os.path.exists(state_file_path):
        return {"exists": False}

    info = {"exists": True, "files": [], "directories": []}

    try:
        contents = os.listdir(databank_path)
        for item in contents:
            item_path = os.path.join(databank_path, item)
            if os.path.isdir(item_path):
                info["directories"].append(item)
            else:
                info["files"].append(item)
    except PermissionError:
        info["error"] = "Permission denied accessing databank directory"

    return info


def unpack_landuse_action(args):
    """Handle the unpack_landuse action."""
    # Set up logging
    log_file_path = os.path.join(args.output, "unpack_landuse.log")
    action_logger = get_orca_logger(
        "orca_orchestrator.unpack_landuse", log_file_path=log_file_path
    )

    action_logger.info("ORCA Orchestrator: Unpack Landuse")
    action_logger.info("Model Year: %s", args.model_year)
    action_logger.info("Input File: %s", args.input)
    action_logger.info("Output Directory: %s", args.output)

    try:
        # Validate input file exists
        if not os.path.exists(args.input):
            action_logger.error("Input file does not exist: %s", args.input)
            return False

        # Validate input file is a zip file
        if not args.input.lower().endswith(".zip"):
            action_logger.error("Input file must be a zip file: %s", args.input)
            return False

        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)

        # Create OrcaDatabank instance
        databank = OrcaDatabank(
            databank_path=args.output, databank_logger=action_logger
        )

        # Unpack the landuse zip file
        success = databank.unpack_landuse_zip(
            zip_file_path=args.input,
            output_dir=args.output,
            model_year=args.model_year,
            export_log=True,
        )

        if success:
            action_logger.info(
                "Successfully extracted landuse files for model year %s",
                args.model_year,
            )
        else:
            action_logger.error("Failed to extract landuse files")

        return success

    except (OSError, IOError) as e:
        action_logger.error("File system error: %s", str(e))
        return False
    except ImportError as e:
        action_logger.error("Import error: %s", str(e))
        return False


def main():
    """Main entry point for the ORCA orchestrator with action-based interface."""
    parser = argparse.ArgumentParser(
        description="ORCA Transportation Model Orchestrator - Unified interface for all ORCA operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  run_models            Initialize and run complete model workflow
  initialize_databank   Initialize databank without running models  
  adls_sync            Synchronize databank with Azure Data Lake Storage
  unpack_landuse       Extract landuse files filtered by model year from zip archives

Examples:
  # Run complete model workflow (most common use case)
  python orchestrator.py --action run_models --databank db_test

  # Initialize databank only
  python orchestrator.py --action initialize_databank --databank db_test --overwrite

  # Cloud synchronization
  python orchestrator.py --action adls_sync --databank db_test --sync-action upload
  python orchestrator.py --action adls_sync --databank db_test --sync-action download --overwrite
  python orchestrator.py --action adls_sync --databank db_test --sync-action list

  # Cloud synchronization with custom project folder
  python orchestrator.py --action adls_sync --databank db_test --sync-action upload --project-folder my_custom_project

  # Utility functions
  python orchestrator.py --action unpack_landuse --model-year 2017 --input landuse.zip --output data

  # Advanced model running with options
  python orchestrator.py --action run_models --databank db_test --mode cloud_production --iterations 3 --resume --project-folder my_custom_project
        """,
    )

    parser.add_argument(
        "--action",
        choices=["run_models", "initialize_databank", "adls_sync", "unpack_landuse"],
        default="run_models",
        help="Action to perform",
    )

    parser.add_argument(
        "--databank", default="db_test", help="Name of the databank (scenario)"
    )

    parser.add_argument(
        "--config",
        default="orca_model_config.yaml",
        help="Configuration file name (default: orca_model_config.yaml)",
    )

    parser.add_argument(
        "--state",
        default="orca_model_state.json",
        help="State file name (default: orca_model_state.json)",
    )

    parser.add_argument(
        "--mode",
        choices=["local_testing", "cloud_production"],
        default="local_testing",
        help="Execution mode (default: local_testing)",
    )

    # Arguments for run_models action
    parser.add_argument(
        "--iterations",
        type=int,
        help="Number of iterations to run (overrides config file setting)",
    )

    parser.add_argument(
        "--steps",
        nargs="+",
        help="Specific model steps to run (e.g., --steps activitysim quetzal). If not specified, uses config file setting",
    )

    # Arguments for initialize_databank action
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing databank if it exists",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually creating files",
    )

    # Arguments for adls_sync action
    parser.add_argument(
        "--sync-action",
        choices=["upload", "download", "list"],
        help="ADLS synchronization action: upload to ADLS, download from ADLS, or list ADLS contents",
    )

    # Arguments for unpack_landuse action
    parser.add_argument(
        "--model-year",
        help="Model year to filter files by (required for unpack_landuse)",
    )

    parser.add_argument("--input", help="Input file path (required for unpack_landuse)")

    parser.add_argument(
        "--output", help="Output directory path (required for unpack_landuse)"
    )

    parser.add_argument(
        "--project-folder",
        help="Override the ADLS project folder path (adls_folder) from config file",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Action-specific validation and execution
    if args.action == "run_models":
        # Validate required arguments for run_models
        if not args.databank:
            parser.error("--databank is required for run_models action")

        # Set up logging
        action_logger = get_orca_logger("run_models", log_file_path="run_models.log")

        action_logger.info("=" * 60)
        action_logger.info("ORCA Model Runner Starting")
        action_logger.info("=" * 60)
        action_logger.info("Databank: %s", args.databank)
        action_logger.info("Mode: %s", args.mode)
        action_logger.info("Config: %s", args.config)

        if args.iterations:
            action_logger.info("Iterations (override): %d", args.iterations)
        if args.steps:
            action_logger.info("Steps (override): %s", args.steps)
        if args.project_folder:
            action_logger.info("Project folder (override): %s", args.project_folder)

        try:
            # Create the orchestrator instance
            orchestrator = OrcaOrchestrator(
                databank_name=args.databank,
                config_file=args.config,
                state_file=args.state,
                mode=args.mode,
                project_folder=args.project_folder,
            )

            # Apply command-line overrides to configuration
            if args.iterations:
                action_logger.info(
                    "Overriding iterations in config: %d", args.iterations
                )
                orchestrator.config["iterations"]["total"] = args.iterations
                # Update state with new iteration count
                orchestrator.state.update(total_iterations=args.iterations)

            if args.steps:
                action_logger.info("Overriding model steps in config: %s", args.steps)
                orchestrator.config["model_steps"] = args.steps
                # Update state with new steps
                orchestrator.state.update(steps=args.steps)

            # Run the model
            action_logger.info("Starting model execution...")
            success = orchestrator.run()

            # Report results
            action_logger.info("=" * 60)
            if success:
                action_logger.info("[SUCCESS] Model execution completed successfully!")

                # Print summary information
                total_iterations = orchestrator.state.get("total_iterations", 0)
                total_steps_completed = orchestrator.state.get(
                    "total_steps_completed", 0
                )

                action_logger.info("Summary:")
                action_logger.info("  - Total iterations: %d", total_iterations)
                action_logger.info(
                    "  - Total steps completed: %d", total_steps_completed
                )
                action_logger.info(
                    "  - Databank location: %s", orchestrator.databank_path
                )

                if args.mode == "cloud_production":
                    action_logger.info("  - Cloud sync: enabled")
                    action_logger.info("  - Model outputs backed up to ADLS")

                # Check for outputs directory
                outputs_dir = os.path.join(orchestrator.databank_path, "outputs")
                if os.path.exists(outputs_dir):
                    output_files = []
                    for _, _, files in os.walk(outputs_dir):
                        output_files.extend(files)
                    action_logger.info(
                        "  - Output files generated: %d", len(output_files)
                    )

                action_logger.info("=" * 60)
                action_logger.info(
                    "Model run completed. Check the databank directory for results:"
                )
                action_logger.info("  %s", orchestrator.databank_path)

            else:
                action_logger.error("[FAILED] Model execution failed!")

                # Print error information if available
                error_msg = orchestrator.state.get("error")
                if error_msg:
                    action_logger.error("Error details: %s", error_msg)

                # Print current state for debugging
                current_step = orchestrator.state.get_next_step()
                current_iteration = orchestrator.state.get_display_iteration()
                action_logger.error(
                    "Failed at iteration %d, step: %s", current_iteration, current_step
                )

                action_logger.info("=" * 60)
                action_logger.info("Check the logs for detailed error information.")
                action_logger.info(
                    "Model state saved to: %s", orchestrator.state.state_file_path
                )

            sys.exit(0 if success else 1)

        except KeyboardInterrupt:
            action_logger.warning("Model execution interrupted by user")
            action_logger.info(
                "Model state has been saved and can resume from last successfully completed step."
            )
            sys.exit(1)

        except (OSError, IOError, RuntimeError) as e:
            action_logger.error("Unexpected error during model execution: %s", str(e))
            action_logger.error("Check the logs for detailed error information")
            sys.exit(1)

    elif args.action == "initialize_databank":
        # Validate required arguments for initialize_databank
        if not args.databank:
            parser.error("--databank is required for initialize_databank action")

        # Set up logging
        action_logger = get_orca_logger(
            "initialize_databank", log_file_path="initialize_databank.log"
        )

        action_logger.info("=" * 60)
        action_logger.info("ORCA Databank Initializer")
        action_logger.info("=" * 60)
        action_logger.info("Databank: %s", args.databank)
        action_logger.info("Config: %s", args.config)
        if args.project_folder:
            action_logger.info("Project folder (override): %s", args.project_folder)

        if args.dry_run:
            action_logger.info("Mode: DRY RUN (no files will be created)")
        if args.overwrite:
            action_logger.info("Overwrite: enabled")

        try:
            # Check if databank already exists
            databank_path = os.path.abspath(args.databank)
            existing_info = check_databank_exists(databank_path)

            if existing_info["exists"]:
                action_logger.warning("Databank already exists at: %s", databank_path)

                # Show what's in the existing databank
                if existing_info.get("error"):
                    action_logger.error(
                        "Error checking databank: %s", existing_info["error"]
                    )
                    sys.exit(1)

                if existing_info["directories"]:
                    action_logger.info(
                        "Existing directories: %s",
                        ", ".join(existing_info["directories"]),
                    )
                if existing_info["files"]:
                    action_logger.info(
                        "Existing files: %s", ", ".join(existing_info["files"])
                    )

                if not args.overwrite:
                    action_logger.error("Use --overwrite to replace existing databank")
                    sys.exit(1)
                else:
                    action_logger.warning("Will overwrite existing databank")
                    if not args.dry_run:
                        # Remove existing databank
                        action_logger.info("Removing existing databank...")
                        shutil.rmtree(databank_path)

            if args.dry_run:
                action_logger.info(
                    "DRY RUN: Would create databank at: %s", databank_path
                )
                action_logger.info(
                    "DRY RUN: Would copy template files from sub-components"
                )
                action_logger.info(
                    "DRY RUN: Would create configuration file: %s", args.config
                )
                action_logger.info("DRY RUN: Would initialize model state file")
                action_logger.info("DRY RUN: Would create outputs directory structure")

                # Show what templates would be copied
                try:
                    # Find default config using the same logic as _create_template_config
                    default_config_locations = [
                        os.path.join(ORCA_DIR, "orca_model_config_default.yaml"),
                        os.path.join(os.getcwd(), "orca_model_config_default.yaml"),
                        os.path.join(
                            os.getcwd(), "orca", "orca_model_config_default.yaml"
                        ),
                    ]

                    default_config_path = None
                    for path in default_config_locations:
                        if os.path.exists(path):
                            default_config_path = path
                            break

                    if default_config_path:
                        import yaml

                        with open(default_config_path, "r", encoding="utf-8") as f:
                            config = yaml.safe_load(f)

                        if "sub_components" in config:
                            action_logger.info(
                                "DRY RUN: Templates that would be copied:"
                            )
                            for step_name, step_config in config[
                                "sub_components"
                            ].items():
                                action_logger.info("  - %s", step_name)
                except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
                    action_logger.warning("Could not preview templates: %s", str(e))

                action_logger.info("DRY RUN: Initialization preview completed")
                sys.exit(0)

            # Create the orchestrator instance (this will initialize the databank)
            action_logger.info("Creating databank structure...")
            orchestrator = OrcaOrchestrator(
                databank_name=args.databank,
                config_file=args.config,
                state_file=args.state,
                mode=args.mode,
                project_folder=args.project_folder,
            )

            # Use the new initialize_databank method
            success = orchestrator.initialize_databank()

            if success:
                action_logger.info("[SUCCESS] Databank initialization completed!")
                action_logger.info("=" * 60)
                action_logger.info("Databank is ready for model execution!")
                action_logger.info("To run the model, use:")
                action_logger.info(
                    "  python orchestrator.py --action run_models --databank %s",
                    args.databank,
                )
            else:
                action_logger.error("[FAILED] Databank initialization failed!")
                sys.exit(1)

        except KeyboardInterrupt:
            action_logger.warning("Initialization interrupted by user")
            sys.exit(1)

        except (OSError, IOError) as e:
            action_logger.error("File system error during initialization: %s", str(e))
            sys.exit(1)

        except ImportError as e:
            action_logger.error("Required module not found: %s", str(e))
            action_logger.error("Make sure all dependencies are installed")
            sys.exit(1)

    elif args.action == "adls_sync":
        # Validate required arguments for adls_sync
        if not args.databank:
            parser.error("--databank is required for adls_sync action")
        if not args.sync_action:
            parser.error("--sync-action is required for adls_sync action")

        # Set up logging
        action_logger = get_orca_logger(
            "adls_data_sync", log_file_path="adls_data_sync.log"
        )

        action_logger.info("=" * 60)
        action_logger.info("ORCA ADLS Data Synchronization")
        action_logger.info("=" * 60)
        action_logger.info("Databank: %s", args.databank)
        action_logger.info("Action: %s", args.sync_action)

        if args.config:
            action_logger.info("Config file: %s", args.config)
        if args.overwrite:
            action_logger.info("Overwrite: enabled")
        if args.project_folder:
            action_logger.info("Project folder (override): %s", args.project_folder)

        try:
            # For download operations, we may need to create the orchestrator even if databank doesn't exist locally
            if args.sync_action == "download" and not os.path.exists(args.databank):
                # Create minimal structure for download
                os.makedirs(args.databank, exist_ok=True)

            orchestrator = OrcaOrchestrator(
                databank_name=args.databank,
                config_file=args.config,
                state_file=args.state,
                mode="local_testing",  # Assume local testing when triggering sync action manually to avoid triggering additional sync commands
                project_folder=args.project_folder,
            )

            # Log ADLS settings
            adls_url, adls_container, adls_folder = orchestrator.get_adls_config()
            action_logger.info("ADLS Account URL: %s", adls_url)
            action_logger.info("ADLS Container: %s", adls_container)
            action_logger.info("ADLS Folder: %s", adls_folder)

            # Perform synchronization
            success = orchestrator.sync_with_adls(
                direction=args.sync_action,
            )

            # Report results
            action_logger.info("=" * 60)
            if success:
                action_logger.info("[SUCCESS] Synchronization completed successfully!")

                if args.sync_action == "upload":
                    action_logger.info(
                        "Databank '%s' has been uploaded to ADLS", args.databank
                    )
                    action_logger.info(
                        "Cloud location: %s/%s/%s/%s",
                        adls_url,
                        adls_container,
                        adls_folder,
                        args.databank,
                    )

                elif args.sync_action == "download":
                    action_logger.info(
                        "Databank '%s' has been downloaded from ADLS", args.databank
                    )
                    action_logger.info(
                        "Local location: %s", os.path.abspath(args.databank)
                    )

                elif args.sync_action == "list":
                    action_logger.info(
                        "ADLS contents listed for databank '%s'", args.databank
                    )

            else:
                action_logger.error("[FAILED] Synchronization failed!")
                action_logger.error("Check the logs for detailed error information")

            # Exit with appropriate code
            sys.exit(0 if success else 1)

        except KeyboardInterrupt:
            action_logger.warning("Synchronization interrupted by user")
            sys.exit(1)

        except (OSError, IOError) as e:
            action_logger.error("File system error during synchronization: %s", str(e))
            sys.exit(1)

        except ImportError as e:
            action_logger.error("Required module not found: %s", str(e))
            action_logger.error(
                "Make sure tlpytools and other dependencies are installed"
            )
            sys.exit(1)

    elif args.action == "unpack_landuse":
        # Validate required arguments for unpack_landuse
        if not args.model_year:
            parser.error("--model-year is required for unpack_landuse action")
        if not args.input:
            parser.error("--input is required for unpack_landuse action")
        if not args.output:
            parser.error("--output is required for unpack_landuse action")

        success = unpack_landuse_action(args)
        sys.exit(0 if success else 1)

    else:
        parser.error(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()
