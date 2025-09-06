# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import StrEnum, auto

# ──────────────────────────────────────────────────────────────────────────────
# Base enum classes following the established patterns
# ──────────────────────────────────────────────────────────────────────────────

class AutoLower(StrEnum):
    """
    StrEnum whose `auto()  # type: ignore` values are lower-case.
    Used for most AI core enums that need string representation.
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

class AutoUpper(StrEnum):
    """
    StrEnum whose `auto()  # type: ignore` values stay as-is (UPPER_CASE).
    Used for status and constant-like enums.
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

# ──────────────────────────────────────────────────────────────────────────────
# Learning Paradigms (Industry Standard)
# ──────────────────────────────────────────────────────────────────────────────

class AILearningParadigm(AutoLower):
    """AI learning paradigm classifications (industry standard)."""
    SUPERVISED = auto()  # type: ignore
    UNSUPERVISED = auto()  # type: ignore
    SEMI_SUPERVISED = auto()  # type: ignore
    REINFORCEMENT = auto()  # type: ignore
    TRANSFER_LEARNING = auto()  # type: ignore
    ACTIVE_LEARNING = auto()  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# Model Families (Industry Standard - replaces MLGenus)
# ──────────────────────────────────────────────────────────────────────────────

class AIArchitectureFamily(AutoLower):
    """High-level AI model families (industry standard)."""
    # Supervised Learning Categories
    REGRESSION = auto()  # type: ignore
    CLASSIFICATION = auto()  # type: ignore
    TIME_SERIES_FORECASTING = auto()  # type: ignore
    
    # Unsupervised Learning Categories
    CLUSTERING = auto()  # type: ignore
    DIMENSIONALITY_REDUCTION = auto()  # type: ignore
    ANOMALY_DETECTION = auto()  # type: ignore
    
    # Neural Network Categories  
    DEEP_LEARNING = auto()  # type: ignore
    COMPUTER_VISION = auto()  # type: ignore
    NATURAL_LANGUAGE_PROCESSING = auto()  # type: ignore
    
    # Advanced Categories
    ENSEMBLE = auto()  # type: ignore
    GENERATIVE_AI = auto()  # type: ignore
    FOUNDATION_MODEL = auto()  # type: ignore
    MULTIMODAL = auto()  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# Algorithm Types (Industry Standard - replaces "Breed")
# ──────────────────────────────────────────────────────────────────────────────

class RegressionAlgorithm(AutoLower):
    """Regression algorithms (traditional and neural)."""
    # Traditional Algorithms
    LINEAR_REGRESSION = auto()  # type: ignore
    POLYNOMIAL_REGRESSION = auto()  # type: ignore
    RIDGE_REGRESSION = auto()  # type: ignore
    LASSO_REGRESSION = auto()  # type: ignore
    ELASTIC_NET_REGRESSION = auto()  # type: ignore
    DECISION_TREE_REGRESSION = auto()  # type: ignore
    RANDOM_FOREST_REGRESSION = auto()  # type: ignore
    GRADIENT_BOOSTING_REGRESSION = auto()  # type: ignore
    XGBOOST_REGRESSION = auto()  # type: ignore
    LIGHTGBM_REGRESSION = auto()  # type: ignore
    CATBOOST_REGRESSION = auto()  # type: ignore
    SUPPORT_VECTOR_REGRESSION = auto()  # type: ignore
    
    # Neural Network Algorithms
    MULTI_LAYER_PERCEPTRON_REGRESSION = auto()  # type: ignore
    DEEP_NEURAL_NETWORK_REGRESSION = auto()  # type: ignore
    CONVOLUTIONAL_NEURAL_NETWORK_REGRESSION = auto()  # type: ignore
    RECURRENT_NEURAL_NETWORK_REGRESSION = auto()  # type: ignore
    LONG_SHORT_TERM_MEMORY_REGRESSION = auto()  # type: ignore
    TRANSFORMER_REGRESSION = auto()  # type: ignore

class ClassificationAlgorithm(AutoLower):
    """Classification algorithms (traditional and neural)."""
    # Traditional Algorithms
    LOGISTIC_REGRESSION_CLASSIFICATION = auto()  # type: ignore
    NAIVE_BAYES_CLASSIFICATION = auto()  # type: ignore
    K_NEAREST_NEIGHBORS_CLASSIFICATION = auto()  # type: ignore
    DECISION_TREES_CLASSIFICATION = auto()  # type: ignore
    RANDOM_FOREST_CLASSIFICATION = auto()  # type: ignore
    GRADIENT_BOOSTING_CLASSIFICATION = auto()  # type: ignore
    XGBOOST_CLASSIFICATION = auto()  # type: ignore
    LIGHTGBM_CLASSIFICATION = auto()  # type: ignore
    CATBOOST_CLASSIFICATION = auto()  # type: ignore
    SUPPORT_VECTOR_MACHINE_CLASSIFICATION = auto()  # type: ignore

    # Neural Network Algorithms
    MULTI_LAYER_PERCEPTRON_CLASSIFICATION = auto()  # type: ignore
    CONVOLUTIONAL_NEURAL_NETWORK_CLASSIFICATION = auto()  # type: ignore
    RECURRENT_NEURAL_NETWORK_CLASSIFICATION = auto()  # type: ignore
    TRANSFORMER_CLASSIFICATION = auto()  # type: ignore
    BERT_CLASSIFICATION = auto()  # type: ignore
    VISION_TRANSFORMER_CLASSIFICATION = auto()  # type: ignore

