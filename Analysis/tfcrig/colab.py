from dataclasses import dataclass

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
