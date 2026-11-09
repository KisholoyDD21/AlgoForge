# AlgoForge 0.5.0 — UI refresh and theme QA

## First-load design decisions

The old first screen leaned on a generic gradient/dashboard treatment. The refreshed landing page leads with a precise product promise, uses a typography-led split layout, and labels the right-hand editor as an illustrative workspace preview. The page then explains the practice loop, core product capabilities and a three-step learning method. Motion and decoration are deliberately restrained so the content—not effects—does the work.

## Theme bug found and fixed

The browser script declared `init()` but did not invoke it. The static HTML could therefore appear while SPA routing and delegated click/input handlers had never been attached. This also meant theme switching could look present without actually being wired to the app. The script now invokes `init()` after DOM readiness, or immediately when the DOM is already ready.

Theme state is applied centrally. The saved preference is read before the first route render. Switching updates:

- `document.body` theme class and inline base colours;
- `document.documentElement.dataset.theme` and the CSS custom-property palette;
- toggle visible label, icon, title, accessible name and `aria-pressed`;
- `<meta name="theme-color">` for browser chrome;
- Monaco's `vs` / `vs-dark` theme when the editor is mounted.

The theme choice is stored under `algoforge-theme` and remains active across route renders. Light mode received explicit palette/component overrides for major navigation, card, form, table, editor, discussion, toast and notice surfaces.

## Cookie notice

This build only uses an essential session cookie and does not enable optional analytics. The notice now says exactly that, links to the privacy page, and sits in document flow rather than floating over the landing content. This is a disclosure/acknowledgement, not a consent mechanism for optional tracking.

## Browser smoke-test scope

Tested using Chromium against the actual shipped HTML, CSS and JavaScript with the `/api/me` endpoint stubbed to return a guest session:

1. initial landing page renders after SPA bootstrap;
2. dark → light updates background, heading contrast, icon, label and `aria-pressed`;
3. light mode remains active after navigating to the sign-in page;
4. light → dark works and dark mode remains after returning to the landing page;
5. at 390px viewport width, document scroll width does not exceed the viewport;
6. no browser page errors were emitted.

The screenshots in this folder are browser captures of the actual frontend. API-backed application pages and live production browser behaviour still require validation against a running deployed service.
