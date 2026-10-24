# Windows app discovery — weekly random-sample report

A reproducible research pipeline for recently human-active public GitHub
repositories, with platform/framework classification, Windows technology detection
using **Microsoft Application Inspector**, a static GitHub Pages dashboard, and a
weekly PDF report emailed through Gmail.

By default each report is a **uniform random sample of 100 repositories** drawn from
every public repository with qualifying human issue/PR activity in the last 30 days,
as recorded by [GH Archive](https://www.gharchive.org/) (raw hourly files; **no
BigQuery**). GitHub GraphQL verifies and enriches each sampled repository.
Percentages carry **95% Wilson confidence intervals**. With n = 100 the worst-case
margin is about **±10 percentage points**; it cannot be tightened without a larger
sample (±5 points needs ≈385 complete scans). Windows-only metrics have much smaller
denominators and therefore much wider intervals.
No example or synthetic percentages are presented as collected findings.

## Read the report on GitHub

The [latest weekly report](reports/README.md) shows metrics, tables, and inline SVG
charts directly in the repository—no GitHub Pages visit required. It appears after
the first successful weekly run on the default branch with this feature enabled.
The interactive Pages dashboard remains available as an optional companion.

## Run locally (Windows x64)

Requirements: Python 3.11+, GitHub CLI (`gh`), and a GitHub login with public
repository API access. No Python packages or .NET SDK are required: the installer
uses Microsoft's self-contained Application Inspector release.

```powershell
gh auth login
python -m unittest discover -s tests -v
python -m discovery.pilot --limit 100 --install-inspector
python -m http.server 8000 --directory site --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Serve over HTTP rather than opening the HTML directly.
The collector writes the real report to `site\data\latest.json` (ignored by git).
The dashboard displays an explicit error until a report exists.

To populate the explorer's **Analysis** column, run this after collection and before
serving or publishing the dashboard:

```powershell
$env:OPENAI_API_KEY = "<your API key>"
$env:OPENAI_MODEL = "gpt-4o"
python -m discovery.analysis
```

This uses the paid OpenAI API (standard library only), not a ChatGPT subscription.
The weekly workflow runs this step automatically: configure an `OPENAI_API_KEY`
Actions secret and optionally an `OPENAI_MODEL` repository variable (default
`gpt-4o`, must support structured JSON outputs). Never commit the API key.
Missing configuration fails the step explicitly. Individual repository/API failures
are logged and shown as unavailable analysis without changing scan results or metrics.
Existing reports show "Analysis not collected" until enriched; no insights are fabricated.
Use `--report PATH` to enrich another report in place.

The first run downloads Application Inspector **1.10.2** into `.tools\inspector`
and verifies the pinned Windows release's SHA-256. Later runs omit
`--install-inspector`. Alternatively, use `--inspector C:\path\ApplicationInspector.CLI.exe`.
The automatic installer is Windows x64 only; the collector can accept a compatible
manually installed executable on other systems.

For a fixed window and seed (GH Archive windows must start and end on whole UTC hours):

```powershell
python -m discovery.pilot --limit 100 --end 2026-10-18T12:00:00Z --seed weekly-2026-10-18
```

Other options: `--discovery auto|gharchive|graphql-search` (default `auto`),
`--confidence 0.95` (for example `0.99` for wider 99% intervals), `--archive-workers 6`,
and `--archive-reserve 300` (randomly ordered replacements for deleted/private repositories).
Per-hour archive reductions are cached in `.cache\gharchive` for reruns with the same seed.

To build the PDF and (optionally) email it:

```powershell
python -m discovery.report_pdf --output site\report.pdf
$env:GMAIL_ADDRESS = "you@gmail.com"; $env:GMAIL_APP_PASSWORD = "<app password>"
python -m discovery.send_email --report site\data\latest.json --pdf site\report.pdf
```

Add `--archive-dir report-history` to also keep a copy named after the report's
generation date in UTC (for example `report-history\report-2026-10-19.pdf`). The weekly
workflow does this and commits each PDF to [`report-history/`](report-history/README.md),
so historical reports are kept and tracked alongside the latest one.

PDF rendering uses headless Chrome, Chromium, or Edge (set `PDF_BROWSER` to override).

To generate the repository-readable report and charts from the same collected data
(standard library only):

```powershell
python -m discovery.report_markdown
```

This writes `reports/README.md` and seven SVG charts. It refuses reports with no
complete scans. It does not collect new data or commit files itself.

Run the real-tool contract tests after installation:

```powershell
$env:INSPECTOR_PATH = (Get-ChildItem .tools\inspector -Filter ApplicationInspector.CLI.exe -Recurse | Select-Object -First 1).FullName
python -m unittest discover -s tests -v
node --check site\app.js
node --test tests\frontend.test.cjs
```

Without `INSPECTOR_PATH`, the real-tool tests explicitly skip; unit tests still run.

To recheck exactly the selected cohort in an existing report after a policy change:

```powershell
python -m discovery.pilot --rerun-report site\data\latest.json
```

This preserves the original activity window and discovery evidence rather than
replacing failed repositories with a new cohort. Previously recorded commit SHAs
are reused; records without a SHA (such as earlier failures) use the current default
branch. Public visibility is rechecked. `--limit` applies only to fresh discovery;
`--end` cannot be combined with `--rerun-report`.

## Discovery and activity

### Default: GH Archive random sample (no BigQuery)

- The window is the 720 whole UTC hours ending three hours before the run
  (GH Archive publishes each hour shortly after it closes).
- Every hourly file `https://data.gharchive.org/YYYY-MM-DD-H.json.gz` is streamed and
  reduced in parallel worker processes (about 15 minutes for 30 days).
