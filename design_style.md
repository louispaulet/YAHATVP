# YAHATVP website design style

This is the canonical visual and interaction guide for the website in
`website/hatvp-transparency-dashboard/frontend`. It describes the existing
design language and is intended to keep new pages, components, and refinements
coherent across the dashboard.

The website is a public civic-data product. Its visual voice is editorial,
calm, precise, and curious: make the data easier to understand without making
it feel sensational or decorative.

## Design principles

- Lead with the question or story, then show the evidence.
- Make scale, definitions, caveats, and source context visible.
- Prefer a long, readable page over a space-consuming lateral rail.
- Use progressive disclosure for secondary analysis and expensive charts.
- Keep the interface warm and human, but never let styling imply a stronger
  claim than the data supports.
- Reuse existing components and Tailwind utilities before introducing a new
  pattern.

## Foundations

### Typography

- Body and interface text: `DM Sans`, with the system sans-serif stack as
  fallback.
- Headings and editorial display text: `Space Grotesk`, with the system
  sans-serif stack as fallback.
- Use `Space Grotesk` for `h1`, `h2`, and `h3`; use `DM Sans` for labels,
  descriptions, tables, controls, and metadata.
- Eyebrows and utility labels are uppercase, bold, compact, and tracked out
  (`tracking-[0.18em]` to `tracking-[0.2em]`).
- Display headings use tight tracking and leading. Keep them readable on small
  screens with responsive Tailwind sizes or `clamp()` when a fluid hero scale
  is needed.
- Body copy should normally use `leading-6` or `leading-7`; explanatory copy
  must not be compressed to fit a card.

### Color tokens

Use the Tailwind theme tokens defined in
`website/hatvp-transparency-dashboard/frontend/src/styles.css`.

| Token | Hex | Use |
| --- | --- | --- |
| `canvas` | `#f6f7f2` | Warm page background |
| `ink` | `#17231f` | Primary text, dark hero and metric surfaces |
| `emerald` | `#1f9d75` | Primary accent, links, active states, positive data cue |
| `lime` | `#d9f99d` | Secondary accent, highlights, generated-data callouts |
| `sky` | `#8ed7e8` | Secondary data series and supporting accents |
| `violet` | `#b8a5e8` | Secondary data series and supporting accents |
| `surface` | `#ffffff` | Cards and primary content surfaces |
| `surface-subtle` | `#f1f3ee` | Quiet inset areas and closed disclosures |
| `border-soft` | `#e1e5df` | Card and table borders |

Existing chart-specific accents may use the established coral values
`#d96c86` and `#b24b67`, or the sky label `#3e8191`, when the chart meaning
requires a distinction. Do not add a new color for a one-off decoration.

### Surfaces, borders, and shadows

- Standard cards use the shared `dashboard-card` class: white surface,
  `1.5rem` radius, soft border, and `shadow-card`.
- Large hero surfaces use approximately `2rem` radius and
  `shadow-card-raised`.
- Dark metric bands use `bg-ink` with white text and `text-lime` section
  labels.
- Prefer one-pixel soft borders and restrained shadows over heavy outlines or
  glass effects.
- Use `rounded-xl` to `rounded-2xl` for controls, tags, inputs, and compact
  sub-surfaces. Use pills only for statuses, language controls, or short
  disclosure labels.

## Layout and spacing

- The main content uses a centered `max-w-7xl` container with `px-5` on small
  screens and `lg:px-8` on larger screens.
- The homepage is a single-column reading journey: hero, snapshot metrics,
  story-led signals, supporting evidence, then next-step routes.
- Section rhythm generally starts at `mt-16`; card grids use `gap-4` or `gap-5`.
- Use responsive grids for related content, but let cards stack naturally on
  mobile. Never introduce a persistent side rail on the public dashboard.
- Use `min-w-0` on grid children and chart wrappers so content can shrink
  without creating page-level overflow.
- When two desktop columns should align, use grid stretching and a shared
  height strategy. If one side is naturally shorter, add useful related
  content rather than leaving a visually accidental gap.
- Tables must wrap long labels on narrow screens. Reserve `overflow-x-auto`
  for genuinely wide data tables, not as a substitute for responsive layout.

## Component patterns

Prefer these existing components and extend them before creating parallel
versions:

- `Panel`: standard section card with eyebrow, heading, description, and
  content slot.
- `HomepageInsightCard`: numbered, tone-coded story card for a headline
  signal; use `flex h-full flex-col` and `flex-1` content for equal-height
  desktop rows.
- `HomepageRouteCard`: consistent next-step navigation card with a clear
  destination and action.
