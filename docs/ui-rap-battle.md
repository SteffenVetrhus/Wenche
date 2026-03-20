# UI RAP BATTLE: SvelteKit vs Streamlit

## THE TALE OF TWO INTERFACES

*DJ scratch* ... Ladies and gentlemen, welcome to the Wenche UI Showdown.
In the left corner, wearing fjord-blue CSS and TypeScript armor — **SvelteKit**.
In the right corner, draped in `st.session_state` and Python simplicity — **Streamlit**.

Let the bars fly.

---

## ROUND 1: ARCHITECTURE

### SvelteKit steps up to the mic:

```
Yo, I'm SvelteKit, I got ROUTES for days,
Six pages, six folders, clean separated ways.
Layout.svelte wrapping everything tight,
Sidebar nav with steps glowing bright.

I got hooks.server.ts proxying my calls,
api.ts with TypeScript interfaces for all.
Store.ts keeping state centralized and clean,
Svelte 5 runes — the freshest you've seen.

$state, $derived, reactivity that COMPILES,
No virtual DOM, no runtime reconcile.
I ship LESS JavaScript to the browser, son,
My bundle's lean, my build is done.
```

### Streamlit fires back:

```
Hold up, Kit — you need a BACKEND just to breathe,
hooks.server.ts proxying? That's a crutch, believe.
I AM the backend. I AM the frontend too,
One file. One thousand lines. And I'm THROUGH.

ui.py — that's my whole existence, fam,
No node_modules, no npm, no package jam.
pip install streamlit and I'm LIVE,
No build step needed just to survive.

You need Vite, Node, adapters, and config files?
I boot up with `streamlit run` and crack smiles.
```

**SCORE: SvelteKit 8/10 | Streamlit 7/10**

SvelteKit's separation of concerns is textbook clean. But Streamlit's "one file, zero build" simplicity is brutally effective for a tool like Wenche.

---

## ROUND 2: STATE MANAGEMENT

### SvelteKit:

```
I got a writable store, FullKonfig typed to the bone,
Every field has an interface, nothing unknown.
Two-way bindings flow like water downhill,
$derived() recomputes — no manual drill.

My regnskap page? Real-time balance checks,
Driftsresultat calculates as the user specs.
Type safety catches bugs before they deploy,
TypeScript interfaces — every field's a decoy-proof ploy.
```

### Streamlit:

```
You call that state? Let me show you PAIN.
session_state with string keys — that's my domain.
"f_skyldige_offentlige_avgifter" — yeah I key by STRING,
a_navn_0, a_fnr_1 — dynamic shareholder bling.

No types? No problem. I cast with int(),
Every. Single. Value. Gets the int()rint.
107 defaults in a dictionary? That's how I roll,
Copy-paste the same field mapping — HEART AND SOUL.

You want foregående år? I prefix with "f_",
That's right — I namespace with a LETTER, chef.
```

**SCORE: SvelteKit 9/10 | Streamlit 4/10**

This round isn't close. SvelteKit has typed interfaces (`SelskapData`, `ResultatData`, `BalanseData`), a centralized store, and `$derived()` for computed values. Streamlit's `session_state` is a flat dictionary of 107+ string keys with manual `int()` casting everywhere. The `f_` prefix convention for previous year data is... creative survival.

---

## ROUND 3: USER EXPERIENCE

### SvelteKit:

```
Sidebar navigation, always visible, always there,
Step badges numbered 1 through 6 with care.
Active state highlighted, you know where you stand,
Scandinavian design system — muted, understated, grand.

CSS custom properties for spacing and radius,
Responsive grid that collapses — nothing miscellaneous.
Cards with borders, alerts with colors that POP,
Hover states, focus rings, I never stop.

formatNOK() gives you "1 234 kr" locale-correct,
Inter font family with letter-spacing — RESPECT.
```

### Streamlit:

```
I got st.tabs() — six tabs across the top,
"1. Oppsett", "2. Selskap" — simple, won't stop.
st.columns(2) gives me my two-column grid,
st.metric() shows computed values — here's what I did:

f"{driftsresultat:,} kr".replace(",", " ")
Yeah I FORMAT CURRENCY WITH STRING REPLACE, what of it?
st.expander() for the optional stuff,
st.spinner() when it loads — smooth enough.

I got st.success(), st.error(), st.warning() built in,
No CSS file needed — Streamlit handles the skin.
Sure it looks... Streamlit-y. Generic. Plain.
But users fill forms, not admire the frame.
```

**SCORE: SvelteKit 9/10 | Streamlit 6/10**

SvelteKit's custom Scandinavian design system with fjord blues and aurora greens is genuinely beautiful. The sidebar navigation gives spatial orientation. Streamlit looks like... Streamlit. Functional but generic. That `.replace(",", " ")` currency formatting vs `formatNOK()` with `Intl.NumberFormat` tells you everything.

---

## ROUND 4: DEVELOPER EXPERIENCE

### SvelteKit:

```
TypeScript catching errors at compile time,
API layer abstracted — every fetch is mine.
Change a field in the interface, errors cascade,
Refactoring's a breeze, not a hand grenade.

Component reuse? Each page is self-contained,
Vite HMR — hot reload, nothing drained.
But yeah... 16 source files across nested folders,
package.json, tsconfig, svelte.config shoulders.
```

### Streamlit:

