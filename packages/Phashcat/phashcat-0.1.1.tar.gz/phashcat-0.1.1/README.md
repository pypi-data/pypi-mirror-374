
# Phashcat

**Phashcat** is a tiny, immutable, monoid-style, fluent builder around the
[`hashcat`](https://hashcat.net/hashcat/) CLI. It lets you compose robust
commands in Python without remembering every flag, while keeping everything
type-checked and chainable.

- **Install**: `pip install Phashcat`
- **Repo**: https://github.com/avitwil/Phashcat
- **Author**: Avi Twil

> **Import once, from one place**
>
> ```python
> from Phashcat import hashcat, flags
> ```

---

## Who is it for?

- **Security engineers / pentesters** who automate cracking workflows, want
  clean scripts, repeatability, and fewer copy–paste mistakes.
- **DevOps / SRE** building pipelines that run `hashcat` on CI/CD, with
  predictable argument construction and clear diffs.
- **Researchers / educators** who demonstrate attack modes and need readable,
  reproducible code snippets for classes, workshops, or papers.
- **Anyone** who dislikes hand-crafting long shell strings and prefers a
  Pythonic, immutable, and composable API.

---

## When should you use Phashcat?

Use Phashcat when you:

- Want to **assemble `hashcat` commands programmatically** with validation.
- Need **immutable, composable configs** (e.g., presets you can merge).
- Prefer **Python lists** for `subprocess.run()` over a single shell string.
- Need a **single point of import** (`from Phashcat import ...`) for clarity
  and maintainability across your project.

You probably **don’t** need Phashcat if you:
- Run `hashcat` only once by hand, or
- Prefer writing plain shell scripts without Python.

---

## Key Features

- **Monoid-style builder**: `.empty()`, `.mappend(other)` for composition.
- **Immutability**: every call returns a new builder — easier to reason about.
- **Fluent API**: `.hash_type(0).attack_mode(3).outfile("...").status(True)`.
- **Light validation**: sanity checks via `flags.VALUE_KIND`.
- **Single import surface**: `from Phashcat import hashcat, flags`.

---

## Quick Start

```python
from Phashcat import hashcat

cmd = (
    hashcat("example0.hash", "?d?d?d?d?d?d")
    .hash_type(0)      # -m 0 (MD5)
    .attack_mode(3)    # -a 3 (brute-force / mask)
    .outfile("cracked.txt")
    .status(True).status_timer(2)
    .workload_profile(3)
    .value()
)

# import subprocess; subprocess.run(cmd, check=True)
````

---

## Common Use Cases

### 1) Straight wordlist (`-a 0`)

```python
from Phashcat import hashcat

cmd = (
    hashcat("example0.hash", "example.dict")
    .hash_type(0)
    .attack_mode(0)
    .outfile("out.txt")
    .status(True)
    .value()
)
```

### 2) Wordlist + rules

```python
cmd = (
    hashcat("example0.hash", "example.dict")
    .hash_type(0).attack_mode(0)
    .rules_file("rules/best64.rule")
    .outfile("out_rules.txt")
    .value()
)
```

### 3) Brute-force mask (`-a 3`) with increment

```python
cmd = (
    hashcat("example0.hash", "?1?1?1?1?1?1")
    .hash_type(0).attack_mode(3)
    .cs1("?l?d")                 # define ?1
    .increment(True).increment_min(4).increment_max(6)
    .outfile("out_inc.txt")
    .value()
)
```

### 4) Hybrid wordlist + mask (`-a 6`)

```python
cmd = (
    hashcat("example0.hash", "example.dict", "?d?d")
    .hash_type(0).attack_mode(6)
    .outfile("out_hybrid6.txt")
    .value()
)
```

### 5) Show / Left (potfile reconciliation)

```python
show_cmd = hashcat("hashes.txt").show(True).value()   # --show
left_cmd = hashcat("hashes.txt").left(True).value()   # --left
```

---

## Presets & Composition (Monoid)

Create reusable presets and merge with `.mappend(...)`:

```python
preset_md5   = hashcat().hash_type(0)
preset_mask  = hashcat().attack_mode(3).workload_profile(3)

cmd = (
    preset_md5
    .mappend(preset_mask)
    .outfile("out.txt")
    .arg("example0.hash", "?a?a?a?a?a?a")
    .status(True)
    .value()
)
```

---

## Reference Tables (via `flags`)

```python
from Phashcat import flags

print(flags.ATTACK_MODES)        # {0: 'Straight', 1: 'Combination', ...}
print(flags.WORKLOAD_PROFILES)   # {1: {...}, 2: {...}, ...}
print(flags.OUTFILE_FORMATS)     # {1: 'hash[:salt]', ...}
```

---

## Ethics & Legality

Use `hashcat` **only** on hashes you are authorized to test. Comply with
local laws, organizational policies, and responsible disclosure guidelines.

---

## Contributing

PRs welcome! Please:

1. Keep imports top-level (`from Phashcat import ...`).
2. Add tests or runnable examples where possible.
3. Update `MANUAL.md` for public API changes.

---

## License

MIT — see `LICENSE`.

**Author: Avi Twil**

