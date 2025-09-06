"""
This module provides classes for defining, validating, and executing complex workflows composed of multiple processing steps and stages. It supports dynamic method invocation from specified modules, workflow validation against templates with type and step rules, and optional method wrapping for object-oriented usage.

Key components:

* Wrapper: Simple container for input data, enabling method injection.
* WorkflowBuilder: Automates sequential execution of methods in a single workflow, including validation and optional wrapping.
* StageWorkflowBuilder: Manages multiple workflows organized in stages and modules, enforcing stage/module constraints and chaining workflows.

This module is designed to facilitate building flexible, validated processing workflows with dynamic and modular behavior.
"""

import importlib
from ..templates.rules import TypeRules
from ..adaptors import accepts_sentences_and_collocates, accepts_tags, is_workflow
from types import ModuleType
import warnings
from functools import wraps

from typing import Any, Callable, TypeVar, ParamSpec, Concatenate
from ..lib_types import Workflow, WorkflowTemplate, StageWorkflow, StepResult, StepConfig, RulesTemplate, StageTemplate, StageModules, StepGenerator, ResultGenerator

P = ParamSpec("P")
R = TypeVar("R")

class Wrapper:
    def __init__(self, input_data: Any):
        """
        A simple wrapper class that stores input data.

        :param input_data: Any data to be wrapped and stored internally.
        :type input_data: Any
        """
        self._input_data: Any = input_data

