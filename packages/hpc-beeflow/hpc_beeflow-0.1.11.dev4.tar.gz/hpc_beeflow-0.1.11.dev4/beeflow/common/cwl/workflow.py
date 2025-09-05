"""Workflow front end for CWL generator."""
import re
from dataclasses import dataclass

from beeflow.common.cwl.cwl import (CWL, CWLInput, CWLInputs, RunInput, Inputs, CWLOutput,
                                    Outputs, Run, RunOutput, Step, Steps, Hints,
                                    InputBinding, MPIRequirement, DockerRequirement,
                                    ScriptRequirement, SlurmRequirement,
                                    CheckpointRequirement, TaskRequirement)


@dataclass
class Input:
    """Represents CWL and Run inputs"""
    name: str
    type_: str
    # This is either a value or a source connection
    value: str = None
    # The prefix or position of the argument
    # This can either be a prefix such as -f or --file
    # Or a position like 2 if the command is "foo <file>"
    prefix: str = None
    position: int = None
    value_from: str = None

    pattern = re.compile(r"^[^/]+/[^/]+$")

    def has_source(self):
        """Check if there's a source."""
        return bool(self.pattern.match(str(self.value)))

    def cwl_input(self):
        """Create a CWLInput from generic Input."""
        if not self.has_source():
            return CWLInput(self.name, self.type_, self.value)
        return None

    def run_input(self):
        """Create a RunInput from generic Input."""
        bindings = {'prefix': self.prefix, 'position': self.position,
                    'value_from': self.value_from}
        source = {}
        if self.has_source():
            source.update({"source": self.value})

        return RunInput(self.name, self.type_, InputBinding(**bindings), **source)


@dataclass
class Output:
    """Represents an output."""
    name: str
    run_type: str
    source: str = None
    glob: str = None

    def cwl_output(self):
        """Create a CWLOutput from generic Input."""
        # The output type that should be used for CWL outputs
        # Currently these are only files
        if not self.source:
            return None
        output_type = "File"
        return CWLOutput(self.name, output_type, self.source)

    def run_output(self):
        """Create a RunOutput from generic Input."""
        if self.glob:
            return RunOutput(self.name, self.run_type, self.glob)
        return RunOutput(self.name, self.run_type)


@dataclass
class MPI:
    """MPI options."""
    nodes: int
    ntasks: int

    def requirement(self):
        """Return MPI requirement object."""
        return MPIRequirement(self.nodes, self.ntasks)


@dataclass
class Slurm(SlurmRequirement):
    """Get Slurm Requirements."""

    def requirement(self):
        """Return a scheduler requirement object."""
        return SlurmRequirement(time_limit=self.time_limit, account=self.account,
                partition=self.partition, qos=self.qos, reservation=self.reservation)


@dataclass
class Charliecloud:
    """Represents charliecloud options."""

    container: str = None
    docker_file: str = None
    container_name: str = None

    def requirement(self):
        """Return a charliecloud requirement object."""
        return DockerRequirement(copy_container=self.container,
                                 docker_file=self.docker_file,
                                 container_name=self.container_name)


@dataclass
class Script:
    """Represents charliecloud options."""

    pre_script: str = None
    post_script: str = None
    enabled: str = None
    shell: str = None

    def requirement(self):
        """Return a charliecloud requirement object."""
        return ScriptRequirement(pre_script=self.pre_script,
                                 post_script=self.post_script,
                                 enabled=self.enabled,
                                 shell=self.shell)


@dataclass
class Checkpoint(CheckpointRequirement):
    """Get Checkpoint Requirements."""

    def requirement(self):
        """Return a checkpoint requirement object."""
        return CheckpointRequirement(file_path=self.file_path,
                                     container_path=self.container_path,
                                     file_regex=self.file_regex,
                                     restart_parameters=self.restart_parameters,
                                     add_parameters=self.add_parameters,
                                     num_tries=self.num_tries,
                                     enabled=self.enabled)


@dataclass
class TaskReq(TaskRequirement):
    """Get Task Requirements."""

    def requirement(self):
        """Return a task requirement object."""
        return TaskRequirement(workdir=self.workdir)


@dataclass
class Task:
    """Represents a task."""
    name: str
    base_command: str
    inputs: list
    outputs: list
    stdout: str = None
    stderr: str = None
    hints: list = None


class Workflow:
    """Represents the actual workflow."""

    def __init__(self, name, tasks):
        self.name = name
        self.tasks = tasks

        # Generate a CWL object from a Workflow object.
        cwl_inputs = []
        for task in self.tasks:
            cwl_inputs.extend([input_.cwl_input()
                               for input_ in task.inputs if input_.cwl_input() is not None])
        cwl_inputs = CWLInputs(cwl_inputs)

        cwl_outputs = []
        for task in self.tasks:
            cwl_outputs.extend([output_.cwl_output()
                                for output_ in task.outputs if output_.cwl_output() is not None])
        cwl_outputs = Outputs(cwl_outputs)

        cwl_steps = Steps([self.generate_step(task) for task in self.tasks])
        self.cwl = CWL(self.name, cwl_inputs, cwl_outputs, cwl_steps)


    def generate_step(self, task):
        """Generates a Step object based off a Task object."""
        # Convert each input to a run input
        base_command = task.base_command
        run_inputs = Inputs([input_.run_input() for input_ in task.inputs])
        run_outputs = Outputs([output_.run_output() for output_ in task.outputs])
        stdout = task.stdout
        stderr = task.stderr

        step_run = Run(base_command, run_inputs, run_outputs, stdout, stderr)
        step_name = task.name

        if task.hints:
            step_hints = Hints([hint.requirement() for hint in task.hints])
            step = Step(step_name, step_run, step_hints)
        else:
            step = Step(step_name, step_run)
        return step

    def dump_wf(self, path=None):
        """Write the workflow."""
        if not path:
            return self.cwl.dump_wf()
        return self.cwl.dump_wf(path)

    def dump_yaml(self, path=None):
        """Write the yaml file."""
        if not path:
            return self.cwl.dump_inputs()
        return self.cwl.dump_inputs(path)