- Qualifying events: `IssuesEvent` and `PullRequestEvent` with action `opened`/`reopened`,
  `IssueCommentEvent` `created` (issue and PR conversation comments),
  `PullRequestReviewEvent` `created`, and `PullRequestReviewCommentEvent` `created`.
  Events must be public. Actor logins ending in `[bot]` or matching bot-name patterns
  are excluded; GH Archive has no account type, so ordinary User accounts can still automate.
- The **population** is every repository ID with at least one qualifying event. Its size
  is reported. Each repository receives the key `sha256(seed:repository_id)`; the
  smallest keys form a uniform random sample without replacement (bottom-k sampling).
  Per-hour bottom-k sets merge exactly, so the sampled repositories' latest event,
  event count, and activity types are exact for the window.
- The seed defaults to the window end timestamp, so each run is reproducible.
- Sampled repositories are verified through GraphQL in random order. Renamed or transferred
  repositories are followed through their numeric ID (`GET /repositories/{id}`).
  Deleted, private, or blocked repositories are ineligible and replaced by the next random
  draw (recorded under `coverage.excluded_after_sampling`). Partial and failed scans are
  **kept** in the sample as nonresponse rather than replaced by easier repositories.
- If more than 5% of archive hours are missing or unreadable, `--discovery auto` falls
  back to bounded GraphQL search (below). That report is labeled non-representative,
  records `coverage.fallback_reason`, and shows no confidence intervals.
- Unlike the GraphQL method, archive discovery includes reopenings and inline PR
  review comments, and is not limited to the last 20 comments/reviews per item.

### Fallback: bounded GraphQL search
- Each report fixes an exclusive UTC end and an inclusive start exactly 30 days earlier.
- Two GraphQL searches select recently updated public issues and PRs, separately.
  Each examines at most `min(2 × limit, 500)` items; `limit` is 1–100.
- A repository qualifies only through an observed opening, conversation comment,
  or submitted PR review inside that window by a GitHub `User` actor not matching
  selected bot names. Unknown/Bot actors do not qualify. Ordinary User accounts
  can still automate, so “human” is an approximation.
- Each issue/PR contributes its opening and last 20 comments, plus last 20 reviews
  for PRs. Truncated connections and bounded searches are reported.
- Repositories are deduplicated by GitHub ID, then ranked by latest **observed**
  qualifying activity. At most `limit` repositories are selected; failures are
  retained, not replaced with easier-to-scan repositories.
- Closing/reopening events, pushes, releases, discussions, and inline review comments
  are outside this pilot. `updatedAt` selects candidates but never proves human activity.
- This favors recently updated discussion/PR activity. It is neither random nor
  guaranteed exhaustive. Counts are not extrapolated to all of GitHub.
- Forks and archived repositories are retained and labeled. Issue activity alone
  does not establish recent code development.

