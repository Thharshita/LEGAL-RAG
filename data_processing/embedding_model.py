from sentence_transformers import SentenceTransformer
from transformers import GPT2TokenizerFast
# from ..my_logger import logger
model = SentenceTransformer('BAAI/bge-m3')
input_texts = [
    'query: how much protein should a female eat',
    'query: summit define',
    "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    "passage: Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments."
]
embeddings = model.encode(input_texts, normalize_embeddings=True)
print(embeddings)
print(embeddings.shape)


class Create_Embeddings:
    def __init__(self, model_name='BAAI/bge-m3'):
        self.model_name= model_name
        self.model = SentenceTransformer(model_name) 
        # max_length=8192,
        # truncate_length=8192
    def create_embeddings(self, input_texts):
        try:
            embeddings = self.model.encode(input_texts, normalize_embeddings=True)
            # logger.info(f"embeddings:{embeddings}")
            # logger.info(f"type:{type(embeddings)}")
            # logger.info(f"shape:{embeddings.shape}")
            return embeddings
    
        except Exception as e:
            pass
            # logger.info(f"Error while creating embedding:{str(e)}")
    

embedding_obj= Create_Embeddings()
result=embedding_obj.create_embeddings(["what"])
print(result)