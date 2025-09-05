import sentence_transformers
from sentence_transformers import SentenceTransformer
from MetaRagTool.Encoders.Encoder import Encoder


class SentenceTransformerEncoder(Encoder):
    MODEL_NAME_LABSE = "sentence-transformers/LaBSE"
    MODEL_NAME_E5SMALL='intfloat/multilingual-e5-small'
    def __init__(self, model_name: str, verbose=False,query_prompt=None,doc_prompt=None):
        import MetaRagTool.Constants as Constants

        super().__init__(model_name, verbose)
        if Constants.trust_remote_code:
            self.model = SentenceTransformer(model_name,trust_remote_code=True)
        else:
            self.model = SentenceTransformer(model_name)

        self.query_prompt= query_prompt
        self.doc_prompt=doc_prompt
        print("Model loaded successfully")

    def encode(self, sentences, isQuery=True):
        if sentence_transformers.__version__ >= "5.0.0":
            if isQuery:
                embeddings = self.model.encode_query(sentences,
                                               # batch_size=256,
                                               show_progress_bar=not isQuery,
                                               convert_to_tensor=False, normalize_embeddings=True,prompt=self.query_prompt)

            else:
                embeddings = self.model.encode_document(sentences,
                                               # batch_size=256,
                                               show_progress_bar=not isQuery,
                                               convert_to_tensor=False, normalize_embeddings=True,prompt=self.doc_prompt)


        else:

            prompt=self.doc_prompt
            if isQuery:
                prompt = self.query_prompt

            embeddings = self.model.encode(sentences,
                                                    # batch_size=256,
                                                    show_progress_bar=not isQuery,
                                                    convert_to_tensor=False, normalize_embeddings=True,prompt=prompt)


        return embeddings