Search/enrichment use `gh api graphql`; repository metadata and languages are fetched
through GraphQL. Source archives use GitHub's public codeload endpoint. Oversized
archives fall back to GitHub's REST Git tree endpoint, then batched GraphQL blob reads.
Truncated, binary-marked, replacement-decoded, or byte-size-mismatched text responses
use pinned public raw source URLs instead; byte loss is not accepted.
Primary language
comes from GitHub; all fetched language-byte counts are retained in JSON, but headline
language charts use one primary language per complete repository. Truncated language
connections are recorded.

## Classification and Windows analysis

Versioned rules in [discovery/rules.py](discovery/rules.py) inspect project targets,
dependency declarations, directory structure, and source patterns. Platforms and
frameworks are **multi-label**; C# or C++ alone never implies Windows.
`Unknown` is retained when evidence is absent.

The broader **Target platforms & environments** taxonomy includes OS targets,
Web, server/backend, containers/Kubernetes, cloud infrastructure, smart contracts,
embedded firmware, WebAssembly, and evidenced Python/Node.js/.NET/JVM/PHP/native/shell
environments. Runtime and deployment indicators are file-scoped where appropriate.
These categories **do not establish OS compatibility**. Unknown means neither OS
nor environment evidence was detected, not proof that the repository is unsupported.

**Dashboard distributions are mutually exclusive and sum to 100%.** They are
calculated **only from complete scans** (partial, failed, and no-eligible-source
repositories are excluded). Each repository is assigned one category:

| Chart | Primary assignment |
|---|---|
| Target platform | One OS target → that OS; several → `Multiple OS (incl. Windows)` / `Multiple OS (no Windows)`; otherwise the first environment in Embedded → Smart contracts → WebAssembly → Web → Server/backend → Cloud/infra → Containers → .NET → JVM → Native → Python → PHP → Node.js → Shell; otherwise Unknown |
| Primary programming language | GitHub's primary language |
| Framework evidence | Most specific framework (Windows desktop → MAUI/Avalonia/Flutter/Electron/React Native/Qt → meta-frameworks before UI libraries → backends); otherwise `No framework detected` |

Percentages use largest-remainder rounding to 0.01% so each chart totals exactly
100%. `Windows` + `Multiple OS (incl. Windows)` equals the Windows candidates
tile. All detected signals remain in the repository table and CSV.

Windows candidates are passed to **Microsoft Application Inspector**, using generated
custom rules from the same versioned taxonomy; bundled Inspector rules are disabled
to keep the measured categories stable. The report records the tool version,
ruleset version, source commit, scan time, exclusions, and file/line evidence.
No cloned source is built or executed.

Windows application types include WinForms, WPF, WinUI/Windows App SDK, UWP,
cross-platform frameworks, Windows services, native/Win32 indicators, and unresolved
console/other. “Desktop” is an umbrella, not a category competing with WinForms.
The native indicator does not prove a graphical application.

An explicit application indicator (e.g. `.NET OutputType`, native executable project,
Android application plugin, web SDK, or Electron main entry) is required for the Windows
application denominator. This intentionally conservative pilot misses some applications,
including some CMake, Rust, Flutter, MAUI, and legacy project layouts. Libraries
and unknown repository purposes are visible but excluded from that denominator.

Repository summaries retain all signals, while `projects` records project-scoped,
**multi-label** findings. A repository can contain a Windows Forms desktop project,
a Windows service, and PowerShell installation scripts without collapsing them into
one application type. The dashboard's expandable **Project findings** shows labels,
qualitative confidence, and supporting file/line links pinned to the scanned commit.
Project paths and labels are searchable; the CSV includes the full `projects` array
as a JSON cell, and the JSON report preserves the structured findings.

Literal MSBuild XML metadata is inspected without evaluating conditions, imports,
or build tasks. Conditional settings remain lower-confidence evidence. Sources
without a unique nearest project, including shared build properties, remain
explicit shared/ambiguous/unassigned entries rather than being copied to every
project.

For supplemental refinement, pass `--semgrep PATH` pointing to a compatible,
locally installed Semgrep executable. Semgrep is optional and is never downloaded
automatically; the default collector still needs no Python packages. Only bundled
local rules are used, with metrics and version checks disabled; repository rule
configuration is not executed. Language-aware C# rules refine Forms inheritance,
service-host calls, and PowerShell host creation; generic text indicators remain
lower confidence. Supplemental engine status and failures are recorded
separately and shown in the dashboard, without replacing Application Inspector or
turning its successful scan into a failure. Engine identity and rule configuration
participate in cache selection.

