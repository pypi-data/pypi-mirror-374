from setuptools import setup, find_packages

with open("README.md", "r") as file:
    description = file.read()

setup(
    name="dstklib",
    version="2.0.1",
    packages=find_packages(),
    install_requires=[
        "spacy",
        "plotly",
        "scikit-learn",
        "pandas",
        "numpy",
        "gensim",
        "fasttext",
        "kneed",
        "umap-learn"
    ],
    python_requires="<3.13",
    long_description=description,
    long_description_content_type="text/markdown"
)