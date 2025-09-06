"""
This module provides classes and factory functions to build and manage complex, multi-stage workflows composed of sequential method executions across different processing modules. It supports workflow validation against predefined templates, method chaining with type enforcement, and flexible execution  control, including partial or complete result retrieval.

Key components include:

* Factory functions like TextProcessing and PlotEmbeddings to easily instantiate common workflows with predefined templates and modules.

Designed to facilitate modular, extensible, and maintainable workflow construction for tasks such as text processing and embedding visualization.
"""

from .workflow_tools import StageWorkflowBuilder
from ..templates import TextProcessingTemplates, TextProcessingStageModules, PlotEmbeddingsTemplates, PlotEmbeddingsStageModules
from ..lib_types import StageWorkflow

def TextProcessing(name: str, workflows: StageWorkflow) -> StageWorkflowBuilder:
    """
    Creates a StageWorkflowBuilder configured for text processing workflows. The modules included are 'tokenizer' in the first stage and 'text_processor' or 'ngrams' in the second.

    :param name: The name of the workflow instance.
    :type name: str
    :param workflows: A StageWorkflow dictionary defining the workflow steps per module/stage.
    :type workflows: StageWorkflow

    :return: An instance of StageWorkflowBuilder configured with text processing templates and modules.
    :rtype: StageWorkflowBuilder
    """
    TextProcessingWorkflow = StageWorkflowBuilder(
        templates=TextProcessingTemplates,
        stage_modules=TextProcessingStageModules, 
        name=name, 
        workflows=workflows
    )

    return TextProcessingWorkflow

def PlotEmbeddings(name: str, workflows: StageWorkflow) -> StageWorkflowBuilder:
    """
    Creates a StageWorkflowBuilder configured for word embedding plotting workflows. The modules included are 'data_visualization.clustering' in the first stage and 'data_visualization.embeddings' in the second.

    :param name: The name of the workflow instance.
    :type name: str
    :param workflows: A StageWorkflow dictionary defining the workflow steps per module/stage.
    :type workflows: StageWorkflow

    :return: An instance of StageWorkflowBuilder configured with embedding plotting templates and modules.
    :rtype: StageWorkflowBuilder
    """
    PlotEmbeddingsWorkflow = StageWorkflowBuilder(
        templates=PlotEmbeddingsTemplates, 
        stage_modules=PlotEmbeddingsStageModules, 
        name=name, 
        workflows=workflows
    )

    return PlotEmbeddingsWorkflow