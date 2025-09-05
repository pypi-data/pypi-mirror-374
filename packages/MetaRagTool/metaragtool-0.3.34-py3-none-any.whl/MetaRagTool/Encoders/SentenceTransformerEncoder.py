import sentence_transformers
from sentence_transformers import SentenceTransformer
from MetaRagTool.Encoders.Encoder import Encoder


class SentenceTransformerEncoder(Encoder):
    MODEL_NAME_LABSE = "sentence-transformers/LaBSE"
    MODEL_NAME_E5SMALL='intfloat/multilingual-e5-small'
    def __init__(self, model_name: str, verbose=False):
        import MetaRagTool.Constants as Constants

        super().__init__(model_name, verbose)
        if Constants.trust_remote_code:
            self.model = SentenceTransformer(model_name,trust_remote_code=True)
        else:
            self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")

    def encode(self, sentences, isQuery=True):
        if sentence_transformers.__version__ >= "5.0.0":
            if isQuery:
                embeddings = self.model.encode_query(sentences,
                                               # batch_size=256,
                                               show_progress_bar=not isQuery,
                                               convert_to_tensor=False, normalize_embeddings=True)

            else:
                embeddings = self.model.encode_document(sentences,
                                               # batch_size=256,
                                               show_progress_bar=not isQuery,
                                               convert_to_tensor=False, normalize_embeddings=True)


        else:
            embeddings = self.model.encode_document(sentences,
                                                    # batch_size=256,
                                                    show_progress_bar=not isQuery,
                                                    convert_to_tensor=False, normalize_embeddings=True)


        return embeddings


