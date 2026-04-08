---
name: axum-rust-template
description: "Scaffolds Rust web APIs with Axum framework, Diesel ORM models and migrations, and Domain-Driven Design project structure. Use when building a Rust REST API, backend server, or when the user mentions Axum, Diesel, DDD architecture, or Rust web development."
---

# Axum Rust API

Set up and develop a Rust API using Axum with Diesel ORM and Domain-Driven Design architecture.

## Setup

### 1. Clone the Template

```bash
git clone --depth 1 https://github.com/Eng0AI/axum-rust-template.git .
```

If the directory is not empty:

```bash
git clone --depth 1 https://github.com/Eng0AI/axum-rust-template.git _temp_template
mv _temp_template/* _temp_template/.* . 2>/dev/null || true
rm -rf _temp_template
```

### 2. Remove Git History (Optional)

```bash
rm -rf .git
git init
```

### 3. Configure Database

```bash
# Install Diesel CLI if not present
cargo install diesel_cli --no-default-features --features postgres

# Set database URL
echo 'DATABASE_URL=postgres://postgres:password@localhost/axum_app' > .env

# Create database and run migrations
diesel setup
diesel migration run
```

### 4. Build and Run

```bash
cargo build
cargo run
```

### 5. Verify Setup

```bash
# Server should respond (default port varies — check src/main.rs)
curl http://localhost:3000/health
```

## Project Structure (DDD Layers)

- `src/domain/` — Entities, value objects, domain logic
- `src/application/` — Use cases, service traits
- `src/infrastructure/` — Diesel models, repository implementations, database access
- `src/presentation/` — Axum route handlers, request/response types

## Development Workflow

**Add a new entity:**

1. Create a Diesel migration: `diesel migration generate create_<entity>`
2. Define the table in the `up.sql` migration file
3. Run the migration: `diesel migration run`
4. Add the domain model in `src/domain/`
5. Implement the Diesel model and repository in `src/infrastructure/`
6. Add route handlers in `src/presentation/`

**Run tests:**

```bash
cargo test
```
