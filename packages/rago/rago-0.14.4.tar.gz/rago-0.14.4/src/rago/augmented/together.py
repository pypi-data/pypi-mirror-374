"""Classes for augmentation with Together embeddings."""

from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, cast

import numpy as np

from typeguard import typechecked

from rago._optional import require_dependency
from rago.augmented.base import AugmentedBase, EmbeddingType

if TYPE_CHECKING:
    from together import Together


@typechecked
class TogetherAug(AugmentedBase):
    """Class for augmentation with Together embeddings."""

    default_model_name = (
        'togethercomputer/m2-bert-80M-2k-retrieval'
        # Together embedding model
    )
    default_top_k = 3

    def _load_optional_modules(self) -> None:
        self._together = require_dependency(
            'together',
            extra='together',
            context='Together',
        )
        self._Together = self._together.Together

    def _setup(self) -> None:
        """Set up the object with initial parameters."""
        if not self.api_key:
            raise ValueError('API key for Together is required.')
        self.model = self._Together(api_key=self.api_key)

    def get_embedding(self, content: list[str]) -> EmbeddingType:
        """Retrieve the embedding for given texts using Together API."""
        cache_key = sha256(''.join(content).encode('utf-8')).hexdigest()
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cast(EmbeddingType, cached)

        client = cast('Together', self.model)
        all_embeddings = []
        for text in content:
            response = client.embeddings.create(
                model=self.model_name, input=text
            )
            embedding = response.data[0].embedding
            all_embeddings.append(embedding)
        result = np.array(all_embeddings, dtype=np.float32)

        self._save_cache(cache_key, result)

        return result

    def search(
        self, query: str, documents: list[str], top_k: int = 0
    ) -> list[str]:
        """Search an encoded query into vector database."""
        if not hasattr(self, 'db') or not self.db:
            raise Exception('Vector database (db) is not initialized.')
        document_encoded = self.get_embedding(documents)
        query_encoded = self.get_embedding([query])
        top_k = top_k or self.top_k or self.default_top_k or 1

        self.db.embed(document_encoded)
        scores, indices = self.db.search(query_encoded, top_k=top_k)

        self.logs['indices'] = indices
        self.logs['scores'] = scores
        self.logs['search_params'] = {
            'query_encoded': query_encoded,
            'top_k': top_k,
        }

        retrieved_docs = [documents[i] for i in indices if i >= 0]

        return retrieved_docs
