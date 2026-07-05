# Excluded reference assets

To keep this repository lightweight, two large binary sample-asset libraries from the
upstream Arcads pack were **not** vendored here:

- `references/influencers/` — AI-generated character reference sheets (~106 MB)
- `references/products/` — product reference photos (~7 MB)

The lighter `references/aesthetics/` and `references/examples/` directories are kept as
illustrative references (image files themselves are gitignored by the pack; see
`.gitignore`).

To restore the full reference libraries, clone the upstream repo and copy them in:

```bash
git clone https://github.com/krusemediallc/arcads-claude-code.git
cp -r arcads-claude-code/references/influencers ./references/
cp -r arcads-claude-code/references/products   ./references/
```

These are sample/regenerable assets — the skills, prompting libraries, and scripts in
this pack are fully intact without them.
