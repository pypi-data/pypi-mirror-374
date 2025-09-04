from migenpro.ml.machine_learning_main import *
from migenpro.post_analysis.ml_summarise import *
from migenpro.post_analysis.ml_model_analysis import *
from os import path

class CommandLineInterface:
    def __init__(self):
        self.args = self.parse_arguments()
    
    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser()

        num_trees_arg = parser.add_argument(
            "-t", 
            "--num_trees", 
            help="number of trees used in rf.", 
            default=100, 
            type=int
        )
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
        max_iter_arg = parser.add_argument(
            "--gb_max_iter",
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
        max_iter_arg = parser.add_argument(
            "-m", 
            "--max_iter", 
            help="maximum number of iterations", 
            default=100, 
            type=int
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
            help="The absolute path to the phenotype that is going to be analysed, granted it is automatically generated. ",
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
            default=3,
            type=int
        )
        phenotype_arg = parser.add_argument(
            "-phenotype",
            "--phenotype",
            default="spore",
            type=str
        )
        rfe_arg = parser.add_argument(
            "-rfe",
            "--rfe",
            default=False,
            type=bool
        )
        parser.add_argument("--oversample", help="Oversample train dataset to a maximum of two", action="store_true")

        args = parser.parse_args()

        # Validate args #
        if args.num_trees < 1:
            raise argparse.ArgumentError(
                num_trees_arg, "Number of trees must be greater than 0."
            )
        if args.max_iter < 1:
            raise argparse.ArgumentError(
                max_iter_arg, "Maximum number of iterations must be greater than 0."
            )
        if args.proportion_train < 0 or args.proportion_train > 1:
            raise argparse.ArgumentError(
                proportion_train_arg, "Proportion of training data must be between 0 and 1, not \"{args.proportion_train}\""
            )
        if args.train and not isfile(args.input):
            raise argparse.ArgumentError(input_arg, f"Phenotype matrix file {args.input} does not exist you cannot train model without supervision.")
        if not isfile(args.feature_matrix):
            raise argparse.ArgumentError(
                feature_matrix_arg, f"Genome feature matrix file {args.feature_matrix} does not exist."
            )
        if args.model_load != "" and not isfile(args.model_load):
            raise argparse.ArgumentError(
                model_load_arg,
                "Model load path {args.model_load} does not exist, to specify a model to use --l <model_file.pkl>",
            )
        if args.model_load != "" and not isfile(args.model_load).split(".")[-1] == "pkl":
            raise argparse.ArgumentError(
                model_load_arg,
                "Model file {args.model_load} is not a pickled file, to specify a model to use --l <model_file.pkl>",
            )

        if not(args.train or args.predict):
            raise argparse.ArgumentError(train_arg, "Either --train/-n  or --predict/-r must be true.")

        return args

class CommandLineTest:
    def __init__(self):
        self.args = self.parse_arguments()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser()

        num_trees_arg = parser.add_argument(
            "-t", 
            "--num_trees", 
            help="number of trees used in rf.", 
            default=100, 
            type=int
        )
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
        max_iter_arg = parser.add_argument(
            "--gb_max_iter",
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
        max_iter_arg = parser.add_argument(
            "--max_iter", 
            help="maximum number of iterations", 
            default=100, 
            type=int
        )
        proportion_train_arg = parser.add_argument(
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
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/phenotype_matrix.tsv",
            type=path.abspath,
        )
        output_arg = parser.add_argument(
            "-o",
            "--output",
            help="Location for file containing predictions and true values. ",
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/",
            type=path.abspath,
        )
        feature_matrix_arg = parser.add_argument(
            "-a",
            "--feature_matrix",
            # default="/home/mike-loomans/git/genopro/data/phenotype_output/spore_output/protein_domains.tsv",
            default="/home/mike-loomans/git/genopro/data/phenotype_output/temperature_output/protein_domains.tsv",
            type=path.abspath,
        )
        threads_arg = parser.add_argument(
            "-j",
            "--threads",
            default=3,
            type=int
        )
        phenotype_arg = parser.add_argument(
            "-phenotype",
            "--phenotype",
            default="spore",
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


if __name__ == "__main__":
    cli = CommandLineTest() if '--test' in argv else CommandLineInterface()
    print("""
    ###############
    ## Load data ##
    ###############""")
    feature_matrix = FeatureMatrix(cli.args.feature_matrix)
    feature_matrix.load_matrix()
    phenotype_matrix = PhenotypeMatrix(cli.args.input)
    phenotype_matrix.load_matrix()
    intersect_genomes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
    feature_matrix_subset = feature_matrix.create_subset(intersect_genomes)
    phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes)

    # Automatically remove duplicate indexes, keeping the first instance
    phenotype_matrix_subset = phenotype_matrix_subset[~phenotype_matrix_subset.index.duplicated(keep='first')]

    ################################
    ## Five fold cross validation ##
    ################################

    for i in range(1,6):
        current_iteration_output_dir = path.join(cli.args.output, f"iteration_{i}")
        print(f"""
        ##############################################
        ## Train and predict models: Iteration: {i}   ##
        ############################################## """)
        models = MachineLearningModels(dt_depth=cli.args.dt_depth, rf_depth=cli.args.rf_depth,
                                       gb_depth=cli.args.gb_depth, num_trees=cli.args.num_trees,
                                       max_iter=cli.args.max_iter, output=current_iteration_output_dir,
                                       proportion_train=cli.args.proportion_train, rf_min_leaf=cli.args.rf_min_leaf,
                                       rf_min_split=cli.args.rf_min_split, gb_min_samples=cli.args.gb_min_samples,
                                       gb_learning_rate=cli.args.gb_learning_rate, classifiers=classifiers)
        # models.set_datasets(feature_matrix_subset, phenotype_matrix_subset, cli.args.oversample, cli.args.threads)
        # models.train_models(n_jobs = cli.args.threads) 
        # models.predict_models_test()
        # models.predict_models_train()
        # models.save_models()

        print("""
        #####################
        ## Method analysis ##
        #####################""")
        machine_learning_output_data = MachineLearningData(cli.args.output)
        summary_graphs = SummaryGraphs(machine_learning_output_data, current_iteration_output_dir, False)
        summary_graphs.analyse_classifiers()
        summary_graphs.make_method_summary_graphs()
        summary_graphs.output_scores_to_table()

        summary_graphs = SummaryGraphs(machine_learning_output_data, current_iteration_output_dir)
        summary_graphs.analyse_classifiers()
        summary_graphs.make_method_summary_graphs()
        summary_graphs.output_scores_to_table()

        print("""
        ####################
        ## Model analysis ##
        ####################""")

        for model_path in models.get_pickled_models():
            if not path.isdir(str(current_iteration_output_dir)):
                makedirs(str(current_iteration_output_dir) + sep)

            model = LoadedMachineLearningModel(model_path)
            print("Starting model analysis for " + model.model_name)
            
            modelAnalysis = ModelAnalysis(cli.args.phenotype, model, feature_matrix_subset, phenotype_matrix_subset)
            if model.gini:
                figure_gini_path = (
                    current_iteration_output_dir
                    + sep
                    + f"gini_feature_importance_figure_iteration_{i}"
                    + model.model_name
                    + "_"
                    + cli.args.phenotype
                    + ".png"
                    )

                gini_figure_summary_path = (
                    current_iteration_output_dir
                    + sep
                    + f"gini_feature_importance_summary__iteration_{i}"
                    + model.model_name
                    + "_"
                    + cli.args.phenotype
                    + ".tsv"
                    )

                modelAnalysis.gini_feature_importance(figure_gini_path, gini_figure_summary_path, 10)
        
        # Performing rfe each iteration is excessive and takes a long time.
        if cli.args.rfe:
            print("Performing recursive feature elimination and assesing feature importance, this might take a while...")
            figure_rfe_path = (
                str(cli.args.output)
                + sep
                + "rfe_feature_importance_figure_iteration"
                + model.model_name
                + "_"
                + cli.args.phenotype
                + ".png"
                )
            modelAnalysis.rfe_feature_importance(figure_rfe_path, 1)
            print("RFE feature importance analysis is finished. ")
