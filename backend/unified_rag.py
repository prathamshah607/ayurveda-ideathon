import os
import torch
from typing import List, Dict, Tuple, Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# --- CONFIGURATION ---
DB_PATHS = {
    "asthrid": "./chroma_db_asthrid",      # Ashtanga Hridaya - General Ayurveda principles
    "sushruta": "./chroma_sushruta",        # Sushruta Samhita - Surgery & procedures
    "ayurgenix": "./chroma_db_ayurgenix"    # Clinical dataset - Disease treatments
}

EMBEDDING_MODEL = "intfloat/e5-large-v2"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required. Set it before running.")

# Database specializations for routing
DB_SPECIALIZATIONS = {
    "asthrid": {
        "name": "Ashtanga Hridaya",
        "keywords": [
            "dosha", "vata", "pitta", "kapha", "prakriti", "dinacharya", "ritucharya",
            "seasonal", "daily routine", "lifestyle", "diet", "constitution", "balance",
            "tridosha", "panchakarma", "rasayana", "swasthavritta", "principles",
            "sutrasthana", "basic", "fundamental", "ayurveda basics", "health maintenance"
        ],
        "description": "Classical Ayurvedic principles, Dosha theory, daily/seasonal routines, lifestyle guidelines"
    },
    "sushruta": {
        "name": "Sushruta Samhita", 
        "keywords": [
            "surgery", "surgical", "procedure", "wound", "injury", "trauma", "fracture",
            "marma", "shalya", "operation", "incision", "excision", "cauterization",
            "nidana", "diagnosis", "prognosis", "anatomy", "sharira", "instruments",
            "yantra", "shastra", "suturing", "bloodletting", "raktamokshana", "leech",
            "bone", "dislocation", "abscess", "tumor", "fistula", "hemorrhoids", "piles"
        ],
        "description": "Surgical procedures, wound care, trauma, anatomical knowledge, diagnostic methods"
    },
    "ayurgenix": {
        "name": "AyurGenix Clinical Database",
        "keywords": [
            "treatment", "formulation", "medicine", "drug", "prescription", "dosage",
            "disease", "disorder", "condition", "symptoms", "diagnosis", "cure",
            "herbs", "herbal", "remedy", "yoga", "asana", "therapy", "diabetes",
            "hypertension", "arthritis", "fever", "cold", "cough", "infection",
            "chronic", "acute", "severity", "clinical", "patient", "case"
        ],
        "description": "Clinical disease treatments, herbal formulations, dosages, modern disease correlations"
    }
}


