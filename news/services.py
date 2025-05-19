from sentence_transformers import SentenceTransformer


class TextEmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer(
                "sentence-transformers/use-cmlm-multilingual",
            )
        return cls._instance

    def get_embedding(self, text):
        return self.model.encode(text)
