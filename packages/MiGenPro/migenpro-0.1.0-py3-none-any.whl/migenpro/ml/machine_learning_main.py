import argparse
import logging
import re
import traceback
from genericpath import isfile  # Check if a file exists, during argument parsing in one line.
from os import path, makedirs, sep
from sys import argv

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.experimental import enable_halving_search_cv # THIS IS NEEDED FOR HalvingGridSearchCV
from sklearn.model_selection import train_test_split, GridSearchCV, HalvingGridSearchCV
from sklearn.tree import DecisionTreeClassifier
from migenpro.ml.ml_functions import *


class MachineLearningModels:
    """
    A class representing machine learning models for training and prediction.

    Attributes:
        classifiers (list): A list of machine learning classifiers.
        class_names (list): A list of class names used in classification.
        clf_models (list): A list of trained classifier models.
        features_used (str): The features used in the models.
    """

    def __init__(self,
                classifiers: list,
                dt_depth: int = 5,
                rf_depth: int = 10,
                gb_depth: int = 5,
                num_trees: int = 100,
                max_iter: int = 1000,
                output: str = "output/",
                proportion_train: float = 0.8,
                rf_min_leaf: int = 1,
                rf_min_split: int = 2,
                gb_min_samples: int = 2,
                gb_learning_rate: float = 0.1):
        """
        Initializes a MachineLearningModels object.

        Args:
            classifiers:
            dt_depth (int): Maximum depth for tree-based models.
            num_trees (int): Number of trees for ensemble models.
            max_iter (int): Maximum iterations for boosting models.
            feature_matrix (str): Path to the feature matrix file.
            output (str): Path to save the output results.
            proportion_train (float): Proportion of data to use for training.
            rf_min_leaf (int): Minimum leaf size for random forest.
            rf_min_split (int): Minimum split size for random forest.
            gb_min_samples (int): Minimum number of samples for gradient boosting splits.
            gb_learning_rate (float): Learning rate for gradient boosting.
        """
        self.dt_depth = dt_depth
        self.rf_depth = rf_depth
        self.gb_depth = gb_depth
        self.num_trees = num_trees
        self.max_iter = max_iter
        self.rf_min_leaf = rf_min_leaf
        self.rf_min_split = rf_min_split
        self.gb_min_samples = gb_min_samples
        self.gb_learning_rate = gb_learning_rate

        self.classifiers = [RandomForestClassifier, GradientBoostingClassifier, DecisionTreeClassifier]
        self.class_names = []
        self.clf_models = []  # List of trained models
        self.features_used = None
        self.output = output
        self.model_dir = path.join(output, "mlmodels")
        self.oversample = oversample
        self.proportion_train = proportion_train

        self.X_test = pd.DataFrame()
        self.X_train = pd.DataFrame()
        self.Y_test = pd.Series(dtype="float64")
        self.Y_train = pd.Series(dtype="float64")
        self.pickled_models = []

    def set_datasets(self, observed_values: pd.DataFrame, observed_results: pd.DataFrame, sampling_type: str=None, n_jobs=1, min_variance: int=1, label: str="protein_domain"):
        """
        Set the datasets that are to be used in the MachineLearningModels object. 

        Args:
            observed_values (pd.DataFrame): DataFrame containing the observed feature values.
            observed_results (pd.DataFrame): DataFrame containing the observed results (target values).
            sampling_type (str, optional): Type of sampling to apply. Defaults to None.
                Options include:
                - 'SMOTEN': Synthetic Minority Over-sampling Technique for Nominal and Continuous features.
                - 'undersampling': Randomly reduce the number of samples in the majority class.
                - 'oversampling': Randomly replicate samples from the minority class.
            n_jobs (int, optional): Number of parallel jobs to run for resampling. Defaults to 1.
            min_variance (int, optional): Minimum variance threshold for feature filtering. Features with variance below this threshold will be removed. Defaults to 1.
            label (str): Label output. Defaults to "protein_domain".

        """
        self.features_used = label
        variance_filtered_observed_values = filter_features_by_variance(observed_values, min_variance)
        X_train_raw, self.X_test, Y_train_raw, self.Y_test = train_test_split(
            variance_filtered_observed_values,
            observed_results,
            test_size=round(1 - self.proportion_train, 2),
            train_size=round(self.proportion_train, 2),
            stratify=observed_results,
        )
        if sampling_type:
            logging.info("Now oversampling data. ")
            self.X_train, self.Y_train = resample_data(X_train=X_train_raw, Y_train=Y_train_raw, sampling_type=sampling_type, n_jobs=n_jobs)  #  oversample(X_train=X_train_raw, Y_train=Y_train_raw, n_jobs=n_jobs)
            logging.info("Finished oversampling data. ")
        else:
            self.X_train, self.Y_train = X_train_raw, Y_train_raw

    def load_model(self, model_load_path: str):
        """
        Loads a pre-trained model from a file specified in the command-line arguments.

        args:
            model_load_path (str) path to model.
        """
        self.clf_models.append(load_model(model_load_path))

    def get_model_dir(self, classifier_name: str):
        if self.features_used not in self.model_dir:
            return path.join(self.model_dir, self.features_used, classifier_name, "")
        else:
            return path.join(self.model_dir, classifier_name, "")

    def save_models(self):
        """
        Saves trained models to files in the specified directory.
        """
        for clf_model in self.clf_models:
            classifier_name = clf_model.__class__.__name__
            specific_model_dir = self.get_model_dir(classifier_name)
            model_file = specific_model_dir + classifier_name + "_" + self.features_used + ".pkl"
            save_model(clf_model, model_file)
            self.pickled_models.append(model_file)

    def train_models(self, n_jobs=1):
        """
        Train a machine learning model with the given X and Y training data
        """
        self.classifiers = [
            DecisionTreeClassifier(max_depth=self.dt_depth), 
            RandomForestClassifier(max_depth=self.rf_depth, n_estimators=self.num_trees, min_samples_leaf=self.rf_min_leaf, min_samples_split=self.rf_min_split, n_jobs=n_jobs),
            GradientBoostingClassifier(n_estimators=self.max_iter, min_samples_split=self.gb_min_samples, learning_rate=self.gb_learning_rate, max_depth=self.gb_depth),
            # Uncomment the MLPClassifier if needed and configure its parameters
            # MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
        ]

        for classifier in self.classifiers:
            classifier_name = classifier.__class__.__name__
            specific_model_dir = self.get_model_dir(classifier_name)

            if not path.isdir(specific_model_dir):
                makedirs(specific_model_dir)

            logging.info("Now training model: " + classifier_name)
            with parallel_backend('threading', n_jobs=n_jobs):
                self.clf_models.append(classifier.fit(self.X_train, self.Y_train))  # X_train will be converted to a sparse matrix.

    def perform_grid_search(self, param_grids: dict, cv: int = 5, scoring: str = "matthews_corrcoef"):
        """
        Perform grid search for hyperparameter tuning for each classifier.

        Args:
            param_grids (dict): A dictionary where keys are classifier names and values are parameter grids.
            cv (int): Number of cross-validation folds. Default is 5.
            scoring (str): Scoring metric for evaluating model performance. Default is "matthews".

        Returns:
            dict: A dictionary with classifier names as keys and best parameter sets as values.
        """
        best_params = {}
        for classifier in self.classifiers:
            classifier_name = classifier.__class__.__name__
            if classifier_name in param_grids:
                logging.info(f"Performing grid search for {classifier_name}...")
                grid_search = GridSearchCV(
                    estimator=classifier,
                    param_grid=param_grids[classifier_name],
                    cv=cv,
                    scoring=scoring
                )
                grid_search.fit(self.X_train, self.Y_train)
                self.clf_models.append(grid_search.best_estimator_)  # Save the best model
                best_params[classifier_name] = grid_search.best_params_
                logging.info(f"Best params for {classifier_name}: {grid_search.best_params_}")

        return best_params


    def perform_halving_grid_search_search(self, param_grids: dict, cv: int = 2, scoring: str = "matthews_corrcoef") -> dict:
        """
        Perform successive halving grid search for hyperparameter tuning for each classifier.

        Args:
            param_grids (dict): A dictionary where keys are classifier names and values are parameter grids.
            cv (int): Number of cross-validation folds. Default is 2.
            scoring (str): Scoring metric for evaluating model performance. Default is "matthews".
            label (str): When

        Returns:
            dict: A dictionary with classifier names as keys and the best parameter sets as values.
        """
        best_params = {}
        for classifier in self.classifiers:
            classifier_name = re.search(r"\.([^.]*)'>", str(classifier)).group(1) #.__class__.__name__
            if classifier_name in param_grids:
                init_classifier = classifier()
                print(f"Performing grid search for {classifier_name}...")
                grid_search = HalvingGridSearchCV(
                    estimator=init_classifier,
                    param_grid=param_grids[classifier_name],
                    cv=cv,
                    scoring=scoring
                )
                grid_search.fit(self.X_train, self.Y_train)
                self.clf_models.append(grid_search.best_estimator_)  # Save the best model
                best_params[classifier_name] = grid_search.best_params_

        return best_params


    def predict_models_train(self):
        """
        Performs a prediction on the datasets used for training
        """
        self.predict_models(self.X_train, self.Y_train, "train")

    def predict_models_test(self):
        """
        Performs a prediction on the test dataset. 
        """
        self.predict_models(self.X_test, self.Y_test, "test")

    def predict_models(self, X_predict: pd.DataFrame, Y_observed: pd.Series, type: str):
        """
        Uses trained models to predict phenotype values for the test dataset.
        """
        for clf_model in self.clf_models:
            specific_output_dir = path.join(str(self.output), clf_model.__class__.__name__,
                                            clf_model.__class__.__name__ + f"-{type}-output.tsv")
            self.machine_learning_predict(clf_model=clf_model, output_file=specific_output_dir, X_predict=X_predict,
                                     Y_observed=Y_observed)



    def _get_merged_test_results(sellf, predictions_test: str, probability_test: str, class_names: list,
                                    X_predict: pd.DataFrame, Y_observed: pd.Series):
        """
        Merges prediction results with the test dataset.

        Args:
            predictions_test (str): Predicted values.
            probability_test (str): Predicted probabilities.
            class_names (list): Class names.

        Returns:
            pd.DataFrame: Merged results dataframe.

        """
        try:
            merged_result_test = pd.DataFrame(dtype="float64")
            merged_result_test["Genomes"] = X_predict.index.values
            merged_result_test["Observation"] = Y_observed.tolist()
            merged_result_test["ObservedString"] = Y_observed.tolist()
            merged_result_test["Prediction"] = predictions_test.tolist()
            merged_result_test["PredictedString"] = predictions_test

            # Store the various probability intervals for the different classes.
            _, columns = probability_test.shape
            for probability_column in range(0, columns):
                merged_result_test[class_names[probability_column]] = probability_test[:,
                                                                        probability_column].tolist()

            merged_result_test["ConfidencePrediction"] = merged_result_test.apply(lambda row: row[row['PredictedString']], axis=1).tolist()

        except Exception:
            logging.error(traceback.format_exc())
            raise Exception(f"Something went wrong while reading the results of a machine learning model. ")

        return merged_result_test

    def _save_merged_results(self, merged_result_test: pd.DataFrame, output_file: str):
        """
        Saves merged prediction results to a file.

        Args:
            merged_result_test (pd.DataFrame): Merged results dataframe.
            output_file (str): Path to the output file.
        """
        output_dir = sep.join(output_file.split(sep)[:-1])
        if not path.isdir(output_dir):
            makedirs(output_dir)

        try:
            merged_result_test.to_csv(output_file, sep="\t")
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error("Saving of the output failed for " + output_file)

    def machine_learning_predict(self, clf_model, output_file: str, X_predict: pd.DataFrame, Y_observed: pd.Series):
        """
        Predict phenotype values with the given models using X_test to predict and verify these result with Y_test the results are summarized and written to the output file in tsv format.

        Args:
            clf_model: Trained classifier model.
            output_file (str): Path to save the prediction results.
        """

        classifier_name = clf_model.__class__.__name__
        class_names = list(clf_model.classes_)

        # Remove any features not encountered while training the model.
        clean_X_test = feature_conversion(clf=clf_model, feature_data=X_predict)

        try:
            predictions_test = clf_model.predict(clean_X_test)
            probability_test = clf_model.predict_proba(X=clean_X_test)

            ############################ Data exportation ############################
            merged_result_test = self._get_merged_test_results(predictions_test, probability_test, class_names,
                                                               X_predict,
                                                               Y_observed)

            self._save_merged_results(merged_result_test, output_file)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("prediction failed for " + classifier_name)
    
    def get_pickled_models(self):
        return self.pickled_models

