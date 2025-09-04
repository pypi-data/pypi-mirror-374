"""
CWL-based microbial genome annotation pipeline.

This module provides a command-line interface and workflow execution logic
for annotating microbial genomes using Common Workflow Language (CWL) pipelines.
"""
from os import makedirs
import argparse
import logging
from pathlib import Path
from typing import Optional, Union
import re
from tqdm import tqdm  # Added for download progress
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandLineInterface:
    """Handles command-line argument parsing and validation.

    Attributes:
        args (argparse.Namespace): Parsed command-line arguments
    """

    def __init__(self) -> None:
        """Initialize the command line interface and parse arguments."""
        self.args = self.parse_arguments()

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse and validate command-line arguments.

        Returns:
            argparse.Namespace: Parsed command-line arguments

        Raises:
            argparse.ArgumentError: If invalid arguments are provided
        """
        parser = argparse.ArgumentParser(
            description="CWL Workflow Runner for Microbial Genome Annotation",
            epilog="Example: python annotate.py -i genomes.txt -c workflow.cwl -o results"
        )

        parser.add_argument(
            "-i", "--input",
            required=True,
            help="Path to file containing list of input FASTA files",
            type=Path,
            metavar="FILE"
        )

        parser.add_argument(
            "-c", "--cwl",
            required=True,
            help="URL or path to CWL workflow file",
            type=str,
            metavar="URL_OR_PATH"
        )

        parser.add_argument(
            "-o", "--output",
            default=Path("results"),
            help="Output directory path (default: %(default)s)",
            type=Path,
            metavar="DIR"
        )

        parser.add_argument(
            "-t", "--threads",
            default=2,
            help="Number of parallel threads to use (default: %(default)s)",
            type=int,
            choices=range(1, 65),
            metavar="[1-64]"
        )

        return parser.parse_args()


class GenomeAnnotationWorkflow:
    """Manages execution of genome annotation workflows using CWL.

    Attributes:
        cwl_file (Path | link): Resolved path or link to CWL workflow.
        output_dir (Path): Directory for workflow outputs
        threads (int): Number of parallel threads to use
        cache_dir (Path): Directory for cached remote resources
    """
    def __init__(
            self,
            output_dir: str | Path,
            threads: int = 2,
            cache_dir: Optional[Path] = None
        ) -> None:
        """Initialize the workflow runner.

        Args:
            output_dir: Directory for workflow outputs
            threads: Number of parallel execution threads
            cache_dir: Cache directory for remote resources

        Raises:
            FileNotFoundError: If local CWL file doesn't exist
            ValueError: For invalid thread counts
        """
        self.output_dir = output_dir.resolve() if isinstance(output_dir, Path) else Path(output_dir).resolve()
        self.threads = threads
        self.cache_dir = cache_dir or Path("cwl_cache")
        self.cwl_file = "https://workflowhub.eu/workflows/1170/git/1/raw/workflow_microbial_annotation_packed.cwl"
        self._validate_environment()

    def _validate_environment(self) -> None:
        """Validate system environment and dependencies."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate_input_template(self, fasta_path: str, yaml_file_path: Path | str):
        """Generate YAML input template for a FASTA file.
        Args:
            yaml_file_path:  yaml file path
            fasta_path: Path to input FASTA file
        """
        template = f"""
            cwl:tool: {self.cwl_file}
            threads: {self.threads}
            genome_fasta:
                class: File
                location: {fasta_path}
            """

        with open(yaml_file_path, "w") as f:
            f.write(template)

    @staticmethod
    def execute_workflow(yaml_input: Path, specific_output_dir: str):
        """Execute CWL workflow with given input parameters.

        Args:
            yaml_input: Path to YAML input file

        Raises:
            cwltool.errors.WorkflowException: For workflow execution errors
        """
        try:
            command = f"cwltool --no-warnings --outdir {specific_output_dir} {yaml_input} "
            # Run cwltool and capture output
            result = subprocess.run(
                command,
                check=True,
                shell=True,
                capture_output=True,
                text=True
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def process_batch(self, fasta_paths: str | list[str] ) -> None:
        """Process a batch of genomes from various input types.
        Args:
            fasta_paths:
                - A single FASTA path or URL
                - A list of FASTA paths or URLs
                - A path to a file containing FASTA paths or URLs
        Raises:
            ValueError: For empty input or invalid formats
        """

        def is_url(s: str) -> bool:
            """Check if str is url"""
            return bool(re.match(r'^https?://', s.strip()))

        if isinstance(fasta_paths, (str, Path)):
            fasta_paths = str(fasta_paths).strip()
            path_obj = Path(fasta_paths)

            if not is_url(fasta_paths) and path_obj.is_file() and path_obj.suffix not in [".fasta", ".fa", "fasta.gz", "fna.gz"]:
                # It's a list file containing paths or URLs
                with open(path_obj, "r") as f:
                    fasta_paths = [line.strip() for line in f if line.strip()]
            else:
                # It's a single FASTA file or URL either is fine.
                fasta_paths = [fasta_paths]
        elif isinstance(fasta_paths, list):
            fasta_paths = [str(p).strip() for p in fasta_paths if p]
        else:
            raise ValueError("Invalid input type for fasta_paths")
        if not fasta_paths:
            raise ValueError("No valid FASTA paths or URLs provided")

        for fasta in tqdm(fasta_paths, desc="Annotating genomes"): # for progress
            # try:
            genome_identifier = re.match(r".*/(.*[0-9]{9}\.[0-9]{1}.*)/", fasta).group(1)
            yaml_file_path = Path(self.output_dir) / f"{genome_identifier}.yaml"
            specific_output_dir = Path(self.output_dir) / f"{genome_identifier}_annotation"

            makedirs(specific_output_dir, exist_ok=True)

            self.generate_input_template(fasta, yaml_file_path)
            result = self.execute_workflow(yaml_file_path, specific_output_dir=specific_output_dir)
            logger.debug(f"Annotation results: {result}")

if __name__ == "__main__":
    """Main execution entry point."""
    try:
        cli = CommandLineInterface()
        args = cli.args

        workflow = GenomeAnnotationWorkflow(
            cwl_source=args.cwl,
            output_dir=args.output,
            threads=args.threads
        )

        workflow.process_batch(args.input)
        logger.info("Annotation pipeline completed successfully")

    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}")
        raise SystemExit(1) from e