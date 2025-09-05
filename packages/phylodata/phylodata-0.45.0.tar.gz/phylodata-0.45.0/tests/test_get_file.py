import datetime
import os
from pathlib import Path
from unittest import mock

from pytest import fixture

from phylodata.data_types import (
    Experiment,
    ExperimentType,
    File,
    FileType,
    Metadata,
    Paper,
)
import pytest
from phylodata.loader.preview_env import PREFER_PREVIEW_ENV
from phylodata.paper_with_experiment import PaperWithExperiment


@fixture()
def set_preview_env_var_to_true(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            PREFER_PREVIEW_ENV: "true",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


@fixture()
def set_preview_env_var_to_false(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            PREFER_PREVIEW_ENV: "false",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


@fixture
def experiment() -> PaperWithExperiment:
    return PaperWithExperiment(
        files=[],
        paper=Paper(
            doi="",
            title="",
            year=2018,
            authors=[],
            abstract="",
            bibtex="",
        ),
        experiment=Experiment(
            type=ExperimentType.BEAST2_Experiment,
            human_readable_id="",
            origin="",
            upload_date=datetime.date.today(),
            version=0,
            title="",
            description="",
        ),
        samples=[],
        evolutionary_model=[],
        trees=None,
        metadata=Metadata(evo_data_pipeline_version=""),
        local_path=Path(),
    )


def test_single_file_is_found(experiment: PaperWithExperiment):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path(),
        ),
    ]

    config = experiment.get_file("beast2.xml")
    assert config
    assert config.name == "beast2.xml"


def test_missing_file_raises_error(experiment: PaperWithExperiment):
    experiment.files = []
    with pytest.raises(FileNotFoundError):
        experiment.get_file("beast2.xml")


def test_full_file_is_preferred_if_nothing_specified(experiment: PaperWithExperiment):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2.xml"),
        ),
        File(
            name="beast2 (preview).xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2 (preview).xml"),
            is_preview=True,
        ),
    ]

    config = experiment.get_file("beast2.xml")
    assert config
    assert config.name == "beast2.xml"


def test_full_file_is_preferred_if_preview_is_false(
    experiment: PaperWithExperiment,
):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2.xml"),
        ),
        File(
            name="beast2 (preview).xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2 (preview).xml"),
            is_preview=True,
        ),
    ]

    config = experiment.get_file("beast2.xml", prefer_preview=False)
    assert config
    assert config.name == "beast2.xml"


def test_preview_file_is_preferred_if_preview_is_true(
    experiment: PaperWithExperiment,
):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2.xml"),
        ),
        File(
            name="beast2 (preview).xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2 (preview).xml"),
            is_preview=True,
        ),
    ]

    config = experiment.get_file("beast2.xml", prefer_preview=True)
    assert config
    assert config.name == "beast2 (preview).xml"


def test_full_file_is_preferred_if_preview_env_is_false(
    experiment: PaperWithExperiment, set_preview_env_var_to_false
):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2.xml"),
        ),
        File(
            name="beast2 (preview).xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2 (preview).xml"),
            is_preview=True,
        ),
    ]

    config = experiment.get_file("beast2.xml")
    assert config
    assert config.name == "beast2.xml"


def test_preview_file_is_preferred_if_preview_env_is_true(
    experiment: PaperWithExperiment, set_preview_env_var_to_true
):
    experiment.files = [
        File(
            name="beast2.xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2.xml"),
        ),
        File(
            name="beast2 (preview).xml",
            type=FileType.BEAST2_CONFIGURATION,
            size_bytes=0,
            md5="",
            local_path=Path("beast2 (preview).xml"),
            is_preview=True,
        ),
    ]

    config = experiment.get_file("beast2.xml")
    assert config
    assert config.name == "beast2 (preview).xml"