class MatrixFile:
    """
    A class representing a generic matrix file.

    Attributes:x
        file_path (str): The file path to the matrix file.
        file_df (DataFrame): The DataFrame containing the data loaded from the file.
    """

    def __init__(self, file_path: str):
        """
        Initializes a MatrixFile object.

        Args:
            file_path (str): The file path to the matrix file.
        """
        self.file_path = file_path
        self.file_df = pd.DataFrame()

    def load_matrix(self):
        """
        Loads the matrix data from the file into the file_df attribute.
        """
        if self.file_path.endswith(".gz"):
            self.file_df = pd.read_csv(self.file_path, delimiter="\t", index_col=0, compression="gzip")
        else:
            self.file_df = pd.read_csv(self.file_path, delimiter="\t", index_col=0)
        self.file_df.index = self.file_df.index.str.strip()

    def create_subset(self, indices):
        return self.file_df.loc[indices]

    def get_intersected_genomes(self, intersect_df):
        """
        Retrieves the intersected genomes between the phenotype matrix and a feature matrix.

        Args:
            intersect_df (DataFrame): A DataFrame to intersect with.

        Returns:
            list: A list of intersected genome IDs.
        """
        return intersect_df.index.intersection(self.file_df.index).to_list()

    def get_matrix(self):
        return self.file_df

