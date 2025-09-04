# File management
import argparse # Argument parsing
import glob # Determine what files exist within certain directories.
from os import path, sep, listdir, makedirs

# Graphs
import pandas as pd # Standard format for the training and testing data.
import matplotlib
# matplotlib.use('cairo')  # Use non-interactive backend
import matplotlib.pyplot as plt # Graph plotting.
import numpy as np # Used for isnan() function.
from sklearn.metrics import roc_curve, auc, f1_score, precision_recall_curve, precision_score, recall_score, matthews_corrcoef, confusion_matrix, accuracy_score  # Machine learning performance metrics.
from sys import argv
import seaborn as sns

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from os import path, makedirs, sep
from sklearn.metrics import (f1_score, accuracy_score, precision_score,
                             recall_score, matthews_corrcoef,
                             precision_recall_curve, roc_curve, auc,
                             confusion_matrix)


class SummaryGraphs:
    def __init__(self, machine_learning_output_data, output_dir: str, test=True):
        self.machine_learning_output_data = machine_learning_output_data
        self.test = "test" if test else "train"
        self._init_metrics_storage()
        self._setup_directories(output_dir)
        self._init_plotting_resources()

    def _init_metrics_storage(self):
        """Initialize all metric storage containers"""
        self.metrics = []
        self.roc_data = []
        self.prc_data = []
        self.classifiers = self.machine_learning_output_data.classifiers

    def _setup_directories(self, output_dir):
        """Create required output directories"""
        self.output_dir = output_dir
        self.graph_output_dir = path.join(output_dir, "graphs")
        self._create_directory(self.graph_output_dir)

    def _init_plotting_resources(self):
        """Initialize plotting-related resources"""
        self.hatch_gradients = [
            '/', '\\', '|', '---', '+', 'x', 'o', '.', '-', '//',
            'xx', '\\\\', '--', '..', '++', 'oooo', '....', '\\\\\\\\',
            '//..', 'o++x', '--oo', '|xx+', '\\\\\\|', 'x.x.', '++//',
            '|\\--', 'o--|', '.o\\x', '+.oo', 'o//o', '|++|', '.x--',
            '+\\\\+', '.-x-', '\\x\\o', 'xxxx', '----', '\\\\//', '||++'
        ]

    def _create_directory(self, dir_path):
        """Utility for safe directory creation"""
        if not path.exists(dir_path):
            makedirs(dir_path)

    def output_scores_to_table(self):
        """Export metrics to TSV file"""
        if not self.metrics:
            self.analyse_classifiers()

        output_file = path.join(self.graph_output_dir, f"{self.test}-summary.tsv")
        pd.DataFrame(self.metrics).to_csv(output_file, index=False)

    def make_method_summary_graphs(self):
        """Generate all summary bar charts"""
        metrics_df = pd.DataFrame(self.metrics)
        self._create_bar_chart(metrics_df, "f1_score", "F1", color=["black", "red", "green", "blue", "cyan"])
        self._create_bar_chart(metrics_df, "accuracy", "Accuracy", hatch=True)
        self._create_bar_chart(metrics_df, "auc", "AUC", hatch=True)
        self._create_bar_chart(metrics_df, "mcc", "Matthew Correlation Coefficient", hatch=True)

    def _create_bar_chart(self, metrics_df, metric, title, color="grey", hatch=False):
        """Generic bar chart creation"""
        fig, ax = plt.subplots(figsize=(10, 6))

        if hatch:
            hatches = self.hatch_gradients[:len(metrics_df)]
            ax.bar(self.classifiers, metrics_df[metric], color=color, hatch=hatches)
        else:
            ax.bar(self.classifiers, metrics_df[metric], color=color)

        ax.set_title(f"{title} Chart")
        ax.set_ylabel(title)
        ax.set_ylim(0.5, 1)
        plt.xticks(rotation=55, horizontalalignment="center")

        self._save_figure(fig, f"BarChart{metric.upper()}")

    def _save_figure(self, fig, chart_type):
        """Save figure with standardized naming"""
        fig.savefig(
            path.join(self.graph_output_dir,
                      f"Summary_{self.machine_learning_output_data.characteristic}_{chart_type}.png"),
            bbox_inches="tight",
            dpi=1200
        )
        plt.close(fig)

    def analyse_classifiers(self):
        """Main analysis entry point"""
        for classifier in self.classifiers:
            self._process_classifier(classifier)

        self._plot_classifiers_performance(
            pd.DataFrame(self.metrics),
            pd.DataFrame(self.roc_data),
            pd.DataFrame(self.prc_data)
        )

    def _process_classifier(self, classifier):
        """Process individual classifier results"""
        method_dir = self._create_classifier_directory(classifier)
        results = self._get_classifier_results(classifier)

        if results["Observation"].empty:
            raise FileNotFoundError(f"Missing results for {classifier}")

        metrics = self._calculate_basic_metrics(results)
        self._process_probability_data(classifier, results, metrics)
        self.metrics.append(metrics)

    def _create_classifier_directory(self, classifier):
        """Create classifier-specific output directory"""
        classifier_dir = path.join(self.graph_output_dir, classifier)
        self._create_directory(classifier_dir)
        return classifier_dir

    def _get_classifier_results(self, classifier) -> pd.DataFrame:
        """Retrieve results for a single classifier"""
        return self.machine_learning_output_data.get_results_for_method(classifier, self.test)

    def _calculate_basic_metrics(self, results):
        """Calculate basic classification metrics"""
        return {
            "classifier": results["classifier"],
            "f1_score": f1_score(results["observed_values"], results["predicted_values"], average="micro"),
            "accuracy": accuracy_score(results["observed_values"], results["predicted_values"]),
            "precision": precision_score(results["observed_values"], results["predicted_values"], average="micro"),
            "recall": recall_score(results["observed_values"], results["predicted_values"], average="micro"),
            "mcc": matthews_corrcoef(results["observed_values"], results["predicted_values"])
        }

    def _process_probability_data(self, classifier, results, metrics):
        """Handle probability-based metrics and curves"""
        if len(results["probability_classes"].columns) > 2:
            self._process_multiclass_case(classifier, results)
        else:
            self._process_binary_case(classifier, results, metrics)

    def _process_multiclass_case(self, classifier, results):
        """Handle multiclass classification metrics"""
        for i, class_name in enumerate(results["probability_classes"].columns):
            observed_binary = [1 if class_name == obs else 0 for obs in results["observed_values_string"]]
            self._calculate_curve_metrics(classifier, class_name, observed_binary,
                                          results["probability_classes"].iloc[:, i])

    def _process_binary_case(self, classifier, results, metrics):
        """Handle binary classification metrics"""
        tn, fp, fn, tp = confusion_matrix(results["observed_values"], results["predicted_values"]).ravel()
        metrics["specificity"] = tn / (tn + fp)
        positive_class = results["probability_classes"].columns[1]
        observed_binary = [1 if positive_class == obs else 0 for obs in results["observed_values_string"]]
        self._calculate_curve_metrics(classifier, positive_class, observed_binary,
                                      results["probability_classes"].iloc[:, 1])

    def _calculate_curve_metrics(self, classifier, class_name, observed_binary, probabilities):
        """Calculate ROC and PRC metrics"""
        precision, recall, _ = precision_recall_curve(observed_binary, probabilities)
        fpr, tpr, _ = roc_curve(observed_binary, probabilities)
        auc_value = auc(fpr, tpr)

        self.roc_data.append({
            "classifier": classifier,
            "class": class_name,
            "fpr": fpr,
            "tpr": tpr,
            "auc": auc_value
        })

        self.prc_data.append({
            "classifier": classifier,
            "class": class_name,
            "precision": precision,
            "recall": recall
        })

    def _plot_classifiers_performance(self, metrics_df, roc_data_df, prc_data_df):
        """Coordinate performance plotting"""
        self._plot_roc_curves(roc_data_df)
        self._plot_prc_curves(prc_data_df)
        self._plot_metric_summary(metrics_df)

    def _plot_roc_curves(self, roc_data_df):
        """Plot ROC curves for all classifiers"""
        fig, ax = plt.subplots(figsize=(10, 6))
        for _, row in roc_data_df.iterrows():
            ax.plot(row["fpr"], row["tpr"],
                    label=f"{row['classifier']} ({row['class']}, AUC={row['auc']:.3f})")
        ax.plot([0, 1], [0, 1], "k--", label="Chance (AUC=0.5)")
        self._finalize_plot(fig, ax, "ROC Curve", "False Positive Rate (FPR)",
                            "True Positive Rate (TPR)", "roc_curve_all_classifiers.png")

    def _plot_prc_curves(self, prc_data_df):
        """Plot Precision-Recall curves for all classifiers"""
        fig, ax = plt.subplots(figsize=(10, 6))
        for _, row in prc_data_df.iterrows():
            ax.plot(row["recall"], row["precision"],
                    label=f"{row['classifier']} ({row['class']})")
        self._finalize_plot(fig, ax, "Precision-Recall Curve", "Recall",
                            "Precision", "precision_recall_curve_all_classifiers.png")

    def _plot_metric_summary(self, metrics_df):
        """Plot summary metric comparison"""
        fig, ax = plt.subplots(figsize=(10, 6))
        metrics_df.plot(x="classifier", y=["f1_score", "accuracy", "auc", "mcc"],
                        kind="bar", ax=ax)
        self._finalize_plot(fig, ax, "Performance Metrics by Classifier",
                            "Classifier", "Score", "classifier_metrics_summary.png")

    def _finalize_plot(self, fig, ax, title, xlabel, ylabel, filename):
        """Common plot finalization tasks"""
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(path.join(self.output_dir, filename), dpi=300)
        plt.close(fig)

