"""
Module for orchestrating and automating the execution of multiple workflows and hooks.

Provides the ModelBuilder class which manages a sequence of WorkflowBuilder, StageWorkflowBuilder, or Hook instances, allowing flexible, stepwise processing of input data through these workflows.

Features:

* Sequential execution of workflows with intermediate results.
* Options to retrieve results from specific workflows, all workflows, or only the final output.
* Supports integration with various workflow types for modular model construction.

This module facilitates building complex processing models by combining and controlling multiple modular workflows in a unified manner.
"""

from ..workflows import WorkflowBuilder, StageWorkflowBuilder
from ..hooks import Hook

from typing import Any
from ..lib_types import StepResult, StepGenerator, ResultGenerator

class ModelBuilder:
    """
    Automates the execution of a sequence of workflows on a WorkflowBuilder or Hook subclass.

    :param workflows: A list of Workflow, StageWorkflows or Hook to execute.
    :type workflows: list[WorkflowBuilder | StageWorkflowBuilder | Hook]

    Usage:
    
    .. code-block:: python

        CustomModel = ModelBuilder(workflows=[workflow1, workflow2, hook1])
        final_result = CustomModel(input_data)
    """

    def __init__(self, workflows: list[WorkflowBuilder | StageWorkflowBuilder | Hook]):
        """
        Initializes WorkflowBuilder with given attributes.
        """

        self.workflows: list[WorkflowBuilder | StageWorkflowBuilder | Hook] = workflows

    def _run(self, input_data: Any) -> StepGenerator:
        """
        Executes each workflow or hook sequentially on the input data, yielding intermediate results.

        :param input_data: The initial data to be processed by the workflows.
        :type input_data: Any

        :return: A generator that yields StepResult objects containing the name of the workflow and the corresponding output after execution.
        :rtype: StepGenerator
        """
        result: Any = input_data

        for workflow in self.workflows:            
            result = workflow(result)
            yield StepResult(name=workflow.name, result=result)


    def __call__(self, input_data: Any, return_workflows: list[str] | None = None, return_all: bool = False) -> ResultGenerator | StepGenerator | Any:
        """
        Runs the workflows on the input data.

        :param input_data: Input data to process.
        :type input_data: Any
        :param return_workflows: If provided, yields results only for these workflows. Defaults to None
        :type return_workflows: list[str] or None
        :param return_all: If True, yields results for all workflows. Defaults to False.
        :type return_all: bool

        :return: Final result, or a generator of step/workflow results.
        :rtype: ResultGenerator | StepGenerator | Any
        """
            
        if return_workflows:
            return (result for name, result in self._run(input_data) if name in return_workflows)
        elif return_all:
            return self._run(input_data)
        else:
            result = input_data
            for _, result in self._run(input_data):
                pass
            return result