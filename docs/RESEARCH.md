# AlgoForge research dossier

**Last reviewed:** 3 November 2026  
**Purpose:** Translate established DSA practice, competitive programming, online-judge, security and web-product patterns into evidence-based product decisions.

This is applied product research, not a formal usability study, legal opinion, penetration test or exhaustive competitive audit. Platform features and terms change; recheck primary sources before each import or production release.

## 1. Comparative product review

| Platform / resource | Evidence-backed capability or model | Product lesson | AlgoForge decision |
|---|---|---|---|
| LeetCode | Official help describes editable custom test cases, Run Code feedback, a separate Submit action, judge evaluation and submission history. | Keep experimentation distinct from judged submissions. | Separate Run Custom Tests and Submit; store submissions and verdicts. |
| Codeforces | Official API exposes `problemset.problems` and returns problem objects plus statistics; API documentation specifies a maximum of one request per two seconds. | Use an official, rate-limited metadata source and retain canonical IDs/URLs. | Metadata-only importer with request pacing and deduplication. |
| CodeChef | Problem-setting guidance expects a clear statement, solution, test inputs/outputs and an approach write-up; setting is reviewed and tested. | A problem is more than a title and statement; it needs validated test design and reference reasoning. | Original problem authoring checklist and private test-suite workflow. |
| AtCoder | Public contest/problem archive supports contest-led practice and progression. | Preserve contest provenance and source links. | AtCoder is a discovery source; no unofficial account sync is claimed. |
| CSES | Topic-organised problem set supports systematic algorithm study. | Topic progression is valuable alongside difficulty. | Topic and pattern roadmaps. |
| HackerRank | Skills, language practice and assessment-oriented experiences. | Language choice and structured practice paths reduce friction. | Multi-language playground and roadmap views. |
| GeeksforGeeks | Topic-oriented explanations and practice catalogue. | Explanations and taxonomy complement problem solving. | Pattern explainers and curated links; no article mirroring. |
| NeetCode / Striver community sheets | Pattern-led interview-preparation lists are useful discovery and sequencing aids. | A deliberate sequence is more useful than an unstructured 500-item list. | Pattern-first roadmaps with provenance review. |

### Primary references

- LeetCode Help Center, *Start your Coding Practice*: https://support.leetcode.com/hc/en-us/articles/360012016874-Start-your-Coding-Practice
- LeetCode Terms of Service: https://leetcode.com/terms/
- Codeforces API help: https://codeforces.com/apiHelp/
- Codeforces problemset API method: https://codeforces.com/apiHelp/methods
- CodeChef problem-setting guidelines: https://www.codechef.com/problemsetting/
- CodeChef problem setter FAQ: https://www.codechef.com/wiki/faq-problem-setters
- CSES Problem Set: https://cses.fi/problemset/
- AtCoder Problems: https://atcoder.jp/
- HackerRank preparation: https://www.hackerrank.com/interview/preparation-kits
- NeetCode roadmap: https://neetcode.io/roadmap
- TheAlgorithms organisation: https://github.com/TheAlgorithms
- cp-algorithms: https://github.com/cp-algorithms/cp-algorithms

## 2. Online judge architecture

Judge0 CE documents a modular online execution API, sandboxed compilation/execution, multi-file submissions, execution constraints, detailed results and optional API authentication. Its documented CE version is v1.13.1; version, release cadence, image provenance and known vulnerabilities must be checked again at deployment time.

References:
- https://ce.judge0.com/
- https://ce.judge0.com/docs
- https://github.com/judge0/judge0

**Design decision:** the FastAPI service coordinates submissions; it does not invoke compilers or run user code in-process. The Judge0 service is a separate trust boundary. Production requires dedicated authenticated HTTPS judge infrastructure, resource isolation, egress restrictions, queue limits, telemetry and adversarial testing.

## 3. Content provenance and reuse

LeetCode's terms identify questions and solutions as platform content and prohibit crawling/scraping/spidering. A public GitHub repository does not automatically grant permission to republish the problem statements, examples, editorials or judge data it references. Codeforces' API is a documented metadata channel; the importer should remain within published limits and keep canonical source links.