class TimeSeriesAlgorithm(AutoLower):
    """Time series specific algorithms."""
    # Statistical Models
    AUTOREGRESSION_TIME_SERIES = auto()  # type: ignore
    ARIMA_TIME_SERIES = auto()  # type: ignore
    SARIMA_TIME_SERIES = auto()  # type: ignore
    EXPONENTIAL_SMOOTHING_TIME_SERIES = auto()  # type: ignore
    PROPHET_TIME_SERIES = auto()  # type: ignore

    # Machine Learning Models
    LSTM_TIME_SERIES = auto()  # type: ignore
    GRU_TIME_SERIES = auto()  # type: ignore
    TRANSFORMER_TIME_SERIES = auto()  # type: ignore
    TEMPORAL_CONVOLUTIONAL_NETWORK = auto()  # type: ignore
    N_BEATS = auto()  # type: ignore

class ClusteringAlgorithm(AutoLower):
    """Clustering algorithm types."""
    K_MEANS_CLUSTERING = auto()  # type: ignore
    HIERARCHICAL_CLUSTERING = auto()  # type: ignore
    DBSCAN_CLUSTERING = auto()  # type: ignore
    GAUSSIAN_MIXTURE_CLUSTERING = auto()  # type: ignore
    SPECTRAL_CLUSTERING = auto()  # type: ignore

class DimensionalityReductionAlgorithm(AutoLower):
    """Dimensionality reduction algorithm types."""
    PRINCIPAL_COMPONENT_ANALYSIS = auto()  # type: ignore
    T_SNE = auto()  # type: ignore
    UMAP = auto()  # type: ignore
    LINEAR_DISCRIMINANT_ANALYSIS = auto()  # type: ignore

class AnomalyDetectionAlgorithm(AutoLower):
    """Anomaly detection algorithm types."""
    ISOLATION_FOREST_ANOMALY_DETECTION = auto()  # type: ignore
    ONE_CLASS_SVM_ANOMALY_DETECTION = auto()  # type: ignore
    LOCAL_OUTLIER_FACTOR_ANOMALY_DETECTION = auto()  # type: ignore
    AUTOENCODER_ANOMALY_DETECTION = auto()  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# Training and Update
# ──────────────────────────────────────────────────────────────────────────────


class AIModelUpdateType(AutoLower):
    """Model training and retraining strategies (compute-intensive learning)."""
    # Initial Training Strategies
    INITIAL_TRAINING = auto()  # type: ignore
    # Complete Retraining Strategies
    COMPLETE_RETRAINING = auto()  # type: ignore
    # Incremental/Continuous Training (with backpropagation/optimization)
    INCREMENTAL_TRAINING = auto()  # type: ignore
    ONLINE_LEARNING = auto()  # type: ignore  # real time learning from streaming data
    
    # Neural Network Training Approaches
    STATEFUL_MODEL_STATE_UPDATE = auto()  # type: ignore

    # Transfer and Fine-tuning (compute-intensive)
    TRANSFER_LEARNING = auto()  # type: ignore
    FINE_TUNING = auto()  # type: ignore
    
    # Advanced Strategies
    ENSEMBLE_RETRAINING = auto()  # type: ignore
    A_B_TESTING_RETRAINING = auto()  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# Model Performance & Metrics
# ──────────────────────────────────────────────────────────────────────────────

class RegressionMetric(AutoLower):
    """Regression performance metrics."""
    MEAN_ABSOLUTE_ERROR = auto()  # type: ignore
    MEAN_SQUARED_ERROR = auto()  # type: ignore
    ROOT_MEAN_SQUARED_ERROR = auto()  # type: ignore
    MEAN_ABSOLUTE_PERCENTAGE_ERROR = auto()  # type: ignore
    SYMMETRIC_MEAN_ABSOLUTE_PERCENTAGE_ERROR = auto()  # type: ignore
    R_SQUARED = auto()  # type: ignore
    ADJUSTED_R_SQUARED = auto()  # type: ignore
    EXPLAINED_VARIANCE = auto()  # type: ignore
    MAX_ERROR = auto()  # type: ignore
    MEDIAN_ABSOLUTE_ERROR = auto()  # type: ignore
    HUBER_LOSS = auto()  # type: ignore
    LOG_COSH_LOSS = auto()  # type: ignore
    QUANTILE_LOSS = auto()  # type: ignore
    HIT_RATE = auto()  # type: ignore
    DIRECTIONAL_ACCURACY = auto()  # type: ignore

