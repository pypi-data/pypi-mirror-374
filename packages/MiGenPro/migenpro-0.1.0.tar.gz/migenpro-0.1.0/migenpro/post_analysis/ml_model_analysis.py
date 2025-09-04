# Generic imports
import argparse  # Argument parsing
from os import path, sep, makedirs
from re import sub  # Regex to remove json from uniprot API response
from sys import argv

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt  # Plotting graphs
import numpy as np  # standard deviation calculation feature importance calculation.
import pandas as pd  # Initial format given for the dataset that will have to parsed.
from joblib import parallel_backend
# import shap

# Custom functions
from migenpro.ml.ml_functions import (
    load_model,
    feature_conversion
)

# Metrics
from sklearn import tree
from sklearn.feature_selection import RFE

# Uniprot API
from migenpro.post_analysis.uniprot_api_access import pfam_domain_call
from migenpro.ml.machine_learning_main import FeatureMatrix, PhenotypeMatrix

class CommandLineInterface:
    def __init__(self):
        self.args = self.parse_arguments()

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--phenotype_matrix",
            help="The absolute path to the medium that is going to be d, granted it is automatically generated. ",
            type=str,
        )
        parser.add_argument(
            "-l",
            "--model",
            help="location of models to load",
            type=str,
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            type=str,
        )
        parser.add_argument(
            "-f",
            "--feature_matrix",
            help="Protein domain matrix file",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--train_proportion",
            help="proportion of dataset that is used for training",
            default=0.7,
            type=float,
        )
        parser.add_argument(
            "-v",
            "--variable_name",
            help="Name of the column in the phenotype file. ",
            default="Phenotype",
            type=str,
        )
        parser.add_argument("--rfe", help="Perform recursive feature importance. ", action="store_true")
        parser.add_argument("--shap", help="Perform Shapley feature importance. ", action="store_true")
        parser.add_argument("--gini", help="Perform gini feature importance. ", action="store_true")
        # TODO add parse error catchers 
        return parser.parse_args()

class CommandLineTest:
    def __init__(self):
        self.args = self.parse_arguments()

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--phenotype_matrix",
            help="The absolute path to the medium that is going to be analysed, granted it is automatically generated. ",
            default="data/phenotype_output/temperature_output/phenotype_matrix.tsv",
            type=str,
        )
        parser.add_argument(
            "-l",
            "--model",
            help="location of models to load",
            default="data/phenotype_output/temperature_output/iteration_1/mlmodels/protein_domains/RandomForestClassifier/RandomForestClassifier_protein_domains.pkl",
            type=str
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            default="data/phenotype_output/temperature_output/mloutput/iteration_1/graphs/",
            type=str,
        )
        parser.add_argument(
            "-f",
            "--feature_matrix",
            help="Feature matrix file",
            default="data/phenotype_output/temperature_output/protein_domains.tsv",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--train_proportion",
            help="propertion of dataset that is used for training",
            default=0.7,
            type=float,
        )
        parser.add_argument(
            "-v",
            "--variable_name",
            help="Name of the column in the phenotype file. ",
            default="temperature",
            type=str,
        )
        parser.add_argument("--shap", help="Perform Shapley feature importance. ", action="store_true", default=False)
        parser.add_argument("--rfe", help="Perform recursive feature importance. ", action="store_true", default=False)
        parser.add_argument("--gini", help="Perform gini feature importance. ", action="store_true", default=True)
        parser.add_argument("--test", help="Run in test mode", action="store_true")

        return parser.parse_args()

class LoadedMachineLearningModel:
    """
    Represents a single machine learning model.s

    Attributes:
        clf_model (object): The loaded classifier model.
        model_name (str): The name of the classifier model.
        gini (bool): Indicates if the model has feature importances based on Gini impurity.
    """
    def __init__(self, model: str):
        self.clf_model = load_model(model)
        self.model_name = self.clf_model.__class__.__name__
        self.module = getattr(self.clf_model, '__module__', '')
        self.gini = hasattr(self.clf_model, "feature_importances_")            

