"""
Defines type-based exclusion rules that constrain which methods can be applied to data at different stages in a workflow.

Each rule maps a data type (e.g., `POSTaggedWordList`, `Sentences`, `str`, `Neighbors`) to a set of module-specific restrictions. These rules help ensure that operations are semantically valid and compatible with the current data representation, enabling type-aware validation and error handling during workflow execution.

Structure:

Each rule is a `RulesTemplate` (dict) where:

* Keys are module names (e.g., "tokenizer", "text_processor").
* Values define methods to exclude (either a list of method names or "*" for all).

The `TypeRules` dictionary aggregates all individual rules and serves as a centralized configuration for type-based behavior enforcement.

Use case:
These rules are primarily used in the validation step of workflow builders to prevent method misuse based on data type.
"""

from ..lib_types import RulesTemplate

POSTaggedWordListRules: RulesTemplate = {
    "tokenizer": {
        "exclude": ["pos_tagger"]
    },
    "text_processor": {
        "exclude": ["join"]
    },
    "ngrams": {
        "exclude": "*"
    }
}

SentencesRules: RulesTemplate = {
    "text_processor": {
        "exclude": ["get_vocabulary", "save_to_file"]
    },
    "ngrams": {
        "exclude": "*"
    }
}

StringRules: RulesTemplate = {
    "text_processor": {
        "exclude": ["to_lower", "get_vocabulary", "join", "save_to_file"]
    }
}

NeighborsRules: RulesTemplate = {
    "geometric_distance": {
        "exclude": "*"
    }
}

TypeRules: dict[str, RulesTemplate] = {
    "POSTaggedWordList": POSTaggedWordListRules,
    "Sentences": SentencesRules,
    "str": StringRules,
    "Neighbors": NeighborsRules
}
