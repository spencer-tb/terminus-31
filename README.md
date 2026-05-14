# terminus-31

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/github/license/spencer-tb/terminus-31)](LICENSE)

<p align="center">
  <em>The agent-first EL testing space station.</em>
  <br/>
  <em>Pin the spec, pin every client, fuzz the difference.</em>
</p>

`terminus-31` is a workspace that bundles the Ethereum execution-layer spec (EELS) with every major client implementation, all pinned to the same devnet branch, and drives [goevmlab](https://github.com/holiman/goevmlab)'s differential fuzzer at them. Designed first for agents: structured output, one-command install, every flag printable.

The `-31` is leetspeak for `EL` (`E`→`3`, `L`→`1`).

## Install

```bash
uv tool install git+https://github.com/spencer-tb/terminus-31
```

That's it. Now just:

```bash
t31 fuzz-8037 --devnet bal-devnet-7
```

Other install methods:

```bash
# Local development clone
git clone https://github.com/spencer-tb/terminus-31
cd terminus-31
uv sync
uv run t31 --help

# As a uv tool, pinned to a specific commit
uv tool install git+https://github.com/spencer-tb/terminus-31@<sha>
```

## Commands

| Command | What it does |
|---|---|
| `t31 init --devnet <name>` | Clones the manifest's repos and tools into `./tools/` |
| `t31 check --devnet <name>` | Probes `$PATH` for every manifest binary; prints install hints when one is missing |
| `t31 fuzz-8037 --devnet <name>` | Runs goevmlab's `generic-fuzzer` across every available client with the four EIP-8037 engines |
| `t31 help` | Dumps every subcommand's flags in one go |

Common `fuzz-8037` flags: `--hours N` to cap a run, `--parallel N` to set worker count (default 4), `--engine NAME` (repeatable) to narrow the engine set.

## What's pinned to a devnet

Per `manifests/<feat>-devnet-<N>.toml` (e.g. `bal-devnet-7.toml`):

| | Ref | Role |
|---|---|---|
| **EELS** | `devnets/bal/7` | Executable spec; statetest oracle |
| **revm** | `bal-devnet-7` | Rust EVM; `revme` statetest |
| **Nethermind** | `bal-devnet-7` | C# client; `nethtest` statetest |
| **Nimbus** | `bal-devnet-7` | Nim client; `evmstate` statetest |
| **goevmlab** | `spencer-tb/goevmlab/bal-devnet-7` | Fork with four EIP-8037 fuzz engines |

Drop a new manifest file when the next devnet lands and the same commands work against it.

## EIP-8037 engines

`spencer-tb/goevmlab/bal-devnet-7` ships four engines:

| Engine | Targets |
|---|---|
| `eip8037` | Broad state-gas surface; randomised auth lists, reservoir-boundary tx.gas |
| `eip8037_sstore_restoration` | Engineered SSTORE 0→x→0 cycles |
| `eip8037_deep_calls` | Depth 5–50 CALL chains with leaf SSTORE |
| `eip8037_create_sd_same_tx` | CREATE+SELFDESTRUCT in same tx (EIP-6780 × EIP-8037) |

## Why "31"

`E` → `3`, `L` → `1`. EL → 31.

## License

MIT.
