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


## Governed repository entry response

The controlled entry layer also exposes:

`GET /repository-entry/{owner}/{repo}`

It preserves safe repository metadata returned by GitHub and adds the mandatory first navigation directive:

```json
{
  "schema": "governed-repository-entry-response/v1",
  "repository": {
    "full_name": "owner/repo",
    "default_branch": "main",
    "permissions": {}
  },
  "governance_entry": {
    "required": true,
    "priority": 0,
    "path": "00_GSCC_ENTRY.md",
    "instruction": "READ_BEFORE_ANY_OTHER_REPOSITORY_OPERATION",
    "blocks_normal_entry": true,
    "start_here_status": "NOT_YET_APPLICABLE"
  }
}
```

This endpoint is the repository-controlled response-enrichment boundary.

Important boundary: GitHub Apps and provider-native connectors that call GitHub directly do not pass through this endpoint automatically. Repository code cannot rewrite another application's native GitHub API response. Those clients must be configured to use this controlled entry surface if the directive must be guaranteed in their first response.
