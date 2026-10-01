# GACR Bridge Contract

GACR can operate without a provider-specific bridge. A bridge is optional and exists only to solve provider/client capabilities that GitHub cannot provide by itself, such as:

- supplying a ChatGPT/Claude conversation reference to GACR;
- supplying a stable client-instance identifier;
- receiving an external wake/takeover notification;
- opening or focusing the appropriate local conversation;
- launching an API-based standby worker.

## Client → GACR Beacon

A bridge may call the existing `gacr_beacon` / `gacr_register` repository-dispatch surface with safe correlation metadata:

```text
provider
provider_ref
provider_url (optional; not persisted by default)
client_instance_id
bridge_registration_ref
session_id (when already known)
repository/task/branch/PR context when available
wake_channels
```

The bridge must never transmit ChatGPT cookies, browser session cookies, API keys, GitHub tokens or page contents.

For a browser integration, the minimum useful information is:

```text
current conversation reference
client_instance_id
timestamp
```

GACR Correlator combines this with repository/session facts.

## GACR → External Bridge Wake

When a standby session registered `EXTERNAL_BRIDGE`, GACR Dispatcher creates a safe dispatch record.

If the repository configures:

- repository variable `GACR_BRIDGE_WEBHOOK_URL`;
- repository secret `GACR_BRIDGE_WEBHOOK_TOKEN`;

the GACR workflow can POST the wake contract to that endpoint.

The endpoint must treat `dispatch_id` as an idempotency key.

Receiving a wake event **does not grant write authority**. The worker must fetch its GACR agent context and complete exact-HEAD takeover reconciliation before mutation.

## What the bridge may automate

A provider bridge may:

- notify the user;
- focus/open an existing conversation;
- start an API/worker agent when the provider supports it;
- send a new GACR Beacon/heartbeat.

A bridge must not fabricate a conversation ID or bypass GACR claim/authority gates.

## Browser boundary

The repository cannot read a browser address bar remotely. A browser/client bridge can observe its own tab URL and explicitly submit the resulting provider reference to GACR.

This keeps the provider/client boundary explicit while allowing automatic correlation when a bridge is installed.
