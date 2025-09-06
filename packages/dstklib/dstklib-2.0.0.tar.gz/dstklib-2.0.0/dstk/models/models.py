"""
This module contains predefined and commonly used distributional semantic models. Each model is implemented as a high-level pipeline that integrates multiple stages of text processing, embedding generation, and similarity computation.

Currently supported models:

* *StandardModel*: A count-based model using a context window, PPMI weighting, and dimensionality reduction via SVD. Based on the description found in the book 'Distributional semantics' by Lenci & Sahlgren (2023).
* *SGNSModel*: A prediction-based model using Word2Vec's Skip-Gram with Negative Sampling (SGNS), as described by Lenci & Sahlgren (2023).

These pipelines are modular and composable, built from reusable workflows to support both experimentation and production use.

Future versions of this module may include additional models and hybrid approaches.
"""

from ..workflows import WorkflowBuilder, TextProcessing, StageWorkflowBuilder, Wrapper
from ..templates import TextMatrixBuilderTemplate,  WeightMatrixTemplate, CountModelsTemplate, GeometricDistanceTemplate, PredictModelsTemplate
from .model_tools import ModelBuilder
from ..hooks import ModelToDataframe, Hook

from typing import Any
from ..lib_types import Language, StepResult, StepGenerator, ResultGenerator

def StandardModel(text: str, model: str | Language, custom_stop_words: list[str] | None = None, window_size: int = 2, n_components: int = 100, return_workflows: list[str] | None = None, return_all: bool = False)-> ResultGenerator | StepGenerator | Wrapper:
    """
    This pipeline generates word embeddings using the standard model as defined by (Lenci & Sahlgren 97). It preprocesses the text by removing stop words, lowering the words and segmenting the text using a context window. The co-occurrence matrix is weighted with PPMI and reduced with truncated SVD. Then, cosine similarity is appliad as the distance metric.

    :param text: The text to extract the embeddings from.
    :type text: str
    :param model: The spaCy NLP model to tokenize the text.
    :type model: str or Language
    :param window_size: The size of the context window to segment the text. Defaults to 2.
    :type window_size: int
    :param n_components: The number of dimensions of the embeddings. Defaults to 100.
    :type n_components: int
    :param return_workflows: If provided, yields results only for these workflows. Defaults to None
    :type return_workflows: list[str] or None
    :param return_all: If True, yields results for all workflows. Defaults to False.
    :type return_all: bool

    :return: Wrapper for cosine_similarity and nearest_neighbors, or a generator of step/workflow results.
    :rtype: ResultGenerator | StepGenerator | Wrapper
    """

    StandardTextWorkflow: StageWorkflowBuilder = TextProcessing(
        name="ProcessedText",
        workflows= {
            "tokenizer": [
                {"apply_model": {"model": model}},
                {"get_tokens": {}},
                {"remove_stop_words": {"custom_stop_words": custom_stop_words}}
            ],
            "ngrams": [
                {"extract_ngrams": {"window_size": window_size}}
            ],
            "text_processor": [
                {"tokens_to_text": {}},
                {"to_lower": {}},
                {"join": {}}
            ]
        }
    )

    StandardMatrix: WorkflowBuilder = WorkflowBuilder(
        name="Matrix",
        module_name="text_matrix_builder",
        template=TextMatrixBuilderTemplate,
        workflow=[
            {"create_dtm": {}},
            {"create_co_occurrence_matrix": {}}
        ]
    )

    StandardWeightMatrix: WorkflowBuilder = WorkflowBuilder(
       name="WeightedMatrix",
       module_name="weight_matrix",
       template=WeightMatrixTemplate,
       workflow=[
            {"pmi": {"positive": True}}
       ]
    )

    StandardCountModels: WorkflowBuilder = WorkflowBuilder(
        name="Embeddings",
        module_name="count_models",
        template=CountModelsTemplate,
        workflow=[
            {"scale_matrix": {}},
            {"svd_embeddings": {"n_components": n_components}}
        ]
    )

    StandardGeometricDistance: WorkflowBuilder = WorkflowBuilder(
        name="GeometricDistance",
        module_name="geometric_distance",
        template=GeometricDistanceTemplate,
        workflow=[
            {"cos_similarity": {}},
            {"nearest_neighbors": {}}
        ],
        wrapper=True
    )

    Model: ModelBuilder = ModelBuilder(
        workflows=[
            StandardTextWorkflow,
            StandardMatrix,
            StandardWeightMatrix,
            StandardCountModels,
            StandardGeometricDistance
        ]
    )

    return Model(input_data=text, return_workflows=return_workflows, return_all=return_all)


