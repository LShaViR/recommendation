# Culture circle assignment

A high-performance styling engine that generates complete, personalized outfits in sub-second time. This system uses a **Hybrid Heuristic-Vector approach** to simulate the decision-making process of a professional fashion stylist.
<img width="3890" height="1947" alt="diagram-export-22-01-2026-21_17_08" src="https://github.com/user-attachments/assets/2ffe498e-136f-4aa0-b9f0-86e78177cca3" />



## 🏗️ Technical Stack

- **Frontend:** Next.js, Tailwind CSS, shadcn/ui.
- **API Server:** FastAPI (Asynchronous Python).
- **Background Worker:** Arq (Redis-based) running the same codebase for model inference.
- **Database:** PostgreSQL with **pgvector** extension for vector similarity.
- **Infrastructure:** Vultr (VM Instances, Managed DB, and S3-compatible Object Storage).
- **AI Models:**
- **Vision:** `clip-ViT-B-32` (Embeddings, Occasions, Archetypes, Formality).
- **Text:** `all-MiniLM-L6-v2` (Semantic product search).

- **Image Processing:** PIL (Pillow).

---

## 🧠 Recommendation Logic

The system splits the "intelligence" into two distinct phases to ensure a fast user experience.

### Phase 1: Product Ingestion & Matching (Offline)

When a seller creates a product, the background worker performs the "heavy lifting":

1. **AI Tagging:** Uses CLIP to extract **Occasion tags** (e.g., Wedding, Office), **Archetypes** (e.g., Streetwear, Minimalist), and a **Formality Score** (0 for Casual to 1 for Formal).
2. **Embeddings:** Generates visual and textual embeddings. _Current Trade-off: Style embeddings are currently used as complementary embeddings; specialized co-occurrence logic is in the roadmap._
3. **Graph Construction:** \* Finds 1,000 potential candidates across different categories (ensuring no same-category matches like Shirt + Shirt).

- Calculates a **Stylist Score** using: `Season Score` + `Occasion Score` + `Visual Style Score` + `Fit Compatibility`.
- Saves the top 40 compatible pairs into the `ProductCompatibility` table.

### Phase 2: Personalized Recommendation (Online)

When a user views a product, the API response is near-instant because it only ranks pre-filtered candidates:

1. **Retrieval:** Fetches the pre-computed 40 candidates for the base product.
2. **Personalized Scoring:** \* **Price Score:** Matches the product price against the **User's Spending Profile**.

- **Style Score:** Compares the **User's Style DNA** with the product's embedding using cosine similarity.

3. **Outfit Assembly:** Groups products into 5 distinct "Full Look" outfits (Top + Bottom + Shoe + Accessory).

---

## ⚡ Optimization & Performance

The system is designed for **sub-300ms** industry standards:

- **Precomputation:** By calculating compatibility at the ingestion phase, we avoid heavy math during the user request.
- **Latency:** Average request time is **40-60ms** (tested on local machine over 50 calls) for 600+ products.
- **Frontend:** Implements image lazy-loading, pagination, and client-side caching to reduce redundant network traffic.

---

## 🛠️ Installation & Setup

### Prerequisites

- Docker & Docker Compose.
- Cloud Storage credentials (Vultr/S3) for image handling.

### Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/outfit-ai.git
cd outfit-ai

```

2. **Configure Environment:**
   Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
VULTR_REGION=...
VULTR_ACCESS_KEY=...
VULTR_SECRET_KEY=...

```

3. **Launch with Docker:**

```bash
docker compose -f docker-compose-development.yml --env-file .env up --build

```

4. **Install pnpm package in fe:**

```bash
cd fe
pnpm install
pnpm run dev

```

---

## ⚖️ Trade-offs & Assumptions

- **Storage vs. Speed:** I chose to precompute and store compatibility data. This requires more database storage but is the reason the system can serve outfits in under 100ms.
- **Style vs. Complementary Embeddings:** Currently, the system uses the same CLIP vector for both style and matching. While effective, a dedicated "Complementary Model" would further improve fashion accuracy.
- **Cost Optimization:** No external LLM APIs (like GPT-4o) were used. All AI logic runs on local open-source models to minimize operational costs.
