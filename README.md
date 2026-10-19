# Windows app discovery — pilot

A bounded, reproducible research pipeline for recently human-active public GitHub
repositories, with platform/framework classification, Windows technology detection
using **Microsoft Application Inspector**, and a static GitHub Pages dashboard.

**This is not a census or representative sample of all public repositories.**
No example or synthetic percentages are presented as collected findings.

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

The first run downloads Application Inspector **1.10.2** into `.tools\inspector`
and verifies the pinned Windows release's SHA-256. Later runs omit
`--install-inspector`. Alternatively, use `--inspector C:\path\ApplicationInspector.CLI.exe`.
The automatic installer is Windows x64 only; the collector can accept a compatible
manually installed executable on other systems.

For a fixed window:

```powershell
python -m discovery.pilot --limit 100 --end 2026-10-18T12:00:00Z
```

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
These categories **do not establish OS compatibility**; an additional **OS targets
only** chart preserves `Unspecified` when no OS evidence exists. Unknown in the
broader chart means neither OS nor environment evidence was detected, not proof
that the repository is unsupported. This taxonomy change must be considered when
comparing Unknown percentages to older OS-centric reports.

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

Classification is **repository-level**, not a project dependency graph. Signals in
different projects in a monorepo can combine. Regex matching can also match comments,
strings, unused declarations, or conditional code. Dependencies do not establish
runtime API use; precision/recall have not been benchmarked. The pilot rules are
indicators, not authoritative compatibility assertions.

## Metric definitions

| Metric | Denominator |
|---|---|
| Platform/framework prevalence | All complete source scans |
| OS-target distribution | All complete source scans; runtime-only evidence remains OS Unspecified |
| Primary-language distribution | All complete source scans |
| Windows application types | Complete Windows scans with explicit application evidence |
| Windows component adoption | Same eligible Windows application repositories |
| Exploratory Windows-candidate component adoption | All complete Windows-targeting scans, including libraries/unknown purposes |

For component `c`: `100 × repositories detecting c / eligible Windows applications`.
Each repository contributes one binary detection indicator per component, regardless
of repository size or number of matches. This equals the average per-repository
indicator. Win32 and COM overlap; percentages need not sum to 100%.
No eligible repositories produces `null` / **N/A**, not 0%.
These figures are not source-line shares or runtime-call percentages.
The separately labeled exploratory Windows-candidate chart is not an application
distribution and must not be substituted for the application-level headline metric.

Partial and failed scans are excluded from headline distributions and displayed
as separate dashboard counts. Repositories with a fully examined inventory but no
eligible source use `not_applicable`; they are **not** counted as complete code scans,
failed operations, or included in the source-distribution denominator.
If all eligible source was omitted due to a budget or encoding problem, the scan
remains partial instead of becoming not applicable.
The explorer shows all selected repositories, including errors, source-retrieval
method, Inspector incompleteness, and exclusion counts.
JSON downloads contain the full report; CSV contains repository-level classifications
and source-retrieval information.

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

## GitHub Actions and Pages (not enabled automatically)

[.github/workflows/test.yml](.github/workflows/test.yml) runs unit tests and JavaScript
syntax checks on pushes/PRs. [.github/workflows/pilot.yml](.github/workflows/pilot.yml)
runs daily at 06:23 UTC or manually, installs Inspector, runs integration tests,
collects data, stores a diagnostic artifact, and deploys the static site on success.

When you choose to deploy:

1. Push this implementation.
2. In repository **Settings → Pages**, select **GitHub Actions** as the source.
3. Run **Collect pilot and publish Pages** manually, initially with a small limit.
4. Review coverage, failures, and classification evidence before increasing to 100.

The default workflow token is used for public GraphQL reads. Its rate limit is lower
than a normal user token. Optionally configure a least-privilege `DISCOVERY_TOKEN`
repository secret with public read access if the workflow hits limits. Credentials
are only passed to the collector, never embedded into the site. Do not grant scan
jobs write access to source repositories.

The daily report and 14-day diagnostic artifacts are persistent outputs; analysis
cache is opportunistic and may be evicted. This pilot does not retain a historical
metrics series. Raw source archives are not published or committed.

## Next research milestones

1. Manually label a diverse cohort and measure precision/recall, including an audit
   of non-Windows predictions.
2. Add project-level application detection and broader framework/API fixtures.
3. Add archive-backed discovery, incremental events, coverage monitoring, and history.
4. Benchmark throughput and cost before moving beyond the bounded pilot.