def SGNSModel(text: str, model: str | Language, path: str, return_workflows: list[str] | None = None, return_all: bool = False, **kwargs) -> StepGenerator | ResultGenerator | Any:
    """
    This pipeline generates word embeddings using Skip-Gram with Negative Sampling (SGNS) as defined by (Lenci & Sahlgren 162). It preprocesses the text by extracting the sentences, removing stop words and lowering them. The embeddings are extracted by using word2vec to do SGNS. Then, cosine similarity is appliad as the distance metric.

    :param text: The text to extract the embeddings from.
    :type text: str
    :param model: The spaCy NLP model to tokenize the text.
    :type model: str or Language
    :param path: The path to save the processed senteces.
    :type path: str
    :param kwargs:  Additional keyword arguments to pass to gensim.models.Word2Vec. Common options include:

        * **vector_size:** Size of the word embedding vectors.
        * **workers:** Number of CPU cores to be used during the training process.
        * **negative:** Specifies how many "noise words" to sample for each positive example during training. Typical values range from 5 to 20. Higher values make training slower but can improve embedding quality.
        * **window (int):** Maximum distance between the current and predicted word.
        * **min_count (int):** Ignores all words with total frequency lower than this.

    For more information check: https://radimrehurek.com/gensim/models/word2vec.html
    :param return_workflows: If provided, yields results only for these workflows. Defaults to None
    :type return_workflows: list[str] or None
    :param return_all: If True, yields results for all workflows. Defaults to False.
    :type return_all: bool

    :return: Wrapper for cosine_similarity and nearest_neighbors, or a generator of step/workflow results.
    :rtype: ResultGenerator | StepGenerator | Wrapper
    """

    PredictTextWorkflow: StageWorkflowBuilder = TextProcessing(
        name="ProcessedText",
        workflows= {
            "tokenizer": [
                {"apply_model": {"model": model}},
                {"get_sentences": {}},
                {"remove_stop_words": {}}
            ],
            "text_processor": [
                {"tokens_to_text": {}},
                {"to_lower": {}},
                {"join": {}},
                {"save_to_file": {"path": path}}
            ]
        }
    )

    SGNSPredictWorkflow: WorkflowBuilder = WorkflowBuilder(
        name="SGNS",
        module_name="predict_models",
        template=PredictModelsTemplate,
        workflow=[
            {"word2vec": {"sg": 1, **kwargs}}
        ]
    )

    PredictGeometricDistance: WorkflowBuilder = WorkflowBuilder(
        name="GeometricDistance",
        module_name="geometric_distance",
        template=GeometricDistanceTemplate,
        workflow=[
            {"cos_similarity": {}},
            {"nearest_neighbors": {}}
        ],
        wrapper=True
    )    

    EmbeddingsHook: Hook = ModelToDataframe.rename(new_name="Embeddings")

    Model: ModelBuilder = ModelBuilder(
        workflows=[
            PredictTextWorkflow,
            SGNSPredictWorkflow,
            EmbeddingsHook,
            PredictGeometricDistance
        ]
    )

    return Model(input_data=text, return_workflows=return_workflows, return_all=return_all)