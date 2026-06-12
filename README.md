# PRIME-KG VN: Clinical Knowledge Graph (ICD-10 & OMOP CDM)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Data: Clinical](https://img.shields.io/badge/Data-Clinical_Medicine-red.svg)]()

## 📝 Introduction
PRIME-KG VN (Scientific Edition) is an advanced, automated framework designed to construct a large-scale clinical knowledge graph tailored for the Vietnamese healthcare ecosystem. By integrating the localized ICD-10 disease classification matrix with standard international clinical vocabularies, this platform establishes a **fully evidence-traceable, high-density relational network**. Crucially, to ensure absolute data provenance and strict verifiability, **every single data point, entity, and relationship inserted into the graph is strictly coupled with an immutable reference link (source URL) pointing directly to the original underlying content.**

Nine types of clinical entities are mapped into a unified semantic schema conceptually aligned with the target domains of the OMOP Common Data Model (OMOP CDM), establishing an interoperable cross-referencing system optimized for cross-database health analytics rather than direct physical database alteration.

Using the **ICD-10** coding system from the Vietnamese Ministry of Health as its backbone, this project creates a structured network linking diseases with tens of thousands of other medical entities (Symptoms, Drugs, Complications, etc.). Data is aggregated and automatically cleaned from official domestic and international sources, providing a foundational infrastructure for clinical decision support systems, semantic medical search engines, and observational health data networks with **zero-hallucination verification**.

---

## 💡 Technical Features & System Architecture

The system is built with fault-tolerant principles and rigorous data architecture:

- **Strict Data Provenance & Traceability Layer:** Every node and edge in the network contains explicit metadata linking back to its origin. The system guarantees that no relational link is formed without an accompanying `source_url` and a verbatim text snippet (`evidence`) serving as an unalterable proof of truth.
- **Hard-Anchoring Architecture:** Unlike random graph generation systems, this platform does **NOT** use LLMs to hallucinate relationship types. Edges are mathematically defined via `RELATION_RULES`, and internal `EXCLUDES`/`INCLUDES` links are extracted directly from the WHO guidance columns in the source ICD-10 file.
- **Knowledge Hub (Deduplication):** Merges identical Nodes (based on SHA-256 hash), automatically concatenating descriptions and compiling `evidence` streams from multiple independent source URLs into a single, comprehensive knowledge entry without bloating the graph layout.
- **igraph & Neo4j Compatibility:** Generates continuous `node_index` values, ensuring 100% accurate `x_id`/`y_id` mapping, ready for ingestion into any graph database.
- **Anti-Crash Mechanism:** Integrates cross-audit features to resume from checkpoints on failed disease extractions. Combines auto-save per cluster and a rotating SearXNG URL algorithm to bypass rate-limiting.

---

## 🌐 5-Tier Data Pipeline & Edge Source Percentages

Web scraping is optimized using `ThreadPoolExecutor` and divided into five tiers of authority. **Notably, the system automatically translates keywords into English** when querying international tiers. 

The overall graph contains **76,415 directed edges**, distributed with precise data lineage and direct link attribution across the following authority tiers:

1. **Tier 1 (VN Official):** `gov.vn`, `tapchiyhocduphong.vn`, `vjmed.org.vn`, `vjid.vn`, `yhth.vn`, etc.  
   *Data Contribution:* 36,269 edges (**47.46%** of the graph)
2. **Tier 2 (VN Major Hospitals & Pharmacies):** `vinmec.com`, `nhathuoclongchau.com.vn`, `medlatec.vn`, `pharmacity.vn`, `tamanhhospital.vn`, `hongngochospital.vn`, etc.  
   *Data Contribution:* 26,070 edges (**34.12%** of the graph)
3. **Tier 3 (International Academia - Auto-translated):** `ncbi.nlm.nih.gov`, `thelancet.com`, `jamanetwork.com`, `nejm.org`, `sciencedirect.com`, etc.  
   *Data Contribution:* 1,342 edges (**1.76%** of the graph)
4. **Tier 4 (Health Organizations - Auto-translated):** `who.int`, `cdc.gov`, `nih.gov`, `msdmanuals.com`, `mayoclinic.org`, `clevelandclinic.org`, `hopkinsmedicine.org`, `nhs.uk`, etc.  
   *Data Contribution:* 3,795 edges (**4.97%** of the graph)
5. **Tier 5 (Extended Sources):** Performs open-search queries if the top 4 tiers do not provide the required number of articles.  
   *Data Contribution:* 8,939 edges (**11.70%** of the graph)

---

## 🤖 Multi-Agent AI Pipeline

Instead of a single bloated prompt, the system utilizes Ollama (Qwen3-VL 8B) operating three independent agents with strict `format: json` enforcement to maintain data integrity:

