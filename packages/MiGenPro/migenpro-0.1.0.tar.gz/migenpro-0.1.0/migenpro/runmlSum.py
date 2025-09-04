from migenpro.post_analysis.ml_summarise import *

#                _                               _       _     _           
#               (_)                             (_)     | |   | |          
#   __ _ ___ ___ _  __ _ _ __   __   ____ _ _ __ _  __ _| |__ | | ___  ___ 
#  / _` / __/ __| |/ _` | '_ \  \ \ / / _` | '__| |/ _` | '_ \| |/ _ \/ __|
# | (_| \__ \__ \ | (_| | | | |  \ V / (_| | |  | | (_| | |_) | |  __/\__ \
#  \__,_|___/___/_|\__, |_| |_|   \_/ \__,_|_|  |_|\__,_|_.__/|_|\___||___/
#                   __/ |                                                  
#                  |___/                                 

phenotypes = ["gram", "motility"] # , "", "temperature" ]
metrics = ['Accuracy_data', 'AUC', 'F1', 'Precision', 'Recall', 'Matthews']
bar_width = 0.15 
classifiers = ["DecisionTreeClassifier", "GradientBoostingClassifier", "RandomForestClassifier"]
dir_with_multiple_phentype_outputs = "/home/mike-loomans/git/genopro/data/phenotype_output"


for phenotype in phenotypes:
    for classifier in classifiers:
        # Generate the list of test output file paths for different iterations
        test_output_dirs = [f"{dir_with_multiple_phentype_outputs}/{phenotype}_output/mloutput/protein_domains/iteration_{iteration}" for iteration in range(1, 6)]

        for output_dir in test_output_dirs:
            machine_learning_output_data = MachineLearningData(output_dir)
            summary_graphs = SummaryGraphs(machine_learning_output_data, output_dir)
            summary_graphs.analyse_classifiers()
            summary_graphs.make_method_summary_graphs()
            summary_graphs.output_scores_to_table()

