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
    "asthrid": "./chroma_db_asthrid",      # Ashtanga Hridaya
    "sushruta": "./chroma_sushruta",        # Sushruta Samhita
    "ayurgenix": "./chroma_db_ayurgenix"    # Clinical dataset
}

EMBEDDING_MODEL = "intfloat/e5-large-v2"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

DB_SPECIALIZATIONS = {
    "asthrid": {
        "name": "Ashtanga Hridaya",
        "keywords": ["dosha", "vata", "pitta", "kapha", "prakriti", "dinacharya", "ritucharya", "seasonal", "daily routine", "lifestyle", "diet", "constitution", "balance", "tridosha", "panchakarma", "rasayana", "swasthavritta", "principles", "sutrasthana"],
        "description": "Classical Ayurvedic principles, Dosha theory, daily/seasonal routines, lifestyle guidelines"
    },
    "sushruta": {
        "name": "Sushruta Samhita", 
        "keywords": ["surgery", "surgical", "procedure", "wound", "injury", "trauma", "fracture", "marma", "shalya", "operation", "incision", "excision", "cauterization", "nidana", "diagnosis", "prognosis", "anatomy", "sharira", "instruments", "yantra", "shastra", "suturing", "bloodletting", "raktamokshana", "leech", "bone", "dislocation", "abscess", "tumor", "fistula", "hemorrhoids", "piles"],
        "description": "Surgical procedures, wound care, trauma, anatomical knowledge, diagnostic methods"
    },
    "ayurgenix": {
        "name": "AyurGenix Clinical Database",
        "keywords": ["treatment", "formulation", "medicine", "drug", "prescription", "dosage", "disease", "disorder", "condition", "symptoms", "diagnosis", "cure", "herbs", "herbal", "remedy", "yoga", "asana", "therapy", "diabetes", "hypertension", "arthritis", "fever", "cold", "cough", "infection", "chronic", "acute", "severity", "clinical", "patient", "case"],
        "description": "Clinical disease treatments, herbal formulations, dosages, modern disease correlations"
    }
}

class DualPersonaRAG:
    def __init__(self):
        print("🌿 Initializing Dual-Persona Ayurveda RAG System...")
        
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
        
        # Router LLM
        self.router_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=100
        )
        
        self.doctor_prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic Vaidya engaging in peer-to-peer clinical consultation. 
Your audience is a trained Ayurvedic physician who understands Sanskrit terminology, pathology (Samprapti), and pharmacology (Dravyaguna).

Review the retrieved clinical context and provide a structured, high-level professional response.

CONTEXT FROM CLASSICAL TEXTS & CLINICAL DATA:
{context}

═══════════════════════════════════════════════════════════════
QUERY: {question}
═══════════════════════════════════════════════════════════════

INSTRUCTIONS FOR DOCTOR OUTPUT:
1. **Clinical Precision:** Use precise terminology (e.g., *Samprapti Ghataka*, *Dosha-Dushya Sammurchana*).
2. **Diagnosis & Pathology:** Analyze the *Nidana* (etiology) and *Rupa* (symptomatology) if applicable.
3. **Treatment Protocol (Chikitsa Sutra):**
   - Specific formulations with *Anupana* (adjuvants) and precise dosage.
   - *Shodhana* (purification) appropriateness.
   - *Pathya/Apathya* (Wholesome/Unwholesome regimen).
4. **Prognosis:** Mention if the condition is *Sadhya*, *Krichra-Sadhya*, or *Yapya*.
5. **References:** Explicitly cite the *Sthana* and *Chapter* from the retrieved context.

RESPONSE FORMAT:
- **Samprapti (Pathology):** ...
- **Chikitsa Sutra (Line of Treatment):** ...
- **Aushadhi (Medication):** ...
- **Pathya/Apathya:** ...
- **Clinical References:** ...
""")

        self.patient_prompt = ChatPromptTemplate.from_template("""You are a compassionate Senior Ayurvedic Doctor talking to a patient.
Your goal is to explain the Ayurvedic perspective clearly, confusing terms, offer actionable advice, and ensure safety.

Review the retrieved context and translate it into a patient-friendly guide.

CONTEXT FROM TEXTS:
{context}

═══════════════════════════════════════════════════════════════
PATIENT QUESTION: {question}
═══════════════════════════════════════════════════════════════

INSTRUCTIONS FOR PATIENT OUTPUT:
1. **Clarity & Empathy:** Explain using simple English. If you use a Sanskrit term (like *Vata*), immediately explain what it means (e.g., "the energy of movement").
2. **Actionable Advice:** clearly list what to do and what to avoid.
3. **Diet & Lifestyle:** Focus heavily on *Dinacharya* (daily routine) and diet changes available in a modern kitchen.
4. **Herbal Remedies:** Mention remedies but strictly emphasize safety and consulting a doctor for prescription meds.
5. **Why this helps:** Briefly explain the "Ayurvedic Logic" behind the cure (e.g., "Because you have excess heat, we use cooling herbs...").
6. **Safety Disclaimer:** Always end with a standard medical disclaimer.

