# Brownfield Summary Template

Template for `.planning/brownfield-analysis.md` — synthesized codebase analysis for user presentation.

**Purpose:** Compress 7 codebase analysis documents (`.planning/codebase/*.md`) into a single, actionable summary. This template guides the brownfield-analyzer agent to produce a two-tier document: an executive summary for quick scanning and detailed sections for reference. The output is read by the brownfield-flow workflow and presented to the user before purpose selection (fix/improve/refactor).

---

## File Template

```markdown
# Codebase Analysis Summary

**Analysis Date:** [YYYY-MM-DD]
**Codebase Health:** [Good / Moderate / Concerning]
**Primary Language:** [Language + version from STACK.md]
**Project Size:** [N source files across M directories]

## Executive Summary

| Dimension | Finding | Confidence |
|-----------|---------|------------|
| Architecture | [Pattern name + key characteristic — one line from ARCHITECTURE.md] | [HIGH/MEDIUM] |
| Tech Stack | [Primary language + framework + runtime — one line from STACK.md] | [HIGH/MEDIUM] |
| Code Quality | [Dominant convention pattern + maturity signal — one line from CONVENTIONS.md] | [HIGH/MEDIUM] |
| Testing | [Framework + coverage level + test type presence — one line from TESTING.md] | [HIGH/MEDIUM] |
| Integrations | [Count of external services + key dependency — one line from INTEGRATIONS.md] | [HIGH/MEDIUM] |
| Structure | [Organization pattern + key directory count — one line from STRUCTURE.md] | [HIGH/MEDIUM] |
| Concerns | [Count by severity: N critical, M moderate — one line from CONCERNS.md] | [HIGH/MEDIUM] |

## Top Concerns

[Extract top 3-5 concerns from CONCERNS.md, ranked by impact. Each must include severity tag.]

1. **[Concern title]** — [One-line description with affected file path] (severity: critical)
2. **[Concern title]** — [One-line description with affected file path] (severity: critical/moderate)
3. **[Concern title]** — [One-line description with affected file path] (severity: moderate)
4. **[Concern title]** — [One-line description with affected file path] (severity: moderate/minor)
5. **[Concern title]** — [One-line description with affected file path] (severity: minor)

## Architecture Overview

[Source: .planning/codebase/ARCHITECTURE.md]

Extract and compress:
- Overall pattern name (monolith, microservices, layered, serverless, etc.)
- Number of conceptual layers and their names
- Primary data flow pattern (request lifecycle)
- Key abstractions used throughout
- Entry points

Format: 5-10 bullet points max. Include file paths from source. Tag INFERRED assessments.

## Technology Stack

[Source: .planning/codebase/STACK.md]

Extract and compress:
- Primary and secondary languages with versions
- Runtime environment and package manager
- Core framework(s) and their versions
- Critical dependencies (top 3-5 only)
- Build/dev tooling

Format: 5-10 bullet points max. Versions must be included where specified in source.

## Code Quality & Conventions

[Source: .planning/codebase/CONVENTIONS.md]

Extract and compress:
- Naming patterns (files, functions, variables)
- Formatting tools and config (Prettier, ESLint, etc.)
- Import organization pattern
- Error handling strategy
- Code maturity assessment: consistent/inconsistent, modern/legacy patterns

Format: 5-10 bullet points max. Note deviations between areas (e.g., "new code uses X, legacy uses Y").

## Testing State

[Source: .planning/codebase/TESTING.md]

Extract and compress:
- Test framework and runner
- Test file organization pattern
- Test types present (unit, integration, E2E) and which are missing
- Coverage level (if specified) or coverage gaps
- Key run commands

Format: 5-10 bullet points max. Highlight missing test types as concerns.

## External Integrations

[Source: .planning/codebase/INTEGRATIONS.md]

Extract and compress:
- Count of external services by category (payment, auth, storage, monitoring)
- Key services with SDK/client info
- Authentication patterns (where secrets live, not values)
- Webhook endpoints if any
- Environment configuration pattern

Format: 5-10 bullet points max. Include env var names from source.

## Codebase Structure

[Source: .planning/codebase/STRUCTURE.md]

Extract and compress:
- Top-level directory layout summary (not full tree)
- Organization pattern (feature-based, layer-based, hybrid)
- Key file locations (entry points, configs, core logic)
- Naming conventions for files and directories
- Where new code should go

Format: 5-8 bullet points max. This section can be shorter than others.

## Detailed Concerns

[Source: .planning/codebase/CONCERNS.md]

Extract and organize all concerns, grouped by category with severity tags:

**Critical:**
- [Concern] — [Impact + affected files] (from: [source section in CONCERNS.md])

**Moderate:**
- [Concern] — [Impact + affected files] (from: [source section in CONCERNS.md])

**Minor:**
- [Concern] — [Impact + affected files] (from: [source section in CONCERNS.md])

Format: This section may be longer than others (10-20 lines). Include file paths for every concern. Group by severity, then by CONCERNS.md source category (Tech Debt, Known Bugs, Security, Performance, Fragile Areas).

---

*Brownfield analysis generated: [YYYY-MM-DD]*
*Full source documents: .planning/codebase/*.md*
*Update by re-running brownfield analyzer after codebase changes*
```

