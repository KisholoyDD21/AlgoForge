# Research notes — AlgoForge

**Research date:** 30 October 2026  
**Scope:** DSA platform capabilities, problem metadata sources, execution architecture and content reuse.

## Findings

### Online judging

Judge0 is a purpose-built code execution system for online IDEs, education and competitive programming. Its documentation describes sandboxed compilation/execution, asynchronous submission tokens, detailed result fields, custom CPU/memory/time constraints and multiple-file execution. The official project currently describes self-hosted and managed deployment options and support for 90+ languages. AlgoForge uses Judge0 as a separate service and never executes user code inside the FastAPI web process.

Sources:
- https://ce.judge0.com/docs
- https://github.com/judge0/judge0

### Public problem metadata

The official Codeforces API exposes a `problemset.problems` method with problem metadata and a corresponding statistics array. The API documentation states a maximum request rate of one call per two seconds. The importer therefore makes a single API request and stores names, ratings, tags, solved-count metadata and canonical problem URLs only.

Sources:
- https://codeforces.com/apiHelp/methods?locale=en
- https://codeforces.com/apiHelp/

### Third-party content and rights

LeetCode's Terms of Service state that platform content includes questions and solutions and that its content is owned, controlled or licensed by LeetCode unless otherwise specified. The project therefore retains title/source/difficulty/pattern metadata and links to the original problem; it does not bulk-copy statements, editorials or hidden tests.

Source:
- https://leetcode.com/terms/

### Open algorithm-learning repositories

TheAlgorithms organisation publishes language-specific educational algorithm implementations, including Python, Java, C, C++ and TypeScript repositories. Those repositories are useful as algorithm-study references, but they are not a replacement for a verified 500-question problem bank.

The `cp-algorithms` organisation maintains algorithm and data-structure articles. Its repository page identifies the content repository's CC BY-SA 4.0 licence. Attribution and share-alike requirements must be retained if its text is adapted.

Sources:
- https://github.com/TheAlgorithms
- https://github.com/cp-algorithms/cp-algorithms

### Community-curated study sheets

Public repositories and trackers for Striver's A2Z sheet and NeetCode-style roadmaps provide useful discovery material and question links. Their presence on GitHub does not automatically grant rights to reproduce every original problem statement or solution. Before an import, each repository's current licence and provenance must be inspected.

Examples reviewed:
- https://github.com/Codensity30/Strivers-A2Z-DSA-Sheet
- https://github.com/geckguy/striver-a2z-sheet
- https://github.com/ThatDeparted2061/Striver-DSA-Resources

## AlgoForge implementation decisions

1. Use source-linked metadata rather than mirror third-party statements or private tests.
2. Maintain 19 original AlgoForge statements with 77 platform-owned sample/hidden tests as the initial genuinely judgeable track.
3. Use the Codeforces official API for a reproducible metadata-only importer toward a 500-record catalogue.
4. Use Judge0 as an independently deployed sandbox for C/C++/Java/Python; the app submits batch test cases and aggregates server-side verdicts.
5. Keep test inputs/expected outputs private; return execution output only for cases marked as samples.
6. Call runtime and memory data measured values, not Big-O proof. Complexity estimates remain low-confidence static heuristics.
7. Do not present a successful standalone playground run as an Accepted problem verdict.
8. Treat external platform completions as self-reported until an authorised integration verifies them.
9. Use scheduled contests only with AlgoForge-owned problems and server-enforced start/end and registration checks.

## Limitations

- Repository stars and activity change frequently and are not used as a permanent quality ranking.
- The importer can rank by Codeforces solved count and diversify tags, but “top” remains a product curation heuristic, not an objective universal ranking.
- Current runtime import depends on outbound network access to Codeforces.
- Third-party platform APIs and terms can change; recheck them before public release.