def determineAccuracy(observed_values, predicted_values):
    """
    Calculate the accuracy of predictions.

    Args:
        observed_values (pd.Series or list): The actual observed values.
        predicted_values (pd.Series or list): The predicted values.

    Returns:
        float: The accuracy of the predictions as a ratio of correct predictions to total predictions.
    """
    observed_values = observed_values if type(observed_values) == list else observed_values.tolist()
    predicted_values = predicted_values if type(predicted_values) == list else predicted_values.tolist()
    correct = incorrect = 0
    for i in range(0, len(observed_values)):
        if bool(observed_values[i] == predicted_values[i]):
            correct += 1
        else:
            incorrect += 1
    return correct / (correct + incorrect)


def mutliclassResultsToBinary(observed_values, predicted_values):
    """
    Convert multiclass prediction results to binary format.

    Args:
        observed_values (pd.Series or list): The actual observed values.
        predicted_values (pd.Series or list): The predicted values.

    Returns:
        list: A list of binary values where 1 indicates a correct prediction and 0 indicates an incorrect prediction.
    """
    observed_values = observed_values if type(observed_values) == list else observed_values.tolist()
    predicted_values = predicted_values if type(predicted_values) == list else predicted_values.tolist()
    
    binary_predicted = []
    for index, value in enumerate(observed_values):
        # If the predicted value matches the observed value, append 1, else append 0.
        if predicted_values[index] == value:
            binary_predicted.append(1)
        else:
            binary_predicted.append(0)
    return binary_predicted


