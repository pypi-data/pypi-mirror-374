"""Module containing the BiobbObject generic parent class."""
import difflib
import importlib
import os
import shutil
import warnings
import argparse
from logging import Logger
from pathlib import Path
from pydoc import locate
from sys import platform
from typing import Optional, Union
from biobb_common.configuration import settings
from biobb_common.command_wrapper import cmd_wrapper
from biobb_common.tools import file_utils as fu
from biobb_common import biobb_global_properties


class BiobbObject:
    """
    | biobb_common BiobbObject
    | Generic parent class for the rest of the Biobb clases.
    | The BiobbOject class contains all the properties and methods that are common to all the biobb blocks.

    Args:
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):

            * **io_dict** (*dict*) - ({}) Input/Output files dictionary.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash -c") Path to the binary executable of the container shell.
            * **container_generic_command** (*str*) - ("run") Which command typically run or exec will be used to execute your image.
            * **stage_io_dict** (*dict*) - ({}) Stage Input/Output files dictionary.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **disable_sandbox** (*bool*) - (False) Disable the use of temporal unique directories aka sandbox. Only for local execution.
            * **global_properties_list** (*list*) - ([]) list of global properties.
            * **chdir_sandbox** (*bool*) - (False) Change directory to the sandbox using just file names in the command line. Only for local execution.
            * **binary_path** (*str*) - ('') Path to the binary executable.
            * **disable_logs** (*bool*) - (False) Disable the logs.
            * **global_log** (*Logger object*) - (None) Log from the main workflow.
            * **out_log** (*Logger object*) - (None) Log from the step.
            * **err_log** (*Logger object*) - (None) Error log from the step.
            * **out_log_path** (*str*) - (None) Path to the log file.
            * **err_log_path** (*str*) - (None) Path to the error log file.
            * **can_write_console_log** (*bool*) - (True) Can write console log.
            * **can_write_file_log** (*bool*) - (True) Can write file log.
            * **prefix** (*str*) - (None) Prefix if provided.
            * **step** (*str*) - (None) Name of the step.
            * **path** (*str*) - ('') Absolute path to the step working dir.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **cmd** (*list*) - ([]) Command line list, NOT read from the dictionary.
            * **return_code** (*int*) - (0) Return code of the command execution, NOT read from the dictionary.
            * **timeout** (*int*) - (None) Timeout for the execution of the command.
            * **tmp_files** (*list*) - ([]) list of temporal files, NOT read from the dictionary.
            * **env_vars_dict** (*dict*) - ({}) Environment Variables dictionary.
            * **shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the shell.
            * **dev** (*str*) - (None) Development options.
            * **check_extensions** (*bool*) - (True) Check extensions of the input/output files.
            * **check_var_typing** (*bool*) - (True) Check typing of the input/output files.
            * **locals_var_dict** (*dict*) - ({}) Local variables dictionary.
            * **doc_arguments_dict** (*dict*) - ({}) Documentation arguments dictionary.
            * **doc_properties_dict** (*dict*) - ({}) Documentation properties dictionary.


    """

    def __init__(self, properties=None, **kwargs) -> None:  # type: ignore
        # Merge global properties, priorizating local ones
        properties = biobb_global_properties.dict() | properties or {}

        # Input/Output files
        self.io_dict: dict[str, dict[str, str]] = {"in": {}, "out": {}}

        # container Specific
        self.container_path: Optional[str] = properties.get("container_path")
        self.container_image: str = properties.get("container_image", '')
        self.container_volume_path: str = properties.get("container_volume_path", "/data")
        self.container_working_dir: Optional[str] = properties.get("container_working_dir")
        self.container_user_id: Optional[str] = properties.get("container_user_id")
        self.container_shell_path: str = properties.get("container_shell_path", "/bin/bash -c")
        self.container_generic_command: str = properties.get("container_generic_command", "run")

        # stage
        self.stage_io_dict: dict[str, dict[str, str]] = {"in": {}, "out": {}}
        self.sandbox_path: Union[str, Path] = properties.get("sandbox_path", Path().cwd())
        self.disable_sandbox: bool = properties.get("disable_sandbox", False)

        # Properties common in all BB
        self.global_properties_list: list[str] = properties.get("global_properties_list", [])
        self.chdir_sandbox: bool = properties.get("chdir_sandbox", False)
        self.binary_path: str = properties.get("binary_path", '')
        self.disable_logs: bool = properties.get("disable_logs", False)
        self.global_log: Optional[Logger] = properties.get("global_log", None)
        self.out_log: Optional[Logger] = None
        self.err_log: Optional[Logger] = None
        self.out_log_path: Optional[Union[Path, str]] = properties.get("out_log_path", None)
        self.err_log_path: Optional[Union[Path, str]] = properties.get("err_log_path", None)
        self.can_write_console_log: bool = properties.get("can_write_console_log", True)
        self.can_write_file_log: bool = properties.get("can_write_file_log", True)
        self.prefix: Optional[str] = properties.get("prefix", None)
        self.step: Optional[str] = properties.get("step", None)
        self.path: str = properties.get("path", "")
        self.remove_tmp: bool = properties.get("remove_tmp", True)
        self.restart: bool = properties.get("restart", False)
        self.cmd: list[str] = []
        self.return_code: int = 0
        self.timeout: Optional[int] = properties.get("timeout", None)
        self.tmp_files: list[Union[str, Path]] = []
        self.env_vars_dict: dict = properties.get("env_vars_dict", {})
        self.shell_path: Union[str, Path] = properties.get("shell_path", os.getenv("SHELL", "/bin/bash"))
        self.dev: Optional[str] = properties.get("dev", None)
        self.check_extensions: bool = properties.get("check_extensions", True)
        self.check_var_typing: bool = properties.get("check_var_typing", True)
        self.locals_var_dict: dict[str, str] = dict()
        self.doc_arguments_dict, self.doc_properties_dict = fu.get_doc_dicts(self.__doc__)

        try:
            self.version = importlib.import_module(
                self.__module__.split(".")[0]
            ).__version__
        except Exception:
            self.version = None

    def check_arguments(
            self,
            output_files_created: bool = False,
            raise_exception: bool = True
    ):
        for argument, argument_dict in self.doc_arguments_dict.items():
            fu.check_argument(
                path=Path(self.locals_var_dict[argument])
                if self.locals_var_dict.get(argument)
                else None,
                argument=argument,
                optional=argument_dict.get("optional", False),
                module_name=self.__module__,
                input_output=argument_dict.get(
                    "input_output", "").lower().strip(),
                output_files_created=output_files_created,
                type=argument_dict.get("type", None),
                extension_list=list(argument_dict.get("formats")),
                check_extensions=self.check_extensions,
                raise_exception=raise_exception,
                out_log=self.out_log,
            )
        if output_files_created:
            fu.log("", self.out_log, self.global_log)

    def check_properties(
        self,
        properties: dict,
        reserved_properties: Optional[set[str]] = None,
        check_var_typing: bool = False,
    ):
        if not reserved_properties:
            reserved_properties = set()
        reserved_properties = {"system", "working_dir_path", "tool"}.union(reserved_properties)
        reserved_properties = reserved_properties.union(set(self.global_properties_list))
        error_properties = set([prop for prop in properties.keys() if prop not in self.__dict__.keys()])

        # Check types
        if check_var_typing and self.doc_properties_dict:
            for prop, value in properties.items():
                if self.doc_properties_dict.get(prop):
                    property_type = self.doc_properties_dict[prop].get("type")
                    classinfo: object = locate(property_type).__class__
                    if classinfo == type:
                        classinfo = locate(property_type)
                    if not isinstance(value, classinfo):  # type: ignore
                        warnings.warn(
                            f"Warning: {prop} property type not recognized. Got {type(value)} Expected {locate(property_type)}"
                        )

        error_properties = set(
            [prop for prop in properties.keys() if prop not in self.__dict__.keys()]
        )
        error_properties -= reserved_properties
        for error_property in error_properties:
            close_property = difflib.get_close_matches(
                error_property, self.__dict__.keys(), n=1, cutoff=0.01
            )
            close_property = close_property[0] if close_property else ""  # type: ignore
            warnings.warn(
                "Warning: %s is not a recognized property. The most similar property is: %s"
                % (error_property, close_property)
            )

    def check_init(self, properties):
        """Check that the arguments and properties passed have the correct types and formats."""
        self.check_properties(properties)
        self.check_arguments()

    def check_restart(self) -> bool:
        if self.version:
            fu.log(
                f"Module: {self.__module__} Version: {self.version}",
                self.out_log,
                self.global_log,
            )

        if self.restart:
            if fu.check_complete_files(self.io_dict["out"].values()):  # type: ignore
                fu.log(
                    "Restart is enabled, this step: %s will the skipped" % self.step,
                    self.out_log,
                    self.global_log,
                )
                return True
        return False

    def stage_files(self):
        """Stage the input/output files in a temporal unique directory aka sandbox."""
        if self.disable_sandbox:
            self.stage_io_dict = self.io_dict.copy()
            # If we are not using a sandbox, we use the current working directory as the unique directory
            self.stage_io_dict["unique_dir"] = os.getcwd()
            return
        # Create a unique directory for the sandbox
        unique_dir = str(Path(fu.create_unique_dir(path=str(self.sandbox_path), prefix="sandbox_", out_log=self.out_log)).resolve())
        self.stage_io_dict = {"in": {}, "out": {}, "unique_dir": unique_dir}

        # Only remove unique_dir if using sandbox
        self.tmp_files.append(unique_dir)

        for io in ["in", "out"]:
            for file_ref, file_path in self.io_dict.get(io, {}).items():
                if not file_path:
                    # Skip optional files not set
                    continue
                file_path = Path(file_path)
                # Assign INTERNAL PATH to IN/OUT files
                if file_path.exists() or io == "out":
                    if io == "in":
                        fu.log(f"Copy to stage: {file_path} --> {unique_dir.split('/')[-1]}", self.out_log)
                        doc = self.doc_arguments_dict.get(file_ref)
                        if doc and doc['type'] == 'dir' and file_path.suffix != '.zip':
                            shutil.copytree(file_path, os.path.join(unique_dir, file_path.name))
                        else:
                            shutil.copy2(file_path, unique_dir)
                    # Container
                    if self.container_path:
                        self.stage_io_dict[io][file_ref] = os.path.join(self.container_volume_path, file_path.name)
                    # Local
                    else:
                        self.stage_io_dict[io][file_ref] = os.path.join(unique_dir, file_path.name)
                        if self.chdir_sandbox:
                            self.stage_io_dict[io][file_ref] = file_path.name
                elif io == "in":
                    # Default IN files in GMXLIB path like gmx_solvate -> input_solvent_gro_path (spc216.gro)
                    self.stage_io_dict[io][file_ref] = file_path

    def create_cmd_line(self) -> None:
        # Not documented and not listed option, only for devs
        if self.dev:
            fu.log(f"Adding development options: {self.dev}",
                   self.out_log, self.global_log)
            self.cmd += self.dev.split()

        # Containers
        host_volume: str = str(self.stage_io_dict.get("unique_dir", ''))
        self.container_path = self.container_path or ""
        # Singularity
        if self.container_path.endswith("singularity"):
            fu.log(
                "Using Singularity image %s" % self.container_image,
                self.out_log,
                self.global_log,
            )
            if not Path(self.container_image).exists():
                fu.log(
                    f"{self.container_image} does not exist trying to pull it",
                    self.out_log,
                    self.global_log,
                )
                container_image_name = str(
                    Path(self.container_image).with_suffix(".sif").name
                )
                singularity_pull_cmd = [
                    self.container_path,
                    "pull",
                    "--name",
                    container_image_name,
                    self.container_image,
                ]
                try:
                    from biobb_common.command_wrapper import cmd_wrapper

                    cmd_wrapper.CmdWrapper(
                        singularity_pull_cmd, self.shell_path, self.out_log
                    ).launch()
                    if Path(container_image_name).exists():
                        self.container_image = container_image_name
                    else:
                        raise FileNotFoundError
                except FileNotFoundError:
                    fu.log(
                        f"{' '.join(singularity_pull_cmd)} not found",
                        self.out_log,
                        self.global_log,
                    )
                    raise FileNotFoundError
            singularity_cmd = [
                self.container_path,
                self.container_generic_command,
                "-e",
            ]

            if self.env_vars_dict:
                singularity_cmd.append("--env")
                singularity_cmd.append(
                    ",".join(
                        f"{env_var_name}='{env_var_value}'"
                        for env_var_name, env_var_value in self.env_vars_dict.items()
                    )
                )

            singularity_cmd.extend(
                [
                    "--bind",
                    host_volume + ":" + self.container_volume_path,
                    self.container_image,
                ]
            )

            # If we are working on a mac remove -e option because is still no available
            if platform == "darwin":
                if "-e" in singularity_cmd:
                    singularity_cmd.remove("-e")

            if not self.cmd and not self.container_shell_path:
                fu.log(
                    "WARNING: The command-line is empty your container should know what to do automatically.",
                    self.out_log,
                    self.global_log,
                )
            else:
                cmd = ['"' + " ".join(self.cmd) + '"']
                singularity_cmd.append(self.container_shell_path)
                singularity_cmd.extend(cmd)
            self.cmd = singularity_cmd
        # Docker
        elif self.container_path.endswith("docker"):
            fu.log(
                "Using Docker image %s" % self.container_image,
                self.out_log,
                self.global_log,
            )
            docker_cmd = [self.container_path, self.container_generic_command]
            if self.env_vars_dict:
                for env_var_name, env_var_value in self.env_vars_dict.items():
                    docker_cmd.append("-e")
                    docker_cmd.append(f"{env_var_name}='{env_var_value}'")
            if self.container_working_dir:
                docker_cmd.append("-w")
                docker_cmd.append(self.container_working_dir)
            if self.container_volume_path:
                docker_cmd.append("-v")
                docker_cmd.append(host_volume + ":" + self.container_volume_path)
            if self.container_user_id:
                docker_cmd.append("--user")
                docker_cmd.append(self.container_user_id)

            docker_cmd.append(self.container_image)

            if not self.cmd and not self.container_shell_path:
                fu.log(
                    "WARNING: The command-line is empty your container should know what to do automatically.",
                    self.out_log,
                    self.global_log,
                )
            else:
                cmd = ['"' + " ".join(self.cmd) + '"']
                docker_cmd.append(self.container_shell_path)
                docker_cmd.extend(cmd)
            self.cmd = docker_cmd
        # Pcocc
        elif self.container_path.endswith("pcocc"):
            # pcocc run -I racov56:pmx cli.py mutate -h
            fu.log(
                "Using pcocc image %s" % self.container_image,
                self.out_log,
                self.global_log,
            )
            pcocc_cmd = [
                self.container_path,
                self.container_generic_command,
                "-I",
                self.container_image,
            ]
            if self.container_working_dir:
                pcocc_cmd.append("--cwd")
                pcocc_cmd.append(self.container_working_dir)
            if self.container_volume_path:
                pcocc_cmd.append("--mount")
                pcocc_cmd.append(host_volume + ":" + self.container_volume_path)
            if self.container_user_id:
                pcocc_cmd.append("--user")
                pcocc_cmd.append(self.container_user_id)

            if not self.cmd and not self.container_shell_path:
                fu.log(
                    "WARNING: The command-line is empty your container should know what to do automatically.",
                    self.out_log,
                    self.global_log,
                )
            else:
                cmd = ['\\"' + " ".join(self.cmd) + '\\"']
                pcocc_cmd.append(self.container_shell_path)
                pcocc_cmd.extend(cmd)
            self.cmd = pcocc_cmd
        # Local execution
        else:
            pass
            # fu.log('Not using any container', self.out_log, self.global_log)

    def execute_command(self):

        cwd = os.getcwd()
        if self.chdir_sandbox:
            os.chdir(self.stage_io_dict["unique_dir"])

        self.return_code = cmd_wrapper.CmdWrapper(
            cmd=self.cmd,
            shell_path=self.shell_path,
            out_log=self.out_log,
            err_log=self.err_log,
            global_log=self.global_log,
            env=self.env_vars_dict,
            timeout=self.timeout,
            disable_logs=self.disable_logs
        ).launch()

        if self.chdir_sandbox:
            os.chdir(cwd)

    def run_biobb(self):
        self.create_cmd_line()
        self.execute_command()

    def copy_to_host(self):
        """Copy output files from the sandbox to the host system."""
        for file_ref, file_path in self.stage_io_dict["out"].items():
            dest_path = Path(self.io_dict["out"][file_ref])

            # For directories, we need to ensure the directory exists in the sandbox
            if self.doc_arguments_dict[file_ref]['type'] == 'dir':
                # If the output is a directory, ensure it exists in the sandbox
                sandbox_dir_path = Path(self.stage_io_dict["unique_dir"]).joinpath(file_path)
                fu.log(f"Copy directory to host: {sandbox_dir_path} --> {dest_path}", self.out_log, self.global_log)
                fu.copytree_new_files_only(sandbox_dir_path, dest_path)
            else:
                if not file_path:
                    continue
                sandbox_file_path = Path(self.stage_io_dict["unique_dir"]).joinpath(Path(file_path).name)
                # Ensure file exists in the sandbox
                if not sandbox_file_path.exists():
                    continue
                # Only copy if destination doesn't exist or is different from source
                if not dest_path.exists() or not sandbox_file_path.samefile(dest_path):
                    shutil.copy2(sandbox_file_path, dest_path)

    def create_tmp_file(self, extension: str) -> None:
        """Create a temporary file in the unique directory. These files are
        removed when self.remove_tmp_files is called."""
        tmp_file = fu.create_unique_file_path(self.stage_io_dict["unique_dir"], extension)
        self.tmp_files.append(tmp_file)
        return tmp_file

    def remove_tmp_files(self):
        # Make sure current directory is not in the tmp_files list
        if str(os.getcwd()) in self.tmp_files:
            self.tmp_files.remove(str(os.getcwd()))

        if self.remove_tmp:
            fu.rm_file_list(self.tmp_files, self.out_log)

    @classmethod
    def get_main(cls, launcher, description):
        """Get command line execution of this building block. Please check the command line documentation."""
        def main():
            # Get the arguments and properties from the class docstring
            doc_arguments_dict, _ = fu.get_doc_dicts(cls.__doc__)
            # Create the argument parser
            parser = argparse.ArgumentParser(description=description,
                                             formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
            parser.add_argument(
                "-c", "--config", required=False,
                help="This file can be a YAML file, JSON file or JSON string",
            )
            # Use the doc_arguments_dict to add arguments to the parser
            # If we have only one input or output argument, we can use shorthand flags -i/-o
            input_args = [arg for arg, arg_dict in doc_arguments_dict.items() if arg_dict.get("input_output", "").lower().startswith("input")]
            output_args = [arg for arg, arg_dict in doc_arguments_dict.items() if arg_dict.get("input_output", "").lower().startswith("output")]

            for argument, argument_dict in doc_arguments_dict.items():
                # Determine if we should add shorthand flags
                shorthand_flags = [f'--{argument}']
                if len(input_args) == 1 and argument in input_args:
                    shorthand_flags.insert(0, '-i')
                elif len(output_args) == 1 and argument in output_args:
                    shorthand_flags.insert(0, '-o')

                if argument_dict["optional"]:
                    parser.add_argument(*shorthand_flags, required=False, help=argument_dict.get("description", ""))
                else:
                    parser.add_argument(*shorthand_flags, required=True, help=argument_dict.get("description", ""))
            # Parse the arguments from the command line
            args = parser.parse_args()
            args.config = args.config or "{}"
            # Get the properties from the configuration yaml
            properties = settings.ConfReader(config=args.config).get_prop_dic()
            args_dict = vars(args)
            args_dict.pop('config', None)
            # Remove keys with None values from args_dict
            args_dict = {k: v for k, v in args_dict.items() if v is not None}
            # Return the function without executing it
            launcher(**args_dict, properties=properties)
        return main