RESPONSE FORMAT:
- **Understanding Your Condition:** (Simple explanation)
- **Dietary Advice (Food as Medicine):** ...
- **Lifestyle Changes:** ...
- **Recommended Herbs/Remedies:** ...
- **Important Safety Note:** ...
""")

        # ═══════════════════════════════════════════════════════════════
        # AYUSH HUB PROMPT - Grounded in Official AYUSH Principles
        # ═══════════════════════════════════════════════════════════════
        self.ayush_prompt = ChatPromptTemplate.from_template("""You are an expert consultant for the Ministry of AYUSH (Ayurveda, Yoga & Naturopathy, Unani, Siddha, Homeopathy).
Your role is to explain health queries through the lens of classical Ayurvedic principles as recognized by the Government of India.

Grounding Context from Classical Texts:
{context}

═══════════════════════════════════════════════════════════════
QUERY: {question}
═══════════════════════════════════════════════════════════════

STRUCTURE YOUR RESPONSE USING THESE AYUSH-RECOGNIZED AYURVEDIC PRINCIPLES:

### 1. PANCHAMAHABHUTA (Five Element Analysis)
Analyze which of the five elements are involved in this condition/query:
- **Akasha (Space/Ether):** Governs hollow spaces, sound, and subtle channels.
- **Vayu (Air):** Governs movement, breath, nerve impulses.
- **Agni (Fire):** Governs transformation, metabolism, vision.
- **Jala (Water):** Governs fluidity, taste, cohesion.
- **Prithvi (Earth):** Governs structure, stability, smell.

### 2. TRIDOSHA (Bio-Energy Assessment)
Identify which Dosha(s) are primarily involved and their state (balanced/aggravated/depleted):
- **Vata (Air + Space):** Movement, creativity, anxiety when imbalanced.
- **Pitta (Fire + Water):** Metabolism, intellect, inflammation when imbalanced.
- **Kapha (Earth + Water):** Structure, immunity, congestion when imbalanced.

Explain the *Vikriti* (imbalance) vs ideal *Prakriti* (constitution).

### 3. SAPTADHATU (Tissue Layer Impact)
Which of the seven tissues are affected and how?
1. **Rasa** (Plasma/Lymph) - Nourishment, hydration
2. **Rakta** (Blood) - Oxygenation, vitality
3. **Mamsa** (Muscle) - Strength, movement
4. **Meda** (Fat/Adipose) - Lubrication, energy storage
5. **Asthi** (Bone) - Structure, support
6. **Majja** (Marrow/Nerve) - Nervous system, cognition
7. **Shukra** (Reproductive) - Vitality, immunity, reproduction

### 4. AGNI (Digestive Fire Status)
Assess the state of Agni and its role:
- **Sama Agni:** Balanced digestion (ideal)
- **Vishama Agni:** Irregular (Vata-type)
- **Tikshna Agni:** Hyperactive (Pitta-type)
- **Manda Agni:** Sluggish (Kapha-type)

Is **Ama** (metabolic toxins) present? How to address it?

### 5. MALA (Waste Elimination)
Are the three waste products being eliminated properly?
- **Purisha** (Feces) - Bowel health
- **Mutra** (Urine) - Kidney/bladder function
- **Sweda** (Sweat) - Skin/detox pathways

### 6. SWASTHYA (Path to True Health)
As per Sushruta Samhita, true health (*Swastha*) requires:
- Balanced Doshas
- Balanced Agni
- Healthy Dhatus & proper Mala elimination
- **Prasanna Atma, Indriya, Mana** (Blissful soul, senses, and mind)

Provide the holistic path to achieve this state for the given query.

### 7. RECOMMENDED INTERVENTIONS
Based on the above analysis, recommend:
- **Ahara (Diet):** Specific foods to favor/avoid
- **Vihara (Lifestyle):** Daily routine adjustments
- **Aushadhi (Medicine):** Herbal formulations if applicable
- **Yoga/Pranayama:** Specific practices if relevant

### 8. CLASSICAL REFERENCES
Cite the source texts from the context (Ashtanga Hridaya, Sushruta Samhita, etc.)
""")

        print("✅ Triple-Persona System Ready (Doctor | Patient | AYUSH Hub)!\n")

    def _keyword_route(self, question: str) -> List[str]:
        question_lower = question.lower()
        scores = {}
        for db_name, spec in DB_SPECIALIZATIONS.items():
            if db_name not in self.vector_stores: continue
            score = sum(1 for kw in spec['keywords'] if kw in question_lower)
            scores[db_name] = score
        sorted_dbs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_dbs and sorted_dbs[0][1] >= 2: return [sorted_dbs[0][0]]
        if sorted_dbs and sorted_dbs[0][1] >= 1: return [db for db, score in sorted_dbs[:2] if score > 0]
        return []

    def _llm_route(self, question: str) -> List[str]:
        available_dbs = list(self.vector_stores.keys())
        routing_prompt = f"""Router for Ayurveda system.