References:
- https://leetcode.com/terms/
- https://codeforces.com/apiHelp/
- https://codeforces.com/apiHelp/methods
- https://github.com/cp-algorithms/cp-algorithms (CC BY-SA 4.0; attribution/share-alike obligations apply to adapted content)
- https://github.com/TheAlgorithms (review each repository and file licence before reuse)

**Content model:**

1. External discovery records: title, platform, canonical URL, permitted metadata, local tags and provenance.
2. AlgoForge-original records: original statement, examples, constraints, reference solution, generator/validator and owned hidden tests.
3. Licensed imports: only after recording exact source, licence, required attribution, version/hash and redistribution permissions.

Do not describe external links as natively judged or verified solves unless an authorised integration actually confirms them.

## 4. Security and assurance baseline

OWASP ASVS 5.0.0 is a suitable requirements catalogue for planning and verifying application security controls. It is a verification framework, not a certificate automatically obtained by passing a project test suite. AlgoForge should select and document an appropriate verification scope before a public launch.

References:
- OWASP ASVS 5.0.0: https://asvs.owasp.org/
- ASVS release/downloads: https://asvs.owasp.org/downloads/
- OWASP Developer Guide — ASVS: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/

Required areas include architecture/threat modelling, authentication, session handling, access control, input validation, output encoding, cryptography/secrets, file handling, API security, logging and operational configuration. The judge boundary requires separate threat modelling because it processes hostile user programs.

## 5. Accessibility and product quality

W3C recommends using the latest WCAG version; WCAG 2.2 adds criteria beyond WCAG 2.1 and is an appropriate target for keyboard access, focus visibility, target size, accessible authentication and responsive interaction.

Reference: https://www.w3.org/WAI/standards-guidelines/wcag/

For a coding workspace, accessibility checks should cover keyboard-only editor navigation, focus order, visible focus, non-colour verdict cues, screen-reader labels, reduced motion and zoom/reflow behavior. Automated checks should be combined with manual assistive-technology review.

## 6. Performance and production operation

Next.js' production checklist (used here as a general web-product reference, not a requirement to migrate frameworks) recommends production builds, error handling, safe data access, metadata, accessibility, security checks, Core Web Vitals review and bundle analysis.

Reference: https://nextjs.org/docs/pages/guides/production-checklist

AlgoForge should measure real deployment performance rather than publish invented scores. Record Lighthouse runs and field Core Web Vitals after a production host exists. Use LCP, INP and CLS as user-experience measures; test slow networks and lower-powered devices.

## 7. Product requirements derived from research

| Requirement | Acceptance evidence |
|---|---|
| Run and Submit are distinct | Run custom inputs cannot award an Accepted verdict; only a full private suite can. |
| Source provenance | Every external record has platform, canonical URL and import source. |
| Licence-aware import | Every redistributed statement/solution/test has explicit permission and attribution metadata. |
| Trusted judging | Candidate code runs outside the API process in a restricted execution environment. |
| Hidden-test confidentiality | Hidden inputs/outputs are never returned to client responses or logs. |
| Complexity honesty | Static complexity is labelled an estimate; measured runtime/memory are separate. |
| Pattern-first learning | Every curated question has a primary pattern and topic taxonomy reviewed by a human. |
| Measurable analytics | Active days and contributions derive from persisted events with explicit definitions. |
| Security assurance | A versioned ASVS verification plan and evidence register are maintained. |
| Accessibility | WCAG 2.2-oriented automated and manual test results are recorded. |
| Production reliability | Backups, restore drills, monitoring, incident/rollback plans and load tests are completed. |

## 8. Limitations and open research

- Platform feature comparisons are selective and based on public product documentation, not controlled side-by-side usability tests.
- Difficulty labels differ by platform; AlgoForge's rating buckets are local heuristics.
- The initial 159 records are not a completed 500-question curated curriculum.
- Codeforces import coverage can skew toward Codeforces; a balanced 500-item curriculum needs manual curation across sources and provenance review.
- No public production deployment, independent security audit, accessibility conformance claim, load test or live Judge0 end-to-end test is represented by this dossier.
