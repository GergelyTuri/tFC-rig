import builtins
import os
from dataclasses import dataclass
from datetime import datetime

from google.colab import drive
from IPython.display import HTML, display

@dataclass
class Notebook:
    """
    Serves as a container for metadata about the Google Colaboratory
    notebook from which an analysis is being conducted (from which an
    instance of the analysis pipeline is being run)
    """

    file_root: str = "/content"
    repo_url: str = "https://github.com/GergelyTuri/tFC-rig.git"
    repo_root: str = "/content/tFC-rig"
    repo_branch: str = "cpr/analysis-pipeline"
    data_root: str = "/gdrive/Shareddrives/Turi_lab/Data/aging_project/"

    def setup(self) -> None:
        self._mount_google_drive()
        self._patch_print_for_timestamped_print()

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
        if str(builtins.print).split(" ")[1] != "tprint":
            builtin_print = builtins.print

            def tprint(*args, **kwargs):
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                builtin_print(f">{t}:", *args, **kwargs)

            builtins.print = tprint

    def _enable_text_wrap_in_colab_output(self) -> None:

        def set_css():
            display(
                HTML(
                    '''
                    <style>
                        pre {
                            white-space: pre-wrap;
                        }
                    </style>
                    '''
                )
            )

        get_ipython().events.register('pre_run_cell', set_css)