def probability_divider(observed_values_string, name_probability: str, single_characteristic_probability):
    """
    Divide probabilities into correct and incorrect predictions.

    Args:
        observed_values_string (pd.Series or list): The actual observed values as strings.
        name_probability (str) The value of te given probabiliy class. 
        single_characteristic_probability (pd.Series or list): The probabilities of a single characteristic.

    Returns:
        tuple: Two lists, one with probabilities of correctly predicted values and one with probabilities of incorrectly predicted values.
    """
    observed_values_string = observed_values_string.to_numpy().flatten()  # 1D numpy array
    single_characteristic_probability = single_characteristic_probability.to_numpy().flatten()  # 1D numpy array.
    prob_df = pd.DataFrame()
    true_df = []
    false_df = []
    for index, value in enumerate(observed_values_string):
        if value == name_probability:
            true_df.append(single_characteristic_probability[index])
        else:
            false_df.append(single_characteristic_probability[index])
    return true_df, false_df

# @DeprecationWarning
# class SummaryGraphs():
#     def __init__(self, machine_learning_output_data, output_dir: str, test=True):
#         self.machine_learning_output_data = machine_learning_output_data
#         self.test = "test" if test else "train"
#         self.probability_classes = pd.DataFrame()
#         self.accuracy_data = []
#         self.auc_data = []
#         self.f1_data = []
#         self.precision = []
#         self.specificity = []
#         self.recall = []
#         self.npv = []
#         self.matthews = []
#
#         self.metrics = []
#         self.roc_data = []
#         self.prc_data = []
#
#         self.hatch_gradients = [
#             '/', '\\', '|', '---', '+', 'x',
#             'o', '.', '-', '//', 'xx', '\\\\', '--', '..', '++',
#             'oooo', '....', '\\\\\\\\', '//..', 'o++x', '--oo',
#             '|xx+', '\\\\\\|', 'x.x.', '++//', '|\\--', 'o--|',
#             '.o\\x', '+.oo', 'o//o', '|++|', '.x--', '+\\\\+',
#             '.-x-', '\\x\\o', 'xxxx', '----', '\\\\//', '||++'
#             ]
#         self.classifiers = machine_learning_output_data.classifiers
#         self.output_dir = output_dir
#
#
#         self.graph_output_dir = output_dir + sep + "graphs"
#         if not path.isdir(self.graph_output_dir):
#             makedirs(self.graph_output_dir)
#
#     def output_scores_to_table(self):
#         """
#         Output the scores to a table in a TSV file.
#
#         This method creates a summary table of various performance metrics
#         and writes it to a TSV file. The metrics include accuracy, AUC, F1 score,
#         precision, specificity, recall, NPV, and Normmvv.
#
#         """
#
#         if len(self.metrics) == 0:
#             self.analyse_classifiers()
#
#         metric_df = pd.DataFrame(self.metrics)
#         data = {
#             "classifiers": metric_df["classifier"],
#             "Accuracy_data": metric_df["accuracy"],
#             "AUC": metric_df["auc"],
#             "F1": metric_df["f1_score"],
#             "Precision": metric_df["precision"],
#             "Recall": metric_df["recall"],
#             "Matthews": metric_df["mcc"],
#         }
#
#         if len(self.specificity) == len(self.classifiers):
#             data["Specificity"] = self.specificity
#
#         output_file = self.graph_output_dir + sep  + f"{'test' if self.test else 'train'}-summary.tsv"
#         pd.DataFrame(self.metrics).to_csv(output_file)
#
#
#     def make_method_summary_graphs(self):
#         """
#         Generates and saves summary bar charts for F1 scores, accuracy, and AUC for each method.
#
#         This method creates bar charts to visualize the F1 scores, accuracy percentages, and AUC
#         values for different machine learning classifiers. The charts are saved as high-resolution
#         PNG files in the specified output directory.
#
#         The method produces the following charts:
#         - F1 Score Chart: Displays the F1 scores for each method using different colors.
#         - Accuracy Chart: Displays the accuracy percentages for each method with hatched patterns.
#         - AUC Chart: Displays the Area Under the Curve (AUC) values for each method if AUC data
#         is available.
#
#         Charts are saved to the `graphs` subdirectory within the specified `output_dir`.
#
#         Attributes:
#         ----------
#         classifiers : list
#             A list of method names for which summaries are being created.
#         f1_data : list
#             A list of F1 scores corresponding to each method.
#         accuracy_data : list
#             A list of accuracy percentages corresponding to each method.
#         auc_data : list
#             A list of AUC values corresponding to each method.
#         output_dir : str
#             The directory path where the generated charts will be saved.
#         hatch_gradients : list
#             A list of hatch patterns to apply to the bars for visual differentiation.
#
#         """
#         metrics_df = pd.DataFrame(self.metrics)
#         fig1, f1_plot = plt.subplots(figsize=(10, 6))
#         f1_plot.bar(self.classifiers, metrics_df["f1_score"], color=["black", "red", "green", "blue", "cyan"])
#         f1_plot.set_title("F1 chart")
#         f1_plot.set_ylabel("F1")
#         f1_plot.set_ylim(0.5, 1)
#         plt.xticks(rotation=55, horizontalalignment="center")
#         fig1.savefig(
#             self.output_dir
#             + sep
#             + "graphs"
#             + sep
#             + "Summary_"
#             + self.machine_learning_output_data.characteristic
#             + "_BarChartF1.png",
#             bbox_inches="tight",
#             dpi=1200
#         )
#         plt.close(fig1)
#
#         # Accuracy
#         fig2, accuracy_plot = plt.subplots(figsize=(10, 6))
#         accuracy_plot.bar(self.classifiers, metrics_df["accuracy"], hatch=self.hatch_gradients[0:len(metrics_df["accuracy"])], color="grey")
#         accuracy_plot.set_title("Accuracy chart ")
#         accuracy_plot.set_ylabel("Accuracy")
#         plt.xticks(rotation=30, horizontalalignment="center")
#         accuracy_plot.set_ylim(0.5, 1)
#         fig2.savefig(
#             self.output_dir
#             + sep
#             + "graphs"
#             + sep
#             + "Summary_"
#             + self.machine_learning_output_data.characteristic
#             + "_BarChartAccuracy.png",
#             bbox_inches="tight",
#             dpi=1200
#         )
#         plt.close(fig2)
#
#         # AUC
#         fig3, ax = plt.subplots(figsize=(10, 6))
#         ax.bar(x=self.classifiers, height=metrics_df["auc"], hatch=self.hatch_gradients[0:len(metrics_df["auc"])], color="grey")
#         plt.xticks(rotation=30, horizontalalignment="center")
#         ax.set_ylabel("AUC")
#         fig3.savefig(
#             self.output_dir
#             + sep
#             + "graphs"
#             + sep
#             + "Summary_"
#             + self.machine_learning_output_data.characteristic
#             + "_BarChartAUC.png",
#             bbox_inches="tight",
#             dpi=1200
#         )
#         plt.close(fig3)
#
#         # AUC
#         fig4, ax = plt.subplots(figsize=(10, 6))
#         ax.bar(x=self.classifiers, height=metrics_df["mcc"], hatch=self.hatch_gradients[0:len(metrics_df["mcc"])], color="grey")
#         plt.xticks(rotation=30, horizontalalignment="center")
#         ax.set_ylabel("Matthew correlation coefficient")
#         fig4.savefig(
#             self.output_dir
#             + sep
#             + "graphs"
#             + sep
#             + "Summary_"
#             + self.machine_learning_output_data.characteristic
#             + "_BarChartMCC.png",
#             bbox_inches="tight",
#             dpi=1200
#         )
#         plt.close(fig4)
#         # This code is unneeded as of now, but in case I forget something.
#         plt.close('all')
#
#
#     def _probability_histogram(self, probability_classes: pd.DataFrame(dtype="float64"), observed_values_string: pd.DataFrame(), method_graph_output_dir: str):
#         """
#         Generates and saves probability histograms for each class in the probability data.
#
#         This method creates histograms that illustrate the distribution of predicted probabilities
#         for true and false observations of each class. The histograms are saved as images in the
#         specified output directory.
#
#         Parameters:
#         ----------
#         probability_classes : pd.DataFrame
#             A DataFrame containing the probability scores for each class. Each column corresponds
#             to a different class, and rows represent individual predictions.
#         observed_values_string : pd.DataFrame
#             A DataFrame containing the observed values as strings, used to differentiate between
#             true and false instances in the histogram.
#         method_graph_output_dir : str
#             The directory path where the generated histograms will be saved.
#         """
#         for column in probability_classes.columns:
#             true_df, false_df = probability_divider(
#                 observed_values_string=observed_values_string,
#                 name_probability = column,
#                 single_characteristic_probability=probability_classes[column].reset_index(drop=True),
#             )
#             prob_hist, (prob_hist_fig) = plt.subplots(1, 1, figsize=(10, 10))
#             # Create a histogram that showcases the various confidence values for predictions.
#             prob_hist_fig.hist([true_df, false_df], label=[column, "rest"])
#
#             plt.title("Probability histogram: " + column)
#             legend = plt.legend(loc="upper left", fancybox=True)
#             legend.set_alpha(None)
#             prob_hist.savefig(
#                 method_graph_output_dir
#                 + sep
#                 + "Summary_"
#                 + self.machine_learning_output_data.characteristic
#                 + "_"
#                 + column.replace(".", "").replace("/", "")
#                 + "_probability_hist.png",
#                 bbox_inches="tight",
#                 dpi=1200
#             )
#
#     def analyse_classifiers(self):
#         """
#         Analyzes machine learning classifiers and returns a summary DataFrame
#         containing metrics and ROC/precision-recall data.
#
#         Creates
#         -------
#         metrics_df : pd.DataFrame
#             DataFrame containing F1 score, accuracy, precision, recall, Matthews correlation coefficient,
#             specificity, and AUC for each classifier.
#         roc_data_df : pd.DataFrame
#             DataFrame containing False Positive Rate (FPR), True Positive Rate (TPR), and AUC values
#             for each classifier.
#         prc_data_df : pd.DataFrame
#             DataFrame containing Precision, Recall, and positive class base rate for each classifier.
#         """
#
#         for classifier in self.classifiers:
#             if not path.isdir(path.join(self.graph_output_dir, classifier)):
#                 makedirs(path.join(self.graph_output_dir, classifier))
#
#             method_graph_output_dir = self.graph_output_dir + sep + classifier + sep
#             (
#                 observed_values,
#                 predicted_values,
#                 observed_values_string,
#                 probability_classes,
#             ) = self.machine_learning_output_data.get_results_for_method(classifier, self.test)
#
#             if observed_values.empty:
#                 raise FileNotFoundError(
#                     f"No result file could be found in directory: {path.join(self.output_dir, classifier)}"
#                 )
#
#             # Compute basic metrics
#             f1 = f1_score(observed_values, predicted_values, average="micro")
#             accuracy = accuracy_score(observed_values, predicted_values)
#             precision = precision_score(observed_values, predicted_values, average="micro")
#             recall = recall_score(observed_values, predicted_values, average="micro")
#             mcc = matthews_corrcoef(observed_values, predicted_values)
#
#             # Handle multiclass and binary classification cases
#             if len(probability_classes.columns) > 2:  # Multiclass
#                 aucs = []
#                 for i, class_name in enumerate(probability_classes.columns):
#                     observed_binary = [
#                         1 if class_name == obs else 0
#                         for obs in observed_values_string.tolist()
#                     ]
#                     precision, recall, _ = precision_recall_curve(
#                         observed_binary, probability_classes.iloc[:, i]
#                     )
#                     fpr, tpr, _ = roc_curve(
#                         observed_binary, probability_classes.iloc[:, i]
#                     )
#                     auc_value = auc(fpr, tpr)
#
#                     # Append ROC and PRC data
#                     self.roc_data.append(
#                         {"classifier": classifier, "class": class_name, "fpr": fpr, "tpr": tpr, "auc": auc_value}
#                     )
#                     self.prc_data.append(
#                         {"classifier": classifier, "class": class_name, "precision": precision, "recall": recall}
#                     )
#                     aucs.append(auc_value)
#
#             else:  # Binary classification
#                 tn, fp, fn, tp = confusion_matrix(observed_values, predicted_values).ravel()
#                 specificity = tn / (tn + fp)
#                 positive_classname = probability_classes.columns[1]
#                 observed_binary = [
#                     1 if positive_classname == obs else 0
#                     for obs in observed_values_string.tolist()
#                 ]
#                 precision, recall, _ = precision_recall_curve(
#                     observed_binary, probability_classes.iloc[:, 1]
#                 )
#                 fpr, tpr, _ = roc_curve(
#                     observed_binary, probability_classes.iloc[:, 1]
#                 )
#                 auc_value = auc(fpr, tpr)
#
#                 # Append ROC and PRC data
#                 self.roc_data.append(
#                     {"classifier": classifier, "class": positive_classname, "fpr": fpr, "tpr": tpr, "auc": auc_value}
#                 )
#                 self.prc_data.append(
#                     {"classifier": classifier, "class": positive_classname, "precision": precision, "recall": recall}
#                 )
#                 aucs = [auc_value]
#
#             self.metrics.append(
#                     {
#                         "classifier": classifier,
#                         "f1_score": f1,
#                         "precision": precision,
#                         "recall": recall,
#                         "accuracy": accuracy,
#                         "mcc": mcc,
#                         "auc": sum(aucs) / len(aucs),  # Average AUC
#                     }
#                 )
#
#         # Create DataFrames from metrics and ROC/PRC data
#         metrics_df = pd.DataFrame(self.metrics)
#         roc_data_df = pd.DataFrame(self.roc_data)
#         prc_data_df = pd.DataFrame(self.prc_data)
#         self._plot_classifiers_performance(metrics_df, roc_data_df, prc_data_df)
#
#
#     def _plot_classifiers_performance(self, metrics_df, roc_data_df, prc_data_df):
#         """
#         Generates and saves performance graphs for multiple classifiers.
#
#         Parameters
#         ----------
#         metrics_df : pd.DataFrame
#             DataFrame containing core metrics (F1, accuracy, precision, recall, etc.) for each classifier.
#         roc_data_df : pd.DataFrame
#             DataFrame containing False Positive Rate (FPR), True Positive Rate (TPR), and AUC values for each classifier.
#         prc_data_df : pd.DataFrame
#             DataFrame containing Precision and Recall values for each classifier.
#         """
#         # Set up the style for the plots
#         sns.set(style="whitegrid")
#         plt.figure(figsize=(12, 8))
#
#         ### Plot ROC Curve
#         fig, ax_roc = plt.subplots(figsize=(10, 6))
#         for _, row in roc_data_df.iterrows():
#             ax_roc.plot(row["fpr"], row["tpr"], label=f"{row['classifier']} ({row['class']}, AUC={row['auc']:.3f})")
#
#         ax_roc.plot([0, 1], [0, 1], "k--", label="Chance (AUC=0.5)")
#         ax_roc.set_title("ROC Curve ", fontsize=14)
#         ax_roc.set_xlabel("False Positive Rate (FPR)", fontsize=12)
#         ax_roc.set_ylabel("True Positive Rate (TPR)", fontsize=12)
#         ax_roc.legend(loc="lower right", fontsize=10)
#         plt.tight_layout()
#         plt.savefig(f"{self.output_dir}/roc_curve_all_classifiers.png", dpi=300)
#
#         # Plot Precision-Recall Curve
#         fig, ax_prc = plt.subplots(figsize=(10, 6))
#         for _, row in prc_data_df.iterrows():
#             ax_prc.plot(row["recall"], row["precision"], label=f"{row['classifier']} ({row['class']})")
#
#         ax_prc.set_title("Precision-Recall Curve (All Classifiers)", fontsize=14)
#         ax_prc.set_xlabel("Recall", fontsize=12)
#         ax_prc.set_ylabel("Precision", fontsize=12)
#         # ax_prc.axhline( # TODO Get the number of positive samples and set the baseline.
#         #     y=row["precision"].mean(), color="gray", linestyle="--", label=f"Base Rate ({row['precision'].mean():.2f})"
#         # )
#         ax_prc.legend(loc="lower left", fontsize=10)
#         plt.tight_layout()
#         plt.savefig(f"{self.output_dir}/precision_recall_curve_all_classifiers.png", dpi=300)
#
#         ### Summary Metrics Bar Plot
#         fig, ax_metrics = plt.subplots(figsize=(10, 6))
#         metrics_df.plot(
#             x="classifier",
#             y=["f1_score", "accuracy", "auc", "mcc"],
#             kind="bar",
#             ax=ax_metrics,
#         )
#         ax_metrics.set_title("Performance Metrics by Classifier", fontsize=14)
#         ax_metrics.set_ylabel("Score", fontsize=12)
#         ax_metrics.set_xlabel("Classifier", fontsize=12)
#         ax_metrics.legend(loc="lower right", fontsize=10)
#         plt.tight_layout()
#         plt.savefig(f"{self.output_dir}/{self.test}classifier_metrics_summary.png", dpi=300)
#
#         print(f"Plots saved to {self.output_dir}")