Databases:
1. asthrid: Principles, Dosha, Lifestyle
2. sushruta: Surgery, Anatomy, Wound care
3. ayurgenix: Clinical treatments, formulations

Query: {question}
Which DBs? Return names comma-separated (e.g., "asthrid,sushruta").
Answer:"""
        try:
            response = self.router_llm.invoke(routing_prompt)
            content = response.content.strip().lower()
            selected = [db for db in available_dbs if db in content]
            return selected if selected else available_dbs
        except:
            return available_dbs

    def _retrieve_and_build_context(self, question: str) -> str:
        # Route
        kw_route = self._keyword_route(question)
        targets = kw_route if kw_route else self._llm_route(question)
        
        # Retrieve
        docs_map = {}
        for db in targets:
            if db in self.retrievers:
                docs_map[db] = self.retrievers[db].invoke(question)
        
        # Fallback if empty (basic check)
        if not any(docs_map.values()):
            all_dbs = list(self.vector_stores.keys())
            remaining = [db for db in all_dbs if db not in targets]
            for db in remaining:
                docs_map[db] = self.retrievers[db].invoke(question)
        
        # Build Context String
        context_parts = []
        for db_name, docs in docs_map.items():
            if docs:
                source_name = DB_SPECIALIZATIONS[db_name]['name']
                context_parts.append(f"\nSOURCE: {source_name}")
                for i, doc in enumerate(docs, 1):
                    meta = doc.metadata
                    meta_str = f"Ch: {meta.get('chapter', '?')} | Topic: {meta.get('disease', 'General')}"
                    context_parts.append(f"[{i}] {meta_str}\n{doc.page_content}")
        return "\n".join(context_parts)

    def generate_responses(self, question: str, modes: List[str] = None) -> Dict[str, str]:
        """
        Generate responses for specified modes.
        modes: List containing any of ['doctor', 'patient', 'ayush']. Defaults to all three.
        """
        if modes is None:
            modes = ['doctor', 'patient', 'ayush']
        
        print(f"🔍 Processing Query: {question}")
        context = self._retrieve_and_build_context(question)
        
        results = {"context_used": context}
        
        # Chain 1: Doctor
        if 'doctor' in modes:
            print("   • Generating Doctor Response...")
            doctor_chain = self.doctor_prompt | self.llm | StrOutputParser()
            results["doctor_response"] = doctor_chain.invoke({"context": context, "question": question, "sources": "Combined Knowledge Base"})
        
        # Chain 2: Patient
        if 'patient' in modes:
            print("   • Generating Patient Response...")
            patient_chain = self.patient_prompt | self.llm | StrOutputParser()
            results["patient_response"] = patient_chain.invoke({"context": context, "question": question})
        
        # Chain 3: AYUSH Hub
        if 'ayush' in modes:
            print("   • Generating AYUSH Hub Response...")
            ayush_chain = self.ayush_prompt | self.llm | StrOutputParser()
            results["ayush_response"] = ayush_chain.invoke({"context": context, "question": question})
        
        return results

if __name__ == "__main__":
    rag = DualPersonaRAG()
    
    print("\n" + "═"*60)
    print("🏥 AYURVEDA TRIPLE-PERSONA RAG SYSTEM")
    print("═"*60)
    print("Modes: [1] Doctor  [2] Patient  [3] AYUSH Hub  [A] All")
    print("Commands: 'q' to quit, 'help' for examples")
    print("═"*60)
    
    while True:
        q = input("\n🩺 Enter Medical Query (or 'q' to quit): ").strip()
        if q.lower() in ['q', 'quit']: 
            print("\n🙏 Namaste! Stay healthy.")
            break
        if q.lower() == 'help':
            print("\nExample queries:")
            print("  • What is the Ayurvedic treatment for diabetes?")
            print("  • How to balance Vata dosha?")
            print("  • What causes constipation according to Ayurveda?")
            continue
        if not q: continue
        
        # Mode selection
        mode_input = input("📋 Select mode [1/2/3/A] (default: A): ").strip().lower()
        if mode_input == '1':
            modes = ['doctor']
        elif mode_input == '2':
            modes = ['patient']
        elif mode_input == '3':
            modes = ['ayush']
        else:
            modes = ['doctor', 'patient', 'ayush']
        
        results = rag.generate_responses(q, modes)
        
        # Display Doctor Response
        if 'doctor_response' in results:
            print("\n" + "█"*60)
            print("👨‍⚕️ FOR THE AYURVEDIC PHYSICIAN (Clinical Perspective)")
            print("█"*60)
            print(results['doctor_response'])
        
        # Display Patient Response
        if 'patient_response' in results:
            print("\n" + "·"*60)
            print("🧘 FOR THE PATIENT (Simple & Actionable)")
            print("·"*60)
            print(results['patient_response'])
        
        # Display AYUSH Hub Response
        if 'ayush_response' in results:
            print("\n" + "╔" + "═"*58 + "╗")
            print("║" + " 🏛️  AYUSH HUB (Ministry-Aligned Principles) ".center(58) + "║")
            print("╚" + "═"*58 + "╝")
            print(results['ayush_response'])
