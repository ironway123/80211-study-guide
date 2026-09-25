# Handoff: 802.11 Study Guide

Notes for whoever edits this repo next, whether a person or an AI agent. Read this before you change anything.

## What this is

A self-study guide to IEEE 802.11 (Wi-Fi), aimed at certification-style exam prep (Network+, Security+ and CWNA-level). It has seven sections: standards, frequency bands, propagation, association and the 4-way handshake, WPA2/WPA3 security, 802.11r fast roaming, a "numbers to memorize" table, and a 25-question self-test.

The reader is a student. Every section should answer "what will I be asked, and why is it true?" Explain the mechanism; don't just list facts.

## Repo layout

```
802.11-study-guide.md      ← THE GUIDE. All text edits happen here.
README.md                  ← Short landing page with a table of sections. Update it when sections change.
HANDOFF.md                 ← This file.
images/                    ← 11 SVG diagrams used by the guide. Generated; see below.
tools/export_svgs.py       ← Generates every file in images/.
source/80211-study-guide.html  ← Original HTML version of the guide. Now used only as the
                                 source for 9 of the diagrams.
```

### Which file is the source of truth

| Content | Edit here |
|---|---|
| All prose, tables, callouts, quiz | `802.11-study-guide.md` |
| `bands-spectrum`, `reflection`, `refraction`, `diffraction`, `scattering`, `absorption`, `four-way-handshake`, `ft-over-the-air` | The matching inline `<svg>` in `source/80211-study-guide.html`, then regenerate |
| `channels-2.4ghz`, `key-hierarchy`, `ft-key-hierarchy` | Python drawing code in `tools/export_svgs.py`, then regenerate |
| Diagram colors, fonts, line styles (all diagrams) | `LIGHT` / `DARK` / `RULES` at the top of `tools/export_svgs.py` |

> [!IMPORTANT]
> Don't hand-edit files in `images/`. The next regeneration overwrites them. If you must make a quick fix directly in an SVG, make the same change in its source (the table above) in the same commit.

The HTML's prose is **not maintained** and will drift from the Markdown. Don't copy text from it. Its only remaining job is holding the diagram SVGs.

## Editing workflows

### Change text

Edit `802.11-study-guide.md`. Then check:
- **Anchors:** the Contents list and in-page links (`#5-fast-roaming-with-80211r`, `#how-a-client-chooses-wpa2-vs-wpa3`) use GitHub's heading slugs. If you rename a heading, update every link to it; search for `](#`.
- **Numbers repeated in several places:** keep them consistent. For example, the non-overlapping channel counts appear in the band sections, the width table, the numbers table and the quiz.

### Add a quiz question

Append a `<details>` block at the end of section 7, numbered next in sequence (currently Q25), and copy the existing format exactly:

```html
<details><summary><b>Q26.</b> Question text?</summary>

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
- draws the 2.4 GHz channel chart and both key hierarchies in Python (the channel chart is plotted to scale from real center frequencies).
- wraps each SVG with a shared `<style>` block that holds the light palette plus a `prefers-color-scheme: dark` override, a background card and the arrow/hatch `<defs>`.

To add a diagram, either draw a new `<svg>` inside `<main>` in the HTML (using the existing CSS classes: `ray`, `msg`, `note`, `actor`, `t-muted`, `t-mono`, etc.) and add its name to `names`, or draw it in Python like the key hierarchies. Then reference it from the Markdown with a descriptive alt text: `![what it shows](images/name.svg)`.

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
| 5 GHz channel counts (25 / 12 / 6 / 2) | §1 width table, §6 | Exclude U-NII-4; would change if it's counted |
| Wi-Fi 7 security (SAE-EXT-KEY, GCMP-256) | §4 | Wi-Fi Alliance certification requirements get revised |
| Max PHY rates per amendment | §0 table | Theoretical figures; sources round differently |
| DFS timings (60 s check, 10 s move, 30 min avoid) | §1, §6, Q2 | FCC values; ETSI differs (e.g. longer checks on weather-radar channels) |

## Change history

| Change | Notes |
|---|---|
| Initial guide | Sections 0–4 and 6, quiz Q1–Q18. Built as an HTML page, then converted. |
| Added "How a client chooses WPA2 vs WPA3" | §4. Covers the RSNE/AKM selection, transition mode, the downgrade attack and Transition Disable. Q19–Q20. |
| Added §5 "Fast roaming with 802.11r" | Covers the FT key hierarchy, over the air vs. over the DS, and 802.11k/v. Q21–Q25. The old "Roaming shortcuts" list in §3 became a pointer to §5. |
| Converted to Markdown + SVG | Moved to this repo; diagrams exported to `images/`. |

## Ideas not yet done

- Diagram of the WPA3 SAE Commit/Confirm exchange (the guide describes it but doesn't draw it).
- Diagram of the 802.1X/EAP exchange (supplicant ↔ AP ↔ RADIUS), e.g. EAP-TLS or PEAP.
- Section on 802.11 frame types (management / control / data) and CSMA/CA, RTS/CTS, hidden node.
- Section on Wi-Fi 6/7 features in more depth (OFDMA resource units, BSS coloring, MLO modes).
- Separate answer key or printable flashcards generated from the quiz.