PowerShell scripts and modules do **not** imply Windows compatibility. Installation
and service-management scripts are distinct from evidence of a PowerShell-backed
service: managing a service does not prove that PowerShell implements it.

Classification confidence describes the strength of static evidence, **not** a
measured probability or the statistical confidence intervals used in charts.
Project association is not a resolved dependency graph. Regex matching can match
comments, strings, unused declarations, or conditional code. Dependencies do not
establish runtime API use; precision/recall have not been benchmarked. The pilot
rules are indicators, not authoritative compatibility assertions.

## Metric definitions

| Metric | Denominator |
|---|---|
| Platform/framework prevalence | All complete source scans |
| OS-target distribution | All complete source scans; runtime-only evidence remains OS Unspecified |
| Primary-language distribution | All complete source scans |
| Project application and automation types | Complete repository scans with collected `projects` inventories; each repository counts once per category across all its projects |
| Windows application types | Complete Windows scans with explicit application evidence |
| Windows component adoption | Same eligible Windows application repositories |
| Exploratory Windows-candidate component adoption | All complete Windows-targeting scans, including libraries/unknown purposes |

For component `c`: `100 × repositories detecting c / eligible Windows applications`.
Each repository contributes one binary detection indicator per component, regardless
of repository size or number of matches. This equals the average per-repository
indicator. Win32 and COM overlap; percentages need not sum to 100%.
No eligible repositories produces `null` / **N/A**, not 0%.
These figures are not source-line shares or runtime-call percentages.

The **Project application and automation types** table and chart use the newly
collected project findings rather than the narrower Windows application denominator.
They show measured shares for Windows desktop app, Windows Forms app, WPF app,
WinUI app, UWP app, Windows service, PowerShell, and other detected categories.
Windows desktop app is an umbrella for the four Windows UI frameworks, not proof
that a project is executable. PowerShell includes scripts, modules, and hosting
indicators and does not imply Windows. Categories overlap and need not total 100%;
multiple matching projects in one repository still contribute only one count per
category. Partial/failed scans and older records without `projects` are excluded;
inventories with no recognized type remain in the denominator as unknown.
Source-based application types also include web frontends, backend/API services,
command-line tools, executable applications, libraries/SDKs, Python applications/scripts,
shell/batch automation, build automation, infrastructure as code, container/orchestration
configuration, notebooks, mobile and macOS applications, native desktop applications,
embedded firmware, and smart contracts. These require matching source patterns or
literal project metadata; an OS target or programming language alone is not a type.
All observed types appear in the same table, with no percentage cutoff or **Others**
grouping. A separate coverage note counts repositories with insufficient evidence;
they remain in the denominator but are not assigned a type. New types require
recollection with ruleset `pilot-5`; historical inventories cannot be reclassified
from platform labels alone. Existing source exclusions still apply, including
`.github`, tests, generated files, and dependencies.
The report displays counts, denominator, measured percentage, and sampling intervals
when representative, using the same table/chart style as existing distributions.
Example percentages are never substituted for collected results.
The separately labeled exploratory Windows-candidate chart is not an application
distribution and must not be substituted for the application-level headline metric.

Partial and failed scans are excluded from headline distributions and displayed
as separate dashboard counts. Repositories with a fully examined inventory but no
eligible source use `not_applicable`; they are **not** counted as complete code scans,
failed operations, or included in the source-distribution denominator.
If all eligible source was omitted due to a budget or encoding problem, the scan
remains partial instead of becoming not applicable.