class FeatureMatrix(MatrixFile):
    """
    A class representing a feature matrix file.

    Attributes:
        features_used (str): The features used in the matrix.
    """

    def __init__(self, file_path):
        """
        Initializes a FeatureMatrix object.

        Args:
            file_path (str): The file path to the feature matrix file.
        """
        super().__init__(file_path)
        self.features_used = path.splitext(path.basename(self.file_path))[0]


class PhenotypeMatrix(MatrixFile):
    """
    A class representing a phenotype matrix file.
    """

    def __init__(self, file_path=""):
        """
        Initializes a PhenotypeMatrix object.

        Args:
            file_path (str, optional): The file path to the phenotype matrix file. Defaults to "".
        """
        super().__init__(file_path)

    def create_subset(self, indices: list):
        """
        Returns the given indices rows from the file_df dataframe.
        """
        phenotype = self.file_df.columns[0]
        duplicates_mask = ~self.file_df.loc[indices][phenotype].index.duplicated(keep='first')
        return self.file_df.loc[indices][phenotype][duplicates_mask]


class CommandLineInterface:
    def __init__(self):
        self.args = self.parse_arguments()

    @staticmethod
    def _validate_args(args):
        validation_functions = {
            'num_trees': lambda x: x >= 1,
            'dt_depth': lambda x: x >= 1,
            'rf_depth': lambda x: x >= 1,
            'rf_min_leaf': lambda x: x >= 1,
            'rf_min_split': lambda x: x >= 2,
            'gb_min_samples': lambda x: x >= 2,
            'gb_learning_rate': lambda x: 0 < x <= 1,
            'max_iter': lambda x: x >= 1,
            'proportion_train': lambda x: 0 <= x <= 1,
            'input': lambda x: isfile(x) if args.train else True,
            'feature_matrix': lambda x: isfile(x),
            'model_load': lambda x: isfile(x) and x.split('.')[-1] == 'pkl' if x else True,
            'train_or_predict': lambda x: args.train or args.predict
        }

        error_messages = {
            'num_trees': "Number of trees must be greater than 0.",
            'dt_depth': "Depth must be greater than 0.",
            'rf_depth': "Depth must be greater than 0.",
            'rf_min_leaf': "Minimum leaf size for random forest must be greater than 0.",
            'rf_min_split': "Minimum split size for random forest must be at least 2.",
            'gb_min_samples': "Minimum number of samples for gradient boosting must be at least 2.",
            'gb_learning_rate': "Learning rate for gradient boosting must be in the range (0, 1].",
            'max_iter': "Maximum number of iterations must be greater than 0.",
            'proportion_train': f"Proportion of training data must be between 0 and 1, not \"{args.proportion_train}\"",
            'input': f"Phenotype matrix file {args.input} does not exist you cannot train model without supervision.",
            'feature_matrix': f"Genome feature matrix file {args.feature_matrix} does not exist.",
            'model_load': f"Model load path {args.model_load} does not exist, to specify a model to use --l <model_file.pkl>",
            'train_or_predict': "Either --train/-n or --predict/-r must be true."
        }

        for arg_name, validation_func in validation_functions.items():
            if not validation_func(getattr(args, arg_name, None)):
                raise argparse.ArgumentError(getattr(args, arg_name + '_arg', None), error_messages[arg_name])

    def parse_arguments(self):
        parser = argparse.ArgumentParser()

        dt_depth_arg = parser.add_argument(
            "--dt_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        rf_depth_arg = parser.add_argument(
            "--rf_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        gb_depth_arg = parser.add_argument(
            "--gb_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        num_trees_arg = parser.add_argument(
            "-t",
            "--rf_trees",
            help="number of trees used in rf.",
            default=100,
            type=int
        )
        max_iter_arg = parser.add_argument(
            "-m",
            "--max_iter",
            help="maximum number of iterations for gradient boosting",
            default=100,
            type=int
        )
        rf_min_sample_leaf_arg = parser.add_argument(
            "--rf_min_leaf",
            help="minimum leaf size for random forest.",
            default=10,
            type=int,
        )
        rf_min_sample_split_arg = parser.add_argument(
            "--rf_min_split",
            help="minimum split size for random forest.",
            default=10,
            type=int,
        )
        gb_min_samples_split_arg = parser.add_argument(
            "--gb_min_samples",
            help="minimum number of samples for gradient boosting.",
            default=10,
            type=int,
        )
        gb_learning_rate_arg = parser.add_argument(
            "--gb_learning_rate",
            help="learning rate for gradient boosting.",
            default=0.01,
            type=float
        )
        proportion_train_arg = parser.add_argument(
            "-p",
            "--proportion_train",
            help="proportion of dataset that is used for training",
            default=0.7,
            type=float,
        )
        model_load_arg = parser.add_argument(
            "-l",
            "--model_load",
            help="location of model to load",
            default="",
            type=str
        )
        train_arg = parser.add_argument(
            "-n",
            "--train",
            help="boolean arg that indicates if you want to train new models.",
            action="store_true",
        )
        predict_arg = parser.add_argument(
            "-r",
            "--predict",
            help="boolean arg that indicates if you want to predict values using a preexisting models",
            action="store_true",
        )
        input_arg = parser.add_argument(
            "-i",
            "--input",
            help="Phenotype matrix file location. ",
            default="",
            type=str,
        )
        output_arg = parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            default="output/mloutput",
            type=str,
        )
        feature_matrix_arg = parser.add_argument(
            "-a",
            "--feature_matrix",
            help="Feature matrix file",
            type=str,
            required=True
        )
        threads_arg = parser.add_argument(
            "-j",
            "--threads",
            default=1,
            type=int
        )
        parser.add_argument("--oversample", help="Oversample train dataset to a maximum of two", action="store_true",
                            default=False)

        args = parser.parse_args()

        self._validate_args(args)
        return args


