# EduExtract

**EduExtract** is an AI-powered scientific chemistry extraction platform that converts chemical structures from scientific images into machine-readable molecular representations and enriches them with structured chemical information.

The platform combines **MolScribe, OpenCV, RDKit, OPSIN, PubChem, FastAPI, and Docker** into a modular chemistry-processing pipeline.

---

## 🚀 Key Features

* 🧪 **Chemical Structure Recognition** — Extract chemical structures from images using MolScribe.
* 🔤 **SMILES Generation** — Convert recognized chemical structures into standardized SMILES representations.
* ✅ **SMILES Validation** — Validate and canonicalize molecular structures using RDKit.
* 🔎 **Chemical Metadata Retrieval** — Retrieve compound information from PubChem.
* 🧬 **Chemical Name Resolution** — Convert systematic chemical names into SMILES using OPSIN.
* 🖼️ **Chemical Structure Rendering** — Convert supported SMILES representations into ChemFig/LaTeX and render them as PDF/image output.
* ⚡ **FastAPI Backend** — Expose the chemistry pipeline through REST APIs.
* 🐳 **Docker Support** — Package the application and its dependencies into a reproducible containerized environment.

---

# 🏗️ Architecture

EduExtract contains two primary input pipelines that converge into a common molecular-processing layer.

```text
                    EduExtract
                        │
                     FastAPI
                        │
                Chemistry API
                        │
          ┌─────────────┴─────────────┐
          │                           │
   Chemical Structure             Chemical Name
        Image                          │
          │                            │
      OpenCV                        OPSIN
          │                            │
      MolScribe                        │
          │                            │
          └─────────────┬─────────────┘
                        │
                      SMILES
                        │
                      RDKit
                        │
             Validation & Canonicalization
                        │
                   PubChem API
                        │
              Chemical Metadata
                        │
                        └───────┐
                                │
                              ChemFig
                                │
                              LaTeX
                                │
                           PDF / Image
```

---

# 🔬 Pipeline 1 — Chemical Image → SMILES

The primary extraction workflow is:

```text
Chemical Structure Image
          ↓
Image Preprocessing
          ↓
MolScribe
          ↓
Predicted SMILES
          ↓
RDKit Validation
          ↓
Canonical SMILES
          ↓
PubChem Metadata
```

### Step 1 — Image preprocessing

OpenCV is used to load and preprocess the uploaded image before model inference.

Typical preprocessing includes:

* Image validation
* Color conversion
* Resizing when required
* Preparing the image for model inference

### Step 2 — MolScribe

MolScribe is a chemical structure recognition model that predicts molecular representations from chemical structure images.

Unlike conventional OCR, which primarily recognizes textual characters, MolScribe is designed specifically for chemical structure recognition.

### Step 3 — RDKit validation

The generated SMILES is not blindly trusted.

RDKit attempts to parse the predicted SMILES into a valid molecular structure.

```text
MolScribe
    ↓
SMILES
    ↓
RDKit
    ↓
Valid / Invalid
```

If valid, the SMILES can be canonicalized into a standardized representation.

### Step 4 — PubChem

After validation and canonicalization, the SMILES can be used to retrieve structured chemical metadata from PubChem.

Depending on availability, this may include:

* PubChem CID
* Compound name
* IUPAC name
* Molecular formula
* Molecular weight
* Canonical/isomeric SMILES

---

# 🔤 Pipeline 2 — Chemical Name → SMILES

EduExtract also supports chemical-name-based molecular conversion.

```text
Chemical Name
      ↓
OPSIN API
      ↓
SMILES
      ↓
RDKit
      ↓
Canonical SMILES
      ↓
PubChem Metadata
```

OPSIN is used to parse systematic chemical names and generate machine-readable molecular representations.

This complements the image-based MolScribe pipeline.

---

# 🧬 RDKit Processing Layer

RDKit acts as the common chemistry-processing layer for both pipelines.

```text
MolScribe ──┐
            ├──→ SMILES → RDKit → Canonical SMILES
OPSIN ──────┘
```

