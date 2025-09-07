# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from core_mixins.utils import convert_data_type
from core_mixins.utils import remove_attributes
from core_mixins.utils import rename_attributes

from .base import IBaseETL


class IBaseEtlFromRecord(IBaseETL, ABC):
    """
    Base class for an ETL task that need to do ETLs processes over data (records,
    rows) retrieved from different sources like: file, sFTP server, SQS queues, APIs
    or another data source...
    """

    def __init__(
        self,
        name_mapper: Optional[Dict[str, str]] = None,
        type_mapper: Optional[Dict[str, str]] = None,
        max_per_batch: int = 1000,
        attrs_to_remove: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        """
        :param name_mapper: It defines the old and new name for the attributes.
        :param type_mapper: It defines if a casting must be applied to an attribute.
        :param max_per_batch: Maximum number of elements to process per batch.
        :param attrs_to_remove: Attributes to remove from the records.
        """

        super().__init__(**kwargs)

        self.name_mapper = name_mapper or {}
        self.attrs_to_remove = attrs_to_remove or []
        self.type_mapper = type_mapper or {}
        self.max_per_batch = max_per_batch

    def _execute(self, *args, **kwargs) -> int:
        """Process (by applying transformations) each record from the source"""

        batch_number = 1
        count = 0

        for batch in self.retrieve_records(**kwargs):
            self.info(f"Processing batch # {batch_number}...")
            records = []

            for record in batch:
                # Apply transformations required before the base ones...
                self.pre_transformations(record)

                remove_attributes(record, self.attrs_to_remove)
                rename_attributes(record, self.name_mapper)
                convert_data_type(record, self.type_mapper)

                # Apply transformations required after the base ones...
                self.post_transformations(record)

                records.append(record)
                count += 1

            if records:
                self.process_records(records)

            batch_number += 1

        return count

    @abstractmethod
    def retrieve_records(
        self,
        last_processed: Any = None,
        start: Any = None,
        end: Any = None,
        **kwargs,
    ) -> Iterator[List[Dict]]:
        """
        It retrieves records from sources. It's expected to return batches of records
        because in this way we can manage the amount of records to process in each iteration
        and do not exhaust the resources...

        :return: An iterator that contains a list of records.
        """

    def pre_transformations(self, record: Dict) -> None:
        """Transformations applied before built-in ones..."""

    def post_transformations(self, record: Dict) -> None:
        """Transformations applied after built-in ones..."""

    @abstractmethod
    def process_records(self, records: List[Dict], **kwargs):
        """
        It must implement the actions to do with the records after
        transformations like archive in S3, send to an sFTP server, send to
        an SQS queue or a Kinesis stream...
        """
