# Windows app discovery — latest report

Activity window (UTC): 2026-09-24T09:00:00Z → 2026-10-24T09:00:00Z
Generated: 2026-10-24T12:53:23Z  
Ruleset: pilot-4; Application Inspector: 1.10.2

Uniform random sample from 370185 public repositories with qualifying human activity.
Seed: 2026-10-24T09:00:00Z; archive hours: 720/720; qualifying events: 1202568; deleted/private replacements: 0.
95% Wilson confidence intervals; worst-case margin for complete scans: ±98.0 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 1 |
| Complete scans | 1 |
| Partial | 0 |
| Failed | 0 |
| No eligible source | 0 |
| Windows candidates (subset of complete scans) | 0 |
| Windows applications (subset of complete scans) | 0 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 1 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 1 / 1 | 100.0% | 20.65–100.0% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 1 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| TypeScript | 1 / 1 | 100.0% | 20.65–100.0% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 1 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| React | 1 / 1 | 100.0% | 20.65–100.0% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Unknown / no findings | 1 / 1 | 100.0% | 20.65–100.0% |
| PowerShell | 0 / 1 | 0.0% | 0.0–79.35% |
| Service management | 0 / 1 | 0.0% | 0.0–79.35% |
| UWP app | 0 / 1 | 0.0% | 0.0–79.35% |
| WPF app | 0 / 1 | 0.0% | 0.0–79.35% |
| WinUI app | 0 / 1 | 0.0% | 0.0–79.35% |
| Windows Forms app | 0 / 1 | 0.0% | 0.0–79.35% |
| Windows desktop app | 0 / 1 | 0.0% | 0.0–79.35% |
| Windows service | 0 / 1 | 0.0% | 0.0–79.35% |

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

N/A — no eligible repositories.

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

N/A — no eligible repositories.

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

N/A — no eligible repositories.

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| viljarpuusepp/uhishange | success | TypeScript | Web | React |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
