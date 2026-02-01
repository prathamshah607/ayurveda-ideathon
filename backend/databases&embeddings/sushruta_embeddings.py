# Install these exact packages
# pip install langchain==0.3.24 langchain-chroma langchain-huggingface langchain-text-splitters langchain-groq pymupdf chromadb sentence-transformers

import pymupdf
import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


class SushrutaSamhitaRAG:
    def __init__(self, pdf_path, groq_api_key):
        self.pdf_path = pdf_path
        self.documents = []
        self.vector_store = None
        self.current_sthana = "Unknown"
        self.current_chapter = "Unknown"
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/e5-large-v2"
        )
        
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=4000
        )
    
    def extract_pdf_with_metadata(self):
        """Extract text from PDF with Sthana/Chapter hierarchy"""
        doc = pymupdf.open(self.pdf_path)
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text = self.clean_text(text)
            
            # Skip index/TOC/blank pages
            if self.is_index_page(text) or len(text.strip()) < 100:
                continue
            
            # Extract structure and update tracking
            structure_info = self.extract_structure_info(text, page_num)
            
            # Update current tracking if new section/chapter found
            if structure_info.get("sthana"):
                self.current_sthana = structure_info["sthana"]
                print(f"Page {page_num + 1}: Found Sthana = {self.current_sthana}")
            
            if structure_info.get("chapter"):
                self.current_chapter = structure_info["chapter"]
                print(f"Page {page_num + 1}: Found Chapter = {self.current_chapter}")
            
            self.documents.append(Document(
                page_content=text,
                metadata={
                    "page": page_num + 1,
                    "sthana": self.current_sthana,
                    "chapter": self.current_chapter,
                    "source": self.pdf_path
                }
            ))
        
        print(f"\nExtracted {len(self.documents)} pages from {doc.page_count} total pages")
        doc.close()
    
    def clean_text(self, text):
        """Clean headers, footers, page numbers while preserving structure"""
        # Remove standalone page numbers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[ivxlcdm]+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def is_index_page(self, text):
        """Detect TOC/index pages"""
        if re.search(r'^\s*CONTENT', text, re.MULTILINE | re.IGNORECASE):
            return True
        
        page_ref_pattern = r'[\.\s]{3,}\s*\d+'
        matches = re.findall(page_ref_pattern, text)
        if len(matches) > 5:
            return True
        
        return False
    
    def extract_structure_info(self, text, page_num):
        """Extract Sthana and Chapter information - based on actual PDF format"""
        info = {}
        
        # Look in first 800 chars
        header_text = text[:800]
        
        # STHANA DETECTION - Based on debug output
        # Format 1: "NIDANA STHANA" or "SARIRA STHANAM" (word STHANA/STHANAM)
        # Format 2: "(Section on Anatomy)" or "(Section on Toxicology)"
        
        sthana_patterns = [
            # Match lines like "NIDANA  STHANA" or "SARIRA  STHANAM"
            (r'([A-Z][A-Z\-]+)\s+STHAN[AM]', 'direct'),
            # Match "(Section on Anatomy)" etc
            (r'\(Section\s+on\s+([A-Za-z]+)\)', 'section'),
        ]
        
        for pattern, ptype in sthana_patterns:
            match = re.search(pattern, header_text, re.IGNORECASE)
            if match:
                sthana_name = match.group(1).strip()
                # Clean up the name
                sthana_name = sthana_name.replace('-', ' ').title()
                info["sthana"] = sthana_name
                break
        
        # CHAPTER DETECTION - Based on debug output
        # Format: "CHAPTER I." or "CHAPTER II." followed by title on next line
        # Title starts with "Now we shall discourse..." or "The ..."
        
        chapter_patterns = [
            # Match CHAPTER + Roman numeral + optional title
            r'CHAPTER\s+([IVXLCDM]+)\.\s*\n+(.+?)(?:\n|\()',
            # Match just CHAPTER + Roman numeral
            r'CHAPTER\s+([IVXLCDM]+)\.',
        ]
        
        for pattern in chapter_patterns:
            match = re.search(pattern, header_text, re.IGNORECASE)
            if match:
                chapter_num = match.group(1).strip()
                
                if len(match.groups()) > 1 and match.group(2):
                    chapter_title = match.group(2).strip()
                    # Clean up title
                    chapter_title = re.sub(r'\s+', ' ', chapter_title)
                    # Remove "Now we shall discourse on the" prefix
                    chapter_title = re.sub(r'^Now\s+w[ec]\s+shall\s+discourse\s+on\s+(the\s+)?', '', chapter_title, flags=re.IGNORECASE)
                    # Remove "The" at start
                    chapter_title = re.sub(r'^The\s+', '', chapter_title)
                    # Take first reasonable chunk before period or colon
                    chapter_title = re.split(r'[:\.]', chapter_title)[0]
                    # Truncate long titles
                    if len(chapter_title) > 60:
                        chapter_title = chapter_title[:57] + "..."
                    info["chapter"] = f"Chapter {chapter_num}: {chapter_title}"
                else:
                    info["chapter"] = f"Chapter {chapter_num}"
                break
        
        return info
    
    def chunk_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=400,
            separators=["\n\n", "\n", ":—", "—", ". ", " ", ""]
        )
        
        chunks = []
        for doc in self.documents:
            # Use split_text() then create Documents manually
            split_texts = text_splitter.split_text(doc.page_content)
            
            for chunk_text in split_texts:
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata=doc.metadata.copy()
                ))
        
        print(f"Created {len(chunks)} chunks from {len(self.documents)} pages")
        return chunks

    def create_vector_store(self, chunks, persist_directory="./chroma_sushruta"):
        print(f"Creating vector store for {len(chunks)} chunks...")
        print("This may take 5-10 minutes on CPU with e5-large-v2...")
        
        # Add progress tracking
        from tqdm import tqdm
        for i in tqdm(range(0, len(chunks), 100)):
            batch = chunks[i:i+100]
            if i == 0:
                self.vector_store = Chroma.from_documents(
                    documents=batch,
                    embedding=self.embeddings,
                    persist_directory=persist_directory,
                    collection_name="sushruta_samhita"
                )
            else:
                self.vector_store.add_documents(batch)
        
        print(f"Vector store created with {len(chunks)} chunks")

    
    def load_vector_store(self, persist_directory="./chroma_sushruta"):
        """Load existing vector store"""
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="sushruta_samhita"
        )
        print("Loaded existing vector store")
    
    def query(self, question, k=30):
        
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(question)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""You are an expert in Ayurveda, specifically knowledgeable about Sushruta Samhita. 
Use the following context from Sushruta Samhita to answer the question. If the context doesn't contain the answer, say so clearly.
When citing Sanskrit terms (like Vāta, Pitta, Kapha, Nidāna, etc.), preserve them exactly as written.

Context: {context}

Question: {question}

Answer (provide detailed explanation with Sthana and chapter references when possible):"""
        
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        print(f"\nQuestion: {question}")
        print(f"\nAnswer: {answer}\n")
        
        print("Sources:")
        for i, doc in enumerate(docs, 1):
            print(f"\n{i}. Sthana: {doc.metadata.get('sthana', 'Unknown')}")
            print(f"   Chapter: {doc.metadata.get('chapter', 'Unknown')}")
            print(f"   Page: {doc.metadata.get('page', 'Unknown')}")
            print(f"   Excerpt: {doc.page_content[:250]}...")
        
        return {"answer": answer, "source_documents": docs}


# Usage
if __name__ == "__main__":
    import os
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    rag = SushrutaSamhitaRAG(
        pdf_path="sush.pdf",
        groq_api_key=groq_key
    )
    
    # First time: extract and create vector store
    rag.extract_pdf_with_metadata()
    chunks = rag.chunk_documents()
    rag.create_vector_store(chunks)
    print("Vector store created and persisted.")