class CommandLineTest:
    def __init__(self):
        self.args = self.parse_arguments()

    @staticmethod
    def parse_arguments():
        # Argparser
        parser = argparse.ArgumentParser()
        dt_depth_arg = parser.add_argument(
            "--dt_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        rf_depth_arg = parser.add_argument(
            "--rf_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        gb_depth_arg = parser.add_argument(
            "--gb_depth",
            help="depth of each tree in the forest",
            default=5, type=int
        )
        num_trees_arg = parser.add_argument(
            "-t",
            "--rf_trees",
            help="number of trees used in rf.",
            default=100,
            type=int
        )
        max_iter_arg = parser.add_argument(
            "-m",
            "--max_iter",
            help="maximum number of iterations for gradient boosting",
            default=100,
            type=int
        )
        rf_min_sample_leaf_arg = parser.add_argument(
            "--rf_min_leaf",
            help="minimum leaf size for random forest.",
            default=10,
            type=int,
        )
        rf_min_sample_split_arg = parser.add_argument(
            "--rf_min_split",
            help="minimum split size for random forest.",
            default=10,
            type=int,
        )
        gb_min_samples_split_arg = parser.add_argument(
            "--gb_min_samples",
            help="minimum number of samples for gradient boosting.",
            default=10,
            type=int,
        )
        gb_learning_rate_arg = parser.add_argument(
            "--gb_learning_rate",
            help="learning rate for gradient boosting.",
            default=0.01,
            type=float
        )
        proportion_train_arg = parser.add_argument(
            "-p",
            "--proportion_train",
            help="proportion of dataset that is used for training",
            default=0.8,
            type=float,
        )
        model_load_arg = parser.add_argument(
            "-l", "--model_load", help="location of model to load", default="", type=str
        )
        train_arg = parser.add_argument(
            "-n",
            "--train",
            help="boolean arg that indicates if you want to train new models.",
            default=True,
        )  #
        predict_arg = parser.add_argument(
            "-r",
            "--predict",
            help="boolean arg that indicates if you want to predict values using a preexisting models",
            default=True,
        )
        input_arg = parser.add_argument(
            "-i",
            "--input",
            help="The absolute path to the medium that is going to be analysed, granted it is automatically generated. ",
            default="/media/mike-loomans/T7/backup/genopro/data/phenotype_output/motility_output/phenotype_matrix.tsv",
            type=str,
        )
        output_arg = parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            default="/media/mike-loomans/T7/backup/genopro/data/phenotype_output/motility_output/mloutput/",
            type=str,
        )
        feature_matrix_arg = parser.add_argument(
            "-a",
            "--feature_matrix",
            default="/media/mike-loomans/T7/backup/genopro/data/phenotype_output/motility_output/protein_domains.tsv",
            type=str,
        )
        threads_arg = parser.add_argument(
            "-j",
            "--threads",
            default=1,
            type=int
        )
        parser.add_argument("--oversample", help="Oversample train dataset to a maximum of two", default=False)
        parser.add_argument("--test", help="Run in test mode", action="store_true")
        return parser.parse_args()