class TimeSeriesMetric(AutoLower):
    """Time series specific metrics."""
    MEAN_ABSOLUTE_SCALED_ERROR = auto()  # type: ignore
    SYMMETRIC_MEAN_ABSOLUTE_PERCENTAGE_ERROR = auto()  # type: ignore
    MEAN_ABSOLUTE_RANGE_NORMALIZED_ERROR = auto()  # type: ignore
    NORMALIZED_ROOT_MEAN_SQUARED_ERROR = auto()  # type: ignore
    DIRECTIONAL_ACCURACY = auto()  # type: ignore
    HIT_RATE = auto()  # type: ignore
    CUMULATIVE_GAIN = auto()  # type: ignore
    MAXIMUM_DRAWDOWN = auto()  # type: ignore
    SHARPE_RATIO = auto()  # type: ignore
    SORTINO_RATIO = auto()  # type: ignore
    CALMAR_RATIO = auto()  # type: ignore
    VALUE_AT_RISK = auto()  # type: ignore
    CONDITIONAL_VALUE_AT_RISK = auto()  # type: ignore

class ClassificationMetric(AutoLower):
    """Classification performance metrics."""
    ACCURACY = auto()  # type: ignore
    PRECISION = auto()  # type: ignore
    RECALL = auto()  # type: ignore
    F1_SCORE = auto()  # type: ignore
    F2_SCORE = auto()  # type: ignore
    FBETA_SCORE = auto()  # type: ignore
    ROC_AUC = auto()  # type: ignore
    PR_AUC = auto()  # type: ignore
    LOG_LOSS = auto()  # type: ignore
    BRIER_SCORE = auto()  # type: ignore
    MATTHEWS_CORRELATION = auto()  # type: ignore
    BALANCED_ACCURACY = auto()  # type: ignore
    COHEN_KAPPA = auto()  # type: ignore
    HAMMING_LOSS = auto()  # type: ignore
    JACCARD_SCORE = auto()  # type: ignore
    ZERO_ONE_LOSS = auto()  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# Model Input/Output Types
# ──────────────────────────────────────────────────────────────────────────────

class ModelOutputType(AutoLower):
    """Types of output data from models."""
    REGRESSION_VALUE = auto()  # type: ignore
    CLASSIFICATION_LABEL = auto()  # type: ignore
    CLASSIFICATION_PROBABILITY = auto()  # type: ignore
    MULTI_CLASS_PROBABILITIES = auto()  # type: ignore
    MULTI_LABEL_PREDICTIONS = auto()  # type: ignore
    SEQUENCE_PREDICTION = auto()  # type: ignore
    TIME_SERIES_FORECAST = auto()  # type: ignore
    CLUSTERING_ASSIGNMENT = auto()  # type: ignore
    ANOMALY_SCORE = auto()  # type: ignore
    RANKING = auto()  # type: ignore
    EMBEDDING = auto()  # type: ignore
    FEATURE_IMPORTANCE = auto()  # type: ignore
    UNCERTAINTY_ESTIMATE = auto()  # type: ignore
    EXPLANATION = auto()  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# Model Architectures & Frameworks
# ──────────────────────────────────────────────────────────────────────────────

class AIFramework(AutoLower):
    """Machine learning frameworks."""
    SCIKIT_LEARN = auto()  # type: ignore
    TENSORFLOW = auto()  # type: ignore
    GENAI_PYTHON_SDK = auto()  # type: ignore
    BIGQUERY_AI = auto()  # type: ignore
    BIGQUERY_ML = auto()  # type: ignore
    PYTORCH = auto()  # type: ignore
    KERAS = auto()  # type: ignore
    XGBOOST = auto()  # type: ignore
    LIGHTGBM = auto()  # type: ignore
    CATBOOST = auto()  # type: ignore
    STATSMODELS = auto()  # type: ignore
    PROPHET = auto()  # type: ignore
    NEURALPROPHET = auto()  # type: ignore
    DARTS = auto()  # type: ignore
    SKTIME = auto()  # type: ignore
    TSFRESH = auto()  # type: ignore
    PYOD = auto()  # type: ignore
    HUGGING_FACE = auto()  # type: ignore
    OPTUNA = auto()  # type: ignore
    HYPEROPT = auto()  # type: ignore
    RAY_TUNE = auto()  # type: ignore
    MLFLOW = auto()  # type: ignore
    WANDB = auto()  # type: ignore
    CUSTOM = auto()  # type: ignore