<good_examples>
```markdown
# Codebase Analysis Summary

**Analysis Date:** 2025-01-20
**Codebase Health:** Moderate
**Primary Language:** TypeScript 5.3
**Project Size:** 127 source files across 23 directories

## Executive Summary

| Dimension | Finding | Confidence |
|-----------|---------|------------|
| Architecture | Next.js App Router with server actions, layered (pages → actions → lib) | HIGH |
| Tech Stack | TypeScript 5.3 + Next.js 14 + Prisma 5.8 on Vercel | HIGH |
| Code Quality | Consistent naming, Prettier + ESLint configured, some legacy patterns in older pages | HIGH |
| Testing | Vitest for unit tests, no E2E, ~45% coverage on lib/ only | MEDIUM |
| Integrations | 5 external services (Stripe, Supabase Auth, SendGrid, Sentry, S3) | HIGH |
| Structure | App Router feature-based, well-organized with clear separation | HIGH |
| Concerns | 2 critical (auth bypass, N+1 queries), 4 moderate, 3 minor | HIGH |

## Top Concerns

1. **Admin auth bypass** — Client-side only role check in `app/admin/` pages, no server middleware (severity: critical)
2. **N+1 query pattern** — Course listing fetches lessons per-course in loop, `app/api/courses/route.ts` (severity: critical)
3. **Stripe webhook duplication** — Same verification logic copy-pasted in 3 webhook handlers under `app/api/webhooks/` (severity: moderate)
4. **No E2E test coverage** — Payment flow untested end-to-end, has broken twice in production (severity: moderate)
5. **Unmaintained dependency** — react-hot-toast last updated 18 months ago, React 19 compat unknown (severity: minor)

## Architecture Overview

[Source: .planning/codebase/ARCHITECTURE.md]

- **Pattern:** Next.js App Router with server-side rendering and server actions
- **Layers:** Pages (UI) → Server Actions (data mutation) → Lib (business logic) → Prisma (data access)
- **Data flow:** HTTP request → Next.js middleware (auth check) → Page component (RSC) → Server action → Prisma query → Response
- **Key abstractions:** Server actions in `app/actions/`, shared lib utilities in `lib/`, Prisma models in `prisma/schema.prisma`
- **Entry points:** `app/layout.tsx` (root layout), `middleware.ts` (auth guard), `app/api/` (API routes)
- **State management:** Server-side via Prisma + Supabase Auth sessions, client-side via React state (no Redux/Zustand)
- **Error handling:** Try/catch in server actions, error.tsx boundaries per route segment

## Technology Stack

[Source: .planning/codebase/STACK.md]

- **Primary language:** TypeScript 5.3 (all application code)
- **Framework:** Next.js 14.1 (App Router) on Node.js 20.x
- **ORM:** Prisma 5.8 with PostgreSQL
- **Package manager:** npm 10.x with `package-lock.json`
- **Auth:** Supabase Auth via `@supabase/ssr` v0.1
- **Payments:** Stripe v14.8 (checkout sessions, subscriptions, webhooks)
- **Build/Dev:** Next.js built-in bundler (Turbopack in dev), TypeScript compiler
- **Deployment:** Vercel (auto-deploy on main push)

## Code Quality & Conventions

[Source: .planning/codebase/CONVENTIONS.md]

- **File naming:** kebab-case for all files, PascalCase for React components
- **Formatting:** Prettier configured (`.prettierrc`), 100 char line length, single quotes, semicolons
- **Linting:** ESLint with `@typescript-eslint/recommended`, enforced in CI
- **Import order:** External → Internal (`@/lib`, `@/components`) → Relative → Type imports
- **Error handling:** Try/catch in server actions, Error class extensions for domain errors
- **Maturity assessment:** Consistent in `lib/` and `app/actions/`, inconsistent in older `app/` pages (direct DB queries instead of server actions) [INFERRED: migration in progress]
- **Comments:** JSDoc on public lib functions, sparse elsewhere

## Testing State

[Source: .planning/codebase/TESTING.md]

- **Framework:** Vitest 1.0 with built-in expect assertions
- **File organization:** `*.test.ts` alongside source in `lib/` and `app/actions/`
- **Test types present:** Unit tests only (lib/ functions, server actions)
- **Test types MISSING:** Integration tests, E2E tests (no Playwright/Cypress configured)
- **Coverage:** ~45% on `lib/` directory, 0% on `app/` pages and API routes [INFERRED from test file count]
- **Run command:** `npm test` (Vitest), `npm run test:coverage` (with c8)
- **Key gap:** Payment flow (Stripe checkout → webhook → subscription update) completely untested

## External Integrations

[Source: .planning/codebase/INTEGRATIONS.md]

- **Payment:** Stripe v14.8 — subscriptions + one-time payments (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`)
- **Auth:** Supabase Auth — email/password + Google OAuth (`NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`)
- **Database:** PostgreSQL on Supabase via Prisma (`DATABASE_URL`)
- **Storage:** Supabase Storage — avatars (public bucket), course materials (private bucket)
- **Email:** SendGrid v8.1 — transactional emails (`SENDGRID_API_KEY`)
- **Monitoring:** Sentry — error tracking (`SENTRY_DSN`)
- **Webhooks:** Stripe incoming at `/api/webhooks/stripe` with signature verification
- **Env config:** `.env.local` for dev (gitignored), Vercel dashboard for prod