class UnifiedAyurvedaRAG:
    def __init__(self):
        print("🌿 Initializing Unified Ayurveda RAG System...")
        
        # Initialize embeddings
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Using device: {device}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': device}
        )
        
        # Load all vector stores
        self.vector_stores: Dict[str, Chroma] = {}
        self.retrievers: Dict[str, any] = {}
        
        for db_name, db_path in DB_PATHS.items():
            if os.path.exists(db_path):
                print(f"   ✓ Loading {DB_SPECIALIZATIONS[db_name]['name']}...")
                self.vector_stores[db_name] = Chroma(
                    persist_directory=db_path,
                    embedding_function=self.embeddings
                )
                self.retrievers[db_name] = self.vector_stores[db_name].as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
            else:
                print(f"   ⚠ Warning: {db_path} not found, skipping...")
        
        if not self.vector_stores:
            raise FileNotFoundError("❌ No vector databases found!")
        
        # Initialize LLM
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=8192
        )
        
        # Router LLM (faster model for routing decisions)
        self.router_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=100
        )
        
        print("✅ Unified RAG System Ready!\n")
        self._print_available_sources()
    
    def _print_available_sources(self):
        """Print available knowledge sources"""
        print("📚 Available Knowledge Sources:")
        for db_name in self.vector_stores.keys():
            spec = DB_SPECIALIZATIONS[db_name]
            print(f"   • {spec['name']}: {spec['description']}")
        print()
    
    def _keyword_route(self, question: str) -> List[str]:
        """Fast keyword-based routing"""
        question_lower = question.lower()
        scores = {}
        
        for db_name, spec in DB_SPECIALIZATIONS.items():
            if db_name not in self.vector_stores:
                continue
            score = sum(1 for kw in spec['keywords'] if kw in question_lower)
            scores[db_name] = score
        
        # Sort by score descending
        sorted_dbs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # If top score is significantly higher, route to that DB
        if sorted_dbs and sorted_dbs[0][1] >= 2:
            return [sorted_dbs[0][0]]
        
        # If scores are close or low, return top 2 or all
        if sorted_dbs and sorted_dbs[0][1] >= 1:
            return [db for db, score in sorted_dbs[:2] if score > 0]
        
        return []  # No clear match, will trigger LLM routing
    
    def _llm_route(self, question: str) -> List[str]:
        """LLM-based intelligent routing for complex queries"""
        available_dbs = list(self.vector_stores.keys())
        
        routing_prompt = f"""You are a query router for an Ayurveda knowledge system.
Given the user's question, determine which database(s) to query.

Available databases:
1. asthrid - Ashtanga Hridaya: Dosha theory, constitution, daily routines, seasonal regimens, lifestyle, fundamental Ayurvedic principles
2. sushruta - Sushruta Samhita: Surgical procedures, anatomy, wound care, trauma, diagnostic methods, marma points
3. ayurgenix - Clinical Database: Disease treatments, herbal formulations with dosages, modern disease names, clinical protocols

User Question: {question}

Respond with ONLY the database name(s) separated by comma. Choose 1-2 most relevant.
Examples: "ayurgenix" or "asthrid,sushruta" or "sushruta"

Answer:"""
        
        try:
            response = self.router_llm.invoke(routing_prompt)
            content = response.content.strip().lower()
            
            # Parse response
            selected = []
            for db in available_dbs:
                if db in content:
                    selected.append(db)
            
            return selected if selected else available_dbs
        except Exception as e:
            print(f"   ⚠ Router error: {e}, using all databases")
            return available_dbs
    
    def route_query(self, question: str) -> Tuple[List[str], str]:
        """
        Route query to appropriate database(s)
        Returns: (list of db names, routing method used)
        """
        # Try keyword routing first (fast)
        keyword_result = self._keyword_route(question)
        
        if keyword_result:
            return keyword_result, "keyword"
        
        # Fall back to LLM routing (slower but smarter)
        llm_result = self._llm_route(question)
        return llm_result, "llm"
    
    def _retrieve_from_dbs(self, question: str, db_names: List[str]) -> Dict[str, List[Document]]:
        """Retrieve documents from specified databases"""
        results = {}
        for db_name in db_names:
            if db_name in self.retrievers:
                docs = self.retrievers[db_name].invoke(question)
                results[db_name] = docs
        return results
    
    def _evaluate_response_quality(self, response: str, question: str) -> float:
        """Quick heuristic to evaluate if response is adequate"""
        # Check for indicators of poor response
        poor_indicators = [
            "i don't have",
            "cannot find",
            "no information",
            "not available",
            "i'm not sure",
            "context doesn't contain",
            "unable to answer"
        ]
        
        response_lower = response.lower()
        
        # Count poor indicators
        poor_score = sum(1 for ind in poor_indicators if ind in response_lower)
        
        # Check response length
        if len(response) < 100:
            poor_score += 1
        
        # Calculate quality score (0-1)
        quality = max(0, 1 - (poor_score * 0.3))
        return quality
    
    def _build_context(self, all_docs: Dict[str, List[Document]]) -> str:
        """Build context string from multiple sources"""
        context_parts = []
        
        for db_name, docs in all_docs.items():
            if docs:
                source_name = DB_SPECIALIZATIONS[db_name]['name']
                context_parts.append(f"\n{'='*60}")
                context_parts.append(f"SOURCE: {source_name}")
                context_parts.append('='*60)
                
                for i, doc in enumerate(docs, 1):
                    # Add metadata if available
                    meta_info = []
                    if 'chapter' in doc.metadata:
                        meta_info.append(f"Chapter: {doc.metadata['chapter']}")
                    if 'sthana' in doc.metadata:
                        meta_info.append(f"Sthana: {doc.metadata['sthana']}")
                    if 'disease' in doc.metadata:
                        meta_info.append(f"Disease: {doc.metadata['disease']}")
                    if 'page' in doc.metadata:
                        meta_info.append(f"Page: {doc.metadata['page']}")
                    
                    meta_str = " | ".join(meta_info) if meta_info else ""
                    context_parts.append(f"\n[{i}] {meta_str}")
                    context_parts.append(doc.page_content)
        
        return "\n".join(context_parts)
    
    def query(self, question: str, verbose: bool = True) -> Dict:
        """
        Main query method with intelligent routing and fallback
        """
        if verbose:
            print(f"\n🔍 Query: {question}")
        
        # Step 1: Route the query
        primary_dbs, route_method = self.route_query(question)
        
        if verbose:
            db_names = [DB_SPECIALIZATIONS[db]['name'] for db in primary_dbs]
            print(f"📍 Routing ({route_method}): {', '.join(db_names)}")
        
        # Step 2: Retrieve from primary database(s)
        primary_docs = self._retrieve_from_dbs(question, primary_dbs)
        
        # Step 3: Generate initial response
        context = self._build_context(primary_docs)
        response = self._generate_response(question, context, primary_dbs)
        
        # Step 4: Evaluate response quality
        quality = self._evaluate_response_quality(response, question)
        
        if verbose:
            print(f"📊 Response quality: {quality:.2f}")
        
        # Step 5: Fallback to all databases if quality is low
        fallback_used = False
        if quality < 0.6:
            if verbose:
                print("🔄 Quality low, querying all databases...")
            
            all_dbs = list(self.vector_stores.keys())
            remaining_dbs = [db for db in all_dbs if db not in primary_dbs]
            
            if remaining_dbs:
                fallback_docs = self._retrieve_from_dbs(question, remaining_dbs)
                
                # Merge documents
                all_docs = {**primary_docs, **fallback_docs}
                context = self._build_context(all_docs)
                response = self._generate_response(question, context, all_dbs)
                fallback_used = True
        
        # Step 6: Collect source information
        sources = []
        docs_used = primary_docs if not fallback_used else {**primary_docs, **fallback_docs}
        
        for db_name, docs in docs_used.items():
            for doc in docs:
                sources.append({
                    "source": DB_SPECIALIZATIONS[db_name]['name'],
                    "metadata": doc.metadata,
                    "excerpt": doc.page_content[:200] + "..."
                })
        
        return {
            "answer": response,
            "sources": sources,
            "routing": {
                "primary_databases": primary_dbs,
                "route_method": route_method,
                "fallback_used": fallback_used
            }
        }
    
    def _generate_response(self, question: str, context: str, db_names: List[str]) -> str:
        """Generate response using LLM"""
        source_names = [DB_SPECIALIZATIONS[db]['name'] for db in db_names if db in DB_SPECIALIZATIONS]
        
        prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic physician (Vaidya) with deep knowledge of classical texts and clinical practice.

