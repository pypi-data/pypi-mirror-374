# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Iterator

from .base import IBaseETL


class IBaseEtlFromFile(IBaseETL, ABC):
    """
    Base class for an ETL task that need to do something with a
    file retrieved from a source. Like copy the file
    from sFTP to S3...
    """

    def _execute(self, *args, **kwargs) -> int:
        """Process each file from paths"""

        processed_files = 0

        for path in self.get_paths():
            try:
                self.info(f"Processing file in path: {path}...")
                self.process_file(path, *args, **kwargs)
                self.on_success(path)

                self.info("Processed!")
                processed_files += 1

            except Exception as error:
                self.error(f"Error processing the file: {path}. Error: {error}")
                self.on_error(path)

        return processed_files

    @abstractmethod
    def get_paths(self, *args, last_processed: Any = None, **kwargs) -> Iterator[str]:
        """
        It retrieves the file(s) from the source and return an iterator
        with the paths for the files...

        :return: An iterator that contains the file paths.
        """

    def process_file(self, path: str, *args, **kwargs):
        """Doing something with the file"""

    def on_success(self, path: str, **kwargs):
        """Do something after the file is processed successfully, like archiving..."""

    def on_error(self, path: str, **kwargs):
        """Do something after an error is raised while processing the file..."""