1. **Agent Evaluator (Gatekeeper):** Analyzes the first 2,000 characters of the article. **Blocks** pure Veterinary documents (treating pigs, chickens, dogs, cats) with a 96% accuracy filter while remaining intelligent enough to **Allow** articles concerning Zoonotic diseases.
2. **Agent Extractor (Extraction Engine):** Conducts deep reading of up to 25,000 characters. Extracts 9 types of clinical entities, enforces translation of all data into standardized Vietnamese, and **strictly mandates quoting the exact verbatim sentence from the source document as `evidence` alongside its parent URL.**
3. **Agent Reviewer (Supervisor):** Re-evaluates the extracted entities, cross-checking the extracted data against the original reference link to purge hallucinations or redundant content before final graph insertion.

---

## 📊 Detailed Data Statistics & Scan Gaps

Data collection currently focuses on ICD-10 codes **A00 through G00.1**. Out of 2,872 codes within this targeted range, **1,219 diseases** have been successfully processed and verified with real web data, representing an effective range coverage of **42.44%** (approximately **7.69%** of the 15,844 total codes in the master catalog).

> ⚠️ **Dataset Scope & Evaluation Limitation:** Because data collection is currently in a partial scanning phase (restricted to the `A00`–`G00.1` subgroup), a full macro-structural comparison against the complete global baseline dataset or the entire 15,844-code catalog has been intentionally omitted in this release.

- **Identified Knowledge Gaps:** 1,653 codes within the scanned range are currently marked as sparse/missing due to technical constraints (such as aggregator resource overload, intermediate timeouts, structural web authentication, or a lack of qualified native-language clinical content). Specific data gaps include: `A37.0`, `A37.8`, `A49.1`, `A51.2`, `A59`, `A77.1`, `A95.0`, `B15`, `B15.0`, `B15.9`, `B18.2`, and the `B20.0` through `B20.8` series.

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
| **DiagnosticTest** | Tests / Diagnostics | 2,620 | 8.15% |
| **Pathogen** | Pathogens | 1,861 | 5.79% |
| **Drug** | Medications | 1,658 | 5.15% |

### 2. Graph Density Analysis
For the 1,219 diseases with real-world data, the graph achieves high connectivity: **60.31 links / Disease**. On average, a single disease code is connected to:  
`11.0 Symptoms` | `8.6 Complications` | `8.6 Risk Factors` | `8.5 Interventions` | `7.8 Demographics` | `6.1 Diagnostic Tests` | `4.9 Drugs` | `4.3 Pathogens`.

### 3. Semantic Mapping to OMOP CDM for Clinical Querying

The OMOP Common Data Model version 5.3.1 provides a standard for integrating healthcare data from multiple sources. Our knowledge graph serves as an intelligent semantic routing layer rather than a direct physical data storage unit.

**Table. Query Mapping of KG entities to OMOP CDM tables**

| Source Node Type | Relation | Target Node Type | Target OMOP Table (Query Mapping) |
| :--- | :--- | :--- | :--- |
| **Drug** | `TREATS` | **Disease** | `drug_exposure` |
| **Intervention** | `PART_OF_TREATMENT` | **Disease** | `procedure_occurrence` |
| **RiskFactor** | `INCREASES_RISK_OF` | **Disease** | `observation` |
| **Pathogen** | `CAUSES` | **Disease** | `specimen` / `observation` |
| **Demographic** | `AFFECTS_POPULATION` | **Disease** | `concept` |
| **Disease** | `HAS_SYMPTOM` | **Symptom** | `observation` |
| **Disease** | `DIAGNOSED_BY` | **DiagnosticTest** | `measurement` |
| **Disease** | `HAS_COMPLICATION` | **Complication** | `condition_occurrence` |

By defining this structural correspondence, the KG acts as an automated semantic router for downstream data pipelines, enabling seamless integration with electronic health records and OHDSI analytical tools (ATLAS, Achilles, Circe).

---

## 🚀 Full-Scale Projection & Scaling Strategy

Based on the empirical baseline established from the initial 2,872 scanned codes, we project the graph's scale, resource requirements, and knowledge gaps if the system is expanded to process the entire **15,844 ICD-10 catalog**.

### 1. Projected Graph Scale

| Metric | Current (Tested Range) | Full Projection (15,844 Codes) | Note |
| :--- | :--- | :--- | :--- |
| **Successful Diseases** | 1,219 codes | **15,844 codes** | Target 100% coverage of ICD-10 catalog |
| **Total Edges** | 76,415 edges | **~ 955,000 edges** | Linear growth based on ~60.31 links/disease |
| **Total Nodes** | 32,163 nodes | **~ 200,000 - 250,000 nodes** | Logarithmic growth due to SHA-256 deduplication |
| **Database Size** | ~ 15 MB | **~ 180 - 200 MB** | Edges and Nodes CSV structures only |
| **Evidence Logs** | ~ 120 MB | **~ 1.5 - 2 GB** | Raw JSONL text excerpts with source URLs |