class ModelAnalysis:
    """
    Analyzes the machine learning model.

    Attributes:
        clf_model (object): The classifier model.
        model_name (str): The name of the classifier model.
        feature_column (str): The name of the feature column.
        X_test (pd.DataFrame): The test feature matrix.
        Y_test (pd.Series): The test labels.
        class_names (list): The class names.
    """
    def __init__(self, variable_name: str, LoadedMachineLearningModel, feature_matrix_subset, phenotype_matrix_subset):
        self.clf_model = LoadedMachineLearningModel.clf_model
        self.model_name = LoadedMachineLearningModel.model_name
        self.feature_column = variable_name
        feature_matrix_subset_clean = feature_conversion(clf=self.clf_model, feature_data=feature_matrix_subset) # Strips unseen features. 

        self.X_test = feature_matrix_subset_clean
        self.Y_test = phenotype_matrix_subset

        self.class_names = self.clf_model.classes_

    def _calculate_devs(self, clf, importance_max_index: list, clf_importances: list):
        """
        Calculates standard deviations and importances.

        Args:
            clf (object): The classifier model.
            importance_max_index (list): Indices of the top features.
            clf_importances (list): Feature importances.

        Returns:
            tuple: Standard deviations and importances of the top features.
        """
        ######## Standard deviation calculations ##########
        std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
        max_feature_importances = std[importance_max_index]

        max_std = [std[x] for x in importance_max_index]

        return max_std


    def _feature_text_summary(self, clf_importances, output, max_std="", topn=10):
        """
        Generates a text summary of feature importances.

        Args:
            clf_importances_max (pd.Series): Top feature importances.
            output (str): Path to save the summary.
            max_std (str, optional): Standard deviations of the top features.
        """
        # Text summary
        domain_descriptions = []
        domains = clf_importances.index
        for domain in domains[:topn]:
            uniprot_data_map = pfam_domain_call(domain)
            # Get the description
            description = uniprot_data_map.get(
                "description"
            )  # This will work for the vast majority of featureRegex.
            if description is not None:
                # "*" is greedy and  "*?" is not greedy.
                domain_descriptions.append(
                    sub(r"<(.*?)>", "", description[0].get("text"))
                )  # remove js
            elif uniprot_data_map.get(
                    "wikipedia"
            ) is not None and "extract" in uniprot_data_map.get("wikipedia"):
                description = uniprot_data_map.get("wikipedia")["extract"]
                domain_descriptions.append(sub(r"<(.*?)>", "", description))  # remove js
            else:
                domain_descriptions.append("NA")
        
        # Append null for domains outside of topn
        for domain in domains[topn:]:
            domain_descriptions.append(None)
        # domain_enriched_list = self._enriched_for(clf_importances.index, self.X_test, self.Y_test, self.class_names)

        sum_df = pd.DataFrame()
        sum_df["feature_name"] = clf_importances.index
        sum_df["importance"] = clf_importances.reset_index(drop=True)
        if max_std != "":
            sum_df["standard_deviation"] = max_std
        # sum_df["domain_found_in"] = domain_enriched_list
        sum_df["description"] = domain_descriptions
        sum_df.to_csv(output, sep="\t")

    
    def _visualize_tree(self, clf, output: str, model_name: str, feature_names=[]):
        """
        Visualizes a decision tree.

        Args:
            clf (object): The classifier model.
            output (str): Path to save the visualization.
            model_name (str) Name of model being analyzed.
            feature_names (list, optional): List of feature names.
        """
        fig = plt.figure(figsize=(25, 20))
        class_names = clf.classes_

        if not feature_names:
            feature_names = clf.feature_names_in_

        _ = tree.plot_tree(clf, feature_names=feature_names, class_names=class_names)
        if not path.isdir(output + sep + "Trees"):
            makedirs(output + sep + "Trees")
            
        fig.savefig(output + sep + "Trees" + sep + self.model_name + "_decision_tree.svg")

    def _enriched_for(self, domains, X_test, Y_test, class_names):
        """
        Determines class enrichment for featureRegex.

        Args:
            domains (list): List of featureRegex.
            X_test (pd.DataFrame): The test feature matrix.
            Y_test (pd.Series): The test labels.
            class_names (list): The class names.

        Returns:
            list: Enriched classes for each domain.
        """
        # Determine by counter where a domain is more abundant. 
        mode_results = []
        for domain in domains:
            count_result = []
            domain_presence_list = X_test[domain].tolist()
            for index, presence in enumerate(domain_presence_list):
                if presence == 1:
                    count_result.append(Y_test[index])
            mode_results.append(
                class_names[int(max(set(count_result), key=count_result.count))]
            )
        return mode_results

    # def shap_feature_importance(self, output_fig_path: str, output_summary: str, topn=10):
    #     """
    #     Computes and plots the Shapley values used for feature importance for the given classifier.

    #     Args:
    #         output_fig_path (str): Path to save the output figure.
    #         output_summary (str): Path to save the output summary.
    #         topn (int): The number of top features to display.
    #     """
    #     max_samples = len(self.X_test.index) if len(self.X_test.index) < 1000 else 1000

    #     background = self.X_test[:max_samples] 
    #     # Check if the model is a tree-based model
    #     if self.model_name in ['RandomForestClassifier', 'GradientBoostingClassifier', 'DecisionTreeClassifier']:
    #         # Use TreeExplainer for tree-based models
    #         explainer = shap.TreeExplainer(self.clf_model, background)
    #     else:
    #         # Use Independent masker for other model types (like neural networks)
    #         masker = shap.maskers.Independent(background, max_samples=max_samples)
    #         explainer = shap.Explainer(self.clf_model, masker)
        
    #     # Compute SHAP values on the test set
    #     shap_values = explainer.shap_values(self.X_test) 
    #     shap.summary_plot(shap_values, self.X_test, show=False, max_display=topn ,plot_type='bar')
    #     plt.savefig(output_fig_path, dpi=700)

        # Feature importance is the mean absolute value of Shapley values for each feature
        # feature_importance = np.abs(shap_values.values).mean(axis=0)
        
        # # Get the top N features
        # top_indices = np.argsort(feature_importance)[-topn:]
        # top_features = np.array(self.X_test.columns)[top_indices]  # Assuming X_test is a DataFrame
        # top_importance = feature_importance[top_indices]

        # # Save summary of feature importance
        # with open(output_summary, 'w') as f:
        #     for feature, importance in zip(top_features, top_importance):
        #         f.write(f"{feature}: {importance}\n")

        # # Plot feature importance
        # shap.summary_plot(shap_values, self.X_test, plot_type="bar", max_display=topn)



    def gini_feature_importance(self, output_fig_path: str, output_summary: str, topn=10):
        """
        Computes and plots the Gini-based feature importance for the given classifier.

        Args:
            output_fig_path (str): Path to save the output figure.
            output_summary (str): Path to save the output summary.
            topn (int): The number of top features to display.
        """
        # Impurity-based feature importances can be misleading for high cardinality features (many unique values).
        print("Start feature importance analysis for", self.model_name, "...")
        importances = self.clf_model.feature_importances_
        clf_importances = pd.Series(importances, index=self.clf_model.feature_names_in_)
        importance_max_index = np.argpartition(importances, -topn)[-topn:]
        clf_importances_max = pd.Series(clf_importances.iloc[importance_max_index]).sort_values(axis=0, ascending=False)

        fig, ax = plt.subplots(constrained_layout=True, figsize=(20, 20))

        ##################################### Plotting and data exportation ############################################
        # try:
        if self.model_name == "RandomForestClassifier":
            max_std = self._calculate_devs(self.clf_model, importance_max_index, clf_importances)
            ax.bar(
                clf_importances_max.index, clf_importances_max, yerr=max_std
            )
        else:
            ax.bar(clf_importances_max.index, clf_importances_max)

        fig.suptitle("Feature importances " + self.model_name, fontsize=37)
        ax.set_ylabel("Mean decrease in impurity", fontsize=35)
        plt.xticks(rotation=55, horizontalalignment="right", fontsize=35)
        plt.yticks(fontsize=35)
        fig.savefig(output_fig_path)

        if not path.isfile(output_summary):
            self._feature_text_summary(
                clf_importances=pd.Series(clf_importances).sort_values(axis=0, ascending=False),
                output=output_summary,
                topn=topn
            )
        print("Feature importance analysis for ", self.model_name, " has finished. ")    

    def rfe_feature_importance(self, output_fig, topn=10, n_jobs=1):
        """
        Performs Recursive Feature Elimination (RFE) to determine feature importance.

        Args:
            output_fig (str): Path to save the output figure.
            topn (int): The number of top features to display.
            n_jobs (int): Number of threads to use.

        Returns:
            pd.DataFrame: DataFrame containing feature names and their rankings.
        """
        with parallel_backend('threading', n_jobs=n_jobs):
            # Initialize RFE with the classifier and number of features to select
            rfe = RFE(estimator=self.clf_model, n_features_to_select=topn)
            rfe.fit(self.X_test, self.Y_test)
        
        # Get feature rankings and importance
        feature_ranking = pd.Series(rfe.ranking_, index=self.X_test.columns)
        top_features = feature_ranking[feature_ranking == 1].index

        # Plotting feature importances
        fig, ax = plt.subplots(figsize=(10, 10))
        top_feature_importances = pd.Series(rfe.estimator_.feature_importances_, index=top_features).sort_values()
        top_feature_importances.plot(kind='barh', ax=ax)
        ax.set_title('Top Feature Importances via RFE')
        ax.set_xlabel('Importance')
        ax.set_ylabel('Features')
        plt.tight_layout()
        plt.savefig(output_fig)
        