## Codebase Structure

[Source: .planning/codebase/STRUCTURE.md]

- **Organization:** Next.js App Router feature-based structure
- **Top-level:** `app/` (pages + API), `lib/` (business logic), `components/` (shared UI), `prisma/` (schema + migrations)
- **Key directories:** `app/actions/` (server actions), `app/api/webhooks/` (webhook handlers), `lib/stripe/` (payment logic)
- **Entry points:** `app/layout.tsx` (root), `middleware.ts` (auth), `prisma/schema.prisma` (data model)
- **Naming:** kebab-case directories, index files for barrel exports
- **New code goes in:** Features in `app/`, logic in `lib/`, shared UI in `components/`

## Detailed Concerns

[Source: .planning/codebase/CONCERNS.md]

**Critical:**
- **Admin auth bypass** — Admin pages (`app/admin/page.tsx`, `components/AdminGuard.tsx`) check role client-side only, no server-side middleware verification (from: Security Considerations)
- **N+1 query pattern** — `/api/courses` endpoint runs separate query per course for lessons, 1.2s p95 with 50+ courses (`app/api/courses/route.ts`) (from: Performance Bottlenecks)

**Moderate:**
- **Stripe webhook duplication** — Copy-pasted signature verification in 3 endpoints (`app/api/webhooks/stripe/route.ts`, `checkout/route.ts`, `subscription/route.ts`), security risk if new webhook skips verification (from: Tech Debt)
- **Race condition on subscription** — User shows "free" tier for 5-10s after payment due to webhook latency (`app/checkout/success/page.tsx`) (from: Known Bugs)
- **Dashboard waterfall** — 5 serial API calls on mount, 3.5s until interactive on slow 3G (`app/dashboard/page.tsx`) (from: Performance Bottlenecks)
- **Payment flow untested** — Full Stripe checkout → webhook → activation flow has no E2E tests, has broken twice (from: Test Coverage Gaps)

