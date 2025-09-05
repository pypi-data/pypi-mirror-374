
from typing import Any
from typing import Dict
from typing import List

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class TextEmbedding:
    def __init__(self, model: str) -> None:
        self.__pipeline = pipeline(
            Tasks.sentence_embedding,
            model=model,
            sequence_length=512
        )

    def embed(self, source_sentence: List[str]) -> Any:
        return self.__pipeline(
            input={
                "source_sentence": source_sentence
            }
        )["text_embedding"]

    def compare_sentences(self, source_sentence: List[str], sentences_to_compare: List[str]) -> List[Dict[str, Any]]:
        pipeline_result = self.__pipeline(
            input={
                "source_sentence": source_sentence,
                "sentences_to_compare": sentences_to_compare
            }
        )
        source_len = len(source_sentence)
        return [
            {
                "sentence": sentence,
                "text_embedding": pipeline_result["text_embedding"][source_len + idx],
                "score": pipeline_result["scores"][source_len + idx - 1]
            }
            for idx, sentence in enumerate(sentences_to_compare)
        ]
