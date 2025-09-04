import os
from pathlib import Path

from migenpro.ml.machine_learning_main import FeatureMatrix, PhenotypeMatrix, MachineLearningModels
from migenpro.post_analysis.ml_model_analysis import LoadedMachineLearningModel, ModelAnalysis
from migenpro.post_analysis.ml_summarise import MachineLearningData, SummaryGraphs
from migenpro.querying.genome_annotation import GenomeAnnotationWorkflow
from migenpro.querying.query_executor import QueryExecutor
from migenpro.querying.query_parser import *

def argument_parser():
    """
    Argument parser for the migenpro package.
    This function sets up the command line arguments for the main function.
    """
    import argparse

    parser = argparse.ArgumentParser(description="migenpro package main function")
    parser.add_argument("--config", type=str, help="Path to configuration file", required=False)
    parser.add_argument("--output", type=str, help="Output directory", required=False)
    args, _ = parser.parse_known_args()

    return args

def main() -> None:
    """
    Main function to execute the machine learning workflow.
    This function sets up the environment, runs queries, processes phenotypes,
    and performs machine learning analysis.
    """
    # Set the working directory to the script's directory
    print("Hello, this is the main function of the migenpro package.")
    args = argument_parser()

    print("These are the arguments passed to the main function:")
    print(args)