```
ONE. FILE. Let that sink in, developer.
1,175 lines and I'm the WHOLE endeavor.
Want to understand the app? Read top to bottom,
No jumping between files — I ain't got 'em.

bygg_regnskap() builds the whole model inline,
lagre_config() dumps to YAML — design sublime.
New dev onboarding? "Read ui.py." That's it.
No framework knowledge needed, no TypeScript permit.

But... I'll admit... lines 880 through 990?
That bygg_regnskap() function is a CATHEDRAL of dreams.
110 lines of nested dataclass construction,
Copy-pasted twice for current and previous — no deduction.

And lagre_config()? 125 lines of dict building,
Mirror image of the loading code — yeah, it's chilling.
Change a field? Update it in FOUR places minimum:
_DEFAULTS, load, save, and the form — that's the rhythm.
```

**SCORE: SvelteKit 8/10 | Streamlit 6/10**

SvelteKit wins on maintainability. Streamlit wins on "I can read it all right now." But that Streamlit file has BRUTAL duplication — the same field mappings appear in `_DEFAULTS`, config loading (lines 108-206), `lagre_config()` (lines 209-336), `bygg_regnskap()` (lines 880-990), and the shareholder list building (repeated in both fane_dokumenter and fane_send). Change one field name and you're updating 5+ locations.

---

## ROUND 5: FEATURES & FUNCTIONALITY

### SvelteKit:

```
Six routes, each page focused and lean,
Shareholders? Dynamic add/remove, smooth and clean.
Document generation with inline preview,
Download buttons with proper MIME review.

Connection testing, system registration flow,
Status indicators — green dot means go.
API proxy through hooks.server.ts,
Backend separation — architectural finesse.
```

### Streamlit:

```
I do EVERYTHING you do, and I do it NOW.
Same six steps, same workflow, same plow.
But I got something you DON'T have, Kit —
I build the ACTUAL domain models, legit.

bygg_regnskap() creates real Aarsregnskap objects,
Selskap, Resultatregnskap, Balanse — the PROJECTS.
I call sm_modul.generer() DIRECTLY from the UI,
No API middleman, no proxy, no lie.

ar_modul.valider() checks my work inline,
auth.login() tests the connection fine.
I import the ACTUAL Python modules and run them,
Your API layer? Just an extra abstraction, son.
```

**SCORE: SvelteKit 7/10 | Streamlit 8/10**

Plot twist. Streamlit directly imports and uses the domain models (`Aarsregnskap`, `Selskap`, etc.) and calls the actual business logic modules. SvelteKit talks to a separate API backend. For a tool THIS domain-specific, Streamlit's direct integration is genuinely powerful — zero serialization overhead, real validation, real model construction.

---

## ROUND 6: DEPLOYMENT & OPERATIONS

### SvelteKit:

```
I need Node.js runtime, a build step first,
adapter-node outputs to build/ — well-rehearsed.
But then you ALSO need the Python backend running,
Two processes, two runtimes — double cunning.

Docker? Two containers or one fat image,
Environment variables for API_URL — the lineage.
More infrastructure, more moving parts,
But I scale horizontally — that's the art.
```

### Streamlit:

```
pip install wenche[ui] — DONE.
wenche ui — and I'm spun.
One process, one runtime, one port,
Python all the way — the simplest sort.

No Node. No npm. No build.
Just Python and the dream I've fulfilled.
Your grandma could deploy me (almost),
I'm the path of least resistance — the most.
```

**SCORE: SvelteKit 5/10 | Streamlit 9/10**

For a Norwegian holding company tool used by small enterprises, Streamlit's single-runtime deployment is a knockout. These users aren't running Kubernetes. They're running `pip install` on a laptop.

---

## FINAL SCOREBOARD

| Category              | SvelteKit | Streamlit |
|-----------------------|-----------|-----------|
| Architecture          | 8         | 7         |
| State Management      | 9         | 4         |
| User Experience       | 9         | 6         |
| Developer Experience  | 8         | 6         |
| Features              | 7         | 8         |
| Deployment            | 5         | 9         |
| **TOTAL**             | **46**    | **40**    |

---

## THE VERDICT

### SvelteKit wins on CRAFT. Streamlit wins on PRAGMATISM.

**SvelteKit** is the better-engineered UI. Full stop. It has:
- Type safety across the entire frontend
- A gorgeous custom design system
- Proper separation of concerns
- Reactive computed values that actually compile away
- A maintainable, scalable architecture

**Streamlit** is the better-FITTED UI for THIS project. It has:
- Direct access to domain models — no API layer needed
- Zero additional runtime dependencies beyond Python
- One-command deployment
- A single file a domain expert can read top-to-bottom
- Battle-tested widgets that just work for forms

### The real talk:

SvelteKit is what you BUILD when you want Wenche to feel like a product.
Streamlit is what you SHIP when you want Wenche to solve a problem tomorrow.

SvelteKit is the architect's blueprint.
Streamlit is the carpenter's hammer.

**If Wenche stays a power-user tool for accountants**: Streamlit. Ship it. The `session_state` jank doesn't matter when the user submits one tax return per year.

**If Wenche grows into a multi-user SaaS product**: SvelteKit. That architecture will carry you. Streamlit's 1,175-line monolith will collapse under its own weight.

---

*mic drop*

*DJ plays "Fjord-side" by Notorious B.R.G.*
