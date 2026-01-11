# Web App Builder

Build and deploy web apps to the cloud. Sites deploy to `*.rebyte.pro` with automatic SSL.

## Supported Frameworks

| Framework | Build Command | Output Dir |
|-----------|---------------|------------|
| React (Vite) | `npm run build` | `dist/` |
| Vue (Vite) | `npm run build` | `dist/` |
| Astro | `npm run build` | `dist/` |
| Next.js (static) | `npm run build` | `out/` |
| Svelte | `npm run build` | `build/` |
| Vanilla HTML | None | `.` |

## Quick Start

```bash
# 1. Build your app
npm install
npm run build

# 2. Add SPA routing (for React/Vue)
echo "/*    /index.html   200" > dist/_redirects

# 3. Get upload URL
RESPONSE=$(curl -s -X POST https://api.rebyte.ai/api/data/netlify/get-upload-url \
  -H "Content-Type: application/json" \
  -d '{"taskId": "my-app"}')
DEPLOY_ID=$(echo $RESPONSE | jq -r '.deployId')
UPLOAD_URL=$(echo $RESPONSE | jq -r '.uploadUrl')

# 4. Create and upload ZIP
cd dist && zip -r ../site.zip . && cd ..
curl -X PUT "$UPLOAD_URL" -H "Content-Type: application/zip" --data-binary @site.zip

# 5. Deploy
curl -X POST https://api.rebyte.ai/api/data/netlify/deploy \
  -H "Content-Type: application/json" \
  -d "{\"deployId\": \"$DEPLOY_ID\"}"
```

## Do's and Don'ts

**DO:**
- Build before deploying
- Include `index.html` at root
- Add `_redirects` for SPAs
- Use relative paths

**DON'T:**
- Deploy `node_modules/`
- Deploy source files
- Use SSR (static only)
- Skip the build step

See [SKILL.md](./SKILL.md) for full documentation.