if __name__ == "__main__":
    cli = CommandLineTest() if '--test' in argv else CommandLineInterface() 

    # Load data
    print("Loading matrix")
    feature_matrix = FeatureMatrix(cli.args.feature_matrix)
    feature_matrix.load_matrix()
    phenotype_matrix = PhenotypeMatrix(cli.args.input)
    phenotype_matrix.load_matrix()
    # intersect_genomes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
    intersect_genomes = feature_matrix.file_df.index.intersection(
        phenotype_matrix.file_df.index
    ).to_list()

    feature_matrix_subset = feature_matrix.create_subset(intersect_genomes)
    phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes)

    n_rows_phenotype = phenotype_matrix_subset.size
    n_rows_features, _ = feature_matrix_subset.shape
    if n_rows_phenotype != n_rows_features: # Smoke
        raise Exception(f"Number of rows in phenotype ({n_rows_phenotype}) and feature matrix ({n_rows_features}) do not match")
    else:
        print("Loading matrix successful")

    # Train and predict with models
    print("Starting machine learning")
    classifiers = ["DecisionTreeClassifier", "GradientBoostingClassifier", "RandomForestClassifier"]
    models = MachineLearningModels(dt_depth=cli.args.dt_depth, rf_depth=cli.args.rf_depth, gb_depth=cli.args.gb_depth,
                                   num_trees=cli.args.rf_trees, max_iter=cli.args.max_iter, output=cli.args.output,
                                   proportion_train=cli.args.proportion_train, rf_min_leaf=cli.args.rf_min_leaf,
                                   rf_min_split=cli.args.rf_min_split, gb_min_samples=cli.args.gb_min_samples,
                                   gb_learning_rate=cli.args.gb_learning_rate, classifiers=classifiers)
    models.set_datasets(feature_matrix_subset, phenotype_matrix_subset, cli.args.oversample, cli.args.threads)
    if cli.args.model_load != "":
        models.load_model(cli.args.model_load)
    else:
        models.train_models(n_jobs=cli.args.threads)

    models.predict_models_test()
    models.Y_train.to_csv(path.join(models.output, "y_train.tsv"), sep="\t")
    models.predict_models_train()
    models.save_models()
    print("Machine learning finished. ")
