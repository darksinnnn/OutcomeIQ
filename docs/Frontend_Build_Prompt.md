# Frontend Build Prompt — CAT OutcomeIQ

Paste this whole file as your first message to the agent (Antigravity or otherwise). Attach `Frontend.md`, `Design_System.md`, `Architecture.md`, and `PRD.md` alongside it — this prompt is the instructions, those four are the spec it must follow.

---

## Your job

You are building the **frontend only** for CAT OutcomeIQ, a jobsite mission-intelligence console for a hackathon. A separate team is building the backend in parallel — you will not have a live backend to hit for most of the build, so you are building against a **typed mock data layer** that mirrors the real API contract exactly, so a real backend can be swapped in later by changing one file, not by rewriting components.

Read in this order before writing any code:
1. `PRD.md` — what the product is and the 3 demo scenarios you're building the UI to tell.
2. `Frontend.md` — the full screen-by-screen spec, aesthetic direction, and motion/3D rules. This is your primary spec.
3. `Design_System.md` — literal tokens (colors, type, spacing, radius, motion timing). Wire these into `tailwind.config.ts` verbatim. Do not use any Tailwind default color, font, or shadow.
4. `Architecture.md` §4 (Module contracts) and §3 (Data model) — the exact shape of the data every screen consumes. Your mock fixtures and TypeScript types must match this shape exactly, field for field, so integration later is a config swap, not a rewrite.

## Hard rules

1. **Do not invent your own visual direction.** `Frontend.md` §1 already made the design decisions (color, type, layout, principles) and explicitly ruled out the generic AI-dashboard defaults (cream+terracotta, near-black+neon, rounded-card-everywhere, tracked-out-caps labels, arrow-suffixed buttons). Follow it. Run the anti-vibecoded checklist in `Frontend.md` §8 against every screen before calling it done.
2. **Build against the real contract, not a convenient shortcut.** Every module response in the app must be typed as:
   ```ts
   interface ModuleResponse<T> {
     value: T;
     confidence: number; // 0-1
     evidence: { factor: string; weight_or_probability: number; detail: string }[];
   }
   ```
   Every screen that shows a prediction must render confidence and make evidence clickable/expandable — this is a functional requirement, not a nice-to-have. A number with no evidence affordance is an incomplete screen per this spec.
3. **Mock data must tell the three demo scenarios**, not just look plausible. Build three fixture sets matching `Architecture.md` §5's named scenarios: `FALSE_IDLE`, `ON_TIME_LOW_QUALITY`, `OPERATOR_CONTEXT_MISMATCH` (+ `WHAT_IF_RECOVERY` for the What-If Lab). Each fixture set must be internally consistent — e.g. the `FALSE_IDLE` mission's Reality Engine mock response must actually say `external_workflow` with truck-related evidence, not a generic placeholder string.
4. **One integration seam.** All data access goes through a single `src/lib/api.ts` (or `/data` module) with a `USE_MOCK` flag. Every screen calls this module, never a fixture file directly. When the real backend is ready, flipping `USE_MOCK` to false and pointing `API_BASE_URL` at the FastAPI server should be the entire integration effort.
5. **Screen build order** (from `Implementation_plan.md` Phase 4 — keep this order so a partial build still demos well):
   1. Live Operation
   2. Overview / Mission Center
   3. Root Cause
   4. Outcome Guardian (including the Three.js terrain mesh — see `Frontend.md` §5.2)
   5. What-If Lab
   6. Operator Passport
   Only after all 6 above are real and clickable, scaffold the 4 stretch screens (Training Forge, Operational Memory, Site Stability, Model Health/Admin) as clearly-labeled static "vision" screens — a banner or watermark indicating "concept, not live" is required on these, not optional polish.
6. **3D and motion are scoped, not sprinkled.** Spline appears exactly once (Overview hero). Three.js appears exactly once (Outcome Guardian terrain mesh, height-mapped to real `elevation_error_cm` values from the mock QualityObservation data). Lenis smooth-scroll applies only to the Overview page. Every other screen scrolls natively. Do not add 3D or smooth-scroll anywhere else, even if it looks nice — `Frontend.md` §5 explains why each placement is justified and nowhere else is.
7. **No Caterpillar logo, wordmark, or trademarked yellow.** See `Frontend.md` §7.
8. **Accessibility floor is not optional:** keyboard focus states, `prefers-reduced-motion` respected, status color always paired with a text label, WCAG AA contrast checked specifically on the amber accent and status colors against the dark base.

## Tech stack (do not substitute)

React + TypeScript + Vite · Tailwind (fully re-themed, see Design_System.md §10 for the exact config block) · shadcn/ui primitives restyled to tokens · Framer Motion (state-driven only, not decorative) · `@splinetool/react-spline` · `@react-three/fiber` + `@react-three/drei` · Lenis (Overview only) · Recharts for quantile-band and trend charts · TanStack Query + Zustand · WebSocket client stubbed against mock streaming data (simulate a telemetry tick every few seconds from the `FALSE_IDLE`/`ON_TIME_LOW_QUALITY` fixture timelines so Live Operation looks alive even in mock mode).

## Repo structure for the frontend

```
/frontend
  /src
    /components      # design-system-level primitives (Panel, StatusChip, EvidenceDrawer, etc.)
    /screens          # one folder per screen, matching Frontend.md §3 numbering
    /lib
      api.ts          # the one integration seam — USE_MOCK flag lives here
      types.ts        # ModuleResponse<T> and all per-module payload types, matching Architecture.md §4 exactly
    /mock
      false_idle.ts
      on_time_low_quality.ts
      operator_context_mismatch.ts
      what_if_recovery.ts
      index.ts        # exports a scenario switcher used by the demo
    /styles
      tokens.css / tailwind.config.ts (per Design_System.md)
    App.tsx
  README.md            # how to run, and how to flip USE_MOCK when backend arrives
```

## Definition of done, per screen

- [ ] Matches `Frontend.md`'s spec for that screen (content, layout, interaction).
- [ ] Reads from `src/lib/api.ts`, not a fixture file directly.
- [ ] Every prediction shown has confidence + a working evidence expand/click.
- [ ] Passes the anti-vibecoded checklist (`Frontend.md` §8).
- [ ] Responsive down to the tablet breakpoint (`Design_System.md` §7).
- [ ] If it's one of the 4 stretch screens and not backed by real logic yet, it is visibly labeled as a concept, not presented as live.

## When something in the spec is ambiguous

Default to the more restrained, more explainable choice — this product's whole pitch is "here's the reasoning," so when in doubt, favor showing the evidence over showing a slicker animation. Log any judgment call you make in a `DECISIONS.md` in `/frontend` so the backend integration pass and the rest of the team know what was assumed.

## Done means demoable

At the end of this build, someone should be able to sit down, click through Live Operation → Root Cause → Outcome Guardian → What-If Lab using nothing but `USE_MOCK` fixtures, and see the same three demo scenarios from `PRD.md` §5 tell a coherent story — before a single backend endpoint exists.
