---
name: deno-monorepo-template
description: "Sets up API routes with Hono, defines tRPC procedures, manages database schemas with Drizzle ORM, and configures Supabase connections in a Deno monorepo. Use when building a backend API, adding database tables, creating tRPC endpoints, or working with Deno, Hono, Drizzle, or Supabase."
---

# Deno Monorepo

Set up and develop a full-stack backend using a Deno monorepo with Hono API framework, tRPC for type-safe RPC, Drizzle ORM, and Supabase.

## Setup

### 1. Clone the Template

```bash
git clone --depth 1 https://github.com/runreal/deno-monorepo-template.git .
```

If the directory is not empty:

```bash
git clone --depth 1 https://github.com/runreal/deno-monorepo-template.git _temp_template
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
deno install
```

### 4. Configure Environment

```bash
cp .env.example .env
# Set required Supabase credentials:
# SUPABASE_URL=https://<project-ref>.supabase.co
# SUPABASE_ANON_KEY=<your-anon-key>
# DATABASE_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
```

### 5. Start Development Server

```bash
deno task dev
```

### 6. Verify Setup

Confirm the server starts without errors and responds at the configured port (check `deno.json` tasks for the default).

## Monorepo Structure

- `packages/api/` — Hono HTTP routes and tRPC router
- `packages/db/` — Drizzle ORM schemas and migrations
- `packages/shared/` — Shared types and utilities

## Development Workflow

**Add a new API route:**

1. Define the tRPC procedure in `packages/api/`
2. Add the Drizzle schema in `packages/db/` if new tables are needed
3. Generate a migration: `deno task db:generate`
4. Apply the migration: `deno task db:push`

**Run tasks:**

```bash
deno task test      # Run tests
deno task lint      # Lint code
deno task db:studio # Open Drizzle Studio for DB browsing
```
