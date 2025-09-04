import os
import glob
import subprocess
import urllib
from shutil import which
import docker

class QueryExecutor:
    """
    A class to execute SPARQL queries using SAPP in a Docker container.

    Attributes:
        image (str): The Docker image to use for executing the SPARQL queries.
        query_file (str): The path to the SPARQL query file.
    """

    def __init__(self, query_file: str, sapp_jar_dir: str = "./"):
        """
        Initialize the QueryExecutor with the Docker image and SPARQL query file.

        Args:
            query_file (str): The path to the SPARQL query file.
            sapp_jar_dir (str): Directory to store/download the SAPP JAR file.
        """
        self.sapp_jar_url = "http://download.systemsbiology.nl/sapp/dev/SAPP-2.0.jar"
        self.sapp_jar_path = os.path.join(sapp_jar_dir, "SAPP-2.0.jar")
        self.image = "docker-registry.wur.nl/m-unlock/docker/sapp:2.0"
        self.query_file = query_file

    def _java_installed(self):
        return bool(which("java"))

    def _download_sapp(self):
        if not os.path.isfile(self.sapp_jar_path):
            print(f"Downloading SAPP-2.0.jar to {self.sapp_jar_path}...")
            urllib.request.urlretrieve(self.sapp_jar_url, self.sapp_jar_path)
            print("Download completed.")

    def execute_sapp_locally_directory(self, genome_hdt_directory: str, output_directory: str, regex: str = "*.hdt.gz"):
        """
        Executes the SAPP (SPARQL over HDT) tool locally on HDT files found in the specified directory.
        Args:
            genome_hdt_directory (str): The directory containing HDT files.
            output_directory (str): The directory where the output TSV files will be saved.
            regex (str, optional): The regex pattern to match HDT files. Defaults to "*.hdt.gz".
        """
        if self._java_installed():
            self._download_sapp()

        os.makedirs(output_directory, exist_ok=True)

        if not os.path.isdir(genome_hdt_directory):
            raise FileNotFoundError(f"The *directory* {genome_hdt_directory} does not exist.")

        abs_hdt_files = glob.glob(os.path.join(genome_hdt_directory, "**", regex), recursive=True)

        if not abs_hdt_files:
            raise FileNotFoundError(f"No HDT files matched pattern {regex} in {genome_hdt_directory}")

        for hdt_file in abs_hdt_files:
            base_name = os.path.basename(hdt_file)
            output_path = os.path.join(output_directory, f"{os.path.splitext(base_name)[0]}.tsv")

            command = [
                "java", "-jar", self.sapp_jar_path,
                "-sparql",
                "-query", self.query_file,
                "-i", hdt_file,
                "-o", output_path
            ]

            print(f"Running query on: {base_name}")
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error running SAPP for {base_name}:\n{e.stderr}")

        print(f"\nAll queries executed. Output saved to {output_directory}")

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
            "-query", self.query_file,
            "-i", hdt_file,
            "-o", output_file
        ]

        print(f"Running query on: {os.path.basename(hdt_file)}")
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error running SAPP for {os.path.basename(hdt_file)}:\n{e.stderr}")

        print(f"\nQuery executed. Output saved to {output_file}")

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

                # Prepare volumes
                hdt_dir = os.path.dirname(os.path.abspath(hdt_file))
                query_dir = os.path.dirname(os.path.abspath(self.query_file))
                output_dir_abs = os.path.dirname(os.path.abspath(output_path))

                # The command to run inside the container
                container_hdt_path = f"/hdt/{os.path.basename(hdt_file)}"
                container_query_path = f"/data/{os.path.basename(self.query_file)}"
                container_output_path = f"/output/{os.path.basename(output_path)}"

                command = [
                    "java", "-jar", "/SAPP-2.0.jar",
                    "-sparql",
                    "-query", container_query_path,
                    "-i", container_hdt_path,
                    "-o", container_output_path
                ]

                print(f"Running query on: {base_name}")
                container = client.containers.run(
                    image=self.image,
                    command=command,
                    volumes={
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

            print(f"\nAll queries executed. Output saved to {output_directory}")

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
            print(f"Pulling Docker image: {self.image}")
            client.images.pull(self.image)

            # Prepare volumes
            hdt_dir = os.path.dirname(os.path.abspath(hdt_file))
            query_dir = os.path.dirname(os.path.abspath(self.query_file))
            output_dir_abs = os.path.dirname(os.path.abspath(output_file))

            # The command to run inside the container
            container_hdt_path = f"/hdt/{os.path.basename(hdt_file)}"
            container_query_path = f"/data/{os.path.basename(self.query_file)}"
            container_output_path = f"/output/{os.path.basename(output_file)}"

            command = [
                "java", "-jar", "/SAPP-2.0.jar",
                "-sparql",
                "-query", container_query_path,
                "-i", container_hdt_path,
                "-o", container_output_path
            ]

            print(f"Running query on: {os.path.basename(hdt_file)}")
            container = client.containers.run(
                image=self.image,
                command=command,
                volumes={
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

            print(f"\nQuery executed. Output saved to {output_file}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            client.close()
