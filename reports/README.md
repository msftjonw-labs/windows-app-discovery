# Windows app discovery — latest report

Activity window (UTC): 2026-09-29T21:58:34Z → 2026-10-29T21:58:34Z
Generated: 2026-10-29T21:58:47Z  
Ruleset: pilot-5; Application Inspector: 1.10.2

**Bounded, non-representative GraphQL cohort.** Percentages describe the analyzed cohort only; no confidence intervals are reported.

| Metric | Repositories |
| --- | ---: |
| Sampled | 1 |
| Complete scans | 1 |
| Partial | 0 |
| Failed | 0 |
| No eligible source | 0 |
| Windows candidates (subset of complete scans) | 0 |
| Windows applications (subset of complete scans) | 0 |

## Primary programming languages and their target platforms

GitHub's primary language per repository. The last column splits each language's repositories by primary target platform (an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last), so each language's platform shares add up to 100%.

Each repository belongs to one category; shares total 100% across the 1 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming languages and their target platforms](language_platforms.svg)

| Category | Count / denominator | Share | Target platform distribution |
| --- | ---: | ---: | --- |
| JavaScript | 1 / 1 | 100.0% | Web: 100.0% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 1 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share |
| --- | ---: | ---: |
| No framework detected | 1 / 1 | 100.0% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Types are identified from source patterns and project metadata, not inferred from OS or language. Repositories without sufficient type evidence remain in the denominator and are reported in the classification coverage note, not as application types. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share |
| --- | ---: | ---: |
| Command-line tool | 1 / 1 | 100.0% |
| Python application / script | 1 / 1 | 100.0% |
| Shell / batch automation | 1 / 1 | 100.0% |
| Web frontend | 1 / 1 | 100.0% |
| PowerShell | 0 / 1 | 0.0% |
| Service management | 0 / 1 | 0.0% |
| UWP app | 0 / 1 | 0.0% |
| WPF app | 0 / 1 | 0.0% |
| WinUI app | 0 / 1 | 0.0% |
| Windows Forms app | 0 / 1 | 0.0% |
| Windows desktop app | 0 / 1 | 0.0% |
| Windows service | 0 / 1 | 0.0% |

Classification coverage: 0 repositories have insufficient application-type evidence in the scanned source. They remain in the denominator but are not assigned an application type.

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

N/A — no eligible repositories.

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

N/A — no eligible repositories.

## Windows CI by primary language

Complete scans whose CI configuration (GitHub Actions, AppVeyor, Azure Pipelines, GitLab CI, CircleCI) references a Windows runner or GOOS=windows. Shows intent to build/test on Windows, not run results; dynamic matrices and external CI are not detected. Not an application metric.

![Windows CI by primary language](windows_ci.svg)

| Category | Count / denominator | Share |
| --- | ---: | ---: |
| JavaScript | 0 / 1 | 0.0% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

N/A — no eligible repositories.

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| jonlynch/OpenTopoMap | success | JavaScript | Web | No framework detected |  |  |

## Windows-container compatibility and containerization potential

Static base-image indicators from scanned Dockerfiles and Containerfiles; no build or runtime test.

Among complete Windows-targeted scans, repositories with container/orchestration configuration or Dockerfile/Containerfile base images are excluded. Remaining project-type and Windows-component indicators are heuristic screening evidence, not a test of Windows-container support.

The two assessment scopes overlap; their counts must not be added together.

| Scope | Assessment | Repositories |
| --- | --- | ---: |
| Base-image evidence | Windows base image configured | 0 |
| Base-image evidence | Linux base image configured | 0 |
| Base-image evidence | Mixed or ambiguous base images | 0 |
| Base-image evidence | No container base-image evidence | 1 |
| Base-image evidence | Incomplete source scan | 0 |
| Containerization potential | Potentially suitable; validate with a build/run | 0 |
| Containerization potential | Conditional; dependencies or project type need review | 0 |
| Containerization potential | Poor fit for standard Windows Server containers | 0 |
| Containerization potential | Insufficient project evidence | 0 |
| Containerization potential | Excluded: container/orchestration evidence detected | 0 |
| Containerization potential | Excluded: no Windows target detected | 1 |
| Containerization potential | Not assessed: incomplete scan | 0 |

These are source-level indicators, not proof of build or runtime compatibility. No detected Dockerfile is not proof of incompatibility.

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
