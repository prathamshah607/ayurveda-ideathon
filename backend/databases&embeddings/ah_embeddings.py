import pymupdf
import re
import os
from tqdm import tqdm  # <--- Added TQDM import
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuration
PDF_PATH = "asthrid.pdf"
DB_PERSIST_DIRECTORY = "./chroma_db_asthrid" 
EMBEDDING_MODEL_NAME = "intfloat/e5-large-v2"
BATCH_SIZE = 32  # <--- Smaller batches update the progress bar more frequently

class AshtangaIngestor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.current_sthana = "Sutrasthana"
        self.current_chapter = "Introduction"
        
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} 
        )

    def clean_page_text(self, text: str) -> str:
        """Removes headers/footers specific to the 'asthrid.pdf' layout."""
        text = re.sub(r'---\s*PAGE\s*\d+\s*---', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Astanga\s+Hridaya\s+Sutrastha(na|n)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page\s+No\.\s*\d+', '', text, flags=re.IGNORECASE)
        return re.sub(r'\n{3,}', '\n\n', text).strip()

    def extract_structure_info(self, text: str):
        """Detects Chapter headers."""
        chapter_match = re.search(r'Chapter\s+(\d+):\s+([^\n]+)', text, re.IGNORECASE)
        if chapter_match:
            return {
                "chapter_num": chapter_match.group(1),
                "chapter_name": chapter_match.group(2).strip()
            }
        return None

    def load_and_process_pdf(self):
        """Reads PDF with a progress bar."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"File not found: {self.pdf_path}")

        print(f"📖 Opening {self.pdf_path}...")
        doc = pymupdf.open(self.pdf_path)
        processed_docs = []
        
        # Wrapped in tqdm for page processing progress
        for page_num, page in enumerate(tqdm(doc, desc="Reading Pages", unit="pg")):
            text = page.get_text()
            
            structure = self.extract_structure_info(text)
            if structure:
                self.current_chapter = f"Ch {structure['chapter_num']}: {structure['chapter_name']}"
            
            cleaned_text = self.clean_page_text(text)
            
            if len(cleaned_text) < 50:
                continue

            processed_docs.append(Document(
                page_content=cleaned_text,
                metadata={
                    "page": page_num + 1,
                    "sthana": self.current_sthana,
                    "chapter": self.current_chapter,
                    "source": "Astanga_Hridaya_Sutrasthana"
                }
            ))
            
        print(f"✅ Extracted {len(processed_docs)} valid pages.")
        return processed_docs

    def chunk_documents(self, documents):
        """Chunking logic."""
        print("✂️  Chunking documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=[
                "\n\n",
                r"\n\d+\.\s+",
                r"\n[A-Z\s]+:",
                ". ",
                " ",
                ""
            ],
            is_separator_regex=True
        )
        
        chunks = text_splitter.split_documents(documents)
        
        for doc in chunks:
            header = f"SOURCE: {doc.metadata['source']} | {doc.metadata['chapter']}\n---\n"
            doc.page_content = header + doc.page_content
            
        print(f"🧩 Split into {len(chunks)} chunks.")
        return chunks

    def create_vector_db(self, chunks):
        """Embeds chunks in batches with a progress bar."""
        print(f"⚙️  Initializing Vector Store at '{DB_PERSIST_DIRECTORY}'...")
        
        # 1. Initialize empty Chroma instance first
        vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=DB_PERSIST_DIRECTORY
        )
        
        total_chunks = len(chunks)
        print(f"🚀 Starting Embedding Process for {total_chunks} chunks...")

        # 2. Iterate in batches to allow tqdm to update
        # Using a list comprehension to slice chunks into batches
        batches = [chunks[i:i + BATCH_SIZE] for i in range(0, total_chunks, BATCH_SIZE)]

        for batch in tqdm(batches, desc="Embedding Batches", unit="batch"):
            vector_store.add_documents(documents=batch)

        print("✅ Vector Database successfully created and persisted!")

if __name__ == "__main__":
    try:
        ingestor = AshtangaIngestor(PDF_PATH)
        
        # 1. Load & Clean
        raw_docs = ingestor.load_and_process_pdf()
        
        # 2. Chunk
        chunked_docs = ingestor.chunk_documents(raw_docs)
        
        # 3. Vectorize & Save (Now with progress bar!)
        ingestor.create_vector_db(chunked_docs)
        
    except Exception as e:
        print(f"❌ Error: {e}")