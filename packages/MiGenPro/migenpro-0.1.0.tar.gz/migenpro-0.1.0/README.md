# Migenpro
![Coverage](https://gitlab.com/wurssb/migenpro/badges/package_creation/coverage.svg)
![codequality](https://migenpro-0402eb.gitlab.io/pylint.svg)


## Getting started

###
Pull the git repo:
```bash
git pull git@gitlab.com:pig-paradigm/migenpro.git
cd migenpro
```

### Installing the needed dependencies. 
A pip requirements.txt file is located in the installation directory which you can install using the following command.

```bash 
conda create -n migenpro python=3.12.5 pip --file installation/requirements.txt
```

### Annotating genomes using SAPP
To annotate genomes we use a cwltool workflow with SAPP that output the desired genome annotations in hdt files.

```bash 
cwltool --no-warnings --outdir ./data https://gitlab.com/m-unlock/cwl/-/raw/dev/workflows/workflow_microbial_annotation.cwl --genome_fasta https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/005/845/GCA_000005845.2_ASM584v2/GCA_000005845.2_ASM584v2_genomic.fna.gz
```
Luckily we have automated this process within the python package. 

### Training machine learning models 
```bash
python3 src/main/resources/python/machineLearning.py \
    --featureMatrix ./output/phentype_matrix.tsv \
    --phenotypeMatrix output/protein_domain_matrix.tsv \
    --model_load [Location_of_model] \
    --train
    --predict
```


### Predicting phenotypes with existing models
You can do this through the docker container or from the source code. 
1. You will need to obtain a protein domain matrix of the desired genomes you can do this using the java code. 
2. For ease of use we will use the python scripts that were made with the following command. The default output directory is "output/mloutput" if desired you can change this using the --output [output\_directory\_location]

```bash
python3 src/main/resources/python/machineLearning.py \
    --featureMatrix ./output/phentype_matrix.tsv \
    --model_load [Location_of_model] \
    --predict
```

3. Wait for the script to finish and retrieve the results of your prediction from the output directory. 
There the predictions are given in the following format: 

```text
################################################
# Genome # Phenotype # Prediction # Confidence #
# GCA123 # Temprature # mesophilic # 0.96      #
################################################
```

## Recreating the results from the study
The files needed to recreate our results are located in the `./data/phenotype_output` folder. We use the previously created `protein_domain.tsv` and `phenotype.tsv` files. 
Run the `create_graphs.sh`  bash script 
```bash 
./recreate.sh
```
