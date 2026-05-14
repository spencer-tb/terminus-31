# CLAUDE.md

terminus-31 runs the goevmlab differential fuzzer over Ethereum
execution-layer clients pinned to a devnet branch.

## Commands

- `terminus-31 init --devnet <name>` — clone manifest repos+tools to `tools/`
- `terminus-31 check --devnet <name>` — verify each manifest binary is on PATH
- `terminus-31 fuzz-8037 --devnet <name>` — run goevmlab generic-fuzzer with the EIP-8037 engines

## Conventions

- Manifests live at `manifests/<feat>-devnet-<N>.toml`. They pin every
  spec / client / tool to a specific branch (`devnets/bal/7` for EELS,
  `bal-devnet-7` for clients).
- `tools/` is populated by `init` and gitignored. Each subdir is its
  own git repo at the manifest's ref.
- `out/` holds fuzz campaign output; gitignored.
- Binaries are expected on `$PATH`. `check` prints install hints when
  one is missing.
