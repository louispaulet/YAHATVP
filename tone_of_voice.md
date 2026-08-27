# YAHATVP website tone of voice

This is the canonical writing guide for user-facing language across
`website/hatvp-transparency-dashboard/frontend`. Use it with
`design_style.md`: the design guide defines how the interface looks and this
guide defines how it speaks.

The audience is a curious member of the public who may not know the HATVP
dataset, its schema, or its limitations. The writing should help that person
form a useful next question, understand what a number represents, and reach
the source without needing specialist vocabulary.

## Voice in five words

- **Curious:** invite investigation and useful questions.
- **Clear:** prefer everyday words and concrete explanations.
- **Precise:** say exactly what is counted, compared, or inferred.
- **Candid:** put limitations and caveats beside the claim they qualify.
- **Respectful:** describe public records without judging the people in them.

The overall tone is editorial civic data: confident enough to guide a reader,
quiet enough to avoid sensationalism, and transparent enough to earn trust.

## Core rules

### Start with the reader’s question

Frame sections around what someone can learn or do:

- “Find a person or filing.”
- “What stands out”
- “What this snapshot means”
- “Choose your next question.”

Use a short headline followed by one clear explanation. Do not make the reader
decode an internal table name before they understand why it matters.

### Explain before interpreting

Describe the measurement first, then offer a restrained interpretation. For
example, say that average annual reported income is shown beside total observed
assets and explain that the bars show relative scale. Do not turn that display
into a claim about wealth, spending, or financial behaviour.

### Keep evidence and uncertainty together

Every data-dependent claim should make its scope clear with language such as:

- “in this snapshot”
- “published” or “reported”
- “observed”
- “inferred from published civilité fields”
- “flagged for review”
- “missing or unmapped”

Do not hide caveats in a distant methodology page when they change how the
nearby figure should be read.

### Respect the people represented

The dashboard is about public records, not about assigning motives or blame.
Use neutral descriptions of declarants, mandates, institutions, income, assets,
and filing history. A review flag is a data-quality or interpretation prompt,
not evidence of misconduct.

## Word choices

Use the established vocabulary consistently:

| Prefer | Avoid | Reason |
| --- | --- | --- |
| declarant | target, subject, suspect | Neutral public-record language |
| public declaration | dossier, secret file | Describes the published object |
| filing or declaration | submission when the UI is about records | Plain language for the reader |
| amended filing / later public version | correction, error, suspicious filing | An amendment is not automatically a fault |
| reported income | earnings or salary when the field is broader | Match the source scope |
| observed assets | wealth, fortune, net worth | The aggregate is not a complete wealth measure |
| flagged for review | problematic, fraudulent, false | Flags require interpretation and review |
| missing or unmapped | unknown person, incomplete person | The missing value is the field, not the person |
| snapshot | live truth, final record | The view is a dated publication state |
| source declaration | original truth | Keep source and interpretation distinct |

Avoid loaded words such as “scandal”, “shocking”, “exposes”, “richest”,
“corrupt”, “caught”, “proof”, and “secret” unless they appear in a quoted
source context that is explicitly identified as such. Never use a headline to
imply wrongdoing from a large amount, a change, an amendment, or a missing
field.

## Sentence and headline style

- Use sentence case for new headings and explanatory copy. Preserve established
  navigation labels where the interface already uses them.
- Prefer active, direct verbs: “Search a declarant”, “Read the source”,
  “Open the declaration”.
- Keep headlines short and specific. A headline may be editorial, but the
  supporting sentence must explain the data plainly.
- Use one idea per sentence where a definition or caveat is involved.
- Prefer “this snapshot” over vague words such as “here” or “the data”.
- Avoid rhetorical questions that imply an answer, especially about individual
  people or amounts.
- Avoid all-caps prose. Uppercase is a visual treatment reserved for eyebrows
  and compact metadata labels in the design system.
- Use numerals for counts and apply the existing locale-aware formatters. Do
  not manually add separators, currency symbols, or compact units in copy.

## Data-sensitive language

