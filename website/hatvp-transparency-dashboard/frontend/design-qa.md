**Findings**

- No actionable P0, P1, or P2 fidelity issues remain.

**Comparison evidence**

- Source visual truth: `/Users/louispaulet/.codex/generated_images/01a01be6-8588-7410-8a7c-b42bfb09b7ce/exec-66ea47f4-2ee6-416e-96f6-bd2c90ec0b6b.png`.
- Implementation capture: `implementation-analysis-desktop.png`, rendered at 1440 × 1024 CSS pixels with device scale factor 1 on `http://127.0.0.1:4176/#/analysis`.
- Combined comparison: `analysis-design-comparison.png`; the selected visual is above the browser-rendered implementation. Both were normalized to a 1440 × 1024 desktop frame.
- State: English, loaded analysis data, “Exclude 0€ salary” enabled. The toggle was exercised in both directions; the displayed salary-bin values changed and returned to the default state.

**Required fidelity surfaces**

- Fonts and typography: Existing DM Sans and Space Grotesk remain consistent with the dashboard while the title, chart heading, and utility labels now follow the selected design’s stronger navy hierarchy.
- Spacing and layout rhythm: The desktop view uses the selected two-column introduction/chart composition, a restrained divider system, and a paired leaderboard grid. At a 390 × 844 viewport the columns stack without horizontal overflow.
- Colors and visual tokens: The redesign uses the source direction’s paper canvas, navy data line, pale blue median line, and small emerald cues, while retaining amber review labels.
- Image quality and asset fidelity: The selected mock contains no app-owned raster imagery. The existing dashboard mark remains unchanged; all data visualizations continue to use the application’s Recharts components.
- Copy and content: All live analysis content, localisation, review labels, and data-dependent control behavior are preserved. No mock data or new product controls were added.

**Implementation Checklist**

- [x] Make the salary comparison the primary above-the-fold analytical object.
- [x] Replace the prior bar-pair treatment with an average/median line comparison.
- [x] Pair the two DOB leaderboards using shared structure instead of disconnected cards.
- [x] Retain the zero-salary chart and compact the detailed age-bin values.
- [x] Verify the loaded desktop layout, responsive stacked layout, and zero-salary control.

**Follow-up Polish**

- [P3] The prior global-navigation mark note was addressed by the shared-header polish documented in the homepage redesign section below.

final result: passed

## 2026-09-06 — Quality-register column spacing

**Refinement**

- Added a small desktop-only gutter between the issue-type and contacted-HATVP
  columns in the quality register. The existing stacked mobile card treatment
  remains unchanged.

**Functional and responsive checks**

- [x] Local Chrome preview showed a restrained gutter between the first two
  columns at a 1470 × 735 desktop viewport; the issue label no longer runs
  visually into the contacted-HATVP date.
- [x] The existing mobile override still applies zero horizontal cell padding
  inside the stacked cards, so the new desktop-only rule does not alter the
  mobile layout or its overflow behavior.
- [x] Frontend tests (35) and the TypeScript/Vite production build passed;
  browser console inspection reported no warnings or errors.

final result: passed

## 2026-09-05 — Viewport-triggered women’s-share chart

**Interaction evidence**

- The local Chrome smoke check showed the women’s-share panel without a
  manual control before it entered the viewport.
- Scrolling the panel into view mounted the lazy chart bundle and displayed the
  plot with its visible legend, supporting values, and accessible chart label.
- The chart remained visible after scrolling past and back to the panel; the
  old “Show chart” control was absent.

**Functional checks**

- [x] Frontend tests: 35 passed.
- [x] TypeScript/Vite production build passed.
- [x] Chrome console inspection reported no warning or error messages from the
  change.

final result: passed

## 2026-09-05 — Reading-path and accessibility polish

**Refinement**

- Added a keyboard skip link and stable `main-content` target.
- Added route orientation focus, query-scoped loading, search-field guidance,
  snapshot-reading disclosure, declaration section anchors, and a technical
  source-fields disclosure.
- Corrected the populated asset chart accessible label so it no longer uses the
  empty-state sentence.
