# PROJECT MAPPING

This mode is for an existing project that must be understood before modification.

It separates:

```text
CURRENT_ARCHITECTURE = observed facts
TARGET_ARCHITECTURE = explicit desired design
GAP_MAP = differences and migration constraints
```

The mapping surface includes repository topology, runtimes, frontend/backend boundaries, APIs, databases and migrations, external adapters, scheduled work, authentication, containers, CI/CD, observable deployment bindings, tests, ADRs and existing governance.

Mapping is read-only by default. A target architecture may be proposed, but it is never represented as already implemented.
