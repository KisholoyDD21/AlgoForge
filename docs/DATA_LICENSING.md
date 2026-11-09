# Data and licensing policy

## What AlgoForge stores

The local curated list stores problem title, canonical link, platform name, difficulty, pattern/topic tags and a short authored note explaining that the source platform owns the statement. The Codeforces importer stores public problem metadata returned by the official API: contest identifier, index, name, rating, tags, solved-count-derived selection and canonical link.

## What AlgoForge deliberately does not mirror

- Third-party problem statements and constraints
- Sample input/output copied from third-party pages
- Editorial text and proprietary explanations
- Hidden test cases or judge data
- Platform source code, logos or protected trade dress
- User submissions from third-party accounts

This is an implementation safeguard, not a legal conclusion that every metadata field may always be reused. Operators should review source terms and applicable law before making a public or commercial deployment.

## Codeforces import

The importer uses the official API endpoint `https://codeforces.com/api/problemset.problems`. It keeps its request volume to one endpoint call, observes the API's published limit (one request per two seconds), and stores metadata with source links. Difficulty buckets are an application-side heuristic based on Codeforces rating:

- Easy: rating up to 1100
- Medium: rating 1101–1800
- Hard: rating above 1800

These labels are intended for AlgoForge filtering. They are not official statements of universal difficulty and may not be equivalent to LeetCode's labels.

## GitHub repository reuse

Check the current `LICENSE` file, owner, provenance and dependencies of each repository at the point of import. A repository's open/public visibility is not itself a licence. For CC BY-SA materials, retain attribution and comply with share-alike requirements. For MIT-licensed algorithm code, preserve required copyright and permission notices if any code is copied. This project currently links to learning references instead of bundling their files.

## User-submitted code

When configured with Judge0, AlgoForge sends user-submitted source code and stdin to that separate execution service. The app stores code and returned execution metadata for signed-in users' history. The operator must publish the actual data processor, retention, deletion and security details for the deployed Judge0 instance in the privacy policy.

## Legal review required

This file is engineering guidance, not legal advice. Obtain an appropriate legal review before public/commercial launch, especially for database rights, platform terms, third-party API use, user content, privacy, cookies and cross-border processing.