- Added anchored Explore signal navigation and result counts; the pipeline
  countdown keeps its visible timer while announcing only a stable scheduled
  date and time to assistive technology.
- Added reusable snapshot context, signal-meaning disclosures, locale-backed
  declaration labels, contextual empty-section rows, and text fallbacks for
  salary charts. Source XML remains bounded and can be copied without changing
  the API or exposing contact fields.
- Quality issues now collapse into labelled rows below 850px, source actions
  use Lucide icons, and the shared focus outline remains visible across the
  expanded navigation and disclosure controls.
- Declaration annual amount bars now include a text table with localized year
  and amount headers for keyboard and screen-reader readers.
- Declaration details now explain original versus later public versions in a
  localized publication-history section before technical source fields.

**Responsive and interaction checks**

- Local browser checks at 320 × 844 and 1024 × 768 reported document width
  equal to viewport width.
- Verified the skip link, search disclosure, route focus target, and declaration
  section navigation in the local build.
- Frontend tests (34) and the TypeScript/Vite production build passed.

final result: passed

## 2026-08-27 — Supporting evidence balance polish

**Selected visual source**

- Source visual truth: the user-provided Chrome capture of the homepage
  supporting-evidence and methodology section, showing the declaration-type
  table on the left and an under-filled methodology card on the right.
- Intended refinement: preserve the two-column desktop reading path, fill the
  right-side gap with useful snapshot context, and keep the section stacked on
  mobile.

**Implementation captures and comparison evidence**

- Captured the local implementation in Chrome DevTools at 1440 × 1024 with
  loaded English data. The declaration-type panel and the right column both
  measured 851px high; the right column contains the methodology card followed
  by the new “One view, four tables” panel.
- Compared the same loaded state against the provided capture: the lower
  section keeps its original content and hierarchy, while the added coverage
  panel removes the empty right-side runout with source-backed counts.
- Captured the same route at a 390 × 844 mobile viewport. The declaration table
  wraps long labels, the right-side panels follow below it, and the document
  scroll width remains equal to the viewport width.

**Functional and responsive checks**

- [x] The new coverage panel reuses the overview snapshot counts and existing
  locale-aware number formatting.
- [x] English/French copy is present and covered by the homepage test suite.
- [x] Desktop panels align at the bottom; mobile panels remain a readable
  single-column flow.
- [x] Chrome console inspection reported no warning or error messages from the
  implementation.

final result: passed

## 2026-08-27 — Story-first civic homepage redesign

**Selected visual source**

- Source visual truth: `/Users/louispaulet/.codex/generated_images/01a0400b-e4a6-77c2-bc34-ed4dc50d4c54/exec-ad82a515-c3a0-4580-ac22-62f885d4fa9a.png`.
- The implementation follows the selected long-scroll, no-side-rail direction: editorial hero, dark snapshot band, story-led reading section, compact supporting evidence, and Explore next links.

**Implementation captures and comparison evidence**

- Captured the local implementation in the browser at 1440 × 1024, 1024 × 768, 390 × 844, and 320 × 844 CSS pixels.
- Desktop comparison confirmed the full-width hero, HATVP mark, snapshot summary, At a glance band, and compact evidence rhythm against the selected visual source.
- Mobile comparison confirmed a single-column flow with wrapped primary and section navigation, no lateral rail, no clipped search control, and no horizontal overflow.

**Functional and responsive checks**

- [x] Snapshot values render from the live overview slice: 2026-08-24, 17,899 declarations, 7,318 people, 227,943 income rows, and 4,784 asset rows.
- [x] Homepage search navigates to `#/search?q=Lecornu` and the primary Explore, Search, and Sources & methods links resolve to their existing routes.
- [x] English/French switching updates the homepage title and supporting copy without warnings or errors.
- [x] Overview content renders first; income, assets, declaration, and gender slices remain in loading shells until the deferred sentinel is approached, then resolve before the reading section is reached.
- [x] The women’s-share chart stays collapsed by default and renders after the disclosure is opened with an accessible chart description.
- [x] Browser checks reported body width equal to viewport width at all four sizes and no console warnings or errors on fresh page loads.

final result: passed