class CommandLineInterface:
    def __init__(self):
        self.args = self.parse_arguments()

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o",
            "--output_dir",
            help="Location of the overarching directory. ",
            type=str
        )
        return parser.parse_args()

class CommandLineTest:
    def __init__(self):
        self.args = self.parse_arguments()

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o",
            "--output_dir",
            help="Location of the overarching directory. ",
            type=str,
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/iteration_1"
        )
        parser.add_argument("--test", help="Run in test mode", action="store_true")
        return parser.parse_args()

class MachineLearningData:
    """
    A class for parsing machine learning output files and extracting data.

    Attributes:
        output_dir_path (str): The directory path where the output files are located.
        characteristic (str): A characteristic of the machine learning data.
    """

    def __init__(self, output_dir_path: str):
        """
        Initializes a MachineLearningData object.

        Args:
            output_dir_path (str): The directory path where the output files are located.
        """
        self.output_dir_path = output_dir_path
        self.characteristic = "machine_learning_summary"
        self.n_data = 0
        self.classifiers = self.list_output_classfiers(self.output_dir_path)

    @staticmethod
    def list_output_classfiers(output_dir: str):
        """
        List the classifier directories in the output directory, excluding certain subdirectories.

        Args:
            output_dir (str): The path to the output directory.

        Returns:
            list: A list of classifier directory names.
        """

        
        # Use glob to find all directories that end with "Classifier"
        pattern = path.join(output_dir, "**", "*Classifier")
        classifiers = glob.glob(pattern, recursive=True)
        
        # Filter out non-directories
        return list(set([d.split(sep)[-1] for d in classifiers if path.isdir(d)]))


    @staticmethod
    def output_file_data_parsing(list_of_files: list) -> pd.DataFrame:
        """
        Parses output files in the specified directory and extracts relevant data.

        Returns:
            Tuple: A tuple containing observed values, predicted values, observed values as strings,
                   and probability classes.
        """
        observed_values = pd.Series(dtype="float64")
        observed_values_string = pd.Series(dtype="float64")
        predicted_values = pd.Series(dtype="float64")
        probability_classes = pd.DataFrame(dtype="float64")

        for file in list_of_files:
            ml_output_df = pd.read_csv(file, delimiter="\t", header=0)
            columns = ml_output_df.columns
            if ("Observation" in columns and "Prediction" in columns and "ObservedString" in columns):
                observed_values = pd.concat([observed_values, ml_output_df["Observation"]])
                predicted_values = pd.concat([predicted_values, ml_output_df["Prediction"]])
                observed_values_string = pd.concat(
                    [observed_values_string, ml_output_df["ObservedString"]]
                )
                if len(observed_values) != len(predicted_values):
                    print("Mismatch between the observed and predicted values in file:", file)

                class_names = ml_output_df.columns[6:-1]  # Assuming class names start from column 6
                probability_classes = pd.concat(
                    [probability_classes, ml_output_df[class_names]], ignore_index=True
                )

        return (
            observed_values,
            predicted_values,
            observed_values_string.reset_index(drop=True),
            probability_classes
        )

    def get_results_for_method(self, method: str, test="test") -> pd.DataFrame:
        """
        Retrieves results for a method used from the output files.

        Args:
            method (str): The method for which results are requested.
            test (bool): default is True, whether you only to have only the test case if False uses the train output.
        Returns:
            Tuple: A tuple containing observed values, predicted values, observed values,
                   and probability classes for the specified method.
        Raises:
            ValueError: If the method file is not present.

        """
        file_search = f"*-{test}-output.tsv"

        list_of_output_files_for_method = [output_file for output_file in glob.glob(path.join(self.output_dir_path, "**", file_search), recursive=True) if method in output_file]
        if not list_of_output_files_for_method:
            raise FileNotFoundError("No output files were found for method '{}' using regex {}.".format(method, file_search))

        return self.output_file_data_parsing(list_of_output_files_for_method)

def main():
    cli = CommandLineTest() if '--test' in argv else CommandLineInterface()
    machine_learning_output_data = MachineLearningData(cli.args.output_dir)
    # Train
    summary_graphs = SummaryGraphs(machine_learning_output_data, cli.args.output_dir)
    summary_graphs.analyse_classifiers()
    summary_graphs.make_method_summary_graphs()
    summary_graphs.output_scores_to_table()

    # Test
    summary_graphs = SummaryGraphs(machine_learning_output_data, cli.args.output_dir, False)
    summary_graphs.analyse_classifiers()
    summary_graphs.make_method_summary_graphs()
    summary_graphs.output_scores_to_table()

if __name__ == "__main__":
    main() 