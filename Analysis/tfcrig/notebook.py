import builtins
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from time import monotonic

try:
    from google.colab import drive, output
except ImportError:
    drive = None
    output = None
from IPython.core.getipython import get_ipython
from IPython.display import HTML, display

# This is replaced in a Notebook with a timestamped print, but it can
# be interesting to have access to it
builtin_print = builtins.print


@dataclass
class Notebook:
    """
    Serves as a container for metadata about the Google Colaboratory
    notebook from which an analysis is being conducted (from which an
    instance of the analysis pipeline is being run). Executing the
    notebook setup should enable other `tfcrig` analysis code to be
    written and executed in an environment-agnostic way. That is, such
    that it does not need to know about Google Drive as the _specific_
    execution environment, enabling the code to be run in other
    contexts.
    """

    # Google Colab
    file_root: str = "/content"

    # GitHub
    repo_url: str = "https://github.com/GergelyTuri/tFC-rig.git"
    repo_root: str = "/content/tFC-rig"
    repo_branch: str = "cpr/analysis-pipeline"

    # Google Drive
    data_root: str = "/gdrive/Shareddrives/Turi_lab/Data/aging_project/"

    # Jupyter Notebook
    max_cell_height: str = 200

    def setup(self) -> None:
        self._mount_google_drive()
        self._patch_print_for_timestamped_print()
        self._configure_timestamped_logging()
        self._enable_text_wrap_in_colab_output()
        self._set_output_height_all_cells()

    def _mount_google_drive(self) -> None:
        """
        Mounts Google Drive to the notebook environment.

        Do we ever need to remount? We can always remount with:

            drive.mount("/gdrive", force_remount=True)

        """
        drive.mount("/gdrive")
        self._check_data_root_exists()

    def _check_data_root_exists(self) -> None:
        """
        Ensures that the provided `data_root` points to a real path.
        Only useful if run after having mounted a Google Drive
        """
        if not os.path.exists(self.data_root):
            raise Exception(
                f"Data folder '{self.data_root}' is not available!!!",
            )

    def _patch_print_for_timestamped_print(self) -> None:
        """
        Overwrites the builtin Python `print` function with one that
        timestamps each printed messages. This is useful in a Jupyter-
        notebook-like environment to confirm when an analysis had last
        been run.
        """

        def tprint(*args, **kwargs):
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            builtin_print(f">{t}:", *args, **kwargs)

        if str(builtins.print).split(" ")[1] != "tprint":
            builtins.print = tprint

    def _enable_text_wrap_in_colab_output(self) -> None:
        """
        Registers a `css` event before the execution of a cell in
        Google Colaboratory, so that text output is wrapped
        """

        def set_css():
            display(
                HTML(
                    """
                    <style>
                        pre {
                            white-space: pre-wrap;
                        }
                    </style>
                    """
                )
            )

        get_ipython().events.register("pre_run_cell", set_css)

    def _configure_timestamped_logging(self) -> None:
        """
        Configures the root `logging` logger to print a timestamp when
        any child logger prints a message
        """

        class TimestampedFormatter(logging.Formatter):
            def format(self, record):
                record.custom_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return super().format(record)

        root_logger = logging.getLogger()
        # Remove all existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        handler = logging.StreamHandler()
        handler.setFormatter(TimestampedFormatter(">%(custom_time)s: %(message)s"))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    def _set_output_height_all_cells(self) -> None:
        """
        Registers an even that executes JavaScript before the execution
        of any cell, to set a max height
        """

        def set_output_height_for_all_cells():
            script = f"""
google.colab.output.setIframeHeight(0, true, {{maxHeight: {self.max_cell_height}}});
            """
            output.eval_js(script)

        get_ipython().events.register("pre_run_cell", set_output_height_for_all_cells)

    def _add_cell_timing(self) -> None:
        """
        To be careful of analysis pipeline execution time, print out
        the time it takes each cell to execute
        """
        class CellTimer:
            def __init__(self):
                self.start_time = None

            def start(self, *args, **kwargs):
                self.start_time = monotonic()

            def stop(self, *args, **kwargs):
                try:
                    delta = round(monotonic() - self.start_time, 2)
                    builtin_print(f"\n⏱️ Execution time: {delta}s")
                except TypeError:
                    # The `stop` will be called when the cell that
                    # defines `CellTimer` is executed, but `start`
                    # was never called, leading to a `TypeError` in
                    # the subtraction. Skip it
                    pass


        timer = CellTimer()

        get_ipython().events.register("pre_run_cell", timer.start)
        get_ipython().events.register("post_run_cell", timer.stop)