For random samples every distribution row also has `ci_low`/`ci_high`: the Wilson score
interval at `--confidence` (default 95%) for `count / denominator`.
`metrics.margin_of_error` is the worst-case (p = 50%) normal-approximation margin for the
complete-scan denominator. Intervals describe sampling error only, not classification
error or nonresponse bias from partial/failed scans. The population is in the millions,
so no finite-population correction is applied. GraphQL-fallback reports set these to `null`.
The explorer shows only Windows candidates (complete scans with a Windows platform
signal), matching the Windows candidates tile, including source-retrieval method,
Inspector incompleteness, and exclusion counts. Search and scan-status filters apply
within that subset.
The **Analysis** column explains the problems solved and summarizes community feedback
using OpenAI-generated text with source links. Counts are issues opened during the
report's existing UTC window, excluding pull requests (bot-created issues are included
in this count). Feedback uses only human issue openings/comments in that same window,
from a bounded sample of up to 10 most recently updated issues and the last 10 comments
per issue; bots and out-of-window comments are excluded. Issues updated after the window
can still contain eligible comments, so the search has no upper update-time bound.
Recent activity can push relevant older issues/comments outside this sample, especially
when enriching old reports. Issue count alone is never treated as sentiment or popularity;
absent feedback is reported as insufficient evidence.

Only currently public repositories are analyzed. Public description, README at the
scanned SHA, and issue/comment excerpts are sent to OpenAI: README up to 8,000 characters,
issue excerpts up to 800, comments up to 400. Descriptions and issue bodies reflect
their retrieved versions, not historical window snapshots. The report publishes summary,
counts, source URLs, model/time, and sampling limitations, not raw excerpts.
AI claims should be checked against sources; the response schema restricts citations
to collected source IDs, and community citations to in-window human issue/comment
sources. Citations are also validated before publication, but this does not prove
every generated claim. API usage incurs model costs.
Existing scan diagnostics and evidence remain available in a collapsed **Scan / evidence**
section in each Analysis cell. Other dashboard charts and sampling metrics are unchanged.
JSON downloads contain the full report; CSV contains repository-level classifications,
project findings with evidence and confidence, AI analysis, and source-retrieval information for
all selected repositories.

## Bounds, safety, and persistence

- Compressed source download: 150 MiB; eligible source input: 256 MiB / 20,000 files.
  If the compressed download exceeds its limit, retrieve the pinned Git tree and
  fetch only eligible source files using GraphQL batches of at most 40 blobs and
  4 MiB of expected content per batch (a single larger file may exceed the batch
  byte target but not the per-file limit). Selective retrieval is capped at 10,000
  files / 256 MiB of input and prioritizes manifests.
  Truncated Git trees and omitted files due to retrieval limits make a scan partial,
  never complete. Other download errors are not silently retried through this fallback.
- Files: supported source extensions only, up to 8 MiB each. Accept UTF-8, BOM-marked
  UTF-16/UTF-32, and recognizable BOM-less UTF-16. Normalize decoded text and line
  endings to UTF-8 for both classifiers. Unsupported encodings are counted explicitly;
  no lossy decoding or arbitrary single-byte encoding guesses are used. Skipped
  oversized or unsupported-encoding source makes a scan partial.
- Exclude tests, samples, examples, generated files, vendored/dependency directories,
  build outputs, documentation, datasets, and fixture directories. The exact
  directory/extension policy is in the rules module.
  A directory named `packages` is not automatically third-party: monorepo packages
  remain in scope. Known dependency caches such as `.nuget` and `node_modules` are excluded.
  HTML/CSS, shell/PowerShell, PHP, Terraform/Bicep, Solidity, and extensionless
  Dockerfile/Makefile build definitions are now included.
  JSON/JSONC is limited to named project/application manifests (e.g. package,
  composer, deno, tsconfig, appsettings); other JSON is classified as data assets.
  Text files are limited to CMakeLists and requirements files. Data assets do not
  contribute API evidence or make source scans partial merely due to their size.
  Complete means complete within this explicitly declared first-party source scope,
  not a scan of every repository byte; the narrower asset scope changes comparisons
  to earlier pilot policies.
  Lock files (such as `package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`) and known
  generated artifacts are excluded **before** file-size checks, so they do not make
  a repository partial merely because they are large. Oversized ordinary source
  remains an explicit partial-scan reason.
  Unsupported extensions and binary files are counted but considered out of scope.
- Unsafe archive/tree paths fail the scan. Symlinks and submodules are counted as
  out of scope and skipped without following their targets; a symlink alone no
  longer rejects an otherwise usable repository. Source is extracted into a temporary
  directory that is removed after analysis. Inspector does not crawl nested archives.
