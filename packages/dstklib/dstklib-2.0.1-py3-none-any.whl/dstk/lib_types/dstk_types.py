from typing import TypeAlias, TypeVar, Any, TypedDict, NotRequired, NamedTuple, Generator
from .spacy_types import Token
from .sklearn_types import csc_matrix, csr_matrix
from .numpy_types import ndarray, NDArray, str_
from .pandas_types import Index
from .fasttext_types import FastText
from .gensim_types import Word2Vec
from collections import Counter

#: Numeric types accepted (integer or float).
Number: TypeAlias = int | float

#: A generic type variable for words, bounded to str or spaCy Token.
Word = TypeVar("Word", bound=str | Token)

#: A list of words (strings or spaCy Tokens).
Words: TypeAlias = list[Word]

#: A tuple representing a group of collocates (words).
Collocates: TypeAlias = tuple[Word, ...]

#: A list of collocate tuples.
CollocatesList = list[Collocates]

class POSTaggedWord(NamedTuple):
    """
    Represents a word paired with its Part-Of-Speech (POS) tag.

    :param word: The word, either as a string or spaCy Token.
    :type word: str or Token
    :param pos: The POS tag of the word.
    :type pos: str
    """

    word: str | Token
    pos: str

#: A list of POS-tagged words.
POSTaggedWordList: TypeAlias = list[POSTaggedWord]

class Bigram(NamedTuple):
    """
    Represents a bigram collocation between two words.

    :param collocate: The collocate word.
    :type collocate: str or Token
    :param target_word: The target word in the bigram.
    :type target_word: str
    """

    collocate: str | Token
    target_word: str

#: A list of bigram tuples.
BigramList: TypeAlias = list[Bigram]

#: Directed collocates represented as a tuple of a word and a pair of directional tags.
DirectedCollocates: TypeAlias = tuple[Word, tuple[str, str]]

#: A list of directed collocates.
DirectedCollocateList: TypeAlias = list[DirectedCollocates]

#: Union type of all tagged word lists.
TaggedWordsList: TypeAlias = CollocatesList | DirectedCollocateList | POSTaggedWordList | BigramList

#: A list of sentences, where each sentence is a list of words.c
WordSenteces: TypeAlias = list[Words]
#: A list of tagged sentences, each containing tagged words.c
TaggedSentences: TypeAlias = list[TaggedWordsList]

#: Union type representing either plain or tagged sentences.
Sentences: TypeAlias = WordSenteces | TaggedSentences


#: A tuple representing a neighboring word and its association score.
class Neighbor(NamedTuple):
    word: str
    score: float
#: A list of neighboring words with scores.
Neighbors: TypeAlias = list[Neighbor]

#: A union of neural language model types.
NeuralModels: TypeAlias = Word2Vec | FastText

#: A counter mapping words (strings) to their frequency counts.
WordCounts: TypeAlias = Counter[str]

#: A union of matrix types from SciPy or NumPy.
Matrix: TypeAlias = csr_matrix | csc_matrix | ndarray

#: Labels used in pandas DataFrames, representing index or column labels.
#:
#: This can be a NumPy ndarray of strings, a pandas Index, a list of strings, or None.
Labels: TypeAlias = NDArray[str_] | Index | list[str] | None

StepConfig = TypedDict(
    "StepConfig",
    {
        "include": NotRequired[list[str] | str],
        "exclude": NotRequired[dict[str, int]],
        "repeat": bool,
        "chaining": bool,
        "step_name": str
    },
    total=True
)
"""
Configuration for a processing step in a workflow.

:param include: Methods to include, either a list of strings or a single string.
:type include: list[str] or str, optional
:param exclude: Methods to exclude, as a dictionary mapping strings to integers.
:type exclude: dict[str, int], optional
:param repeat: Whether the a method can be used more than once.
:type repeat: bool
:param chaining: Whether method cchaining is enabled.
:type chaining: bool
:param step_name: The name of the step.
:type step_name: str
"""

WorkflowTemplate = TypedDict(
    "WorkflowTemplate",
    {
        "steps": dict[int, StepConfig],
        "base_type": str,
        "triggers": dict[str, str]
    }
)
"""
Template for an entire workflow, consisting of steps, a base type and triggers.

:param steps: Mapping from step numbers to step configurations.
:type steps: dict[int, StepConfig]
:param base_type: The base type of the workflow.
:type base_type: str
:param triggers: Mapping from method names to the data types they produce. When a method changes the current data type (the default return type),the corresponding trigger activates rules that enable or disable subsequent methods.
:type triggers: dict[str, str]
"""

#: A workflow is a list of ordered steps, where each step is a dictionary
#: mapping method names to their keyword arguments.
Workflow: TypeAlias = list[dict[str, dict[str, Any]]]
#: A stage workflow contains multiple workflows organized by module names.
#: Each key is a module name (e.g., 'tokenizer', 'ngrams', 'text_processor'),
#: and the value is the workflow steps for that module.
StageWorkflow: TypeAlias = dict[str, Workflow]
#: Mapping from stage names to their corresponding workflow templates.
#:
#: Each key is a stage name (a string identifying a module),
#: and the value is a `WorkflowTemplate` describing the processing steps and triggers
#: allowed in that stage.
StageTemplate: TypeAlias = dict[str, WorkflowTemplate]
#: Mapping from stage indices (integers) to sets of module names allowed in that stage.
#:
#: Each key is a stage number, and the value is a set of module names (strings) that
#: are enabled or active during that stage of the stage workflow.
StageModules: TypeAlias = dict[int, set[str]]

ExcludedMethods = TypedDict(
    "ExcludedMethods",
    {
        "exclude": list[str] | str
    }
)
"""
Specifies methods to exclude by name.

:param exclude: A list of method names or a single method name to exclude.
:type exclude: list[str] or str
"""

#: Template defining rules for excluding methods once a specific type is triggered.
#:
#: The outer dictionary keys are module names (e.g., 'tokenizer', 'text_processor'),
#: and the values specify which methods should be excluded in that module.
#:
#: For example, when the data type changes to 'POSTaggedWordList', these rules
#: prevent further usage of specific methods like 'pos_tagger' in the tokenizer module
RulesTemplate: TypeAlias = dict[str, ExcludedMethods]

class StepResult(NamedTuple):
    """
    Represents the result of executing a single workflow or model step.

    :param name: The name of thec step.
    :param result: The output produced by the step.
    """

    name: str
    result: Any


#: Generator that yields `StepResult` objects, each representing the name and result of a workflow step.
StepGenerator: TypeAlias = Generator[StepResult, None, None]

#: Generator that yields results of workflow steps without step metadata.
ResultGenerator: TypeAlias = Generator[Any, None, None]
