from pymongo import MongoClient
from django.conf import settings
import huggingface_hub, json, os
from CONNECTIONS_KEYS import HFACE_ENDPOINT_NAME, HFACE_USER_NAME, HFACE_API_KEY
from haystack.dataclasses import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret
from haystack.components.embedders import HuggingFaceAPIDocumentEmbedder, HuggingFaceAPITextEmbedder
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator


def get_mongo_client():
    client = MongoClient(
        host=settings.MONGO_CLIENT['HOST'],
        port=settings.MONGO_CLIENT['PORT'],
        username=settings.MONGO_CLIENT['USERNAME'],
        password=settings.MONGO_CLIENT['PASSWORD']
    )
    return client

def get_mongo_db():
    client = get_mongo_client()
    db = client[settings.MONGO_CLIENT['DB_NAME']]
    return db



def initiate():
    endpoint = huggingface_hub.get_inference_endpoint(
        name=HFACE_ENDPOINT_NAME,  # endpoint name
        namespace=HFACE_USER_NAME,  # user name
    )
    if endpoint.status == 'paused':
        # print("Endpoint is in: ",endpoint.status, " mode")
        endpoint.resume()
    if endpoint.status != 'running':
        print("Endpoint is in: ", endpoint.status, " mode")
        endpoint.wait()

    status = "Endpoint is in: " + endpoint.status + " mode"
    return status



def chunks_text_file(text, chunk_size=250):
    #with open(file_path, 'r', encoding='utf-8') as file:
        #text = file.read()
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def pipeline_embedder(chunks):
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
    document_embedder = HuggingFaceAPIDocumentEmbedder(
        api_type="inference_endpoints",
        api_params={"url": "https://gcyju4jiduuxjeex.eu-west-1.aws.endpoints.huggingface.cloud"},
        token=Secret.from_token(HFACE_API_KEY)
    )

    documents = []
    for chunk in chunks:
        documents.append(Document(content=chunk))

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("document_embedder", document_embedder)
    indexing_pipeline.add_component("doc_writer", DocumentWriter(document_store=document_store))
    indexing_pipeline.connect("document_embedder", "doc_writer")
    indexing_pipeline.run({"document_embedder": {"documents": documents}})

    return document_store

def write_to_mongodb(filename, document_store):
    documents = document_store.filter_documents(filters=None)
    for doc in documents:
        #embedding_str = json.dumps(doc.embedding)
        db = get_mongo_db()
        data = {
            'file': filename,
            'content': doc.content,
            'embedding': doc.embedding
        }
        result = db["embeddings_RAG"].insert_one(data)

        message = "data is written to db"
    return 1


def fetch_from_mongodb(file_name):
    docstore = InMemoryDocumentStore(embedding_similarity_function="cosine")
    db = get_mongo_db()
    documents_from_db = db["embeddings_RAG"].find({"file": file_name})
    documents = []
    for doc in documents_from_db:
        documents.append(Document(content=doc["content"], embedding=doc["embedding"]))
        #print(doc["content"])


    docstore.write_documents(documents)
    #print(type(docstore))
    return docstore


def pipeline_RAG(documents, query: str = "this is a test"):
    query = query
    print("query:", query)

    template = """
    Given the following information, answer the question.

    Context: 
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Question: {{ query }}?
    """
    pipe = Pipeline()

    query_embedder = HuggingFaceAPITextEmbedder(
        api_type="inference_endpoints",
        api_params={"url": "https://gcyju4jiduuxjeex.eu-west-1.aws.endpoints.huggingface.cloud"},
        token=Secret.from_token(HFACE_API_KEY)
    )

    pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=documents, top_k=5))
    pipe.add_component("query_embedder", query_embedder)
    pipe.add_component("prompt_builder", PromptBuilder(template=template))
    pipe.add_component("llm", OpenAIGenerator(api_key=Secret.from_token(os.environ.get("OPENAI_API_KEY"))))

    pipe.connect("query_embedder.embedding", "retriever.query_embedding")
    pipe.connect("retriever", "prompt_builder.documents")
    pipe.connect("prompt_builder", "llm")

    res = pipe.run({
        "query_embedder": {
            "text": query
        },
        "prompt_builder": {
            "query": query
        }
    }, include_outputs_from={"retriever", "llm"})

    response = res['llm']['replies']
    return response


