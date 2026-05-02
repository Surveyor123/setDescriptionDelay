# Set Description Delay

An NVDA add-on that extends the built-in delayed character description feature with a configurable delay and an instant description mode.

## Description

NVDA includes a "Delayed descriptions for characters on cursor movement" checkbox in Voice settings. When enabled, NVDA announces the phonetic description of a character (e.g. "alpha" for "a") after a fixed, hardcoded delay when the cursor moves over it.

This add-on extends that feature in two ways:

- **Configurable delay**: A spinbox is added directly below the "Delayed descriptions for characters on cursor movement" checkbox in the Voice settings panel, both visually and in tab order. You can set the delay in milliseconds (0–5000).
- **Instant description mode**: If the delay is set to 0, the character itself is not announced at all — instead, the phonetic description is spoken immediately. For characters with no phonetic description (punctuation, whitespace, etc.), normal speech rules apply so that other add-ons (such as Phonetic Punctuation) continue to work correctly.

## Requirements

- NVDA 2026.1 or later

## Installation

1. Download the `.nvda-addon` file.
2. Open it with NVDA (double-click or press Enter on it).
3. Follow the installation prompts and restart NVDA when asked.

> **Note:** If **EnhancedPhoneticReading** is installed on your system, a warning dialog will appear shortly after installation. Because both add-ons patch the same internal speech functions, using them together may cause unpredictable behaviour such as doubled speech or missed character descriptions. It is recommended to remove one of them to avoid conflicts.

## Usage

1. Open NVDA Settings (NVDA+N → Preferences → Settings).
2. Go to the **Voice** category.
3. Check **"Delayed descriptions for characters on cursor movement"** if it is not already checked.
4. The **"Description delay (ms, 0=instant)"** spinbox appears directly below the checkbox, both visually and in tab order.
5. Set your preferred delay:
   - **0** — Speak the phonetic description immediately instead of the character.
   - **1–5000** — Speak the character first, then speak the phonetic description after the specified number of milliseconds.
6. Click OK or Apply to save.

## Notes

- The spinbox is hidden when the "Delayed descriptions for characters on cursor movement" checkbox is unchecked.
- The add-on works alongside other add-ons that patch `speech.speakTextInfo` (such as BrowserNav and Phonetic Punctuation). The `_FakeTextInfo` object exposes the `obj` attribute to maintain compatibility.
- The delay value is global and applies to all synthesizers and voices. Use NVDA configuration profiles if you need different values for different synthesizers.