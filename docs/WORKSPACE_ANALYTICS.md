# Professional workspace and DSA analytics

## Coding workspace

The problem workspace supports a resizable statement/editor split, Monaco with a textarea fallback, C/C++/Java/Python templates, custom input cases, optional expected-output comparison, per-case status/runtime/memory/diagnostic display, and a separate full-suite Submit operation. Ctrl/Cmd+Enter runs the custom cases in a problem workspace and the single program runner in the scratchpad.

Drafts are stored in browser local storage for guests. Signed-in learners also sync drafts to the backend after a debounce. Drafts are scoped by user, problem, language and execution mode. When code changes, the previous code/stdin pair becomes a restorable version; the API retains at most 30 snapshots per draft. Custom testcase rows are per-run and are not yet included in draft snapshots.

Function-style execution is currently available for four original problems: Running Sum, Maximum Pair Sum, Binary Search Index and Missing Number. Each has explicit function signatures and runner wrappers in C, C++, Java and Python. The server adds the trusted input decoder/output wrapper, so users submit only the solution function/class. Other problems remain in standard input/output mode until their signatures and wrappers are implemented and tested.

Custom inputs belong to the current learner. A provided expected output is compared by Judge0. A blank expected output means execution-only and has no pass/fail assertion. Custom test runs never mark the problem solved. Only a complete pass of the platform-owned private suite can return AlgoForge Accepted and update solved progress. Hidden problem tests are never returned to the browser.

## Analytics definitions

- **Total Active Days:** number of distinct activity dates with one or more recorded completions.
- **Contributions:** sum of recorded problem completions across activity dates. External problem completions can be self-reported and are therefore not always verified by an external judge.
- **Pattern / Topic Mastery:** solved questions divided by all catalogue questions tagged with that pattern or topic, expressed as a percentage.
- **Weak Patterns / Weak Topics:** only categories with at least one attempt and less than 60% mastery are flagged. Untouched categories are not labelled weak.
- **Weekly Report:** per-day recorded completions for the last seven calendar dates in the learner's configured timezone, plus a comparison with the previous seven dates.
- **Consistency:** active dates in the last 7 and 14 days, 14-day active rate and recent completions.
- **Recommendations:** unsolved questions are ranked toward weak patterns first and easier levels before harder levels.
- **Learning Projection:** remaining catalogue items divided by the average daily recorded completions over the last 14 days. This is a simple trend estimate, may include self-reported completions, and is not a guarantee.

The analytics API is authenticated and derives all metrics from saved first-party progress/activity rows. It does not use seeded sample statistics.
