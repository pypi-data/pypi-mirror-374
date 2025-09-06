"""
Defines reusable templates that specify the structure and constraints of workflows and step-based pipelines.

Each template outlines the allowed sequence of method steps for a given module, enforcing constraints such as:

* Which methods are permitted or excluded at each step (`include` / `exclude`)
* Whether methods can be used more than once (`repeat`)
* Whether more than one method can be selected on each step (`chaining`)
* How types are transformed via `triggers`

Key Components:

* **Workflow Templates** (`WorkflowTemplate`): Describe valid method sequences for individual modules (e.g., tokenization, text processing, dimensionality reduction).
* **Stage Templates** (`StageTemplate`): Group related modules into stages to define multi-module workflows.
* **Stage Modules** (`StageModules`): Define allowed module names for each stage in a stage-based workflow.

These templates are used by `WorkflowBuilder` and `StageWorkflowBuilder` to validate workflows and enforce correct sequencing of operations.

Examples of Defined Templates:

* `TokenizerTemplate`: Defines the tokenization workflow including model selection, unit selection (sentences/tokens), and token processing.
* `TextProcessorTemplate`: Defines generic text processing steps like  lowercasing, joining, etc.
* `TextMatrixBuilderTemplate`: Specifies steps to create a document-term and co-occurrence matrix.
* `PlotEmbeddingsTemplate`: Governs how word embeddings are plotted after clustering.

The templates provide a flexible and declarative way to define what each step in a workflow is allowed to do based on processing intent and data type.
"""

from ..lib_types import WorkflowTemplate, StageTemplate, StageModules

TokenizerTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": ["apply_model"],
            "repeat": False,
            "chaining": False,
            "step_name": "select_model"
        },
        1: {
            "include": ["get_sentences", "get_tokens"],
            "repeat": False,
            "chaining": False,
            "step_name": "select_processing_unit"
        },
        2: {
            "include": ["remove_stop_words", "alphanumeric_raw_tokenizer"],
            "repeat": False,
            "chaining": False,
            "step_name": "tokenization"
        },
        3: {
            "include": "*",
            "repeat": True,
            "chaining": True,
            "step_name": "token_processing"
        }
    },
    "base_type": "Words", # is this necessary?
    "triggers":  {
        "pos_tagger": "POSTaggedWordList",
        "get_sentences": "Sentences"
    }
}

TextProcessorTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": "*",
            "repeat": False,
            "chaining": True,
            "step_name": "text_processing"
        }
    },
    "base_type": "Words",
    "triggers": {}
}

NgramsTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "exclude": {"count_collocates": 1},
            "repeat": False,
            "chaining": False,
            "step_name": "find_ngrams"
        },
        1: {
            "include": ["count_collocates"],
            "repeat": False,
            "chaining": False,
            "step_name": "count_collocates"
        }
    },
    "base_type": "Words",
    "triggers": {}
}

TextMatrixBuilderTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": ["create_dtm"],
            "repeat": False,
            "chaining": True,
            "step_name": "document_term_matrix"
        },
        1: {
            "include": ["create_co_occurrence_matrix"],
            "repeat": False,
            "chaining": False,
            "step_name": "co_occurrence_matrix"
        }
    },
    "base_type": "DataFrame",
    "triggers": {}
}

WeightMatrixTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": "*",
            "repeat": False,
            "chaining": False,
            "step_name": "weight_matrix"
        }
    },
    "base_type": "DataFrame",
    "triggers": {}
}

CountModelsTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": ["scale_matrix"],
            "repeat": False,
            "chaining": False,
            "step_name": "scale_matrix"
        },
        1: {
            "include": "*",
            "repeat": False,
            "chaining": False,
            "step_name": "dimensionality_reduction"
        }
    },
    "base_type": "DataFrame",
    "triggers": {}
}

GeometricDistanceTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": "*",
            "repeat": False,
            "chaining": False,
            "step_name": "geometric_distance"
        }
    },
    "base_type": "float",
    "triggers": {
        "nearest_neighbors": "Neighbors"
    }
}

PredictModelsTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "exclude": {"save_model": 1},
            "repeat": False,
            "chaining": False,
            "step_name": "select_model"
        },
        1: {
            "include": ["save_model"],
            "repeat": False,
            "chaining": False,
            "step_name": "save_model"
        }
    },
    "base_type": "NeuralModels",
    "triggers": {
        "save_model": "str"
    }
}

ClusteringTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": "*",
            "repeat": False,
            "chaining": False,
            "step_name": "clustering"
        }
    },
    "base_type": "DataFrame",
    "triggers": {}
}

PlotEmbeddingsTemplate: WorkflowTemplate = {
    "steps": {
        0: {
            "include": "*",
            "repeat": False,
            "chaining": False,
            "step_name": "embedings_plot"
        }
    },
    "base_type": "Figure",
    "triggers": {}
}

# Stage templates

TextProcessingTemplates: StageTemplate = {
    "tokenizer": TokenizerTemplate,
    "text_processor": TextProcessorTemplate,
    "ngrams": NgramsTemplate
}

TextProcessingStageModules: StageModules = {
    0: {"tokenizer"},
    1: {"text_processor", "ngrams"}
}

PlotEmbeddingsTemplates: StageTemplate = {
    "data_visualization.clustering": ClusteringTemplate,
    "data_visualization.embeddings": PlotEmbeddingsTemplate,
}

PlotEmbeddingsStageModules: StageModules = {
    0: {"data_visualization.clustering"},
    1: {"data_visualization.embeddings"}
}