def other() -> None:
    """
    Another function that can be used for additional processing or testing.
    """
    print("This is another function in the migenpro package.")
    ############################### VARIABLES ########################################
    print(os.getcwd())
    bacdive_hdt = "/home/WUR/looma017/git/genopro/data/bacdive.hdt"
    all_phenotypes = ["spore","motility","oxygen","gram","ph", "temperature"]
    classifiers = ["DecisionTreeClassifier", "GradientBoostingClassifier", "RandomForestClassifier"]

    param_grids = {
        "DecisionTreeClassifier": {
            "max_depth": [3, 5, 10, 15],
        },
        "RandomForestClassifier": {
            "n_estimators": [50, 100, 200, 500, 1000, 2000],
            "max_depth": [5, 10, 20, 30],
            "min_samples_leaf": [1,10,100,200],
            "min_samples_split": [2, 5, 10]
        },
        "GradientBoostingClassifier": {
            "n_estimators": [50, 100, 200, 500, 1000],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 5, 7],
            "min_samples_split": [2, 5, 10],
        }
    }

    ############################### PHENOTYPES #######################################
    # Parse and run queries

    # for phenotype in all_phenotypes:
    #     query = f"/home/mike/git/genopro//migenpro/resources/sparql_phenotype/{phenotype}.sparql"
    #     output_file = f"/home/mike/git/genopro/data/phenotype_output/{phenotype}_output/phenotype.tsv"
    #
    #     # run query
    #     qe = QueryExecutor(query_file=query)
    #     qe.execute_sapp_locally_file(hdt_file=bacdive_hdt, output_file=output_file)
    #     # qe.execute_sapp_in_docker_single_file(hdt_file=bacdive_hdt, output_file=output_file)
    #     # Parse query
    #     phenotype_output = QueryParser(file_path=output_file)
    #     # phenotype_output.filter_by_relative_frequency(0.005)
    #     phenotype_output.filter_by_absolute_frequency(500)
    #     phenotype_output.filter_by_species_frequency(10)
    #     phenotype_output.convert_to_phenotype_matrix()
    #     phenotype_output.write_phenotype_matrix_to_file(output_file.replace("phenotype.tsv", "phenotype_matrix.tsv"))


    ########################### ANNOTATION ####################################
    # Now that we have gathered the phenotypes and their corresponding genomes we want to annotate these genomes.
    # To avoid annotating the same genome multiple times we take the unique genomes and annotate them for accession later.
    # unique_genomes = set()
    #
    # for phenotype in all_phenotypes:
    #     matrix_file = f"data/phenotypes/{phenotype}_output/phenotype_matrix.tsv"
    #
    #     # Read matrix file and collect genomes
    #     with open(matrix_file, 'r') as f:
    #         header = next(f)
    #         for line in f:
    #             genome_id = line.split('\t')[0] # Assuming first column is genome ID
    #             unique_genomes.add(genome_id)

    # genome_list = list(unique_genomes)
    # print(f"Found {len(genome_list)} unique genomes for annotation")
    # # Create input file list (assuming genomes are stored as individual FASTA files)
    # with open("data/genomes_to_annotate.txt", "w") as f:
    #     for genome_id in genome_list:
    #         # Assuming this path structure exists
    #         f.write(f"data/genomes/{genome_id}.fa\n")
    #
    #
    # # Initialize annotation processor
    # annotation_processor = GenomeAnnotationWorkflow(
    #     output_dir="data/annotations",
    #     threads=4
    # )
    #
    # annotation_processor.process_batch(list(unique_genomes))

    ###################
    ## Start analysis #
    ###################


    best_parameters = {}
    for phenotype in all_phenotypes:
        feature_matrix = f"/home/mike/git/genopro/data/phenotype_output/{phenotype}_output/protein_domains.tsv"
        phenotypeMatrix = f"/home/mike/git/genopro/data/phenotype_output/{phenotype}_output/phenotype_matrix.tsv"
        output = f"/home/mike/git/genopro/data/phenotype_output/{phenotype}_output/"

        print("""
        ###############
        ## Load data for {phenotype} ##
        ###############""")

        feature_matrix = FeatureMatrix(feature_matrix)
        feature_matrix.load_matrix()
        phenotype_matrix = PhenotypeMatrix(phenotypeMatrix)
        phenotype_matrix.load_matrix()
        intersect_genomes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
        feature_matrix_subset = feature_matrix.create_subset(intersect_genomes)
        phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes)

        # Smoke
        assert len(feature_matrix_subset.index) == len(phenotype_matrix_subset.index.unique())

        models = MachineLearningModels(classifiers=classifiers)
        models.set_datasets(feature_matrix_subset, phenotype_matrix_subset, "smoten", 20)
        # models.perform_grid_search(param_grids=param_grids)

        best_parameters[phenotype] = models.perform_halving_grid_search_search(param_grids=param_grids, cv=5)
        for classifier in classifiers:
            print(f"Best params for prediction {phenotype} using {classifier}: {best_parameters.get(phenotype)}\n\n")

        # for classifier in classifiers:



        ################################
        ## Five fold cross validation ##
        ################################

        # for i in range(1, 6):
        #     current_iteration_output_dir = path.join(output, f"iteration_{i}")
        #     print(f"""
        #     ##############################################
        #     ## Train and predict models: Iteration: {i}   ##
        #     ############################################## """)
            # models = MachineLearningModels(dt_depth=best_parameters[phenotype].get("dt_depth"),
            #                                rf_depth=best_parameters[phenotype].get("rf_depth"),
            #                                gb_depth=best_parameters[phenotype].get("gb_depth"),
            #                                num_trees=best_parameters[phenotype].get("num_trees"),
            #                                max_iter=best_parameters[phenotype].get("max_iter"),
            #                                output=current_iteration_output_dir, proportion_train=0.7,
            #                                rf_min_leaf=best_parameters[phenotype].get("rf_min_leaf"),
            #                                rf_min_split=best_parameters[phenotype].get("rf_min_split"),
            #                                gb_min_samples=best_parameters[phenotype].get("gb_min_samples"),
            #                                gb_learning_rate=best_parameters[phenotype].get("gb_learning_rate"),
            #                                classifiers=classifiers)
            # models.set_datasets(feature_matrix_subset, phenotype_matrix_subset,'SMOTEN',20)
            # models.train_models(n_jobs = 20)
            # models.predict_models_test()
            # models.predict_models_train()
            # models.save_models()

            # print("""
            # #####################
            # ## Method analysis ##
            # #####################""")
            # machine_learning_output_data = MachineLearningData(output)
            # summary_graphs = SummaryGraphs(machine_learning_output_data, current_iteration_output_dir, False)
            # summary_graphs.analyse_classifiers()
            # summary_graphs.make_method_summary_graphs()
            # summary_graphs.output_scores_to_table()
            #
            # summary_graphs = SummaryGraphs(machine_learning_output_data, current_iteration_output_dir)
            # summary_graphs.analyse_classifiers()
            # summary_graphs.make_method_summary_graphs()
            # summary_graphs.output_scores_to_table()

            # print("""
            # ####################
            # ## Model analysis ##
            # ####################""")

            # for model_path in models.get_pickled_models():
            #     if not path.isdir(str(current_iteration_output_dir)):
            #         os.makedirs(str(current_iteration_output_dir) + os.sep)
            #
            #     model = LoadedMachineLearningModel(model_path)
            #     print("Starting model analysis for " + model.model_name)
            #
            #     modelAnalysis = ModelAnalysis(phenotype, model, feature_matrix_subset, phenotype_matrix_subset)
            #     if model.gini:
            #         figure_gini_path = (
            #                 current_iteration_output_dir
            #                 + os.sep
            #                 + f"gini_feature_importance_figure_iteration_{i}"
            #                 + model.model_name
            #                 + "_"
            #                 + phenotype
            #                 + ".png"
            #         )
            #
            #         gini_figure_summary_path = (
            #                 current_iteration_output_dir
            #                 + os.sep
            #                 + f"gini_feature_importance_summary__iteration_{i}"
            #                 + model.model_name
            #                 + "_"
            #                 + phenotype
            #                 + ".tsv"
            #         )
            #
            #         modelAnalysis.gini_feature_importance(figure_gini_path, gini_figure_summary_path, 10)


if __name__ == "__main__":
    main()
    other()