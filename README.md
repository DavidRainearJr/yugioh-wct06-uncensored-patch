# Yu-Gi-Oh! Ultimate Masters: World Championship Tournament 2006

### Uncensored Card Art + Huge Revolution Fix

A BPS patch for the USA release of **Yu-Gi-Oh! Ultimate Masters: World Championship Tournament 2006**
(Game Boy Advance) that does two things:

1. Uses the **uncensored Japanese card artwork** in every region and language mode.
2. **Fixes the Huge Revolution challenge** logic, which was referencing the wrong internal card ID.

The patch modifies **236 bytes** out of a 32 MiB game. Nothing is added, removed, recompressed, or
relocated — the uncensored artwork is already inside your ROM, the game is simply selecting the
censored versions of it.

> Unofficial fan patch. No ROM image is included or linked. You must supply your own legally
> obtained backup of the exact USA release.

---

## Contents

| File | Size | What it is |
| --- | --- | --- |
| `Yu-Gi-Oh-Ultimate-Masters-2006-Uncensored-v1.0.bps` | 853 bytes | The patch. Apply this with [Floating IPS](https://www.smwcentral.net/?p=viewthread&t=88029). |
| `patch_rom.py` | 3.7 KiB | Optional standalone Python patcher that performs the same changes directly. |

Patch SHA-256: `B862A6664F27775FA5D94FC78FCD4DE07DA359D3AECB928E011A3A3F19D43AC7`

---

## Changes

### 1. Uncensored artwork

Every card-art index in the shared selection table holds a **pair** of entries: the Japanese
uncensored artwork and the international censored artwork. The game picks between them at runtime
based on the ROM's region byte and the selected language.

Of 2,098 pairs, 1,865 already pointed at the same asset in both modes. The remaining **233** pointed
at different artwork. This patch repoints those 233 international entries at the Japanese variants
already stored in the game, so the uncensored art is used no matter which of the game's six
languages is selected.

Because the patch changes the shared index table rather than individual rendering functions, the
restored artwork applies consistently everywhere: full card images, palettes, and both the small and
large card icons.

Examples of what changes:

| Card | Difference |
| --- | --- |
| **Water Omotics** | International artwork adds clothing that is absent from the original Japanese illustration. |
| **Harpie Lady** | The original clothing and body details from the Japanese artwork are restored. |
| **Forbidden One pieces** | Different limbs, same censorship edit — the international Spellbinding Circle background is replaced with the original pentagram. |
| **Elemental Hero Burstinatrix** | The international clothing edit is replaced with the original Japanese illustration. |

Full side-by-side screenshots are available on the project page:
**<https://rainear.net/Yu-Gi-Oh-Ultimate-Masters-2006>**

### 2. Huge Revolution fix

The challenge routine for Huge Revolution generated the wrong internal card ID, so the game failed
to recognise its own card. The correct Konami ID for Huge Revolution is `0x15EF` (`5615` decimal).

```text
Original:  subs r0, #0x4D     0x16DC - 0x62 - 0x4D = 0x162D   (wrong)
Patched:   subs r0, #0x8B     0x16DC - 0x62 - 0x8B = 0x15EF   (correct)
```

The bug and the fix both come from Scrub Busta's 2022 video
[Fixing Konami's BIGGEST Mistake](https://www.youtube.com/watch?v=rKUE2M25_dA), where he works
out the card ID correction using a ROM dump. This patch applies it to the USA release.

Only the immediate byte at file offset `0x00020FC2` is changed.

---

## What it does *not* change

- Card effects, rulings, or game logic (beyond the Huge Revolution ID fix)
- Card text, translations, or any of the six languages
- Region or language settings — English and the other localised text continue to work normally
- The save data format or ROM size, so **you do not need to delete an existing save**
- The ROM's internal game code or header checksum

---

## Installation

### Option A — Floating IPS (recommended)

1. Download and open [Floating IPS (Flips)](https://www.smwcentral.net/?p=viewthread&t=88029).
2. Select **Apply Patch**.
3. Select `Yu-Gi-Oh-Ultimate-Masters-2006-Uncensored-v1.0.bps`.
4. Select the clean USA ROM listed below.
5. Choose a new filename for the patched output.

The patch embeds the source checksum, so it will refuse to apply to the wrong ROM.

### Option B — the Python patcher

Requires Python 3.10 or newer and uses only the standard library.

```powershell
python patch_rom.py "clean-rom.gba"
```

This creates `clean-rom (Uncensored + Huge Revolution Fix).gba` beside the clean input. Pass a second
path to choose a different output filename. The patcher validates the ROM size, SHA-1, artwork table,
and Huge Revolution byte before writing anything, and it refuses to overwrite your clean input ROM.
Add `--force` only when you intend to replace an existing output file.

---

## Required ROM

The patch applies **only** to this exact ROM.

| Property | Value |
| --- | --- |
| Release | USA (En, Ja, Fr, De, Es, It) |
| Internal title | `YUGIOHWCT06` |
| Game code | `BY6E` |
| Maker code | `A4` |
| Size | `33,554,432` bytes (32 MiB) |
| Clean SHA-1 | `9689337D6AAC1CE9699AB60AAC73FC2CFDCCAD9B` |
| Clean SHA-256 | `F405C620DA05A817A5D63F45A4707B914260FB5802FE519B1E31BF050BA8F524` |

### Verify your patched ROM

| Property | Value |
| --- | --- |
| Patched SHA-1 | `A8D79DFF3EB3660E4BFC1ECBC5763CC75F7A3E06` |
| Patched SHA-256 | `8DDAEBE7032BDC0A342494DCC85676310B50F00A6F38BE5B2A8F68B7517AF02A` |
| GBA header checksum | `0x9D` (unchanged) |

---

## How it was done

Investigation used the public
[`testyourmine/ygowct06` disassembly](https://github.com/testyourmine/ygowct06), whose expected ROM
SHA-1 matches this release exactly. It provided labels and code structure for what would otherwise
be raw ARM and Thumb machine code.

### Region and language selection

The game reads the region character from the fourth byte of the GBA game code at address
`0x080000AF`:

```c
#define GET_HEADER_REGION() (*(u16 *)0x080000AE >> 8)
```

For game code `BY6E` that character is `E`; Japanese checks expect `J` (`0x4A`). The selected
language lives in the low three bits of the save field at `gUnk_02000000 + 0x6C2C`, where Japanese
is language value `0`. Card rendering repeatedly evaluates:

```text
variant = 1
if header region == 'J' and selected language == Japanese:
    variant = 0

gCardArtIndexes[card_art_index * 2 + variant]
```

### The artwork index table

| Property | Value |
| --- | --- |
| GBA address | `0x095B5C00` |
| ROM file offset | `0x015B5C00` |
| Logical table size | `0x20C8` bytes |
| ROM file end offset | `0x015B7CC8` (exclusive) |
| Entry format | Little-endian unsigned 16-bit integers |
| Pairs examined | `2,098` |
| Pairs that differed | `233` |

For every differing pair, the international entry is overwritten with the value from its Japanese
entry:

```text
international_art_index = japanese_art_index
```

This only changes *which* existing assets the game selects. No graphics were imported, replaced,
recompressed, or moved.

Elemental Hero Burstinatrix is internal card ID `1814`. Its pair at file offset `0x015B7858`
changes from `(2018, 2019)` to `(2018, 2018)`, redirecting the international slot to the existing
uncensored artwork.

### The Huge Revolution instruction

File offset `0x00020FC2` maps to GBA address `0x08020FC2`, inside the Thumb function labelled
`gEngineEffectGraveyardBanish_08020FA8`. That function derives several card IDs from constants; in
the Huge Revolution path it starts at `0x16DC`, subtracts `0x62`, then hits the instruction above.

The corrected immediate value comes from Scrub Busta's video; the file offset, function label, and
surrounding arithmetic were located here using the disassembly.

```text
4D 38    subs r0, #0x4D     ->  wrong ID
8B 38    subs r0, #0x8B     ->  0x15EF, correct
```

### Verification

The patched ROM was compared byte-for-byte against the clean input.

| Check | Result |
| --- | --- |
| Original ROM unchanged | Passed |
| Input and output sizes equal | Passed (both `33,554,432` bytes) |
| Differing artwork mappings patched | Passed (`233`) |
| All 2,098 artwork pairs now match | Passed |
| Burstinatrix pair is `(2018, 2018)` | Passed |
| Huge Revolution byte is `0x8B` | Passed |
| Changes outside expected locations | `0` |
| Total changed bytes | `236` |
| Internal game code remains `BY6E` | Passed |
| Stored GBA header checksum | `0x9D` |
| Recalculated GBA header checksum | `0x9D` |

The BPS patch itself was validated by decoding it and checking all three embedded CRC32 values
(source, target, and patch); applying it reproduces the patched ROM hash listed above exactly.

---

## Compatibility

The patched ROM stays at the original 32 MiB size and works with GBA emulators (mGBA, no$gba,
VisualBoyAdvance-M, RetroArch) and with compatible flash cartridges that support the original
game's ROM size and save hardware. Existing saves remain valid.

## Credits

- [Scrub Busta](https://www.youtube.com/watch?v=rKUE2M25_dA) — found the Huge Revolution card ID
  bug and worked out the fix. The Huge Revolution half of this patch comes entirely from that
  video; it would not exist without it.
- [`testyourmine/ygowct06`](https://github.com/testyourmine/ygowct06) — the disassembly that made
  the region/language logic and artwork table identifiable.
- Project page and screenshots: **<https://rainear.net/Yu-Gi-Oh-Ultimate-Masters-2006>**

## Legal

This repository contains **no ROM image and no game data** — only a patch file and the script that
produces one. You must supply your own legally obtained backup of the game.

*Yu-Gi-Oh!* and all related properties are trademarks of their respective owners. This is an
unofficial fan project and is not affiliated with or endorsed by Konami or Nintendo.