RDKit is responsible for:

* SMILES validation
* SMILES canonicalization
* Molecular structure parsing
* Basic molecular property calculations where required

Using RDKit before PubChem also prevents malformed model/API output from being sent directly to external services.

---

# 🔎 PubChem Integration

PubChem is used as an external chemical information source.

The workflow is:

```text
Canonical SMILES
       ↓
   PubChem API
       ↓
Compound Metadata
```

This avoids maintaining a manually hardcoded mapping of chemical names and properties.

External API failures such as timeouts, unavailable compounds, or malformed responses are handled separately from the local RDKit validation layer.

---

# 🖼️ Chemical Structure Rendering

The project also contains a rendering pipeline based on ChemFig and LaTeX.

```text
SMILES
  ↓
ChemFig
  ↓
LaTeX
  ↓
PDF
  ↓
PNG / Image
```

This functionality allows supported molecular structures to be converted from textual molecular representations into visual chemical structures.

The rendering pipeline is kept separate from the MolScribe and OPSIN services so that it can be reused with SMILES generated by either pipeline.

> **Note:** The ChemFig conversion currently supports the structures handled by the implemented conversion logic; it should not be considered a universal SMILES renderer.

---

# ⚙️ Backend Architecture

The backend follows a service-oriented structure.

```text
FastAPI Routes
      ↓
Chemistry Services
      ↓
┌───────────────────────────────┐
│ MolScribe                     │
│ OPSIN                         │
│ RDKit                         │
│ PubChem                       │
│ ChemFig / LaTeX Rendering     │
└───────────────────────────────┘
```

The API layer is responsible for handling HTTP requests and responses, while the individual services contain the chemistry and integration logic.

This separation makes individual components easier to test, replace, and maintain.

---

# 📁 Project Structure

```text
EduExtract/
│
├── backend/
│   ├── config/
│   ├── models/
│   ├── routers/
│   ├── services/
│   │   └── chemistry/
│   │       ├── molscribe_service.py
│   │       ├── opsin_service.py
│   │       ├── rdkit_service.py
│   │       ├── pubchem_service.py
│   │       └── rendering_service.py
│   ├── utils/
│   └── main.py
│
├── frontend/
│
├── tests/
│
├── Dockerfile.backend
├── docker-compose.yml
├── requirements.txt
├── ARCHITECTURE.md
├── .dockerignore
├── .gitignore
└── README.md
```

The exact internal structure may vary slightly depending on the deployed version of the project.

---

# 🔌 API Endpoints

The chemistry backend exposes versioned REST endpoints.

## Extract Chemical Structure

```http
POST /api/v1/chemistry/extract
```

### Input

A chemical structure image.

### Processing

```text
Image
 ↓
MolScribe
 ↓
SMILES
 ↓
RDKit
 ↓
PubChem
```

### Response

A structured response containing available information such as:

```json
{
  "extracted_smiles": "c1ccccc1",
  "canonical_smiles": "c1ccccc1",
  "valid": true,
  "compound": {
    "name": "benzene",
    "formula": "C6H6",
    "molecular_weight": 78.11,
    "cid": 241
  }
}
```

---

## Resolve Chemical Name

```http
POST /api/v1/chemistry/resolve-name
```

### Example Input

```json
{
  "name": "benzene"
}
```

### Processing

```text
Chemical Name
 ↓
OPSIN
 ↓
SMILES
 ↓
RDKit
 ↓
PubChem
```

---

## Render Chemical Structure

```http
POST /api/v1/chemistry/render
```

### Example Input

```json
{
  "smiles": "c1ccccc1"
}
```

### Processing

```text
SMILES
 ↓
RDKit Validation
 ↓
ChemFig
 ↓
LaTeX
 ↓
PDF / Image
```

---

# 🛠️ Tech Stack

