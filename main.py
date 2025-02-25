import os
from fastapi import FastAPI

# External dependencies from langchain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Local imports
from prompt_template import getPromptTemplate
from configure_logging import createLogger
import chroma_database

# Constants
CHROMA_PATH = os.getenv('CHROMA_DIR', 'chroma')
PROMPT_TEMPLATE = getPromptTemplate()

logging = createLogger(os.path.basename(__file__))

# FastAPI instance
app = FastAPI()
logging.info("FastApi started.")

# Initialize database
chroma_database.create()

# Initialize Chroma database
embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# Register cleanup function to be called on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    chroma_database.delete()
    logging.info("FastApi shutdown.")

# Route definition
@app.get("/generate/")
def rag(query_text: str):
    logging.info("Query: " + query_text)
    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if not results or results[0][1] < 0.7:
        print("Unable to find matching results.")
        logging.error("Unable to find matching results.")
        return "Unable to find matching results."

    # Prepare context text for the prompt.
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    logging.info("Context Text: " + context_text)

    # Generate prompt.
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)
    logging.info("Prompt: " + prompt)

    # Interact with OpenAI's model.
    model = ChatOpenAI()
    response_text = model.predict(prompt)

    # Prepare formatted response.
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    logging.info("Response: " + formatted_response)

    return "Query: " + query_text, "", prompt, "", formatted_response
