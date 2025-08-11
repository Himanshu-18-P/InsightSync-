import os
import pickle
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader


class PDFIndexer:
    def __init__(self):
        self.pdf_path = None
        self.index_dir = None

        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def set_path(self , pdf_path , index_dir ):
        self.pdf_path = pdf_path
        self.index_dir = index_dir

        os.makedirs(index_dir, exist_ok=True)


    def extract_pdf_text(self, split: bool = True) -> List[Document]:
        """
        Load PDF using LangChain PyPDFLoader and optionally split into chunks.
        """
        loader = PyPDFLoader(self.pdf_path)
        raw_docs = loader.load()

        if not split:
            return raw_docs

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        return splitter.split_documents(raw_docs)

    def build_and_save_indexes(self, split: bool = True):
        """
        Builds and saves FAISS and BM25 indexes for the PDF.
        """
        faiss_path = os.path.join(self.index_dir, "faiss")
        bm25_path = os.path.join(self.index_dir, "bm25.pkl")

        if os.path.exists(faiss_path) and os.path.exists(bm25_path):
            print("Indexes already exist. Skipping rebuild.")
            return

        documents = self.extract_pdf_text(split=split)

        # Build FAISS
        faiss_index = FAISS.from_documents(documents, self.embedding_model)
        faiss_index.save_local(faiss_path)

        # Build BM25
        bm25_index = BM25Retriever.from_documents(documents)
        with open(bm25_path, "wb") as f:
            pickle.dump(bm25_index, f)

        print(f"✅ Indexes built and saved to: {self.index_dir}")

    def load_hybrid_retriever(self , index_dir) -> EnsembleRetriever:
        """
        Loads both FAISS and BM25 retrievers into an EnsembleRetriever.
        """
        faiss_path = os.path.join(index_dir, "faiss")
        bm25_path = os.path.join(index_dir, "bm25.pkl")

        faiss_index = FAISS.load_local(
            faiss_path,
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True
        )

        with open(bm25_path, "rb") as f:
            bm25_index = pickle.load(f)

        retriever = EnsembleRetriever(
            retrievers=[faiss_index.as_retriever(), bm25_index],
            weights=[0.5, 0.5]  # Tune this if needed
        )

        return retriever

    def get_top_k_results(self, index_dir ,  query: str, top_k: int = 5) -> List[dict]:
        """
        Hybrid retrieval on the indexed PDF content.
        Returns a list of result dicts with content and metadata.
        """
        retriever = self.load_hybrid_retriever(index_dir)
        results: List[Document] = retriever.invoke(query, k=top_k)

        return [
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in results
        ]

if __name__ == '__main__':
    print('done')