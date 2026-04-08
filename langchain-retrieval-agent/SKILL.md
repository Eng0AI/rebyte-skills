---
name: langchain-retrieval-agent
description: "Builds a document Q&A application that indexes files into a Supabase pgvector store, performs semantic search, and answers questions with cited sources using LangChain.js and LangGraph. Use when the user wants to search documents, ask questions about files, build a RAG pipeline, set up retrieval-augmented generation, or create a knowledge base with vector embeddings."
---

# LangChain Retrieval Agent

Set up and develop an AI-powered document Q&A application using LangChain.js, LangGraph agents, and Supabase pgvector for retrieval-augmented generation (RAG).

## Setup

### 1. Clone the Template

```bash
git clone --depth 1 https://github.com/Eng0AI/langchain-retrieval-agent.git .
```

If the directory is not empty:

```bash
git clone --depth 1 https://github.com/Eng0AI/langchain-retrieval-agent.git _temp_template
mv _temp_template/* _temp_template/.* . 2>/dev/null || true
rm -rf _temp_template
```

### 2. Remove Git History (Optional)

```bash
rm -rf .git
git init
```

### 3. Install Dependencies

```bash
pnpm install
```

### 4. Configure Environment

```bash
cp .env.example .env
# Set these required variables:
# SUPABASE_URL=https://<project-ref>.supabase.co
# SUPABASE_PRIVATE_KEY=<service-role-key>
# OPENAI_API_KEY=<your-openai-key>
```

### 5. Enable pgvector in Supabase

In the Supabase dashboard SQL editor, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Start Development Server

```bash
pnpm dev
```

### 7. Verify Setup

Open `http://localhost:3000` — the chat interface should load. Try a test query to confirm the agent responds.

## Development Workflow

**Ingest documents into the vector store:**

1. Place documents in the designated ingestion directory
2. Run the ingestion script to chunk, embed, and store in pgvector
3. Verify embeddings exist: check the Supabase table via dashboard or `supabase` CLI

**Customize the retrieval agent:**

- Adjust chunking strategy and embedding model in the ingestion config
- Modify the LangGraph agent's tool definitions to add custom retrieval logic
- Tune the number of retrieved chunks (`k` parameter) for answer quality

**Build for production:**

```bash
pnpm build
pnpm start
```
