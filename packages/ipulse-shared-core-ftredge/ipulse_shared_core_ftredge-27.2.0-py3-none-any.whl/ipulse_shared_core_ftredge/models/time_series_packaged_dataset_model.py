# pylint: disable=missing-module-docstring, missing-class-docstring
from typing import List, Optional, TypeVar, Generic
from datetime import datetime
from pydantic import Field, BaseModel
from ipulse_shared_core_ftredge.models.base_data_model import BaseDataModel
from ipulse_shared_base_ftredge.enums import DatasetLineage, DatasetScope

# Generic type for the records within the dataset
RecordsSamplingType = TypeVar('RecordsSamplingType', bound=BaseModel)

class TimeSeriesPackagedDatasetModel(BaseDataModel, Generic[RecordsSamplingType]):
    """
    An intermediary model for time series datasets that holds aggregated records.
    It provides a generic way to handle different types of time series records.
    """
    dataset_id: str = Field(..., description="The unique identifier for this dataset, often matching the asset ID.")

    dataset_modality: str = Field(..., description="The modality of the dataset, e.g., 'time_series', 'cross_sectional'.")
    dataset_lineage: DatasetLineage = Field(..., description="The lineage of the data, indicating its origin and transformations.")
    dataset_partition: DatasetScope = Field(..., description="The partition type of the dataset, e.g., full, subsampled.")

    # Generic lists for different temporal buckets of records
    max_bulk_records: List[RecordsSamplingType] = Field(default_factory=list)
    latest_bulk_records: Optional[List[RecordsSamplingType]] = Field(default_factory=list)
    latest_intraday_records: Optional[List[RecordsSamplingType]] = Field(default_factory=list)

    # Metadata fields
    max_bulk_updated_at: Optional[datetime] = None
    max_bulk_updated_by: Optional[str] = None
    max_bulk_recent_date_id: Optional[datetime] = None
    max_bulk_oldest_date_id: Optional[datetime] = None
    latest_bulk_recent_date_id: Optional[datetime] = None
    latest_bulk_oldest_date_id: Optional[datetime] = None
    latest_record_updated_at: Optional[datetime] = None
    latest_record_updated_by: Optional[str] = None
    latest_record_change_id: Optional[str] = None
    latest_intraday_bulk_updated_at: Optional[datetime] = None
    latest_intraday_bulk_updated_by: Optional[str] = None

    @property
    def id(self) -> str:
        """Return dataset_id for backward compatibility and consistency."""
        return self.dataset_id
