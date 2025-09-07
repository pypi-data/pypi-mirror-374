import importlib.util
import coverage
import logging
import sys
import os
import time
import tempfile
import threading
import argparse
import json
from pathlib import Path
from collections import deque
from datetime import datetime
from typing import Callable, Optional

from mo.core.plugin.models.properties import Properties
from mo.core.plugin.models.settings import Settings
from mo.modules.capture.plugins.capture_plugin import CapturePlugin
from mop.utils.logger import setup_logger, Colors
from mop.utils.path import pretty_path

logger = setup_logger("capture-plugin-tester")

METADATA_ENTRY_POINTS = {
    "plugin": "mo.plugin",
    "properties": "mo.plugin.properties",
}


class CapturePluginTester:
    """
    Utility class to simulate and test the lifecycle of a MO CapturePlugin,
    loading the plugin using metadata.json entry points.
    """

    def __init__(self, plugin_dir_or_metadata: str = "./"):
        """
        Initializes the CapturePluginTester by loading the plugin class and properties from metadata.json.

        Args:
            plugin_dir_or_metadata (str): Path to the plugin root directory (should contain metadata.json),
                or path directly to a metadata.json file.

        Raises:
            FileNotFoundError: If metadata.json does not exist in the provided path.
            ImportError, TypeError: If the plugin class cannot be loaded or is not a subclass of CapturePlugin.
        """
        path = Path(plugin_dir_or_metadata).resolve()
        if path.is_file() and path.name == "metadata.json":
            self.metadata_path = path
            self.plugin_dir = path.parent
        else:
            self.plugin_dir = path
            self.metadata_path = self.plugin_dir / "metadata.json"

        self.metadata = self._load_metadata_file()
        self.PluginClass = self._load_plugin_class_from_metadata()
        self.properties = self._load_properties_class_from_metadata()

    def _load_metadata_file(self):
        """
        Loads the metadata.json file from the plugin directory or provided file path.

        Returns:
            dict: Parsed plugin metadata as a dictionary.

        Raises:
            FileNotFoundError: If metadata.json does not exist at the expected location.
        """
        if not self.metadata_path.exists():
            logger.error(
                f"Metadata file not found at {pretty_path(self.metadata_path)}")
            raise FileNotFoundError(
                f"Metadata file not found at {pretty_path(self.metadata_path)}")
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _get_entry_point(self, group: str) -> tuple[str, str]:
        """
        Resolves the file path and symbol name for an entry point group from the plugin's metadata.json.

        Args:
            group (str): Entry point group, e.g. 'plugin' or 'properties'.

        Returns:
            tuple: (module_file_path, symbol_name)

        Raises:
            RuntimeError: If the entry point is not found in the metadata.json.
        """
        entry_points = self.metadata.get("entryPoints", {})
        group_key = METADATA_ENTRY_POINTS.get(group, group)
        if group_key not in entry_points:
            logger.error(
                f"Entry point '{group_key}' not found in metadata.json")
            raise RuntimeError(
                f"Entry point '{group_key}' not found in metadata.json")
        entry_point = entry_points[group_key]
        module_path, symbol_name = entry_point.split(":")
        module_file = (self.plugin_dir /
                       (module_path.replace(".", os.sep) + ".py")).resolve()
        return str(module_file), symbol_name

    def _load_plugin_class_from_metadata(self):
        """
        Loads the CapturePlugin class as defined in the metadata.json entry point 'plugin'.

        Returns:
            type: The CapturePlugin subclass to instantiate.

        Raises:
            FileNotFoundError: If the plugin module file is missing.
            ImportError: If the module cannot be imported.
            TypeError: If the class is not found or is not a subclass of CapturePlugin.
        """
        module_file, class_name = self._get_entry_point("plugin")
        if not Path(module_file).exists():
            logger.error(
                f"Module file not found: {pretty_path(Path(module_file))}")
            raise FileNotFoundError(
                f"Module file not found: {pretty_path(Path(module_file))}")
        spec = importlib.util.spec_from_file_location(
            "plugin_module", module_file)
        if spec is None or spec.loader is None:
            logger.error(
                f"Failed to create module spec for: {pretty_path(Path(module_file))}")
            raise ImportError(
                f"Failed to create module spec for: {pretty_path(Path(module_file))}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["plugin_module"] = module
        spec.loader.exec_module(module)
        symbol = getattr(module, class_name)
        if symbol is None or not isinstance(symbol, type) or not issubclass(symbol, CapturePlugin):
            logger.error(
                f"Class '{class_name}' not found or is not a subclass of CapturePlugin in module: {pretty_path(Path(module_file))}")
            raise TypeError(
                f"Class '{class_name}' not found or is not a subclass of CapturePlugin in module: {pretty_path(Path(module_file))}")
        return symbol

    def _load_properties_class_from_metadata(self):
        """
        Loads the plugin Properties instance as defined in the metadata.json entry point 'properties'.

        Returns:
            Properties | None: Instance of the plugin's Properties class, or None if not found.

        Raises:
            TypeError: If the loaded symbol is not an instance of Properties.
        """
        module_file, symbol_name = self._get_entry_point("properties")
        if not Path(module_file).exists():
            logger.warning(
                f"Properties file not found: {pretty_path(Path(module_file))}")
            return None
        spec = importlib.util.spec_from_file_location(
            "properties_module", module_file)
        if spec is None or spec.loader is None:
            logger.warning(
                f"Failed to import properties module: {pretty_path(Path(module_file))}")
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules["properties_module"] = module
        spec.loader.exec_module(module)
        symbol = getattr(module, symbol_name)
        if callable(symbol):
            instance = symbol()
        else:
            instance = symbol
        if not isinstance(instance, Properties):
            logger.warning(
                f"Properties class '{symbol_name}' is not an instance of Properties.")
            raise TypeError(
                f"Properties class '{symbol_name}' is not an instance of Properties.")
        return instance
    
    def _load_simulate_func(self, entrypoint: str):
        """
        Loads a simulation function from a Python file, given an entrypoint in the form 'module.path:func'.

        Args:
            entrypoint (str): Entrypoint string in the format 'module.path:func'.

        Returns:
            Callable | None: The function object if found, or None if not found.

        Raises:
            TypeError: If the symbol is not callable.
        """
        module_path, func_name = entrypoint.split(":")
        module_file = (self.plugin_dir /
                       (module_path.replace(".", os.sep) + ".py")).resolve()
        module_file = str(module_file)
        if not Path(module_file).exists():
            logger.warning(
                f"Function file not found: {pretty_path(Path(module_file))}")
            return None
        spec = importlib.util.spec_from_file_location(
            "func_module", module_file)
        if spec is None or spec.loader is None:
            logger.warning(
                f"Failed to import function module: {pretty_path(Path(module_file))}")
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules["func_module"] = module
        spec.loader.exec_module(module)
        symbol = getattr(module, func_name)
        if not callable(symbol):
            logger.warning(
                f"Function '{func_name}' not found or is not callable in module: {pretty_path(Path(module_file))}")
            raise TypeError(
                f"Function '{func_name}' not found or is not callable in module: {pretty_path(Path(module_file))}")
        return symbol

    @staticmethod
    def _get_output_filename(base_dir: Path, prefix: str, extension: str) -> Path:
        """
        Generates an output filename for test results, including timestamp.

        Args:
            base_dir (Path): Output directory.
            prefix (str): Prefix for the file name.
            extension (str): File extension (with or without dot).

        Returns:
            Path: Path to the output file.
        """
        dt_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{prefix}_{dt_str}.{extension.lstrip('.')}"
        return base_dir / filename

    def run_test(
        self,
        settings: Optional[dict] = None,
        pause_resume: bool = False,
        test_duration: float = 3.0,
        flush_interval: float = 1.0,
        output_folder: Optional[str] = None,
        file_prefix: str = "test_capture",
        verbose: bool = True,
        simulate_func: Optional[Callable] = None,
        simulate_entrypoint: Optional[str] = None,
    ):

        """
        Runs the full test lifecycle for the capture plugin:
        - Configures and prepares the plugin (with settings or default properties).
        - Runs the capture for a given duration, with optional pause/resume.
        - Runs a simulation function (if provided) in parallel during the test.
        - Flushes, saves, and logs captured data to the output file.

        Args:
            settings (dict | None): Plugin settings (if None, uses properties defaults if available).
            pause_resume (bool): Whether to test pause/resume functionality during the run.
            test_duration (float): Duration of the capture test (in seconds).
            flush_interval (float): Interval for flushing/saving data (in seconds).
            output_folder (str | None): Folder to write the output file (temp if None).
            file_prefix (str): Prefix for output file name.
            verbose (bool): If True, outputs detailed logs.
            simulate_func (Callable | None): Optional simulation function (receives duration as arg).
            simulate_entrypoint (str | None): Optional simulation function entrypoint 'module.path:func'.

        Raises:
            TypeError: If plugin or simulate_func loading fails.
        """
        logger.info(
            f"Testing plugin at {Colors.CYAN.value}{pretty_path(self.plugin_dir)}{Colors.RESET.value}")
        plugin = self.PluginClass()
        plugin.load()
        if not settings and self.properties:
            settings = self.properties.get_default_values()
        plugin.configure(Settings(settings))

        # Output directory setup
        if output_folder is None:
            temp_dir = tempfile.TemporaryDirectory()
            output_dir = Path(temp_dir.name)
        else:
            output_dir = Path(output_folder)
            output_dir.mkdir(parents=True, exist_ok=True)
            temp_dir = None

        out_ext = plugin.get_file_extension()
        output_file = self._get_output_filename(
            output_dir, file_prefix, out_ext)

        logger.info(
            f"Output file will be: {Colors.BLUE.value}{pretty_path(output_file)}{Colors.RESET.value}")

        simulate_thread = None
        if simulate_func is not None:
            simulate_thread = threading.Thread(
                target=simulate_func, args=(test_duration,), daemon=True
            )
        elif simulate_entrypoint is not None:
            simulate_func_loaded = self._load_simulate_func(simulate_entrypoint)
            simulate_thread = threading.Thread(
                target=simulate_func_loaded, args=(test_duration,), daemon=True
            )

        plugin.prepare(str(output_dir), output_file.stem)
        captured_data = deque()
        data_lock = threading.Lock()
        pause_range = None
        should_run = True

        def get_timestamp():
            return time.monotonic()

        def on_data(data):
            with data_lock:
                captured_data.append(data)
                if verbose:
                    logger.debug(
                        f"Captured data at {data.timestamp}: {data.data}")

        def flush_worker():
            last_flush = time.monotonic()
            while should_run:
                now = time.monotonic()
                if now - last_flush >= flush_interval:
                    with data_lock:
                        data_to_flush = list(captured_data)
                        captured_data.clear()
                    if data_to_flush:
                        plugin.save(data_to_flush, end_of_data=False)
                        if verbose:
                            logger.info(
                                f"[Flush] Flushed {len(data_to_flush)} data points.")
                    last_flush = now
                time.sleep(0.1)

        start_ts = get_timestamp()
        capture_thread = threading.Thread(
            target=plugin.start,
            args=(start_ts, get_timestamp, on_data),
            daemon=True
        )
        capture_thread.start()

        flush_thread = threading.Thread(target=flush_worker, daemon=True)
        flush_thread.start()

        if simulate_thread:
            simulate_thread.start()

        if pause_resume:
            pause_after = test_duration / 3
            pause_duration = test_duration / 3
            logger.info(
                f"Will pause after {pause_after:.2f}s for {pause_duration:.2f}s")
            time.sleep(pause_after)
            pause_ts = get_timestamp()
            plugin.pause(pause_ts)
            pause_range = [pause_ts, None]
            logger.info(
                f"Plugin paused at {Colors.YELLOW.value}{pause_ts}{Colors.RESET.value}")
            time.sleep(pause_duration)
            resume_ts = get_timestamp()
            plugin.resume(resume_ts)
            pause_range[1] = resume_ts
            logger.info(
                f"Plugin resumed at {Colors.GREEN.value}{resume_ts}{Colors.RESET.value}")
            time.sleep(max(0.0, test_duration - pause_after - pause_duration))
        else:
            time.sleep(test_duration)

        should_run = False
        stop_ts = get_timestamp()
        plugin.stop(stop_ts)
        if simulate_thread:
            simulate_thread.join(timeout=2)
        flush_thread.join()
        capture_thread.join(timeout=2)

        with data_lock:
            remaining = list(captured_data)
            captured_data.clear()
        if remaining:
            plugin.save(remaining, end_of_data=True)
            if verbose:
                logger.info(
                    f"[Final Flush] Saved {len(remaining)} data points.")

        plugin.unload()
        if output_file.exists():
            logger.info(
                f"{Colors.GREEN.value}Success:{Colors.RESET.value} Output file generated: {Colors.GREY.value}{pretty_path(output_file)}{Colors.RESET.value}")
        else:
            logger.error(
                f"{Colors.RED.value}Error:{Colors.RESET.value} Output file not found: {pretty_path(output_file)}")

        if pause_resume and pause_range:
            with data_lock:
                paused = [d for d in remaining if pause_range[0]
                          <= d.timestamp <= pause_range[1]]
            if paused:
                logger.warning(
                    f"{Colors.YELLOW.value}Plugin sent {len(paused)} data points during pause interval!{Colors.RESET.value}")
            else:
                logger.info(
                    f"{Colors.GREEN.value}Pause check:{Colors.RESET.value} No data sent during pause interval. OK!")

        if temp_dir:
            temp_dir.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Test a MO CapturePlugin using its metadata.json.")
    parser.add_argument("--plugin-dir", type=str, default="./",
                        help="Path to the plugin root folder (or metadata.json file) (default: ./)")
    parser.add_argument("--pause", "-p", action="store_true",
                        help="Simulate pause/resume")
    parser.add_argument("--duration", "-d", type=float, default=3.0,
                        help="Test duration in seconds (default 3.0)")
    parser.add_argument("--flush", "-f", type=float, default=1.0,
                        help="Flush interval in seconds (default 1.0)")
    parser.add_argument("--settings", type=str, default=None,
                        help="Path to settings file (JSON)")
    parser.add_argument("--out", "-o", type=str, default=None, help="Output folder")
    parser.add_argument("--prefix", type=str, default="test_capture",
                        help="Prefix for output file name")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Less verbose output")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable DEBUG log output")
    parser.add_argument("--simulate", "-s", type=str, default=None,
                        help="Entrypoint to a simulation function, e.g. 'mop.examples.sim_mouse:run'")
    parser.add_argument("--coverage", "-c", action="store_true",
                        help="Enable coverage ONLY for the plugin entrypoint file")
    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.ERROR)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    settings = None
    if args.settings:
        with open(args.settings, "r") as f:
            settings = json.load(f)

    cov = None
    plugin_file_for_coverage = None
    if args.coverage:
        temp_tester = CapturePluginTester(args.plugin_dir)
        plugin_file_for_coverage, _ = temp_tester._get_entry_point("plugin")
        plugin_file_for_coverage = str(
            Path(plugin_file_for_coverage).resolve())
        logger.info(
            f"{Colors.CYAN.value}Coverage will be measured ONLY for:{Colors.RESET.value} {pretty_path(Path(plugin_file_for_coverage))}")
        cov = coverage.Coverage(source=None, branch=True, include=[
            plugin_file_for_coverage])
        cov.start()
    tester = CapturePluginTester(args.plugin_dir)
    tester.run_test(
        settings=settings,
        pause_resume=args.pause,
        test_duration=args.duration,
        flush_interval=args.flush,
        output_folder=args.out,
        file_prefix=args.prefix,
        verbose=not args.quiet,
        simulate_entrypoint=args.simulate,
    )

    if cov is not None and plugin_file_for_coverage is not None:
        cov.stop()
        cov.save()
        logger.info(
            f"{Colors.CYAN.value}Coverage data saved{Colors.RESET.value} for the plugin file!")
        logger.info(
            f"To see results, run: {Colors.YELLOW.value}coverage report {Colors.RESET.value}")
        logger.info(
            f"To generate HTML report, run: {Colors.YELLOW.value}coverage html {Colors.RESET.value}")

if __name__ == "__main__":
    main()