You have access to knowledge from: {sources}

CONTEXT FROM AYURVEDIC SOURCES:
{context}

═══════════════════════════════════════════════════════════════
USER QUESTION: {question}
═══════════════════════════════════════════════════════════════

INSTRUCTIONS:
1. Answer based ONLY on the provided context. Do not invent information.
2. Structure your response clearly with sections if needed.
3. Preserve Sanskrit/Hindi terms exactly as written (e.g., Vāta, Pitta, Kapha).
4. For treatments, include:
   • Herbs/Formulations with dosages if available
   • Dietary recommendations
   • Lifestyle modifications
5. Cite the source text when possible (e.g., "According to Sushruta Samhita...").
6. If context doesn't contain the answer, clearly state what information is missing.

ANSWER:""")
        
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "sources": ", ".join(source_names),
            "context": context,
            "question": question
        })
    
    def interactive_session(self):
        """Run interactive query session"""
        print("\n" + "="*60)
        print("🌿 UNIFIED AYURVEDA KNOWLEDGE SYSTEM")
        print("="*60)
        print("Ask questions about Ayurveda. Type 'quit' to exit.")
        print("Commands: 'sources' - show available sources")
        print("          'help' - show example queries")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n📝 Your Question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n🙏 Namaste! Stay healthy.")
                    break
                
                if user_input.lower() == 'sources':
                    self._print_available_sources()
                    continue
                
                if user_input.lower() == 'help':
                    self._print_example_queries()
                    continue
                
                # Process query
                result = self.query(user_input)
                
                # Display answer
                print("\n" + "="*60)
                print("🏥 VAIDYA'S RESPONSE:")
                print("="*60)
                print(result['answer'])
                
                # Display sources
                print("\n" + "-"*60)
                print("📚 SOURCES CITED:")
                seen_sources = set()
                for i, src in enumerate(result['sources'][:5], 1):
                    source_key = f"{src['source']}-{src['metadata']}"
                    if source_key not in seen_sources:
                        seen_sources.add(source_key)
                        meta_parts = []
                        for key in ['chapter', 'sthana', 'disease', 'page']:
                            if key in src['metadata']:
                                meta_parts.append(f"{key}: {src['metadata'][key]}")
                        meta_str = " | ".join(meta_parts) if meta_parts else ""
                        print(f"  {i}. {src['source']} - {meta_str}")
                
                # Show routing info
                routing = result['routing']
                route_info = f"Routed via: {routing['route_method']}"
                if routing['fallback_used']:
                    route_info += " → fallback to all DBs"
                print(f"\n🔀 {route_info}")
                print("-"*60)
                
            except KeyboardInterrupt:
                print("\n\n🙏 Namaste! Stay healthy.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _print_example_queries(self):
        """Print example queries for each database"""
        print("\n📖 Example Queries:")
        print("\n  Ashtanga Hridaya (Principles & Lifestyle):")
        print("    • What is the daily routine (dinacharya) according to Ayurveda?")
        print("    • Explain the three doshas and their characteristics")
        print("    • What foods should Pitta prakriti people avoid?")
        
        print("\n  Sushruta Samhita (Surgery & Diagnosis):")
        print("    • What are the marma points in Ayurveda?")
        print("    • How does Sushruta describe wound healing?")
        print("    • What are the diagnostic methods (nidana) for diseases?")
        
        print("\n  AyurGenix Clinical (Treatments):")
        print("    • What is the Ayurvedic treatment for diabetes?")
        print("    • Give me the formulation for arthritis")
        print("    • What herbs are used for hypertension?")


# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    try:
        # Initialize the unified system
        rag = UnifiedAyurvedaRAG()
        
        # Run interactive session
        rag.interactive_session()
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("Please ensure at least one vector database exists.")
    except Exception as e:
        print(f"\n❌ Initialization Error: {e}")
        raise