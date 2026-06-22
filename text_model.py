# from llama_cpp import Llama
from config import settings
# llm = Llama(
#           model_path= "./Phi-3-mini-4k-instruct-q4.gguf", # path to GGUF file
#           n_ctx=4096,  # The max sequence length to use - note that longer sequence lengths require much more resources
#           n_threads=8, # The number of CPU threads to use, tailor to your system and the resulting performance
#           n_gpu_layers=35, # The number of layers to offload to GPU, if you have GPU acceleration available. Set to 0 if no GPU acceleration is available on your system.
#           temperature = 0.0,
#           top_p = 0.1) #instance 

# class OpenSourceModels:
#     def __init__(self):
#         pass
       
#     def phi3(self, prompt):
#         """
#         Method for phi3 instruct model interactions
#         """
#         output = llm(prompt,
#         max_tokens=100,  # Generate up to 256 tokens
#         stop=["<|end|>"], 
#         echo=False,  # Whether to echo the prompt
#         temperature = 0.0,
#         top_p = 0.1

#     )
#         return output["choices"][0]["text"]

import boto3
import os


class S3_bucket:
    def __init__(self):
        """Initialize the Amazon Bedrock runtime client"""
        self.client = boto3.client(
            service_name="s3",
            region_name="us-east-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
   
    def bucket(self):
        return self.client