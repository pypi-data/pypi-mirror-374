# Generic imports
import argparse  # Commandline arguments
import logging
import os  # Path construction
from pickle import load, dump

import numpy as np  # Used for unique() function and to create zero 2d array.
import pandas as pd  # Standard format for the training and testing data.
from imblearn.over_sampling import SMOTEN, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from joblib import parallel_backend
from sklearn.feature_selection import VarianceThreshold

from migenpro.logger_utils import get_logger

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.INFO)



def to_java_output_folder(input_folder):
    """
    Converts the input folder path to the corresponding Java output folder path.
    """
    x = input_folder.split(os.sep)
    outputIndex = x.index("output")
    y = x[: outputIndex + 1]
    return os.sep.join(y)

def ordinalizer(df_features: pd.DataFrame):
    # Converts the string values inside a pandas dataframe to ordinal values.
    def name_changer(variable_names_inner):
        # Creates a dictionary to map variable names to ordinal values
        variable_dict = {name: index for index, name in enumerate(variable_names_inner)}
        # Converts an array with variable strings into an ordinalized array using the mapping
        return df_features.map(lambda value: variable_dict.get(value))

    # Get unique values from the dataframe
    variable_names = sorted(df_features.stack().unique())
    # Convert the values in the dataframe to ordinal values
    ordinal_values = name_changer(variable_names)

    return ordinal_values, variable_names

def filter_features_by_variance(observed_values: pd.DataFrame, min_variance: float):
    """
    Filter features based on their variance.

    args:
        observed_values: The input DataFrame containing the features.
        min_variance: The minimum variance a feature must have to be included.

    returns:
        A DataFrame with features that have at least the specified variance.
    """
    selector = VarianceThreshold(threshold=min_variance)
    selector.fit(observed_values)

    # Get the indices of the columns that meet the variance threshold
    selected_columns = observed_values.columns[selector.get_support()]
    observed_values_filtered = observed_values[selected_columns]

    return observed_values_filtered

def save_model(model, path: str):
    # Save sklearn model.
    with open(path, "wb") as f:
        dump(model, f)


def load_model(model_path):
    # Load sklearn model.
    with open(model_path, "rb") as f:
        return load(f)


def feature_conversion(clf, feature_data):
    """
    Convert the feature columns in a dataset to match the feature names in a trained model, and handle missing features.

    This function ensures that the feature data passed to a classifier (clf) only contains the features that were used 
    during the training of the model. If any features in the dataset are not present in the model, they will be removed. 
    Additionally, if the model expects features that are missing from the dataset, these features will be added with 
    values set to zero. This is useful for aligning datasets with models that may have different or incomplete feature sets.

    Parameters
    ----------
    clf : scikitlearn ml model object
        The trained classifier or model object, which must have the attribute `feature_names_in_`, a list of feature names 
        used during training.
    
    feature_data : pandas.DataFrame
        The input dataframe containing feature data for prediction. The column names in this dataframe may not fully 
        match the model's expected features.

    Returns
    -------
    output_df : pandas.DataFrame
        A modified dataframe where:
        - Columns that do not match the model's expected features are removed.
        - Missing features expected by the model are added with values set to zero.
        The returned dataframe will match the feature set expected by the model.
    
    Raises
    ------
    AttributeError
        If the classifier does not have the attribute `feature_names_in_`.

    Notes
    -----
    - The function adds a "Genome" column to the resulting dataframe based on the index of `feature_data`.
    - This function is particularly useful for models with high-dimensional features (e.g., protein domains) that may not
      be present in every dataset.
    
    Examples
    --------
    > clf.feature_names_in_ = ['Feature1', 'Feature2', 'Feature3']
    > feature_data = pd.DataFrame({'Feature1': [0.5, 0.6], 'Feature2': [1.0, 0.8], 'FeatureX': [0.2, 0.3]})
    > result = feature_conversion(clf, feature_data)
    > print(result)
           Feature1  Feature2  Feature3  Genome
    0         0.5       1.0       0.0      0
    1         0.6       0.8       0.0      1

    """
    column_list = []
    feature_names = list(clf.feature_names_in_)  # pandas series.
    for column_feature in list(feature_data.columns):  # loop over columns in data
        if column_feature not in feature_names:  # column is not in the clf_data
            del feature_data[column_feature]

    # Create list of protein featureRegex not present in the feature_data but present in the model.
    rows_feature_data, _ = feature_data.shape
    for column_clf in feature_names:
        if column_clf not in list(feature_data.columns):
            column_list.append(column_clf)

    # Set these new columns to be zero, as they are not present.
    zero_protein_domains = pd.DataFrame(
        np.zeros((rows_feature_data, len(column_list))), dtype="float64"
    )
    zero_protein_domains.columns = column_list  # Set new protein featureRegex as columns.
    zero_protein_domains["Genome"] = pd.Series(
        feature_data.index, dtype="string"
    )  # Create genome column in new_data.
    zero_protein_domains.set_index(
        "Genome", inplace=True
    )
    output_df = feature_data.join(zero_protein_domains)
    return output_df.dropna()