class WorkflowBuilder: 
    """
    Automates the execution of a sequence of methods as a workflow.

    This class dynamically imports and executes a chain of methods defined in a workflow, optionally validates the workflow against a template, and can wrap methods for object-oriented style usage.

    :param name: Name of the workflow instance.
    :type name: str
    :param module_name: Name of the module containing the methods to be executed.
    :type module_name: str
    :param workflow: A workflow definition, a list of dicts mapping method names to kwargs.
    :type workflow: Workflow
    :param template: Optional workflow template for validation and typing rules. Defaults to None
    :type template: WorkflowTemplate or None
    :param wrapper: If True, creates a Wrapper instance allowing method calls as object methods with internal data injection. Defaults to False.

    Usage:

        .. code-block:: python

            CustomWorkflow = WorkflowBuilder(...)
            result = CustomWorkflow(input_data)
    """

    def __init__(self, name: str, module_name: str,  workflow: Workflow, template: WorkflowTemplate | None = None, wrapper: bool = False) -> None:
        """
        Initializes WorkflowBuilder with given attributes.
        """

        self.name: str = name
        self.module_name: str = module_name
        self.methods: Workflow = workflow
        self.template: WorkflowTemplate | None = template
        self.current_types: list[str] = []
        self.wrap: bool = wrapper

    def _run_methods(self, input_data: Any) -> StepGenerator:
        """
        Executes the sequence of methods in the workflow on the input data.

        For modules 'tokenizer' and 'text_processor' (except 'save_to_file'),
        the method is wrapped to accept sentences and tags.

        :param input_data: The input data to process through the workflow.
        :type input_data: Any

        :return: A generator yielding StepResult instances containing method names and their results.
        :rtype: StepGenerator
        """
        input_output: Any = input_data

        for method_dict in self.methods:
            method_name, kwargs = next(iter(method_dict.items()))

            module: ModuleType = importlib.import_module(f"dstk.modules.{self.module_name}")
            
            method: Callable = getattr(module, method_name)

            if self.module_name in ("tokenizer", "text_processor") and  method_name not in ["save_to_file"]:
                input_output = accepts_sentences_and_collocates(accepts_tags(method))(input_output, **kwargs)
            else:
                input_output = method(input_output, **kwargs)

            yield StepResult(name=method_name, result=input_output)

    def __call__(self, input_data: Any, return_methods: list[str] | None = None, return_all: bool = False) -> StepGenerator | ResultGenerator | Wrapper | Any:
        """
        Executes the workflow on the given input data.

        Depending on parameters, can return results of specific methods, all method results as a generator, the final result, or a Wrapper instance.

        :param input_data: Data to be processed by the workflow.
        :type input_data: Any
        :param return_methods: If specified, only results of these methods are returned.  Defaults to None
        :type return_methods: list[str] or None
        :param return_all: If True, returns a generator for all method results.Defaults to None

        :return: Depending on parameters:
            * Wrapper instance if wrap=True,
            * Generator of selected/all method results,
            * Final processed result otherwise.
        :rtype: StepGenerator | ResultGenerator | Wrapper | Any

        :raises ValueError: If the workflow format is invalid.
        """

        if self.wrap: # Maybe validate workflow too?
            for method_dict in self.methods:
                method_name, kwargs = next(iter(method_dict.items()))

                if kwargs:
                    warnings.warn("Because you set wrapper=True, the arguments you passed to the methods in the workflow will be ignored.")

                module: ModuleType = importlib.import_module(f"dstk.modules.{self.module_name}")
                
                method: Callable = getattr(module, method_name)

                def inject_data(func:  Callable[P, R]) -> Callable[Concatenate[Any, P], R]:
                    @wraps(func)
                    def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
                        return func(self._input_data, *args, **kwargs)
                    return wrapper
                
                setattr(Wrapper, method_name, inject_data(method))
            
            return Wrapper(input_data)

        if not is_workflow(self.methods):
            raise ValueError("The workflow provided does not follow the right format. Please enter a valid workflow")

        if self.template:
            is_valid: bool = self._validate_workflow(base_type=self.template["base_type"])

        if return_methods:
            return (result for name, result in self._run_methods(input_data) if name in return_methods)
        elif return_all:
            return self._run_methods(input_data)
        else:
            result: Any = input_data
            for _, result in self._run_methods(input_data):
                pass
            return result


    def _validate_workflow(self, base_type: str) -> bool:
        """
        Validates the workflow against the given template and type rules.

        Ensures methods are used in valid steps, not repeated improperly,
        and conform to chaining and inclusion/exclusion rules.

        :param base_type: The starting type of the workflow.
        :type base_type: str

        :return: True if workflow passes validation, otherwise raises RuntimeError.
        :rtype: bool

        :raises ValueError: If no template is provided.
        """
        current_line: int = 0
        current_step: int = 0
        excluded_methods: dict[str, str] = {}
        self.current_types.extend([base_type])

        template: WorkflowTemplate | None = self.template

        if template is None:
            raise ValueError(f"A template was not provided for this module.")

        methods: list[str] = [list(method.keys())[0] for method in self.methods]
        steps: list[int] = list(template["steps"].keys())

        while current_line < len(methods):
            current_method: str = methods[current_line]
            step_data: StepConfig = template["steps"][current_step]

            for data_type in self.current_types:
                if data_type in TypeRules:
                    if self.module_name in TypeRules[data_type]:
                        if TypeRules[data_type][self.module_name]["exclude"] == "*":
                            raise RuntimeError(f"You cannot choose the methods from {self.module_name} because you are currently processing by {self.current_types}")

            if "*" in excluded_methods and not step_data["chaining"]:
                raise RuntimeError(f"You cannot use method {current_method} because {excluded_methods['*']}")

            if current_method in excluded_methods:
                raise RuntimeError(f"You cannot use method {current_method} because {excluded_methods[current_method]}")

            if "include" in step_data:
                included_methods: list[str] | str = step_data["include"]

                if included_methods != "*":
                    if current_method not in included_methods:
                        raise RuntimeError(f"The method on step {template['steps'][current_step]['step_name']} must be {included_methods}. Instead, got method {current_method}")
                    
                    for included_method in included_methods:
                        excluded_methods[included_method] = f"it can ony be used on step {template['steps'][current_step]['step_name']}"
                else:
                    excluded_methods["*"] = f"you can select only one method from this module."
            else:
                step_excluded_methods: dict[str, int] = step_data["exclude"]
                if current_method in step_excluded_methods:
                    raise RuntimeError(f"You cannot use method {current_method} because it can only be used in step {template['steps'][step_excluded_methods[current_method]]['step_name']}")

            if not step_data["repeat"]:
                excluded_methods[current_method] = "this method cannot be used twice"

            self._trigger_type(current_method, excluded_methods)

            current_line += 1

            if current_step < len(steps) - 1:
                current_step += 1
            else:
                pass

        return True

    def _trigger_type(self, method_name: str, excluded_methods: dict[str, str]) -> None:
        """
        Updates the current data types and excluded methods based on the triggered method.

        :param method_name: The method that triggers a type change.
        :type method_name: str
        :param excluded_methods: Dictionary tracking excluded methods and their reasons.
        :type excluded_methods: dict[str, str]

        :raises ValueError: If no template is provided.
        """
        template: WorkflowTemplate | None = self.template

        if template is None:
            raise ValueError(f"A template was not provided. Please provide a valid template")
            
        triggers: dict[str, str] = template["triggers"]

        if method_name in triggers and self.module_name:
            rules: RulesTemplate = TypeRules[triggers[method_name]]
            
            if template["base_type"] in self.current_types:
                    self.current_types.pop()

            self.current_types.append(triggers[method_name])

            if self.module_name in rules:
                method_rules: list[str] | str = rules[self.module_name]["exclude"]

                for method in method_rules:
                    excluded_methods[method] = f"you are currently processing by {self.current_types}"