### 2. Compute Load & Time Forecasting
- **Single-thread Processing:** ~33 days continuous running (15,844 codes × 3 mins/code)
- **Multi-threading (8 Workers):** ~4 to 5 days on a dedicated lab server
- **LLM Token Consumption:** ~158 million input tokens (using Qwen3-VL 8B)

### 3. The Path to 100% Coverage
To execute a complete scan successfully, the architecture requires:  
1) **Proxy Rotation Pool** – prevents IP bans  
2) **Vector Database Caching** (ChromaDB/Milvus) – avoids redundant parsing  
3) **Translation Agent Layer** – queries English literature for rare tropical diseases, then back-translates results to Vietnamese while preserving source traceability.

---

## 🕸️ Graph Visualization (Neo4j)

### 1. Macroscopic View
The panoramic view demonstrates complex interconnections between various disease families. Diseases share common entity sets (symptoms, drugs), creating knowledge clusters that support differential diagnosis.

![Overview of disease family connections on Neo4j Graph](image_d33bff.png)

### 2. Microscopic View
Deep-diving into a specific node, e.g., code **A00.0 (Cholera due to Vibrio cholerae 01, biovar cholerae)**, reveals a star-network structure:

![Detailed visualization - Cholera (A00.0)](visualisation_2.png)

From the central Disease node, the system retrieves symptoms (vomiting, diarrhea, dehydration), medications, and hierarchical `IS_SUBTYPE_OF` relationships.

---

## 🛠️ Clinical Mining & Lookup Applications

The practical utility of the graph has been validated across key clinical exploration scenarios.

## Part 1: Disease detection via symptoms of diarrhea, vomiting, cramps, dehydration

### Cypher query

```cypher
MATCH (disease:Entity)-[L:INKS_TO]->(s:Entity)
WHERE toLower(s.name) CONTAINS 'tiêu chảy'
    OR toLower(s.name) CONTAINS 'nôn'
    OR toLower(s.name) CONTAINS 'chuyết rút'
    OR toLower(s.name) CONTAINS 'mất nước'

// 2. Count how many symptoms match the user's input for each disease
WITH disease, count(DISTINCT s) AS So_Trieu_Chung_Khop

// 3. Count TOTAL number of symptoms that disease actually has in the database
MATCH (disease)-[L:INKS_TO]->(all_symptoms:Entity)
WITH disease, So_Trieu_Chung_Khop, count(all_symptoms) AS Tong_So_Trieu_Chung

// 4. Calculate score and rank
RETURN disease.code AS Ma_Benh,
    disease.name AS Ten_Benh,
    So_Trieu_Chung_Khop,
    Tong_So_Trieu_Chung,
    (toFloat(So_Trieu_Chung_Khop) / Tong_So_Trieu_Chung * 100) AS Diem_Uu_Tien

ORDER BY So_Trieu_Chung_Khop DESC, Diem_Uu_Tien DESC
LIMIT 100;
```
### Results

| disease_code | disease_name | matched_symptom_count | total_symptoms | priority_score |
| --- | --- | --- | --- | --- |
| A00.9 | Cholera, unspecified | 9 | 11 | 81.82 |
| A00.0 | Cholera due to Vibrio cholerae 01, biovar cholerae | 9 | 12 | 75.00 |
| A00 | Cholera | 8 | 10 | 80.00 |
| A05 | Other bacterial foodborne intoxication, not elsewhere classified | 8 | 14 | 57.14 |
| A00.1 | Cholera due to Vibrio cholerae 01, biovar eltor | 7 | 9 | 77.78 |
| A07.1 | Giardiasis [lambliasis] | 7 | 10 | 70.00 |
| A04.1 | Enterotoxigenic Escherichia coli infection (ETEC) | 7 | 14 | 50.00 |
| A04.3 | Enterotoxigenic Escherichia coli infection (ETEC) | 7 | 15 | 46.67 |

### Insights

- Cholera codes (A00.x) dominate the ranking due to the complete overlap of all four symptoms: diarrhea, vomiting, cramps, and dehydration.
- Food poisoning (A05) and giardiasis (A07.1) also appear with high match counts, reflecting their clinical presentation.
- The priority score helps distinguish diseases with the same raw symptom count; for example, A00.9 (81.82%) ranks higher than A00.0 (75.00%) even though both match 9 symptoms.

## 📂 Project Structure & Execution

- `run_crawl.py`: Core Script (Scientific Edition) controlling data scraping, Ollama integration, and graph construction.
- `icd10_danh_muc.csv`: Original ICD-10 master list.
- `analyze.py`: Analysis script for statistics, density metrics, and coverage gaps.
- `edges.zip`: Directory containing results (`edges.csv`, `nodes_*.csv`, and `raw_sources.jsonl` logs).

---

© 2025 PRIME-KG VN – Fully evidence‑anchored clinical knowledge graph for the Vietnamese healthcare system.
