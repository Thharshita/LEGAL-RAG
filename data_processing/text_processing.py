from langchain_text_splitters import RecursiveCharacterTextSplitter
from my_logger import logger
# Load example document
with open("D:\\ProductionReadyRag\\test.txt", encoding="utf-8") as f:
    state_of_the_union = f.read()
    print(f"Loaded document with {len(state_of_the_union)} characters")

def text_splitter(pages, chunk_length=700):
    try:  
        cleaned_page_content="/n".join(text for _,text  in pages)
        logger.info('splitting_text')  
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_length,
            chunk_overlap=20,
            length_function=len,
            separators=['\n\n','\n','.']
            )
        splitted_text = splitter.split_text(cleaned_page_content)
        logger.info(f"Text split into {len(splitted_text)} chunks")
        logger.info(f"First chunk: {splitted_text[0]}")
        return splitted_text
    
    except Exception as e:
        logger.error(f"An error occurred while splitting text: {str(e)}")
        return 0, str(e)
    
text_splitter(state_of_the_union, 700)
    

#run using python -m data_processing.text_processing