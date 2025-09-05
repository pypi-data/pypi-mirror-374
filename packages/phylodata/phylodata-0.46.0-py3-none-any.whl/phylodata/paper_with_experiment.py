import os
from collections import defaultdict
from pathlib import Path
from typing import Optional

from phylodata.data_types import (
    EditablePaperWithExperiment,
    EvolutionaryModelComponent,
    Experiment,
    File,
    FileType,
    Metadata,
    NonEditablePaperWithExperiment,
    Paper,
    Sample,
    Trees,
    msgspec,
)
from phylodata.loader.preview_env import PREFER_PREVIEW_ENV


class PaperWithExperiment(msgspec.Struct, rename="camel"):
    paper: Paper
    experiment: Experiment
    files: list[File]
    samples: list[Sample]
    trees: Optional[Trees]
    evolutionary_model: list[EvolutionaryModelComponent]
    metadata: Metadata
    local_path: Path

    @classmethod
    def from_partial(
        cls,
        editable: EditablePaperWithExperiment,
        non_editable: NonEditablePaperWithExperiment,
        local_path: Path,
    ):
        return cls(
            paper=Paper.from_partial(editable.paper, non_editable.paper),
            experiment=Experiment.from_partial(
                editable.experiment, non_editable.experiment
            ),
            files=non_editable.files,
            samples=editable.samples,
            trees=non_editable.trees,
            evolutionary_model=non_editable.evolutionary_model,
            metadata=non_editable.metadata,
            local_path=local_path,
        )

    def get_files(
        self,
        prefer_preview: Optional[bool] = None,
    ) -> list[File]:
        """Retrieves all downloaded files of the experiment.
        For every file, either the full or preview version is returned.

        Args:
            prefer_preview:
                If None, prefers a full file but falls back to a preview file if no full file exists.
                If True, prefers and returns a preview file if available.
                If False, only retrieves full files.
                This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
                to true or false.

        Returns:
            A list of File objects containing the experiment data.
        """
        if prefer_preview is None and os.environ.get(PREFER_PREVIEW_ENV) is not None:
            prefer_preview = os.environ.get(PREFER_PREVIEW_ENV) == "true"

        downloaded_files = [file for file in self.files if file.local_path]

        downloaded_file_variants = defaultdict(list[File])
        for file in downloaded_files:
            downloaded_file_variants[self._strip_preview_suffix(file)].append(file)

        result = []
        for variants in downloaded_file_variants.values():
            preview_variant = [file for file in variants if file.is_preview]
            full_variant = [file for file in variants if not file.is_preview]

            if prefer_preview is None:
                # Prefer full, fall back to preview
                if full_variant:
                    result.extend(full_variant)
                elif preview_variant:
                    result.extend(preview_variant)

            elif prefer_preview:
                # Prefer preview, fall back to full
                if preview_variant:
                    result.extend(preview_variant)
                elif full_variant:
                    result.extend(full_variant)

            else:
                # Only full, skip if none exists
                if full_variant:
                    result.extend(full_variant)

        return result

    def _strip_preview_suffix(self, file: File) -> str:
        name = file.name
        extension = name.split(".")[-1]

        if name.endswith(f" (preview).{extension}"):
            return name[: -len(" (preview)") - len(extension) - 1] + "." + extension

        return name

    def get_files_of_type(
        self,
        file_type: FileType,
        prefer_preview: Optional[bool] = None,
    ) -> list[File]:
        """Retrieves all downloaded files of the experiment of a specific type.
        For every file, either the full or preview version is returned.

        Args:
            file_type:
                The FileType to retrieve.
            prefer_preview:
                If None, prefers a full file but falls back to a preview file if no full file exists.
                If True, prefers and returns a preview file if available.
                If False, only retrieves full files.
                This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
                to true or false.

        Returns:
            A list of File objects containing the experiment data.
        """
        return [
            file for file in self.get_files(prefer_preview) if file.type == file_type
        ]

    def get_file(
        self,
        name: str,
        prefer_preview: Optional[bool] = None,
    ) -> Optional[File]:
        """Retrieves a file of a specific name from a PaperWithExperiment object.

        Args:
            name:
                The name of the file to retrieve.
            prefer_preview:
                If None, prefers a full file but falls back to a preview file if no full file exists.
                If True, prefers and returns a preview file if available.
                If False, only retrieves full files.
                This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
                to true or false.

        Returns:
            The first matching File object, or None if no such file exists.
        Raises:
            FileNotFoundError if no matching file is found.
        """
        matching_files = [
            file
            for file in self.get_files(prefer_preview)
            if self._strip_preview_suffix(file) == name
        ]

        if not matching_files:
            raise FileNotFoundError

        return matching_files[0]

    def get_file_of_type(
        self,
        file_type: FileType,
        prefer_preview: Optional[bool] = None,
    ) -> Optional[File]:
        """
        Retrieves a file of a specified type from a PaperWithExperiment object.

        Args:
            file_type:
                The FileType to retrieve.
            prefer_preview:
                If None, prefers a full file but falls back to a preview file if no full file exists.
                If True, prefers and returns a preview file if available.
                If False, always retrieves a full file.
                This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
                to true or false.

        Returns:
            The first matching File object, or None if no such file exists.
        Raises:
            FileNotFoundError if no matching file is found.
        """
        matching_files = self.get_files_of_type(file_type, prefer_preview)

        if not matching_files:
            raise FileNotFoundError

        return matching_files[0]
