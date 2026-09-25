# Handoff: 802.11 Study Guide

Notes for whoever edits this repo next, whether a person or an AI agent. Read this before you change anything.

## What this is

A self-study guide to IEEE 802.11 (Wi-Fi), aimed at certification-style exam prep (Network+, Security+ and CWNA-level). It has nine sections, numbered 0–8: standards, frequency bands, propagation, frames and CSMA/CA, association and the 4-way handshake, WPA2/WPA3 security, 802.11r fast roaming, a "numbers to memorize" table, and a 35-question self-test.

The reader is a student. Every section should answer "what will I be asked, and why is it true?" Explain the mechanism; don't just list facts.

## Repo layout

```
802.11-study-guide.md      ← THE GUIDE. All text edits happen here.
README.md                  ← Short landing page with a table of sections. Update it when sections change.
HANDOFF.md                 ← This file.
images/                    ← 17 SVG diagrams used by the guide. Generated; see below.
tools/export_svgs.py       ← Generates every file in images/.
source/80211-study-guide.html  ← Original HTML version of the guide. Now used only as the
                                 source for 9 of the diagrams.
```

### Which file is the source of truth

| Content | Edit here |
|---|---|
| All prose, tables, callouts, quiz | `802.11-study-guide.md` |
| `bands-spectrum`, `reflection`, `refraction`, `diffraction`, `scattering`, `absorption`, `four-way-handshake`, `eap-exchange`, `sae-exchange`, `ft-over-the-air` | The matching inline `<svg>` in `source/80211-study-guide.html`, then regenerate |
| `channels-2.4ghz`, `key-hierarchy`, `ft-key-hierarchy`, `frame-format`, `csma-ca`, `hidden-node`, `rts-cts` | Python drawing code in `tools/export_svgs.py`, then regenerate |
| Diagram colors, fonts, line styles (all diagrams) | `LIGHT` / `DARK` / `RULES` at the top of `tools/export_svgs.py` |

> [!IMPORTANT]
> Don't hand-edit files in `images/`. The next regeneration overwrites them. If you must make a quick fix directly in an SVG, make the same change in its source (the table above) in the same commit.

The HTML's prose is **not maintained** and will drift from the Markdown. Don't copy text from it. Its only remaining job is holding the diagram SVGs.

## Editing workflows

### Change text

Edit `802.11-study-guide.md`. Then check:
- **Section numbers:** the text and two diagrams refer to sections by number (e.g. "4-way handshake (section 4)" in `sae-exchange` and `eap-exchange`). If you insert or reorder a section, search for `section [0-9]` in the guide *and* in `source/` and `tools/`, then regenerate.
- **Anchors:** the Contents list and in-page links (`#5-fast-roaming-with-80211r`, `#how-a-client-chooses-wpa2-vs-wpa3`) use GitHub's heading slugs. If you rename a heading, update every link to it; search for `](#`.
- **Numbers repeated in several places:** keep them consistent. For example, the non-overlapping channel counts appear in the band sections, the width table, the numbers table and the quiz.

### Add a quiz question

Append a `<details>` block at the end of section 8, numbered next in sequence (currently Q35), and copy the existing format exactly:

```html
<details><summary><b>Q36.</b> Question text?</summary>

Answer text.
</details>
```

The blank line after `</summary>` matters: without it GitHub won't render Markdown inside the answer. Then update the question count in `README.md`.

### Add a new section

1. Add `## N. Title` in the right place and renumber later sections.
2. Update the Contents list at the top of the guide.
3. Update the section table in `README.md`.
4. Add a few quiz questions covering the new material.

### Change or add a diagram

```bash
python3 tools/export_svgs.py      # from the repo root; rewrites images/
git diff --stat images/           # confirm only the diagrams you meant to change moved
```

Needs only Python 3 (standard library). The script:
- pulls the inline `<svg>` elements out of `<main>` in the HTML **in document order** and maps them to filenames in the `names` list, asserting that the count matches. If you add, remove or reorder SVGs in the HTML, update `names`.
- draws the 2.4 GHz channel chart, both key hierarchies and the four section 3 diagrams (frame format, CSMA/CA timeline, hidden node, RTS/CTS) in Python. The channel chart is plotted to scale from real center frequencies; the timelines are schematic, not to scale.
- wraps each SVG with a shared `<style>` block that holds the light palette plus a `prefers-color-scheme: dark` override, a background card and the arrow/hatch `<defs>`.

To add a diagram, either draw a new `<svg>` inside `<main>` in the HTML (using the existing CSS classes: `ray`, `msg`, `note`, `actor`, `t-muted`, `t-mono`, `halo` for labels that cross a lifeline, `relay` for a relay dot, etc.) and add its name to `names`, or draw it in Python like the key hierarchies. Then reference it from the Markdown with a descriptive alt text: `![what it shows](images/name.svg)`.