| Technology          | Purpose                               |
| ------------------- | ------------------------------------- |
| **Python**          | Core backend and chemistry pipeline   |
| **FastAPI**         | REST API backend                      |
| **OpenCV**          | Image preprocessing                   |
| **MolScribe**       | Chemical structure recognition        |
| **PyTorch**         | ML model inference                    |
| **RDKit**           | SMILES validation and cheminformatics |
| **OPSIN**           | Chemical name → SMILES conversion     |
| **PubChem API**     | Chemical metadata retrieval           |
| **ChemFig / LaTeX** | Chemical structure rendering          |
| **Docker**          | Containerization and deployment       |
| **Uvicorn**         | ASGI server for FastAPI               |

---

# 🐳 Docker

EduExtract is containerized to provide a reproducible runtime environment for the backend and its scientific dependencies.

The project contains:

```text
Dockerfile.backend
docker-compose.yml
.dockerignore
```

## Build the Backend

```bash
docker build -f Dockerfile.backend -t eduextract-backend .
```

## Run the Container

```bash
docker run -p 8000:8000 eduextract-backend
```

The API will then be available at:

```text
http://localhost:8000
```

FastAPI's interactive API documentation can be accessed through:

```text
http://localhost:8000/docs
```

---

## Docker Architecture

```text
Dockerfile
     ↓
docker build
     ↓
Docker Image
     ↓
docker run
     ↓
Container
     ↓
Uvicorn
     ↓
FastAPI
     ↓
EduExtract Chemistry Pipeline
```

Docker packages the application together with its required Python and system-level dependencies, reducing environment-specific setup problems.

---

# 🧪 Local Development

## 1. Clone the repository

```bash
git clone <repository-url>
cd EduExtract
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Start the backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive documentation:

```text
http://localhost:8000/docs
```

---

# 🧪 Testing

Run the test suite using:

```bash
pytest
```

Tests cover the major components of the chemistry pipeline, including:

* Image processing
* MolScribe integration
* SMILES validation
* RDKit processing
* OPSIN integration
* PubChem response handling
* Rendering
* API endpoints

External APIs should be mocked in unit tests where appropriate so that the core test suite does not depend entirely on network availability.

---

# ⚠️ Error Handling

The pipeline handles failures at individual stages rather than allowing one failure to silently corrupt the complete workflow.

Examples include:

* Invalid image
* Unsupported image format
* MolScribe inference failure
* Invalid SMILES
* OPSIN API failure
* PubChem timeout
* Compound not found
* Rendering failure

For example:

```text
Image
 ↓
MolScribe
 ↓
Invalid SMILES
 ↓
RDKit rejects structure
 ↓
Pipeline stops with validation error
```

This prevents invalid molecular representations from being passed to downstream services.

---

# 🔐 Configuration

Environment-specific configuration should be provided through environment variables rather than hardcoded values.

Sensitive configuration such as credentials or secrets should never be committed to the repository.

Example:

```text
.env
```

should remain local and be excluded through `.gitignore`.

---

# 📌 Design Decisions

### Why MolScribe?

Because conventional OCR is designed primarily for text recognition, while MolScribe is specifically designed to recognize chemical structures and generate molecular representations.

### Why RDKit?

To provide deterministic local validation and canonicalization of model/API-generated SMILES before downstream processing.

### Why OPSIN?

To support chemical-name-based molecular conversion in addition to image-based extraction.

### Why PubChem?

To retrieve structured chemical metadata without maintaining a large custom chemical database.

### Why FastAPI?

It provides a lightweight Python API framework with request validation, automatic OpenAPI documentation, and easy integration with Python ML/scientific libraries.

### Why Docker?

The application combines several environment-sensitive scientific and ML dependencies. Docker provides a reproducible runtime environment and simplifies deployment.

---

# 🔮 Future Improvements

Potential improvements include:

* More robust chemical structure rendering
* Improved handling of complex stereochemistry
* Better image preprocessing for noisy scientific figures
* Batch chemical structure extraction
* Confidence scoring for model predictions
* Persistent storage for extracted compounds
* Caching external PubChem requests
* Additional chemical databases
* Improved frontend visualization

---

# 📄 License

This project is developed for educational, research, and portfolio purposes.

Add the appropriate license here if the repository is released under a specific open-source license.
