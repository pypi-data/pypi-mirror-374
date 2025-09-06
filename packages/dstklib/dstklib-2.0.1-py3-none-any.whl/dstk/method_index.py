INDEX = {
    "tokenizer": {
        "apply_model": {
            "input": "str",
            "output": "Doc"
        },
        "get_tokens": {
            "input": "Doc",
            "output": "Words[Tokens]"
        },
        "get_sentences": {
            "input": "Doc",
            "output": "Check it"
        },
        "remove_stop_words": {
            "input": "Words[Token]",
            "output": "Words[Token]"
        },
        "alphanumeric_raw_tokenizer": {
            "input": "Words[Token]",
            "output": "Words[Token]"
        },
        "filter_by_pos": {
            "input": "Words[Token]",
            "output": "Words[Token]"
        },
        "pos_tagger": {
            "input": "Words[Token]",
            "output": "POSTaggedText"
        },
    }
}