**Checking a diagram locally on macOS:** `qlmanage -t -s 900 -o /tmp images/name.svg` renders a PNG preview. It uses the system theme, so check both light and dark if you changed colors.

**Diagram rules:**
- Every color comes from the tokens in `export_svgs.py`; no hard-coded hex values in the HTML SVGs. The exporter asserts there are no leftover `var(` references.
- Keep text labels short. Fonts fall back to the system font when GitHub renders them, so leave slack in tight labels (e.g. the frame labels in the sequence diagrams).
- Keep the three band colors consistent: 2.4 GHz = amber, 5 GHz = teal, 6 GHz = violet. The Markdown mirrors these with 🟧 🟦 🟪.

## Style conventions

- **Voice:** second person and plain. Expand every acronym the first time it appears in a section, e.g. "Protected Management Frames (PMF)".
- **Callouts:** GitHub alert syntax. `> [!TIP]` for exam tips, `> [!WARNING]` for "common trap", `> [!CAUTION]` for attacks. Start the text with a bold label.
- **Frame names** in inline code: `Probe Request`, `EAPOL-Key M1`.
- **Numbers:** units with a space (`20 MHz`, `−67 dBm`); use a real minus sign `−` for negative dBm values.
- **Region:** channel counts and power rules follow **US (FCC)** unless a line says otherwise. The footer says this. Mark any non-US fact explicitly.
- **Approximate values** (material attenuation, RSSI thresholds) are labelled as rough. Keep them labelled.

## Facts to re-verify periodically

These change with regulation or new certifications. Check them before relying on the guide for an exam:

| Topic | Where | Why it may drift |
|---|---|---|
| 6 GHz in Europe (lower 500 MHz only) | §1, 6 GHz | ETSI/CEPT may open the upper band |
| U-NII-4 (5.850–5.925 GHz) status | §1, 5 GHz and spectrum diagram | Device support and rules are still evolving |
| 5 GHz channel counts (25 / 12 / 6 / 2) | §1 width table, §7 | Exclude U-NII-4; would change if it's counted |
| Wi-Fi 7 security (SAE-EXT-KEY, GCMP-256) | §5 | Wi-Fi Alliance certification requirements get revised |
| Max PHY rates per amendment | §0 table | Theoretical figures; sources round differently |
| DFS timings (60 s check, 10 s move, 30 min avoid) | §1, §7, Q2 | FCC values; ETSI differs (e.g. longer checks on weather-radar channels) |

## Change history

Section numbers in this table are as they were at the time of each change.

| Change | Notes |
|---|---|
| Initial guide | Sections 0–4 and 6, quiz Q1–Q18. Built as an HTML page, then converted. |
| Added "How a client chooses WPA2 vs WPA3" | §4. Covers the RSNE/AKM selection, transition mode, the downgrade attack and Transition Disable. Q19–Q20. |
| Added §5 "Fast roaming with 802.11r" | Covers the FT key hierarchy, over the air vs. over the DS, and 802.11k/v. Q21–Q25. The old "Roaming shortcuts" list in §3 became a pointer to §5. |
| Converted to Markdown + SVG | Moved to this repo; diagrams exported to `images/`. |
| Added SAE Commit/Confirm diagram | §4, WPA3-Personal. `images/sae-exchange.svg`, drawn in the HTML source. Added the frame table, anti-clogging bullet and Q26. |
| Added 802.1X/EAP exchange diagram | §4, WPA2-Enterprise. `images/eap-exchange.svg` shows a PEAP login between client, AP and RADIUS, with notes on how EAP-TLS differs. Linked from §3 step 4. Added Q27–Q28. New `halo`, `relay` and `wired-zone` style classes, so every SVG's style block changed. |
| Added §3 "Frames and medium access (CSMA/CA)" | New section before Association: frame format and Frame Control bits, the three frame types, To DS/From DS addressing, CSMA/CA steps and timing, WMM/EDCA, hidden nodes and RTS/CTS, aggregation, airtime. Four Python-drawn diagrams (`frame-format`, `csma-ca`, `hidden-node`, `rts-cts`). Old §3–§7 renumbered to §4–§8, including the "(section 3)" labels in the SAE and EAP diagrams. Two rows in Numbers to memorize; Q29–Q35. |

## Ideas not yet done

- Section on Wi-Fi 6/7 features in more depth (OFDMA resource units, BSS coloring, MLO modes).
- Separate answer key or printable flashcards generated from the quiz.
