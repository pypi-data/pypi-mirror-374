from datetime import datetime
from math import exp
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import msgspec
from tqdm import tqdm

from phylodata.data_types import (
    EditablePaperWithExperiment,
    FileType,
    NonEditablePaperWithExperiment,
)
from phylodata.loader.download_file import download_file
from phylodata.loader.preview_env import PREFER_PREVIEW_ENV
from phylodata.paper_with_experiment import PaperWithExperiment

EDITABLE_METADATA_FILE = "editable_phylodata_metadata.json"
NON_EDITABLE_METADATA_FILE = "non_editable_phylodata_metadata"


@dataclass
class ExperimentToLoad:
    id: str
    version: Optional[int] = None


def load_experiment(
    experiment_id: str,
    version: Optional[int] = None,
    directory: Optional[str | Path] = None,
    download_only_preview: Optional[bool] = None,
    files_to_download: Optional[list[str | FileType]] = None,
    force_download: bool = False,
    citations_file: Optional[str | Path] = None,
) -> PaperWithExperiment:
    """Loads a PhyloData experiment.

    Args:
        experiment_id:
            The human-readable ID of the experiment to load (e.g. felsenstein-1992-estimating).
        version:
            The version of the experiment to load. Defaults to latest.
        directory:
            Path where the experiment files should be stored. If not specified, the directory
            data will be used.
        download_only_preview:
            Whether to only download preview files. This is useful for testing environments.
            This can also be controlled by setting the environment variable
            PHYLODATA_PREFER_PREVIEW to true or false. Defaults to False.
        files_to_download:
            Optional list to restrict the filenames or FileTypes downloaded. Defaults to all.
        force_download:
            Whether to re-download files even if they exist locally. Defaults to False.
        citations_file:
            Path to a file where the citations of the experiments should be stored.

    Returns:
        A PaperWithExperiment object containing the experiment data.
    """
    return load_experiments(
        [ExperimentToLoad(experiment_id, version)],
        directory,
        download_only_preview,
        files_to_download,
        force_download,
        citations_file,
    )[0]


def load_experiments(
    experiments_to_load: list[ExperimentToLoad | str],
    directory: Optional[str | Path] = None,
    download_only_preview: Optional[bool] = None,
    files_to_download: Optional[list[FileType]] = None,
    force_download: bool = False,
    citations_file: Optional[str | Path] = None,
) -> list[PaperWithExperiment]:
    """Loads multiple PhyloData experiments.

    Args:
        experiments_to_load:
            List of experiment IDs or ExperimentToLoad objects specifying which experiments
            to load. If only the ID strings are given, the latest version will be downloaded.
        directory:
            Path where the experiment files should be stored. If not specified, the directory
            data will be used.
        download_only_preview:
            Whether to only download preview files. This is useful for testing environments.
            This can also be controlled by setting the environment variable
            PHYLODATA_PREFER_PREVIEW to true or false. Defaults to False.
        files_to_download:
                Optional list to restrict the FileTypes downloaded. Defaults to all.
        force_download:
            Whether to re-download files even if they exist locally. Defaults to False.
        citations_file:
            Path to a file where the citations of the experiments should be stored.

    Returns:
        A list of PaperWithExperiment objects containing the loaded experiment data.
    """
    if not directory:
        directory = Path("data")
    if isinstance(directory, str):
        directory = Path(directory)

    if download_only_preview is None:
        download_only_preview = os.environ.get(PREFER_PREVIEW_ENV) == "true"

    experiments = []

    for experiment_to_load in tqdm(experiments_to_load):
        if isinstance(experiment_to_load, str):
            experiment_to_load = ExperimentToLoad(experiment_to_load)

        experiment_directory = directory / experiment_to_load.id

        experiment = _download_experiment(
            experiment_to_load.id,
            experiment_directory,
            experiment_to_load.version,
            download_only_preview,
            files_to_download,
            force_download,
        )
        experiments.append(experiment)

    _create_citations_file(experiments, citations_file or directory / "citations.bib")

    return experiments


def _download_experiment(
    experiment_id: str,
    directory: Path,
    version: Optional[int] = None,
    download_only_preview: bool = False,
    files_to_download: Optional[list[str | FileType]] = None,
    force_download: bool = False,
):
    directory.mkdir(parents=True, exist_ok=True)

    # download and load metadata files

    editable_metadata_file = download_file(
        directory,
        experiment_id,
        EDITABLE_METADATA_FILE,
        version,
        force_download,
    )
    with open(editable_metadata_file, "rb") as handle:
        editable_metadata = msgspec.json.decode(
            handle.read(), type=EditablePaperWithExperiment
        )

    non_editable_metadata_file = download_file(
        directory,
        experiment_id,
        NON_EDITABLE_METADATA_FILE,
        version,
        force_download,
    )
    with open(non_editable_metadata_file, "rb") as handle:
        non_editable_metadata = msgspec.json.decode(
            handle.read(), type=NonEditablePaperWithExperiment
        )

    # merge metadata

    metadata = PaperWithExperiment.from_partial(
        editable_metadata, non_editable_metadata, directory
    )

    # download remaining files if needed

    for file in non_editable_metadata.files:
        if (
            files_to_download
            and file.name not in files_to_download
            and file.type not in files_to_download
        ):
            continue

        if file.type == FileType.PHYLO_DATA_EXPERIMENT:
            continue

        if (
            download_only_preview
            and file.type in [FileType.BEAST2_POSTERIOR_LOGS, FileType.POSTERIOR_TREES]
            and not file.is_preview
        ):
            continue

        file.local_path = download_file(
            directory, experiment_id, file.name, version, force_download
        )

    return metadata


def load_experiment_from_local_dir(directory: str | Path) -> PaperWithExperiment:
    """Loads a PhyloData experiment from a local directory.

    Args:
        directory:
            Path to the directory containing the experiment files.

    Returns:
        A PaperWithExperiment object containing the experiment data.
    """
    if isinstance(directory, str):
        directory = Path(directory)

    # load metadata files

    with open(directory / EDITABLE_METADATA_FILE, "rb") as handle:
        editable_metadata = msgspec.json.decode(
            handle.read(), type=EditablePaperWithExperiment
        )

    with open(directory / NON_EDITABLE_METADATA_FILE, "rb") as handle:
        non_editable_metadata = msgspec.json.decode(
            handle.read(), type=NonEditablePaperWithExperiment
        )

    # merge metadata

    experiment = PaperWithExperiment.from_partial(
        editable_metadata, non_editable_metadata, directory
    )
    return experiment


def _create_citations_file(
    experiments: list[PaperWithExperiment], citations_file: Path
):
    year = datetime.now().year

    with open(citations_file, "w") as handle:
        handle.write(f"""@comment{{
    Automatically generated by PhyloData.
}}

@online{{phylodata{year},
    title     = {{PhyloData}},
    author    = {{Tobia Simon Ochsner}},
    year      = {year},
    url       = {{https://phylodata.com}},
}}""")

        for experiment in experiments:
            handle.write(f"\n\n{experiment.paper.bibtex}")
