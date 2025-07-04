import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.config import path_to_training_data
import pyspark.sql.functions as F
from src.create_spark_session import create_spark_session


chroma_db_location = './chroma_langchain_db'
embedding = OllamaEmbeddings(model='mxbai-embed-large')


def create_vectore_store(
        path_to_training_data: str = path_to_training_data,
        collection_name: str = 'predictive_maintenance_report',
        db_location: str = chroma_db_location,
        embedding: OllamaEmbeddings = embedding
    ) -> Chroma:
    """
    Create a vector store using training data and embeddings.

    Args:
        path_to_training_data (str): Path to the training data.
        collection_name (str): Name of the collection for the vector store.
        db_location (str): Directory to persist the vector store.
        embedding (OllamaEmbeddings): Embedding model to use.

    Returns:
        Chroma: The created vector store.
    """
    spark = create_spark_session()
    spark_df = spark.read.format('delta').load(path_to_training_data)

    std_sensor_colums = sorted([col for col in spark_df.columns if col.startswith('std_')])
    selected_columns = std_sensor_colums + ['location', 'maintenance_report', 'model', 'state']
    filtered_df = spark_df.select(*selected_columns).filter(F.col('maintenance_report').isNotNull())
    
    rows = filtered_df.collect()
    documents = []
    ids = []

    for idx, row in enumerate(rows):
        document = Document(
            page_content=' '.join(str(row[c]) for c in std_sensor_colums),
            metadata={
                "location": row["location"],
                "model": row["model"],
                "state": row["state"],
                "maintenance_report": row["maintenance_report"]
            },
            id=str(idx)
        )
        ids.append(str(idx))
        documents.append(document)
        
    vectore_store = Chroma(
        collection_name=collection_name,
        persist_directory=db_location,
        embedding_function=embedding
    )
    
    os.makedirs(chroma_db_location, exist_ok=True)
    vectore_store.add_documents(documents=documents, ids=ids)
    
    return vectore_store


def load_vector_store_as_retrieval(
        collection_name: str = 'predictive_maintenance_report',
        db_location: str = chroma_db_location,
        embedding: OllamaEmbeddings = embedding
    ) -> Chroma:
    """
    Load an existing vector store and return it as a retriever.

    Args:
        collection_name (str): Name of the collection for the vector store.
        db_location (str): Directory where the vector store is persisted.
        embedding (OllamaEmbeddings): Embedding model to use.

    Returns:
        Chroma: The vector store as a retriever.
    """
    
    
    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=db_location,
        embedding_function=embedding
    )

    return vector_store.as_retriever(
            search_kwargs={
                'k': 5,
            }
    )


if __name__ == '__main__':
    create_vectore_store()