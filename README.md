# terminus-31

EIP-8037 differential fuzzer for Ethereum execution-layer devnets.

Pins EELS, revm, Nethermind, and Nimbus to a devnet branch and runs
goevmlab's `generic-fuzzer` across them with our EIP-8037 engines.

## Install

```bash
git clone https://github.com/spencer-tb/terminus-31
cd terminus-31
uv sync
```

## Usage

```bash
# Clone the manifest's repos + tools into ./tools/
terminus-31 init --devnet bal-devnet-7

# Probe PATH for required binaries; print install hints if missing
terminus-31 check --devnet bal-devnet-7

# Run the differential fuzz (4 engines, 4 parallel workers)
terminus-31 fuzz-8037 --devnet bal-devnet-7 --parallel 4
```

`--hours N` to cap a run, `--engine NAME` (repeatable) to override the
default engine set.

## Manifests

`manifests/<feat>-devnet-<N>.toml` pins every spec / client / tool to
a specific branch and lists install hints. Bump the file when a new
devnet drops.

## License

MIT.
