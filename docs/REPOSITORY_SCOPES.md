# REPOSITORY SCOPES

The governed template is owner-agnostic.

Supported target scopes are:

1. organization repositories such as `chainsolutions-wealthtech/*`;
2. repositories on the explicitly targeted personal owner account;
3. another owner only when explicitly authorized.

The same zero-touch governance model applies in every supported scope. The target owner is resolved from the requested repository/context rather than hard-coded to the organization.

Owner scope describes location, not permission.


## Configured creation targets

The central control plane currently exposes these creation choices:

- `chainsolutions-wealthtech` → organization, creator principal `Wealthtechinnovations`;
- `Wealthtechinnovations` → personal account, creator principal `Wealthtechinnovations`;
- `Patricked` → display label for personal account `Patricked-code`, creator principal `Patricked-code`.

The display label and canonical GitHub owner are intentionally distinct for Patricked. The executor always calls GitHub with the canonical owner.

Repository visibility is never inferred: the control plane asks `private` or `public` after the repository name.