- `MetricCard`: compact snapshot count treatment.
- `LoadingShell` and `ChartSkeleton`: loading states that preserve layout while
  data arrives.
- `SliceError`: retryable data-slice error state.
- `SnapshotContext`: compact, locale-aware snapshot date, generation time, and
  source-scope row for evidence-dependent sections.
- `Disclosure`: semantic `<details>` and `<summary>` treatment for secondary
  explanations, technical fields, and bounded source content.

Use the standard panel structure:

```tsx
<Panel eyebrow="..." title="..." description="...">
  {/* reusable content */}
</Panel>
```

Keep new components focused, data-driven, and composable. Avoid duplicating
card markup across routes. Keep visible labels in the locale files rather than
hardcoding user-facing copy in components.

## Data visualization style

- Use the existing Recharts setup and lazy-load heavier chart modules when the
  section is below the initial view.
- Every chart needs an accessible description through `role="img"` and a
  meaningful `aria-label`, plus visible legends or supporting text when color
  alone is insufficient.
- Use the established emerald, coral, sky, violet, and lime palette for data
  meaning; do not introduce arbitrary gradients or decorative chart colors.
- Explain denominators, annualization, exclusions, and caveats next to the
  chart. Comparisons must not imply a shared unit when the measures differ.
- Keep secondary analysis out of the initial reading path when it would
  dominate the main page. For the women’s-share-by-position chart, reveal the
  plot once its panel enters the viewport and keep it open for the rest of the
  visit, so the reader does not need to operate a separate disclosure control.
- Empty and error states must be explicit and readable; never render a blank
  chart area that could be mistaken for zero data.

## Loading and performance

- Load the overview and the above-the-fold shell first.
- Defer income, assets, declarations, and gender slices until the homepage
  sentinel is near the viewport, using the existing deferred-load pattern.
- Keep skeletons in the same approximate shape as the eventual content.
- Lazy-load interactive chart bundles, but preserve an immediate textual
  explanation around them.
- Do not block the first meaningful view on below-the-fold analytical data.
- Respect `prefers-reduced-motion`; loading and chart transitions must not be
  required to understand the data.

## Interaction and accessibility

- Use semantic headings in reading order and descriptive `aria-labelledby` or
  `aria-label` values for sections and charts.
- Every input needs a real label, including visually-hidden labels where the
  visual design uses a placeholder.
- Use the established emerald `focus-visible` outline with a visible offset.
- Interactive targets must be comfortable to tap and must not be clipped by
  responsive containers.
- Links should clearly indicate their destination; primary actions use the
  existing emerald/ink hierarchy rather than unexplained icon-only controls.
- Disclosures must expose their open/closed state and keep their content
  understandable when collapsed.
- Preserve readable contrast on the warm canvas, white cards, dark surfaces,
  and colored data accents.

## Bilingual content

- English and French are first-class views. Add or update both
  `src/config/locales/en.json` and `src/config/locales/fr.json` for visible
  copy.
- Keep dynamic source labels behind the existing translation helpers.
- Allow French text to wrap; do not solve localization with truncation or
  fixed-width labels.
- Test language switching on new page states, including loading, empty, error,
  disclosure, and chart descriptions where applicable.

## Brand and asset rules

- Reuse the HATVP mark at `frontend/public/hatvp-mark.webp` in shared shell
  contexts.
- Prefer the existing icon library for interface icons. Do not replace icons
  with emoji or hand-drawn CSS/SVG shapes.
- Do not add stock photography or decorative imagery to analytical surfaces
  unless the product brief explicitly calls for it.
- Keep the editorial civic tone through typography, color, spacing, and clear
  source language rather than ornamental graphics.

## Responsive QA checklist

Before handing off a website change, inspect at least:

- `1440 × 1024`: desktop hierarchy, card alignment, chart labels, and footer.
- `1024 × 768`: tablet transition and grid wrapping.
- `390 × 844`: mobile controls, table wrapping, disclosure states, and no
  horizontal overflow.
- `320px` wide: minimum supported layout, long French labels, and no clipped
  primary action.

Confirm that the browser console has no new warnings or errors and that the
primary navigation, search, language switcher, and any new disclosure still
work at the narrowest tested width.

## Change discipline

When a new page or component introduces a genuinely new visual pattern, first
check whether an existing component or token can express it. If a new token or
pattern is necessary, update this file and the implementation together, record
the reason in `CHANGELOG.md`, and add visual evidence to
`website/hatvp-transparency-dashboard/frontend/design-qa.md` when the change
affects layout or interaction.
