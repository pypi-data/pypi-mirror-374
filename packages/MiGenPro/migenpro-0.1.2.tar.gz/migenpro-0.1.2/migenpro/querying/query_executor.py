"""Utilities for executing SPARQL queries via SAPP.

This module provides the QueryExecutor class for running SPARQL queries over HDT
files using the SAPP tool, either locally (via Java) or inside Docker. It also
contains helpers for summarising output and a small CLI argument parser.
"""
import argparse
import glob
import logging
import os
import subprocess
import urllib
from concurrent import futures
from pathlib import Path
from re import match
from shutil import which
from typing import Union
from urllib.error import URLError

import pandas as pd
from importlib_resources import files
import docker

from migenpro.logger_utils import get_logger


class QueryExecutor:
    """
    Execute SPARQL queries using SAPP locally or inside Docker, and summarise results.
    """

    def __init__(self, query_file: str, sapp_jar_path: str = "binaries/sapp.jar", java_jar: str = "java", debug=False):
        """
        Initialize the QueryExecutor with the Docker image and SPARQL query file.

        Args:
            query_file (str): The path to the SPARQL query file.
            sapp_jar_path (str): Path to SAPP JAR file.
        """
        if debug:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                     log_level=logging.DEBUG)
        else:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                     log_level=logging.INFO)

        self.sapp_jar_url = "http://download.systemsbiology.nl/sapp/SAPP-2.0.jar"
        self.sapp_jar_path = sapp_jar_path
        self.image = "docker-registry.wur.nl/m-unlock/docker/sapp:2.0"
        self.query_file = query_file
        self.java_jar = java_jar

        if match(r"sparql.*:.*.\.sparql", self.query_file): # is resources file
            query_path_resources = str(files("migenpro.resources").joinpath(os.sep.join(self.query_file.split(":"))))
            self.logger.debug("Path to query located in resources: %s", query_path_resources)
            with open(query_path_resources) as f:
                self.query_content = f.read()
        else:
            self.logger.debug("Path to query located in %s", self.query_file)
            with open(self.query_file) as reading_query_file:
                self.query_content = reading_query_file.read()

        self.query_content = self.format_sparql_query(self.query_content)

    @staticmethod
    def format_sparql_query(query_content):
        """Formats read sparql string into a oneliner that can be passed in the cli. """
        lines = query_content.split('\n')
        lines_without_comments = [line.split('#')[0] for line in lines] # Remove everything after comment
        query_without_comments = ' '.join(lines_without_comments) # remove \n
        one_liner = query_without_comments.replace('\t', ' ') # no tabs
        one_liner = ' '.join(one_liner.split()) # join together.
        return one_liner

    def _java_installed(self):
        return bool(which("java"))

    def _download_sapp(self):
        if not os.path.isfile(self.sapp_jar_path):
            self.logger.info(f"Downloading SAPP.jar to {self.sapp_jar_path}...")
            os.makedirs(os.path.dirname(self.sapp_jar_path), exist_ok=True)
            try:
                urllib.request.urlretrieve(self.sapp_jar_url, self.sapp_jar_path)
            except URLError as e:
                self.logger.error(f"Error downloading SAPP.jar: {e}.")
                self.logger.error("Manually download from: https://gitlab.com/sapp/sapp.gitlab.io/-/blob/main/docs/installation.md")
                raise e

            self.logger.info("Download completed.")

    def execute_sapp_locally_directory(self, hdt_directory: str, output_directory: str=None, regex: str = "*.hdt.gz",
                                       redistribute=False) -> list[str] | str:
        """
        Executes the SAPP (SPARQL over HDT) tool locally on HDT files found in the specified directory.
        Args:
            redistribute: Assign if you want to redistribute the combined output file based on the GenomeID.
            hdt_directory (str): The directory containing HDT files.
            output_directory (str): The directory where the output TSV files will be saved.
            regex (str, optional): The regex pattern to match HDT files. Defaults to "*.hdt.gz".
        """

        if self._java_installed():
            self._download_sapp()
        else:
            raise EnvironmentError("Java has not been installed. ")

        if output_directory is None:
            output_directory = hdt_directory

        os.makedirs(output_directory, exist_ok=True)

        abs_hdt_files = glob.glob(os.path.join(hdt_directory, "**", regex), recursive=True)
        combined_output_queries_file_path = os.path.join(output_directory, "combined_output.tsv")
        if not abs_hdt_files:
            raise FileNotFoundError(f"No HDT files matched pattern {regex} in {hdt_directory}")

        command = [
            "java", "-jar", str(self.sapp_jar_path),
            "-sparql",
            "-query", f"{self.query_content}",
            "-i", hdt_directory,
            "-r",
            "-o", combined_output_queries_file_path
            ]
        self.logger.debug(" ".join(command))

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
            self.logger.debug(result.stdout)
            assert len(glob.glob(os.path.join(output_directory, "*.tsv"))) > 0
        except Exception as e:
            self.logger.error(" ".join(command))
            self.logger.error("Error running SAPP for %s:\n%s", hdt_directory, e)

        # Get the directory path of the HDT file
        self.logger.debug("All queries executed. Output saved to %s", output_directory)
        if redistribute:
            return self._redistribute_combined_output_output(output_directory, combined_output_queries_file_path)
        else:
            return os.path.join(output_directory, "combined_output.tsv")

    def execute_sapp_locally_file(self, hdt_file: str, output_file: str) -> None:
        """
        Executes the SAPP (SPARQL over HDT) tool locally on a single HDT file.

        Args:
            hdt_file (str): The path to the HDT file.
            output_file (str): The path to the output TSV file.

        Raises:
            FileNotFoundError: If the HDT file does not exist.
        """
        if not os.path.isfile(hdt_file):
            raise FileNotFoundError(f"The HDT file {hdt_file} does not exist.")

        if self._java_installed():
            self._download_sapp()

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        command = [
            "java", "-jar", self.sapp_jar_path,
            "-sparql",
            "-query", f"{self.query_content}",
            "-i", hdt_file,
            "-o", output_file
        ]

        self.logger.info(f"Running query on: {os.path.basename(hdt_file)}")
        self.logger.debug(" ".join(command))
        print(" ".join(command))
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
            print(result.stdout)
        except Exception as e:
            self.logger.error(" ".join(command))
            self.logger.error("Error running SAPP for %s:\n%s", hdt_file, e)

        self.logger.info(f"\nQuery executed. Output saved to {output_file}")

    def execute_sapp_in_docker(self, genome_hdt_directory: str, output_directory: str, regex: str):
        """
        Execute SPARQL query using SAPP in a Docker container for multiple HDT files.

        Args:
            genome_hdt_directory (str): The path to the directory containing HDT files.
            output_directory (str): The path to the output dir where the results will be saved.
            regex (str): The regex pattern to match HDT files.
        """
        if not os.path.isdir(genome_hdt_directory):
            raise FileNotFoundError(f"The HDT directory {genome_hdt_directory} does not exist.")

        abs_hdt_files = glob.glob(os.path.join(genome_hdt_directory, "**", regex), recursive=True)
        if not abs_hdt_files:
            raise FileNotFoundError(f"No HDT files matched pattern {regex} in {genome_hdt_directory}")

        os.makedirs(output_directory, exist_ok=True)

        client = docker.from_env()
        try:
            print(f"Pulling Docker image: {self.image}")
            client.images.pull(self.image)

            for hdt_file in abs_hdt_files:
                base_name = os.path.basename(hdt_file)
                output_path = os.path.join(output_directory, f"{os.path.splitext(base_name)[0]}.tsv")
                self.logger.debug(f"output_path genome query: {output_path}")
                # Prepare volumes
                hdt_dir = os.path.dirname(os.path.abspath(hdt_file))
                query_dir = os.path.dirname(os.path.abspath(self.query_file))
                output_dir_abs = os.path.dirname(os.path.abspath(output_path))


                # The command to run inside the container
                container_hdt_path = f"/hdt/{os.path.basename(hdt_file)}"
                container_output_path = f"/output/{os.path.basename(output_path)}"

                command = [
                    "java", "-jar", "/binaries/sapp.jar",
                    "-sparql",
                    "-query", f"{self.query_content}",
                    "-i", container_hdt_path,
                    "-o", container_output_path
                ]

                self.logger.info(f"Running query on: {base_name}")
                container = client.containers.run(
                    image=self.image,
                    command=command,
                    volumes={
                        self.sapp_jar_path: {'bind': '/binaries/sapp.jar', 'mode': 'ro'},
                        query_dir: {'bind': '/data', 'mode': 'ro'},
                        hdt_dir: {'bind': '/hdt', 'mode': 'ro'},
                        output_dir_abs: {'bind': '/output', 'mode': 'rw'}
                    },
                    detach=True,
                    remove=True,
                    stdout=True,
                    stderr=True
                )

                # Capture the logs of the container
                for log in container.logs(stream=True):
                    print(log.strip().decode('utf-8'))

            self.logger.info(f"\nAll queries executed. Output saved to {output_directory}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            client.close()

    def execute_sapp_in_docker_single_file(self, hdt_file: str, output_file: str) -> None:
        """
        Execute SPARQL query using SAPP in a Docker container for a single HDT file.

        Args:
            hdt_file (str): The path to the HDT file.
            output_file (str): The path to the output file where the results will be saved.
        """
        if not os.path.isfile(hdt_file):
            raise FileNotFoundError(f"The HDT file {hdt_file} does not exist.")

        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        client = docker.from_env()
        try:
            self.logger.info(f"Pulling Docker image: {self.image}")
            client.images.pull(self.image)

            # Prepare volumes
            hdt_dir = os.path.dirname(os.path.abspath(hdt_file))
            query_dir = os.path.dirname(os.path.abspath(self.query_file))
            output_dir_abs = os.path.dirname(os.path.abspath(output_file))

            # The command to run inside the container
            container_hdt_path = f"/hdt/{os.path.basename(hdt_file)}"
            container_output_path = f"/output/{os.path.basename(output_file)}"

            command = [
                "java", "-jar", "/binaries/sapp.jar",
                "-sparql",
                "-query", f"{self.query_content}", # container_query_path,
                "-i", container_hdt_path,
                "-o", container_output_path
            ]

            self.logger.info(f"Running query on: {os.path.basename(hdt_file)}")
            container = client.containers.run(
                image=self.image,
                command=command,
                volumes={
                    self.sapp_jar_path: {'bind': '/binaries/sapp.jar', 'mode': 'ro'},
                    # query_dir: {'bind': '/data', 'mode': 'ro'},
                    hdt_dir: {'bind': '/hdt', 'mode': 'ro'},
                    output_dir_abs: {'bind': '/output', 'mode': 'rw'}
                },
                detach=True,
                remove=True,
                stdout=True,
                stderr=True
            )

            # Capture the logs of the container
            for log in container.logs(stream=True):
                print(log.strip().decode('utf-8'))

            self.logger.info("\nQuery executed. Output saved to %s", output_file)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            client.close()

    def summarise_feature_importance_files(self, feature_file_paths: Union[set | list], feature_matrix_file_path: str,
                                           threads: int = 1):
        """
        Summarise multiple genome TSV files into a single TSV file.
        Correctly handles input format: genomeID, accession, count

        Args:
            feature_file_paths: (set|list) Files in tsv format.
            feature_matrix_file_path: (str) feature matrix output path.
            threads: (int): Number of threads to use.
        """

        def read_and_process_file(file) -> pd.DataFrame:
            """Read a TSV file and pivot to create a wide-format row per genome"""
            self.logger.debug(f"now reading {os.path.abspath(file)} ")
            print(f"now reading {os.path.abspath(file)}")
            try:
                # Read TSV with expected columns
                df = pd.read_csv(file, sep='\t')

                # Extract column names
                genome_col = df.columns[0]
                accession_col = df.columns[1]
                feature_col = df.columns[2]

                df_wide = df.pivot_table(
                    index=genome_col,
                    columns=accession_col,
                    values=feature_col,
                    aggfunc='sum',  # Sum counts if duplicate entries exist
                    fill_value=0
                )

                df_wide.reset_index(inplace=True)

                return df_wide

            except Exception as e:
                self.logger.error(f"Error processing {file}: {str(e)}")
                return pd.DataFrame()

        if not feature_file_paths:
            raise ValueError("feature_file_paths must be non-empty. No TSV files found.")

        with futures.ThreadPoolExecutor(max_workers=threads) as executor:
            list_of_dfs = list(executor.map(read_and_process_file, feature_file_paths))

        list_of_dfs = [df for df in list_of_dfs if not df.empty]

        if not list_of_dfs:
            merged_matrix = pd.DataFrame(columns=['Genomes'])
        else:
            merged_matrix = pd.concat(list_of_dfs, ignore_index=True)
            genome_col = merged_matrix.columns[0]  # First column is genome ID
            merged_matrix = merged_matrix.copy()
            merged_matrix = merged_matrix.groupby(genome_col, as_index=False).sum()
            merged_matrix.rename(columns={genome_col: 'Genomes'}, inplace=True)
        #todo Genomes as  GCA_000429345 While phenotypes as GCA_002924615.1
        merged_matrix.to_csv(feature_matrix_file_path, sep='\t', index=False)


    @staticmethod
    def _redistribute_combined_output_output(output_directory: str, combined_output_queries_file_path: str) -> list[str]:
        """
        Take the combined output file and distribute rows into per-genome TSV files.
        Expected combined file format (no header):
            GenomeID\tFeature\tValue
            "GCA_009759665"\t"PF08269"\t2
        Each per-genome file will include a header: GenomeID,Feature,Value.
        Files are written to:
            <output_directory>/genomes/<genome[:7]>/<genome[:10]>/<genome>_annotation/<genome>.tsv
        Returns a list of written file paths.
        """
        written_files: list[str] = []
        combined_path = Path(combined_output_queries_file_path)
        if not combined_path.exists() or combined_path.stat().st_size == 0:
            return written_files

        # Read combined TSV (no header)
        df = pd.read_csv(
            combined_path,
            sep="\t",
            header=0,
            dtype={"GenomeID": str, "Feature": str, "Value": "Int64"}
        )
        df.columns = ["GenomeID", "Feature", "Value"]

        if df.empty:
            return written_files

        # Strip surrounding quotes if present
        for col in ["GenomeID", "Feature"]:
            df[col] = df[col].astype(str).str.strip().str.strip('"').str.strip("'")

        # Group by genome and write files
        for genome_identifier, grp in df.groupby("GenomeID"):
            # Determine per-genome directory structure
            base_dir = Path(output_directory)
            specific_output_dir = (
                base_dir
                / "genomes"
                / genome_identifier[:7]
                / genome_identifier[:10]
                / f"{genome_identifier}_annotation"
            )
            specific_output_dir.mkdir(parents=True, exist_ok=True)

            out_file = specific_output_dir / f"{genome_identifier}_features.tsv"
            grp.to_csv(out_file, sep="\t", header=True, index=False)
            written_files.append(str(out_file))

        # Optionally remove the combined file to avoid mixing with per-genome outputs
        try:
            combined_path.unlink(missing_ok=True)
        except Exception:
            # Non-fatal if we cannot delete
            pass

        return written_files


def command_line_interface_query_executor(previously_unparsed_args: argparse.Namespace) -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    Raises:
        argparse.ArgumentError: If invalid arguments are provided
    """

    # Define the pre-configured options
    pre_configured_options = {
        "sparql_genome": [
            "DomainCopyNumber.sparql",
            "DomainEvalue.sparql",
            "featuresInGenomePerGene.sparql",
            "GenesAroundDomain.sparql",
            "GetGenes.sparql",
            "ProteinDomainsInGene.sparql"
        ],
        "sparql_phenotype": [
            "gram.sparql",
            "motility.sparql",
            "oxygen.sparql",
            "ph.sparql",
            "spore.sparql",
            "temperature.sparql"
        ]
    }

    parser = argparse.ArgumentParser(description='Parse command-line arguments for querying with SPARQL.')

    parser.add_argument(
        '--phenotype_query_file',
        type=str,
        help=f'Path to the SPARQL query file. pre_configured_options: sparql_phenotype:{pre_configured_options.get("sparql_phenotype")}'
    )
    parser.add_argument(
        '--genome_query_file',
        type=str,
        help=f'Path to the SPARQL query file. pre_configured_options: sparql_genome:{pre_configured_options.get("sparql_genome")}'
    )
    parser.add_argument(
        '--phenotype_hdt_file',
        type=str,
        help=f'Phenotype hdt file.'
    )
    parser.add_argument(
        '--rel_frequency',
        type=float,
        help='Relative abundance threshold for filtering phenotypes.'
    )
    parser.add_argument(
        '--abs_frequency',
        type=int,
        default=500,
        help='Absolute threshold for filtering phenotype. Default 500.'
    )
    parser.add_argument(
        '--species_frequency',
        type=int,
        default=10,
        help='Maximum number of genomes belonging to a species. Default 10.'
    )
    parser.add_argument(
        '--sapp_jar',
        type=str,
        default="./binaries/SAPP-2.0.jar",
        help='Directory to store/download the SAPP JAR file.'
    )

    args, _ = parser.parse_known_args(previously_unparsed_args)
    if not (args.phenotype_query_file or args.genome_query_file):
        raise ValueError("Provide either --phenotype_query_file or --genome_query_file to specify SPARQL query.")

    return args