# GSCC GitHub Plugin MCP Proxy

Controlled MCP surface for ChatGPT.

Flow:

```
ChatGPT plugin
  -> /mcp
  -> inspect first tools/call
  -> gscc_provider_first_touch repository_dispatch
  -> GitHub official MCP upstream
  -> tool result
```

The proxy never commits a GitHub token. Configure `GITHUB_PERSONAL_ACCESS_TOKEN` only in the deployment environment.

## Run

```bash
docker build -t gscc-github-plugin .
docker run --rm -p 8080:8080 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  -e GSCC_REPOSITORY=chainsolutions-wealthtech/Governed-Repository-Template \
  gscc-github-plugin
```

Health: `GET /health`.
MCP endpoint: `/mcp/`.

The proxy forwards the upstream GitHub MCP tool catalogue unchanged. The first observed `tools/call` for an observed MCP session emits the canonical `gscc_provider_first_touch` event before the GitHub operation is forwarded.

If the client exposes no MCP session identifier, identity remains `UNRESOLVED`; no provider-private identifier is fabricated.
