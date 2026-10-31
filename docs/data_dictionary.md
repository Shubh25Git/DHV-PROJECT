# NIRF Dataset Data Dictionary

## 1. Overview
The master dataset `data/processed/nirf_master.csv` contains historical NIRF ranking records from 2017 through 2025 across all ranked educational categories in India.

## 2. Field Specifications

| Column Name | Data Type | Description | Value Range / Examples |
|-------------|-----------|-------------|------------------------|
| `year` | Integer | The official ranking year released by the Ministry of Education (MoE). | 2017 to 2025 |
| `category` | String | The discipline or institutional category evaluated by NIRF. | `Overall`, `Engineering`, `Management`, `University`, `College`, `Pharmacy`, `Medical`, `Dental`, `Law`, `Architecture`, `Agriculture`, `Research`, `State Public University` |
| `institute_id` | String | Unique institutional identifier assigned by NIRF / AISHE / MoE. | `IR-O-U-0456`, `IR-E-C-1269`, etc. |
| `name` | String | Standardized official name of the university, college, or institute. | `Indian Institute of Technology Madras`, `Miranda House`, etc. |
| `city` | String | City or municipal location of the institution's main campus. | `Chennai`, `Bengaluru`, `New Delhi`, etc. |
| `state` | String | Standardized Indian State or Union Territory. | `Tamil Nadu`, `Karnataka`, `Maharashtra`, `Delhi`, etc. |
| `score` | Float | The composite weighted NIRF score on a 100-point scale. | 30.31 to 94.46 |
| `rank` | Float / Int | The official rank secured by the institution. Midpoints represent rank bands (e.g. 125.5 for band 101–150). | 1.0 to 300.0 |
| `raw_rank` | String | Original ranking string as reported on the NIRF website, preserving rank bands. | `'1'`, `'2'`, `'101-150'`, `'151-200'` |
| `tlr` | Float | **Teaching, Learning & Resources (TLR)** parameter score (100-point scale). Measures student strength, faculty-student ratio, faculty qualifications, and financial resources. | 0.00 to 100.00 |
| `rpc` | Float | **Research and Professional Practice (RPC)** parameter score (100-point scale). Measures publications, citations, patents, and research projects. | 0.00 to 100.00 |
| `go` | Float | **Graduation Outcomes (GO)** parameter score (100-point scale). Measures university examinations and campus placements / higher studies. | 0.00 to 100.00 |
| `oi` | Float | **Outreach and Inclusivity (OI)** parameter score (100-point scale). Measures regional diversity, women diversity, economically challenged students, and facilities for physically challenged students. | 0.00 to 100.00 |
| `perception` | Float | **Peer & Public Perception (PR)** score (100-point scale). Measures academic peers' and employers' perception. | 0.00 to 100.00 |
| `source_url` | String | Exact official URL from which this specific table record was collected. | `https://www.nirfindia.org/Rankings/2024/OverallRanking.html` |

---

## 3. Parameter Weightage Guidelines
In NIRF, the overall score is computed from the 5 parameters using category-specific weights established by the National Board of Accreditation (NBA):

$$\text{Overall Score} = w_{TLR} \times TLR + w_{RPC} \times RPC + w_{GO} \times GO + w_{OI} \times OI + w_{PR} \times PERCEPTION$$

Where typical weights are:
- TLR: ~0.30
- RPC: ~0.30
- GO: ~0.20
- OI: ~0.10
- PERCEPTION: ~0.10
