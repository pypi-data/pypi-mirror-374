from migenpro.querying.query_parser import QueryParser
from migenpro.ml.machine_learning_main import *
from migenpro.post_analysis.ml_model_analysis import *
from os import path

class CommandLineTest:
    def __init__(self):
        self.args = self.parse_arguments()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser()
        num_trees_arg = parser.add_argument(
            "-t", "--num_trees", help="number of trees used in rf.", default=10, type=int
        )
        depth_arg = parser.add_argument(
            "-d", "--depth", help="depth of each tree in the forest", default=3, type=int
        )
        max_iter_arg = parser.add_argument(
            "-m", "--max_iter", help="maximum number of iterations", default=10, type=int
        )
        proportion_train_arg = parser.add_argument(
            "-p",
            "--proportion_train",
            help="proportion of dataset that is used for training",
            default=0.7,
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
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/phenotype.tsv",
            type=path.abspath,
        )
        output_arg = parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/mloutput/",
            type=path.abspath,
        )
        feature_matrix_arg = parser.add_argument(
            "-a",
            "--feature_matrix",
            # default="/home/mike/git/genopro/data/phenotype_output/spore_output/protein_domains.tsv",
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/protein_domains.tsv",
            type=path.abspath,
        )
        threads_arg = parser.add_argument(
            "-j",
            "--threads",
            default=1,
            type=int
        )
        phenotype_arg = parser.add_argument(
            "-phenotype",
            "--phenotype",
            default="temperature",
            type=str
        )
        rfe_arg = parser.add_argument(
            "-rfe",
            "--rfe",
            default=False,
            type=bool
        )
        parser.add_argument("--oversample", help="Oversample train dataset to a maximum of two", )
        parser.add_argument("--test", help="Run in test mode", action="store_true")
        return parser.parse_args()


param_grids = {
    "DecisionTreeClassifier": {
        "max_depth": [3, 5, 10, 15],
    },
    "RandomForestClassifier": {
        "n_estimators": [50, 100, 200],
        "max_depth": [5, 10, 20, 30],
        "min_samples_leaf": [1,10,100,200],
        "min_samples_split": [2, 5, 10]
    },
    "GradientBoostingClassifier": {
        "n_estimators": [50, 100, 200],
        "learning_rate": [0.01, 0.1, 0.2],
        "max_depth": [3, 5, 7],
        "min_samples_split": [2, 5, 10],
    }
}

if __name__ == "__main__":
    cli = CommandLineTest()
    print("""
        ###############
        ## Load data ##
        ###############""")
    feature_matrix = FeatureMatrix(cli.args.feature_matrix)
    feature_matrix.load_matrix()
    
    
    phenotype_output = QueryParser(file_path=cli.args.input)
    input_matrix = cli.args.input.replace("phenotype.tsv", "phenotype_matrix.tsv")
    phenotype_output.filter_by_absolute_frequency(300)
    phenotype_output.convert_to_phenotype_matrix()
    phenotype_output.write_phenotype_matrix_to_file(input_matrix)

    phenotype_matrix = PhenotypeMatrix(input_matrix)
    phenotype_matrix.load_matrix()
    intersect_genomes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
    feature_matrix_subset = feature_matrix.create_subset(intersect_genomes)
    phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes)

    # Automatically remove duplicate indexes, keeping the first instance
    phenotype_matrix_subset = phenotype_matrix_subset[~phenotype_matrix_subset.index.duplicated(keep='first')]

    models = MachineLearningModels(num_trees=cli.args.num_trees, max_iter=cli.args.max_iter, output=cli.args.output,
                                   proportion_train=cli.args.proportion_train, classifiers=classifiers)
    models.set_datasets(feature_matrix_subset, phenotype_matrix_subset, cli.args.oversample, cli.args.threads)
    # models.perform_grid_search(param_grids=param_grids)
    models.perform_halving_grid_search_search(param_grids=param_grids, label=cli.args.phenotype)
    # models.save_models()



            #     param_grids (dict): A dictionary where keys are classifier names and values are parameter grids.
            # cv (int): Number of cross-validation folds. Default is 5.
            # scoring (str): Scoring metric for evaluating model performance. Default is "matthews".
            # n_jobs (int): Number of parallel jobs to run. Default is -1 (use all processors).
