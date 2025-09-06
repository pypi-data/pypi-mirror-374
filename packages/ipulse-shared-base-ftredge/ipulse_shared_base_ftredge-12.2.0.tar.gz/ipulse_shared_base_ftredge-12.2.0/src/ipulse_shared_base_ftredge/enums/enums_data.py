# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import StrEnum, auto
class AutoLower(StrEnum):
    """
    StrEnum contrary to simple Enum is of type `str`, so it can be used as a string.
    StrEnum whose `auto()  # type: ignore` values are lower-case.
    (Identical to StrEnum's own default, but keeps naming symmetrical.)
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()            # StrEnum already does this

class AutoUpper(StrEnum):
    """
    StrEnum contrary to simple Enum is of type `str`, so it can be used as a string.
    StrEnum whose `auto()  # type: ignore` values stay as-is (UPPER_CASE).
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name                    # keep original upper-case


class DataPrimaryCategory(AutoLower):
    HISTORIC = auto()  # type: ignore # Historical raw data, usually accurate and complete
    LIVE=auto()  # type: ignore # Real-time data, not always certain, can have error. Live and Historic can intersect. Live relates to Streaming data or Websockets data..
    ANALYTICS=auto()  # type: ignore # Analytical data and modelling, derived from historical and prediction data. Normally shall be making Human readable sense. vs. Features
    FEATURES=auto()  # type: ignore # Features data, used for training models
    PREDICTIONS=auto()  # type: ignore # Predictive data, based on models and simulations
    ARCHIVES=auto()  # type: ignore # Archived data,usually not used for refernce but for long term storage and compliance.
    SIMULATIONS=auto()  # type: ignore # Simulation data, based on models and simulations
    DIMENSIONS=auto()  # type: ignore # Reference data, used for lookups and validation
    GOVERNANCE=auto()  # type: ignore # # control-plane / governance / ops
    LOGS=auto()  # type: ignore # Log data, used for logging and monitoring
    MULTIPLE = auto()  # type: ignore # Multiple categories, used for data that can belong to multiple categories
    UNKNOWN = auto()  # type: ignore # Used when the primary category is not specified or unknown

class Subdomain(AutoLower): # EXCEPT FOR DATASETS , these are all GOVERNANCE DataPrimaryCategory
    DATASETS = auto()  # type: ignore
    CONTROLS = auto()  # type: ignore  # Includes control plane, reference data , catalogs etc. 
    MONITORING = auto()  # type: ignore  # Log data, used for logging and monitoring
    UNKNOWN = auto()  # type: ignore

class DataStructureLevel(AutoLower):
    STRUCTURED = auto()     # type: ignore   # e.g., table with schema
    SEMI_STRUCTURED = auto()  # type: ignore # JSON, YAML, etc. 
    UNSTRUCTURED = auto()    # type: ignore  # free text, raw image, PDF

class DataModality(AutoLower):
    """Types of input data for models."""
    TEXT = auto()  # type: ignore
    SCHEMA = auto()  # type: ignore
    TABULAR = auto()  # type: ignore  # rows/cols (can hold numeric + categorical)
    NUMERICAL = auto()  # type: ignore
    CATEGORICAL = auto()  # type: ignore
    IMAGE = auto()  # type: ignore
    AUDIO = auto()  # type: ignore
    VIDEO = auto()  # type: ignore
    GRAPH = auto()  # type: ignore
    GEOSPATIAL = auto()  # type: ignore
    OMICS = auto()  # type: ignore  # e.g., genomics, proteomics
    MULTIMODAL = auto()  # type: ignore
    UNKNOWN = auto()  # type: ignore  # Used when the data modality is not specified or unknown

class ModalityContentDynamics(AutoLower):
    """Dynamics of data modality."""
    STATIC = auto()  # type: ignore  # Static data, does not change over time
    STATIC_VERSIONED = auto()  # type: ignore  # Versioned data, changes over time but retains history
    SEQUENCE= auto()  # type: ignore  # Regular sequence data, e.g., time series with fixed intervals
    TIMESERIES= auto()  # type: ignore  # Regular time series data, e.g., daily stock prices
    MIXED = auto()  # type: ignore  # Mixed data, e.g., text + images
    UNKNOWN = auto()  # type: ignore  # Used when the modality dynamics is not specified or unknown