- Inspector processes every selected source file in batches of at most 100 files
  and 8 MiB (a single larger eligible file is retained). Batches preserve source
  bytes and relative paths, and merge findings and incompleteness counters.
  Each batch has 30-second per-file and 300-second processing budgets, with a
  330-second subprocess timeout. A valid but incomplete tool report preserves
  findings and marks the scan partial, with exact skipped/error/timeout counters.
  The tool's binary heuristic can reject valid non-ASCII text; these omissions
  remain partial, never silently converted to complete. Fatal tool failures remain
  failed operations. No source transformations are used to bypass tool filtering.
- Analysis cache keys include repository ID, commit SHA, rule version, and Inspector
  version. Windows caches also validate the Inspector batching strategy.
  Cached source evidence keeps its original scan time. Bump `RULESET_VERSION`
  whenever classification/measurement logic changes.
- Each run rechecks public visibility and current metadata before using its cache.
- GraphQL requests have bounded transient retries. Auth/discovery failures stop the run.
  Per-repository failures are recorded. A run with no complete scans fails and must
  not deploy. JSON is replaced atomically, never appended to partial output.

## GitHub Actions, Pages, PDF, and email (not enabled automatically)

[.github/workflows/test.yml](.github/workflows/test.yml) runs unit tests and JavaScript
syntax checks on pushes/PRs. [.github/workflows/weekly-report.yml](.github/workflows/weekly-report.yml)
runs **every Monday at 09:00 America/Los_Angeles** (PST in winter, PDT in summer;
uses the Actions schedule `timezone` key) or manually. It runs tests, installs
Inspector, draws the GH Archive sample, scans it, enriches Windows candidates with
OpenAI purpose/community analysis, renders `site/report.pdf`, keeps
the JSON and PDF as a 90-day artifact, commits the latest Markdown report and seven SVG
charts under `reports/`, optionally deploys Pages (the dashboard links the PDF), and
emails the PDF. Scheduled workflows run only from the default branch. Repository
publishing also runs only on the default branch; manual runs on other branches
keep generated reports as artifacts without committing them.

The publishing job alone has `contents: write`; collection remains read-only.
Repository rules must permit `github-actions[bot]` to push report updates to the
default branch. If direct pushes are prohibited, publishing fails visibly; the
generated report remains available as the `repository-report` Actions artifact.
PDF and JSON remain artifacts rather than adding binary files or raw reports to git.

Pages is optional: uncheck **pages** for a manual run, or set the repository Actions
variable `ENABLE_PAGES` to `false` for scheduled runs. Repository publishing and
email still work with Pages disabled. To use only repository reports, skip the
Pages setup below and run manually with **pages** and **email** unchecked; for
scheduled runs also configure Gmail if email delivery is wanted (scheduled email
remains enabled).

When you choose to deploy:

1. Push this implementation to the default branch.
2. In repository **Settings → Pages**, select **GitHub Actions** as the source.
3. Create a Gmail **app password** (Google Account → Security → 2-Step Verification
   must be on → App passwords).
4. Add repository secrets: `GMAIL_ADDRESS` (the sending Gmail account),
   `GMAIL_APP_PASSWORD`, optionally `REPORT_RECIPIENT` (defaults to `GMAIL_ADDRESS`),
   and recommended `DISCOVERY_TOKEN` (a fine-grained token with public read access).
5. Add the `OPENAI_API_KEY` repository secret for the Analysis column, and optionally
   set the `OPENAI_MODEL` repository variable (default `gpt-4o`).
6. Run **Weekly report** manually once (optionally with a small limit and email off).

The default workflow token allows only 1,000 GraphQL points/hour; `DISCOVERY_TOKEN`
raises that to the user limit. Credentials are only passed to the relevant collection,
analysis, and email steps, never embedded into the site, PDF, or logs. Do not grant scan jobs write
access to source repositories. If the Gmail secrets are missing, the email job fails
visibly after Pages has deployed.

The latest repository report is versioned in git; weekly artifacts expire after
90 days. Analysis cache is opportunistic and may be evicted. No separate historical
metric series is maintained. Raw source
archives are not published or committed.

## Next research milestones

1. Manually label a diverse cohort and measure precision/recall, including an audit
   of non-Windows predictions.
2. Add project-level application detection and broader framework/API fixtures.
3. Add incremental archive processing, coverage monitoring, and a historical metrics series.
4. Increase the sample (for example n ≈ 385 for ±5 points) once throughput is benchmarked.