def str2bool(v):
    # Thanks to " https://stackoverflow.com/a/43357954 "
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")
#
# @DeprecationWarning
# def oversample(X_train: pd.DataFrame, Y_train: pd.Series, factor=2, min_threshold=0.7, n_jobs=1):
#     """
#     Oversamples the minority class using SMOTEN (Synthetic Minority Over-sampling Technique).
#
#     Args:
#         X_train (array-like): Feature matrix of shape (n_samples, n_features).
#         Y_train (array-like): Target vector of shape (n_samples).
#         factor (int) the factor by which your least abundant datasets is oversampled.
#         min_threshold (float): The minimum difference threshold for oversampling other classes compared to the most abundant class.
#         n_jobs: Number of threads to use.
#
#     Returns:
#         tuple: A tuple containing the resampled feature matrix and the corresponding target vector.
#             X_train_resampled (array-like): Resampled feature matrix of shape (n_samples_resampled, n_features).
#             Y_train_resampled (array-like): Resampled target vector of shape (n_samples_resampled,).
#
#     Raises:
#         ValueError: If the number of unique classes in Y_train is less than 2.
#         ValueError: If the number of occurances of the least abundant class in Y_train is 1.
#
#     Notes:
#         - k_neighbors is limited to the number of occurrence of the least abundant phenotype, see the KNN algorithm.
#         - SMOTEN works for categorical variables, while SMOTE works with numerical and SMOTENC with hybrids.
#     """
#
#     # Calculate the number of samples required for the minority class and set sampling strategy
#     class_counts = Y_train.value_counts()
#     min_class_count = class_counts.min()
#     majority_class_count = class_counts.max()
#
#     # Define the sampling strategy
#     sampling_strategy = {}
#     for cls, count in class_counts.items():
#         if count < (majority_class_count * min_threshold):
#             sampling_strategy[cls] = count * factor if count * factor < majority_class_count else majority_class_count
#         else:
#             sampling_strategy[cls] = count
#
#     min_phenotype_freq = min_class_count - 1
#     X_train_filled = X_train.fillna(0)
#
#     k_neighbors = min_phenotype_freq if min_phenotype_freq < 5 else 5  # Max neighbors is 5
#     smote_sampling = SMOTEN(sampling_strategy=sampling_strategy, k_neighbors=k_neighbors)
#
#     with parallel_backend('threading', n_jobs=n_jobs):
#         X_train_resample, Y_train_resample = smote_sampling.fit_resample(X_train_filled, Y_train)
#     return X_train_resample, Y_train_resample


def calculate_sampling_strategy(Y_train, factor=2, min_threshold=0.7):
    """Calculate sampling strategy for resampling."""
    class_counts = Y_train.value_counts()
    majority_count = class_counts.max()

    strategy = {}
    for cls, count in class_counts.items():
        if count < (majority_count * min_threshold):
            target = min(count * factor, majority_count)
        else:
            target = count
        strategy[cls] = target
    return strategy


def validate_inputs(Y_train):
    """Validate input data requirements."""
    if len(Y_train.unique()) < 2:
        raise ValueError("Need at least 2 classes in Y_train")
    if Y_train.value_counts().min() == 1:
        raise ValueError("Least abundant class has only 1 sample")


def resample_data(X_train, Y_train, sampling_type: str="SMOTEN", factor=2,
                  min_threshold=0.7, n_jobs=1, **sampler_kwargs):
    """
    Perform resampling using specified strategy.

    Args:
        X_train (array-like or DataFrame): Feature matrix of shape (n_samples, n_features).
        Y_train (array-like or Series): Target vector of shape (n_samples,).
        sampling_type (str, optional): Sampling strategy to use. Options are:
            - "SMOTEN": Uses SMOTEN for categorical feature oversampling.
            - "oversample": Uses RandomOverSampler.
            - "undersample": Uses RandomUnderSampler.
            Default is "SMOTEN".
        factor (float, optional): Controls the desired ratio of minority to majority class after resampling.
            A value of 1.0 aims for full balance. Default is 2.
        min_threshold (float, optional): The minimum class ratio (minority/majority) allowed before resampling is applied.
            Classes with a ratio above this threshold will not be resampled. Default is 0.7.
        n_jobs (int, optional): Number of parallel jobs to run. Passed to joblib's `parallel_backend`. Default is 1.
        **sampler_kwargs: Additional keyword arguments passed to the selected sampler (e.g., `k_neighbors` for SMOTEN).

    Returns:
    tuple: A tuple containing the resampled feature matrix and the corresponding target vector.
        X_train_resampled (array-like): Resampled feature matrix of shape (n_samples_resampled, n_features).
        Y_train_resampled (array-like): Resampled target vector of shape (n_samples_resampled,).

    Raises:
        ValueError: If the number of unique classes in Y_train is less than 2.
        ValueError: If the number of occurances of the least abundant class in Y_train is 1.

    Notes:
        - k_neighbors is limited to the number of occurrence of the least abundant phenotype, see the KNN algorithm.
        - SMOTEN works for categorical variables, while SMOTE works with numerical and SMOTENC with hybrids.
    """
    if sampling_type.lower() == "smoten":
        sampler = SMOTEN
    elif sampling_type.lower() == "oversample":
        sampler = RandomOverSampler
    elif sampling_type.lower() == "undersample":
        sampler = RandomUnderSampler
    elif sampling_type:
        return X_train, Y_train
    else:
        raise ValueError("Unknown sampling strategy: {}".format(sampling_type))

    validate_inputs(Y_train)
    sampling_strategy = calculate_sampling_strategy(Y_train, factor, min_threshold)

    # Handle NA values (modify based on your data needs)
    X_train_filled = X_train.fillna(0)

    # Configure sampler with strategy and parameters
    sampler_instance = sampler(
        sampling_strategy=sampling_strategy,
        **sampler_kwargs
    )

    with parallel_backend('threading', n_jobs=n_jobs):
        return sampler_instance.fit_resample(X_train_filled, Y_train)