def main():
    # Argparser
    cli = CommandLineTest() if '--test' in argv else CommandLineInterface()
    if not path.isdir(str(cli.args.output)):
        makedirs(str(cli.args.output) + sep)

    model = LoadedMachineLearningModel(cli.args.model)
    print("Starting model analysis for " + model.model_name)

    # Load datasets
    feature_matrix = FeatureMatrix(cli.args.feature_matrix)
    feature_matrix.load_matrix()
    phenotype_matrix = PhenotypeMatrix(cli.args.phenotype_matrix)
    phenotype_matrix.load_matrix()

    intersect_genomes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
    feature_matrix_subset = feature_matrix.create_subset(intersect_genomes)
    phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes)
    
    modelAnalysis = ModelAnalysis(cli.args.variable_name, model, feature_matrix_subset, phenotype_matrix_subset)
    if model.gini:
        figure_gini_path = (
            str(cli.args.output)
            + sep
            + "gini_feature_importance_figure_"
            + model.model_name
            + "_"
            + cli.args.variable_name
            + ".png"
            )

        gini_figure_summary_path = (
            str(cli.args.output)
            + sep
            + "gini_feature_importance_summary_"
            + model.model_name
            + "_"
            + cli.args.variable_name
            + ".tsv"
            )
        modelAnalysis.gini_feature_importance(figure_gini_path, gini_figure_summary_path, 10)

    if cli.args.shap:
        figure_shapley_path = (
            str(cli.args.output)
            + sep
            + "shapley_feature_importance_figure_"
            + model.model_name
            + "_"
            + cli.args.variable_name
            + ".png"
            )

        shapley_figure_summary_path = (
            str(cli.args.output)
            + sep
            + "shapley_feature_importance_summary_"
            + model.model_name
            + "_"
            + cli.args.variable_name
            + ".tsv"
            )
        modelAnalysis.shap_feature_importance(figure_shapley_path, shapley_figure_summary_path, 10)

    if cli.args.rfe:
        print("Performing recursive feature elimination and assesing feature importance, this might take a while...")
        figure_rfe_path = (
            str(cli.args.output)
            + sep
            + "rfe_feature_importance_figure_"
            + model.model_name
            + "_"
            + cli.args.variable_name
            + ".png"
            )
        modelAnalysis.rfe_feature_importance(figure_rfe_path, 1)
        print("RFE feature importance analysis is finished. ") # TODO convert to logging statement. 

if __name__ == "__main__":
    main()

