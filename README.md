# PRIME-KG VN: Clinical Knowledge Graph (ICD-10 & OMOP CDM)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data: Clinical](https://img.shields.io/badge/Data-Clinical_Medicine-red.svg)]()

**PRIME-KG VN (Scientific Edition)** is an automated system for gathering, extracting, and constructing a medical knowledge graph with a deep focus on clinical aspects.

Using the **ICD-10** coding system from the Vietnamese Ministry of Health as its backbone, this project creates a structured network linking diseases with tens of thousands of other medical entities (Symptoms, Drugs, Complications, etc.). Data is aggregated and automatically cleaned from official domestic and international sources. The entire graph structure is mapped to be compatible with the **OMOP CDM 5.3.1** standard.

---

## 💡 Technical Features & System Architecture

The system is built with fault-tolerant principles and rigorous data architecture:

* **Hard-Anchoring Architecture:** Unlike random graph generation systems, this platform does **NOT** use LLMs to hallucinate relationship types. Edges are mathematically defined via `RELATION_RULES`, and internal `EXCLUDES`/`INCLUDES` links are extracted directly from the WHO guidance columns in the source ICD-10 file.
* **Knowledge Hub (Deduplication):** Merges identical Nodes (based on SHA-256 hash), automatically concatenating descriptions and `evidence` from multiple articles into a single, comprehensive Node.
* **igraph & Neo4j Compatibility:** Generates continuous `node_index` values, ensuring 100% accurate `x_id`/`y_id` mapping, ready for ingestion into any graph database.
* **Anti-Crash Mechanism:** Integrates cross-audit features to resume from checkpoints on failed disease extractions. Combines auto-save per cluster and a rotating SearXNG URL algorithm to bypass rate-limiting.

---

## 🌐 5-Tier Data Pipeline & Multi-Language Support

Web scraping is optimized using `ThreadPoolExecutor` and divided into five tiers of authority. **Notably, the system automatically translates keywords into English** when querying international tiers:

1. **Tier 1 (VN Official):** `gov.vn`, `tapchiyhocduphong.vn`, `vjmed.org.vn`, etc.
2. **Tier 2 (VN Major Hospitals):** `vinmec.com`, `nhathuoclongchau.com.vn`, `medlatec.vn`, etc.
3. **Tier 3 (International Academia - Auto-translated):** `ncbi.nlm.nih.gov`, `thelancet.com`, `jamanetwork.com`, etc.
4. **Tier 4 (Health Organizations - Auto-translated):** `who.int`, `cdc.gov`, `mayoclinic.org`, etc.
5. **Tier 5 (Extended Sources):** Performs open-search queries if the top 4 tiers do not provide the required number of articles.

---

## 🤖 Multi-Agent AI Pipeline

Instead of a single bloated prompt, the system utilizes Ollama (Qwen3-VL 8B) operating three independent agents with strict `format: json` enforcement:

1. **Agent Evaluator (Gatekeeper):** Analyzes the first 2,000 characters of the article. **Blocks** pure Veterinary documents (treating pigs, chickens, dogs, cats) while remaining intelligent enough to **Allow** articles concerning Zoonotic diseases.
2. **Agent Extractor (Extraction Engine):** Conducts deep reading of up to 25,000 characters. Extracts 9 types of clinical entities, enforces translation of all data into standardized Vietnamese, and strictly mandates quoting the original text as `evidence`.
3. **Agent Reviewer (Supervisor):** Re-evaluates the extracted entities, purging hallucinations or redundant content before final graph insertion.

---

## 📊 Detailed Data Statistics

Data collection currently focuses on ICD-10 codes **A00 through G00.1** (Covering **1,219** diseases with verified web data out of 15,844 total codes, approximately **7.69%**).

### 1. Node Distribution
The graph is categorized into 9 primary clinical entity types (Total: **32,163 Nodes**):

| Entity Type | Concept | Count | Percentage (%) |
| :--- | :--- | :--- | :--- |
| **RiskFactor** | Risk Factors | 4,974 | 15.46% |
| **Symptom** | Clinical Symptoms | 4,832 | 15.02% |
| **Intervention** | Medical Interventions | 4,618 | 14.36% |
| **Disease** | Disease (ICD-10) | 4,232 | 13.16% |
| **Complication** | Complications | 3,894 | 12.11% |
| **Demographic** | Demographics | 3,474 | 10.80% |
| **DiagnosticTest**| Tests / Diagnostics | 2,620 | 8.15% |
| **Pathogen** | Pathogens | 1,861 | 5.79% |
| **Drug** | Medications | 1,658 | 5.15% |

### 2. Graph Density Analysis
The total number of edges is **76,415**. For the 1,219 diseases with real-world data, the graph achieves high connectivity: **60.31 links / Disease**. On average, a single disease code is connected to:
`11.0 Symptoms` | `8.6 Complications` | `8.6 Risk Factors` | `8.5 Interventions` | `7.8 Demographics` | `6.1 Diagnostic Tests` | `4.9 Drugs` | `4.3 Pathogens`.

---

## 🔗 Relationship Structure & OMOP CDM Compatibility

The system defines 8 directed relationship types, mapped directly to the **OMOP Common Data Model (CDM v5.3.1)** tables:

| Source Node Type | Relation | Target Node Type | OMOP CDM Table Mapping |
| :--- | :--- | :--- | :--- |
| **Drug** | `TREATS` | **Disease** | `drug_exposure` |
| **Intervention** | `PART_OF_TREATMENT` | **Disease** | `procedure_occurrence` |
| **RiskFactor** | `INCREASES_RISK_OF` | **Disease** | `observation` |
| **Pathogen** | `CAUSES` | **Disease** | `specimen` / `observation` |
| **Demographic** | `AFFECTS_POPULATION` | **Disease** | `concept` |
| **Disease** | `HAS_SYMPTOM` | **Symptom** | `observation` |
| **Disease** | `DIAGNOSED_BY` | **DiagnosticTest** | `measurement` |
| **Disease** | `HAS_COMPLICATION` | **Complication** | `condition_occurrence` |

---

## 🕸️ Graph Visualization (Neo4j)

### 1. Macroscopic View
The panoramic view clearly demonstrates the complex interconnections between various disease families. Diseases do not exist in isolation; they share common entity sets (symptoms, drugs), creating knowledge clusters that support differential diagnosis.

![Overview of disease family connections on Neo4j Graph](image_d33bff.png)

### 2. Microscopic View
Deep-diving into a specific node, such as code **A00.0 (Cholera due to Vibrio cholerae 01, biovar cholerae)**, reveals a star-network structure:

![Detailed visualization - Cholera (A00.0)](visualisation_2.png)

From the central Disease node, the system retrieves symptoms (vomiting, diarrhea, dehydration), medications, and hierarchical `IS_SUBTYPE_OF` relationships pointing back to the parent disease (Cholera A00).

---

## 📂 Project Structure & Execution

* `run_crawl.py`: Core Script (Scientific Edition) controlling the data scraping flow, Ollama integration, and graph construction.
* `icd10_danh_muc.csv`: Contains the original ICD-10 master list.
* `analyze.py`: Analysis script for statistics, density metrics, and graph coverage (Gaps).
* `edges.zip`: Directory containing results (`edges.csv`, `nodes_*.csv`, and `raw_sources.jsonl` logs).