class StageWorkflowBuilder:
    """
    Manages and runs workflows composed of multiple stages and modules.

    Allows sequential execution of workflows associated with various modules/stages, validating and chaining them according to provided templates and configurations.

    :param templates: A mapping of module names to their workflow templates.
    :type templates: StageTemplate
    :param stage_modules: A mapping of stage indices to allowed module names.
    :type stage_modules: StageModules
    :param name: Name of the stage workflow builder instance.
    :type name: str
    :param workflows: A mapping of module names to their workflows.
    :type workflows: StageWorkflow
    """

    def __init__(self, templates: StageTemplate, stage_modules: StageModules, name: str, workflows: StageWorkflow):
        """
        Initializes StageWorkflowBuilder with given attributes.
        """

        self.name: str = name
        self.stage_workflows: StageWorkflow = workflows
        self.templates: StageTemplate = templates
        self.stage_modules: StageModules = stage_modules
        self.workflows: list[WorkflowBuilder] = []

    def _run_workflow(self, input_data: Any) -> StepGenerator:
        """
        Executes all workflows in sequence on the input data.

        :param input_data: The input data to process through the workflow.
        :type input_data: Any

        :return: A generator yielding StepResult instances containing workflow names and their results.
        :rtype: StepGenerator
        """
        result: Any = input_data

        for workflow in self.workflows:
            result = workflow(input_data=result)

            yield StepResult(name=workflow.name, result=result)
    

    def __call__(self, input_data: Any, return_modules: list[str] | None = None, return_all: bool = False) -> ResultGenerator | StepGenerator | Any:
        """
        Runs the staged workflows on the input data.

        Checks stage/module compatibility, validates workflows against templates, and returns results based on parameters.

        :param input_data: Input data to process.
        :type input_data: Any
        :param return_modules: If provided, yields results only for these modules. Defaults to None
        :type return_modules: list[str] or None
        :param return_all: If True, yields results for all modules. Defaults to False.
        :type return_all: bool

        :return: Final result, or a generator of step/module results.
        :rtype: ResultGenerator | StepGenerator | Any

        :raises RuntimeError: If a module is used in an incorrect stage.
        :raises ValueError: If any workflow is invalid or template is missing.
        """

        self.workflows = []

        max_stage: int = max(self.stage_modules)

        current_stage: int = 0

        for module in self.stage_workflows:

            allowed_modules: set[str] = self.stage_modules[current_stage]

            if module not in allowed_modules:
                raise RuntimeError(f"The module on on stage {current_stage} must be one of the following {allowed_modules}")

            if current_stage < max_stage:
                current_stage += 1

            if not is_workflow(self.stage_workflows[module]):
                raise ValueError(f"Please enter a valid workflow for module {module}")

            module_workflow: WorkflowBuilder = WorkflowBuilder(
                name=f"{module}",
                template=self.templates[module],
                module_name=module,
                workflow=self.stage_workflows[module]
            )

            if self.workflows:
                module_workflow.current_types = self.workflows[-1].current_types

            template: WorkflowTemplate | None = module_workflow.template

            if template is None:
                raise ValueError(f"A template for module {module} not provided")

            module_workflow._validate_workflow(base_type=template["base_type"])

            self.workflows.append(module_workflow)

        if return_modules:
            return (result for name, result in self._run_workflow(input_data) if name in return_modules)
        elif return_all:
            return self._run_workflow(input_data)
        else:
            result = input_data

            for _, result in self._run_workflow(input_data):
                pass

            return result


        