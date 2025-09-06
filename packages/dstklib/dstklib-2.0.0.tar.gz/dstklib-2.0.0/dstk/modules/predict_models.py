"""
This module provides utilities to train, save, and load word embedding models using neural networks models such as Word2Vec (gensim) and FastText (fasttext library).

Functions include:

* *word2vec:* Train Word2Vec embeddings from a corpus file.
* *fastText:* Train FastText embeddings from a corpus file.
* *load_model:* Load a saved model from disk (supports Word2Vec .model and FastText .bin formats).
* *save_model:* Save a trained model to disk in the appropriate format.

Each function supports passing additional keyword arguments to fine-tune training and loading.
"""

from gensim.models import Word2Vec
import fasttext
from pathlib import Path

from ..lib_types import FastText, NeuralModels

def word2vec(path: str, **kwargs) -> Word2Vec:
    """
    Creates word embeddings using the Word2Vec algorithm.

    :param path: The path to a file conatining a list of sentences or collocations from which to build word embeddings.
    :type path: str
    :param kwargs:  Additional keyword arguments to pass to gensim.models.Word2Vec. Common options include:

        * **vector_size:** Size of the word embedding vectors.
        * **workers:** Number of CPU cores to be used during the training process.
        * **sg:** Training algorithm. 1 for skip-gram; 0 for CBOW (Continuous Bag of Words).
        * **window (int):** Maximum distance between the current and predicted word.
        * **min_count (int):** Ignores all words with total frequency lower than this.

    For more information check: https://radimrehurek.com/gensim/models/word2vec.html

    :returns: An instance of gensim's Word2Vec.
    :rtype: Word2Vec
    """

    return Word2Vec(
        corpus_file=path,
        **kwargs
    )

def fastText(path: str, **kwargs) -> FastText:
    """
    Creates word embeddings using the FastText algorithm.

    :param path: The path to a file containing a list of sentences or collocations from which to build word embeddings.
    :type path: str
    :param kwargs: Additional keyword arguments to pass to fasttext.train_unsupervised. Common options include:

        * **dim:** Size of the word embedding vectors.
        * **model:** Training algorithm: skipgram or cbow (Continuous Bag of Words)
        * **thread:** Number of CPU cores to be used during the training process.

    For more information check: https://fasttext.cc/docs/en/options.html
    
    :returns: An instance of fasttext's FastText.
    :rtype: FastText
    """

    return fasttext.train_unsupervised(
        path,
        **kwargs
    )

def load_model(path: str) -> NeuralModels:
    """
    Loads the trained embeddings in .model (Word2Vec) or .bin (FastText) format, depending on the algorithm used.

    :param path: Path to the saved model file.
    :type path: str

    :returns: An instance of gensim's Word2Vec or fasttext's FastText.
    :rtype: NeuralModels
    """

    extension: str = Path(path).suffix.lower()

    if extension == ".model":
        return Word2Vec.load(path)
    elif extension == ".bin":
        return fasttext.load_model(path)
    else:
        raise ValueError(f"Model extension {extension} not recognized.")

def save_model(model: NeuralModels, path: str) -> str:
    """
    Saves the trained embeddings in .model (Word2Vec) or .bin (FastText) format, depending on the algorithm used.

    :param model: A trained Word2Vec or FastText model.
    :type model: NeuralModels
    :param path: The path (without extension) where to save the model.
    :type path: str

    :returns: An instance of gensim's Word2Vec or fasttext's FastText.
    :rtype: NeuralModels
    """
    full_path: Path = Path(path)

    if isinstance(model, Word2Vec):
        model.save(str(full_path.with_suffix(".model")))
    elif isinstance(model, FastText):
        model.save_model(str(full_path.with_suffix(".bin")))
    else:
        raise NotImplementedError(f"Model identifier type {type(model.__name__)} not yet supported")
    
    return str(full_path.resolve())