Use these patterns when writing around the dashboard’s recurring topics:

### Amounts and comparisons

Say what the amount is and where it comes from. Distinguish annualized values,
totals, rows, and people. When measures have different meanings, say they are
shown side by side or compared for scale; do not imply they share a unit.

### Gender fields

Describe the result as a split or balance inferred from the published civilité
field. State that missing or unmapped civilité values are excluded from the
ratio when that is the calculation. Do not present the result as a definitive
statement about every person’s gender identity.

### Amendments

Explain an amended declaration as a later public version that remains part of
the publication history. Do not call it an error, retraction, or correction
unless the source explicitly does so.

### Anomalies and review flags

Use “flagged for review” and explain what the flag asks the reader to inspect.
Keep the source value visible when the product’s data policy requires it, while
making clear whether it is included in an aggregate.

### Historical and recovery sources

Identify the official HATVP publication separately from Wayback, GitHub, or
other preserved historical copies. Call recovery data a preserved source or
archive, not a new HATVP publication.

## UI copy patterns

### Hero and section introductions

Use this order:

1. A concise promise or question.
2. One sentence describing the scope and source.
3. A direct action or a clear route to evidence.

Do not lead with implementation details, endpoint names, or internal pipeline
terminology.

### Cards and charts

Each analytical card should have:

- a short eyebrow that names the theme;
- a descriptive title that says what is shown;
- a brief explanation of the measure;
- a visible legend, note, or caveat when interpretation needs it.

Chart titles should describe the chart, not make an unsupported conclusion.
“Average annual income vs assets” is appropriate; “Who is richest?” is not.

### Actions and links

Use explicit verbs and name the destination:

- “Search”
- “See standout records”
- “Sources and methods”
- “Open declaration”
- “Download CSV”

Avoid generic actions such as “Go”, “Click here”, or “Learn more” when a more
specific label fits.

### Loading, empty, and error states

- Loading: explain what is loading, such as “Loading dashboard data”.
- Empty: state what was not found and keep the distinction from zero visible,
  such as “No asset rows were found in this snapshot.”
- Error: describe the failed slice in plain language and offer a retry action.
- Never blame the user or imply that a missing result proves the absence of a
  person, asset, or declaration in the real world.

## English and French

- English and French are equal product experiences. Add visible copy to both
  locale files in `src/config/locales/`.
- Translate the meaning and level of certainty, not just the individual words.
  Preserve every limitation, denominator, date, and source distinction.
- Keep terminology stable across pages. In French, prefer the established
  product vocabulary such as “déclarant”, “déclaration”, “dépôt modificatif”,
  “instantané”, “patrimoine observé”, and “valeurs déclarées”.
- Let French copy breathe and wrap naturally. Do not shorten a caveat merely to
  keep a card the same height.
- Use the existing locale-aware number, currency, date, and percentage
  formatters rather than embedding English formatting in a translated string.
- Check both languages in headings, buttons, loading states, empty states,
  error states, disclosures, and chart descriptions.

## Accessibility and trust

- Visible text should be understandable without the chart, color, or icon.
- Accessible chart descriptions must use the same careful wording as the visual
  labels and notes.
- Keep labels, buttons, and errors concise enough to scan but complete enough
  to act on.
- Do not use color, capitalization, or punctuation to create urgency that the
  evidence does not support.
- If a term is necessary but technical, define it at first use or link to the
  relevant source/method explanation.

## Review checklist

Before shipping user-facing copy, ask:

- Is the reader’s question or next action clear?
- Does each claim say what is counted and which snapshot or source it uses?
- Are caveats next to the number or interpretation they qualify?
- Does the copy avoid implying wrongdoing, wealth, motive, or certainty that
  the data cannot establish?
- Are “reported”, “observed”, “inferred”, and “flagged for review” used
  deliberately?
- Are English and French both updated with equivalent meaning?
- Will the text still make sense in loading, empty, error, and narrow mobile
  states?
- Does the wording match the visual hierarchy in `design_style.md`?

If the answer to any question is no, revise the copy before polishing its
layout.