class DatasetLineage(AutoLower):
    """Dataset lineage information."""
    # EXTERNAL DATA
    PRIMARY_SUPPLIER = auto()  # type: ignore
    SECONDARY_SUPPLIER = auto()  # type: ignore

    # INTERNAL DATA
    SOURCE_OF_TRUTH = auto()  # type: ignore
    EXACT_COPY = auto()  # type: ignore
    PACKAGED_COPY = auto()  # type: ignore
    ANALYTICS_DERIVATIVE = auto()  # type: ignore
    FEATURES_DERIVATIVE = auto()  # type: ignore
    INTERMEDIARY_DERIVATIVE = auto()  # type: ignore
    MIXED_COPIES = auto()  # type: ignore
    MIXED_COPIES_PACKAGED = auto()  # type: ignore #usually means subsampled or aggregated data
    MIXED_ANALYTICS = auto()  # type: ignore
    MIXED_FEATURES = auto()  # type: ignore
    BACKUP = auto()  # type: ignore
    TEMPORARY = auto()  # type: ignore
    UNKNOWN = auto()  # type: ignore


class DatasetScope(AutoLower):
    """Types of Dataset scope."""

    FULL_DATASET = auto()  # type: ignore
    LATEST_RECORD = auto()  # type: ignore #IF SINGLE LATEST RECORD
    INCREMENTAL_DATASET = auto()  # type: ignore #IF INCREMENTAL LATEST RECORDS
    BACKFILLING_DATASET = auto()  # type: ignore
    PARTIAL_DATASET = auto()  # type: ignore
    SUBSAMPLED_DATASET = auto()  # type: ignore
    FILTERED_DATASET = auto()  # type: ignore

    TRAINING_DATASET = auto()  # type: ignore
    VALIDATION_DATASET = auto()  # type: ignore
    TEST_DATASET = auto()  # type: ignore
    TRAINING_AND_VALIDATION_DATASET = auto()  # type: ignore
    CUSTOM_RANGE_DATASET = auto()  # type: ignore
    CROSS_VALIDATION_FOLD = auto()  # type: ignore
    HOLDOUT_DATASET = auto()  # type: ignore

    MIXED_DATASETS = auto()  # type: ignore



class DataSplitStrategy(AutoLower):
    """Data splitting strategies."""
    RANDOM_SPLIT = auto()  # type: ignore
    TIME_SERIES_SPLIT = auto()  # type: ignore
    GROUP_SPLIT = auto()  # type: ignore
    GEOGRAPHICAL_SPLIT = auto()  # type: ignore
    TEMPORAL_SPLIT = auto()  # type: ignore
    CROSS_VALIDATION = auto()  # type: ignore
    LEAVE_ONE_OUT = auto()  # type: ignore
    LEAVE_P_OUT = auto()  # type: ignore
    HOLDOUT = auto()  # type: ignore
    BOOTSTRAP = auto()  # type: ignore


class DatasetAttribute(AutoLower):
    RECENT_DATE = auto()  # type: ignore
    RECENT_TIMESTAMP = auto()  # type: ignore
    RECENT_DATETIME = auto()  # type: ignore
    OLDEST_DATE = auto()  # type: ignore
    OLDEST_TIMESTAMP = auto()  # type: ignore
    OLDEST_DATETIME = auto()  # type: ignore
    MAX_VALUE = auto()  # type: ignore
    MIN_VALUE = auto()  # type: ignore
    TOTAL_COUNT = auto()  # type: ignore
    TOTAL_SUM = auto()  # type: ignore
    MEAN = auto()  # type: ignore
    MEDIAN = auto()  # type: ignore
    MODE = auto()  # type: ignore
    STANDARD_DEVIATION = auto()  # type: ignore
    NB_FIELDS_PER_RECORDS = auto()  # type: ignore