**Minor:**
- **react-hot-toast unmaintained** — Last update 18 months ago, React 19 compatibility unknown; migrate to sonner (from: Dependencies at Risk)
- **Unvalidated file uploads** — No file type validation in `components/AvatarUpload.tsx`, only bucket size limit (from: Security Considerations)
- **Mobile logout bug** — Logout via mobile nav doesn't await signOut(), redirects to /dashboard instead of /login (`components/MobileNav.tsx`) (from: Known Bugs)

---

*Brownfield analysis generated: 2025-01-20*
*Full source documents: .planning/codebase/*.md*
*Update by re-running brownfield analyzer after codebase changes*
```
</good_examples>

<guidelines>
**What belongs in brownfield-analysis.md:**
- Synthesized findings from the 7 codebase documents
- Executive summary table with one-liner per dimension
- Confidence tags (HIGH = directly observed in source, MEDIUM = inferred from patterns)
- Top concerns ranked by impact with severity tags
- Detailed sections with compressed extractions from each source document
- File paths from source documents (essential for actionability)
- Severity classifications (critical/moderate/minor) for concerns

**What does NOT belong here:**
- Raw analysis data (that stays in `.planning/codebase/*.md` source documents)
- Opinions not grounded in source document findings
- Feature requests or improvement ideas (those come after purpose selection)
- Implementation plans (those are generated downstream based on this summary)
- Information not present in any of the 7 source documents (no new analysis)
- Actual secrets, API keys, or credentials (reference env var names only)

**Two-tier structure:**
- **Tier 1 — Executive Summary** (top of document): The health rating, summary table, and top concerns. This is what gets presented to the user inline by the workflow. Must be scannable in under 30 seconds. Target: 15-20 lines.
- **Tier 2 — Detailed Sections** (body of document): Compressed extractions from each source document. This is reference material the user or downstream agents can consult. Not shown inline unless requested.

**OBSERVED vs INFERRED distinction:**
- **OBSERVED (HIGH confidence):** Facts directly stated in source documents with file path evidence. Example: "Vitest 1.0 configured in vitest.config.ts"
- **INFERRED (MEDIUM confidence):** Assessments derived from patterns in source documents but not explicitly stated. Example: "Migration from direct queries to server actions appears in progress" — mark these with `[INFERRED]` tag.
- Never present inferences as facts. When in doubt, tag as INFERRED.

**File paths are required:**
- Every concern must include at least one file path from the source document
- Architecture and structure sections must reference key locations
- Use backtick formatting: `app/api/webhooks/stripe/route.ts`

**This template is NOT the analysis:**
- This file defines the structure the brownfield-analyzer agent fills in
- The agent reads `.planning/codebase/*.md` documents and writes `.planning/brownfield-analysis.md`
- Each section heading and extraction instruction acts as an implicit prompt for the agent
- The good_example shows expected compression level and format quality

**Section length guidelines:**
- Executive Summary table: exactly 7 rows (one per dimension)
- Top Concerns: 3-5 items (never more than 5)
- Architecture through Structure sections: 5-10 bullet points each
- Detailed Concerns: 10-20 lines (this section gets more space because it drives purpose selection)
- Total document target: 80-120 lines (compressed from 200-1000+ lines of source)

**When the analyzer fills this template:**
1. Read all 7 documents in `.planning/codebase/`
2. Fill executive summary table first (forces one-liner compression per dimension)
3. Extract top concerns and assign severity based on CONCERNS.md categories
4. Fill each detailed section by reading its specified source document
5. Cross-reference: if a concern in CONCERNS.md relates to architecture, include the connection
6. Verify every concern has a file path before finalizing
</guidelines>
