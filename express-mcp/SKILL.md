---
name: express-mcp
description: "Creates Model Context Protocol (MCP) server projects with Express.js and TypeScript, including tool definitions, resource handlers, and HTTP/SSE transport configuration. Use when the user asks to build an MCP server, create MCP tools, set up a Model Context Protocol endpoint, or develop an Express-based tool server for AI agents."
---

# Express MCP Server

Set up and develop an MCP (Model Context Protocol) server using Express.js and TypeScript. Exposes tools and resources that AI agents can discover and invoke.

## Setup

### 1. Clone the Template

```bash
git clone --depth 1 https://github.com/Eng0AI/express-mcp.git .
```

If the directory is not empty:

```bash
git clone --depth 1 https://github.com/Eng0AI/express-mcp.git _temp_template
mv _temp_template/* _temp_template/.* . 2>/dev/null || true
rm -rf _temp_template
```

### 2. Remove Git History (Optional)

```bash
rm -rf .git
git init
```

### 3. Install and Build

```bash
npm install
npm run build
```

### 4. Start Development Server

```bash
npm run dev
```

### 5. Verify Setup

```bash
# Server should respond on the configured port (check src/index.ts for default)
curl http://localhost:3000/health
```

## Development Workflow

**Add a new MCP tool:**

1. Create a tool handler file in `src/tools/`
2. Define the tool schema (name, description, input JSON Schema)
3. Implement the handler function that processes tool calls
4. Register the tool in the server's tool registry

**Add a new MCP resource:**

1. Create a resource handler in `src/resources/`
2. Define the resource URI pattern and description
3. Implement the read handler that returns resource content
4. Register the resource in the server's resource registry

**Build for production:**

```bash
npm run build
npm start
```
