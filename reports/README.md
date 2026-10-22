# Windows app discovery — latest report

Activity window (UTC): 2026-09-22T13:00:00Z → 2026-10-22T13:00:00Z
Generated: 2026-10-22T17:16:44Z  
Ruleset: pilot-4; Application Inspector: 1.10.2

Uniform random sample from 372943 public repositories with qualifying human activity.
Seed: 2026-10-22T13:00:00Z; archive hours: 720/720; qualifying events: 1227805; deleted/private replacements: 3.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.27 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 91 |
| Partial | 3 |
| Failed | 2 |
| No eligible source | 4 |
| Windows candidates (subset of complete scans) | 20 |
| Windows applications (subset of complete scans) | 11 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 91 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 31 / 91 | 34.06% | 25.15–44.27% |
| Windows | 18 / 91 | 19.78% | 12.89–29.11% |
| Python runtime \(OS unspecified\) | 12 / 91 | 13.19% | 7.71–21.65% |
| Linux | 8 / 91 | 8.79% | 4.52–16.4% |
| Native code \(OS unspecified\) | 5 / 91 | 5.49% | 2.37–12.22% |
| Unknown | 3 / 91 | 3.29% | 1.13–9.25% |
| Containers / Kubernetes | 2 / 91 | 2.2% | 0.6–7.66% |
| Multiple OS \(incl. Windows\) | 2 / 91 | 2.2% | 0.6–7.66% |
| Multiple OS \(no Windows\) | 2 / 91 | 2.2% | 0.6–7.66% |
| Node.js tooling/runtime \(OS unspecified\) | 2 / 91 | 2.2% | 0.6–7.66% |
| .NET runtime \(OS unspecified\) | 1 / 91 | 1.1% | 0.19–5.96% |
| Android | 1 / 91 | 1.1% | 0.19–5.96% |
| Cloud / infrastructure | 1 / 91 | 1.1% | 0.19–5.96% |
| Server / backend | 1 / 91 | 1.1% | 0.19–5.96% |
| WebAssembly | 1 / 91 | 1.1% | 0.19–5.96% |
| macOS | 1 / 91 | 1.1% | 0.19–5.96% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 91 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Python | 21 / 91 | 23.08% | 15.62–32.72% |
| TypeScript | 13 / 91 | 14.28% | 8.54–22.92% |
| JavaScript | 9 / 91 | 9.89% | 5.29–17.74% |
| HTML | 8 / 91 | 8.79% | 4.52–16.4% |
| Rust | 6 / 91 | 6.59% | 3.06–13.65% |
| C++ | 4 / 91 | 4.39% | 1.72–10.76% |
| Go | 4 / 91 | 4.39% | 1.72–10.76% |
| PHP | 4 / 91 | 4.39% | 1.72–10.76% |
| C | 3 / 91 | 3.3% | 1.13–9.25% |
| Java | 3 / 91 | 3.3% | 1.13–9.25% |
| C# | 2 / 91 | 2.2% | 0.6–7.66% |
| Kotlin | 2 / 91 | 2.2% | 0.6–7.66% |
| Assembly | 1 / 91 | 1.1% | 0.19–5.96% |
| Astro | 1 / 91 | 1.1% | 0.19–5.96% |
| CSS | 1 / 91 | 1.1% | 0.19–5.96% |
| HCL | 1 / 91 | 1.1% | 0.19–5.96% |
| HLSL | 1 / 91 | 1.1% | 0.19–5.96% |
| Julia | 1 / 91 | 1.1% | 0.19–5.96% |
| Jupyter Notebook | 1 / 91 | 1.1% | 0.19–5.96% |
| R | 1 / 91 | 1.1% | 0.19–5.96% |
| Shell | 1 / 91 | 1.1% | 0.19–5.96% |
| Swift | 1 / 91 | 1.1% | 0.19–5.96% |
| TSQL | 1 / 91 | 1.1% | 0.19–5.96% |
| TeX | 1 / 91 | 1.1% | 0.19–5.96% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 91 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 56 / 91 | 61.54% | 51.27–70.87% |
| Next.js | 13 / 91 | 14.28% | 8.54–22.92% |
| React | 11 / 91 | 12.09% | 6.89–20.36% |
| Angular | 2 / 91 | 2.2% | 0.6–7.66% |
| Electron | 2 / 91 | 2.2% | 0.6–7.66% |
| Vue | 2 / 91 | 2.2% | 0.6–7.66% |
| Windows Forms | 2 / 91 | 2.19% | 0.6–7.66% |
| FastAPI | 1 / 91 | 1.1% | 0.19–5.96% |
| Flask | 1 / 91 | 1.1% | 0.19–5.96% |
| Spring Boot | 1 / 91 | 1.1% | 0.19–5.96% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Unknown / no findings | 80 / 91 | 87.91% | 79.64–93.11% |
| PowerShell | 8 / 91 | 8.79% | 4.52–16.4% |
| Cross-platform: Electron | 2 / 91 | 2.2% | 0.6–7.66% |
| Windows Forms app | 2 / 91 | 2.2% | 0.6–7.66% |
| Windows desktop app | 2 / 91 | 2.2% | 0.6–7.66% |
| Cross-platform: React Native | 1 / 91 | 1.1% | 0.19–5.96% |
| Service management | 1 / 91 | 1.1% | 0.19–5.96% |
| UWP app | 0 / 91 | 0.0% | 0.0–4.05% |
| WPF app | 0 / 91 | 0.0% | 0.0–4.05% |
| WinUI app | 0 / 91 | 0.0% | 0.0–4.05% |
| Windows service | 0 / 91 | 0.0% | 0.0–4.05% |

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 9 / 11 | 81.82% | 52.3–94.86% |
| PowerShell install script | 3 / 11 | 27.27% | 9.75–56.56% |
| PowerShell script | 3 / 11 | 27.27% | 9.75–56.56% |
| Windows Forms | 2 / 11 | 18.18% | 5.14–47.7% |
| Cross-platform: React Native | 1 / 11 | 9.09% | 1.62–37.74% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 10 / 11 | 90.91% | 62.26–98.38% |
| COM | 3 / 11 | 27.27% | 9.75–56.56% |
| .NET native interop | 2 / 11 | 18.18% | 5.14–47.7% |
| DirectX | 1 / 11 | 9.09% | 1.62–37.74% |
| WinRT | 1 / 11 | 9.09% | 1.62–37.74% |
| Windows Registry | 1 / 11 | 9.09% | 1.62–37.74% |
| Windows Shell | 1 / 11 | 9.09% | 1.62–37.74% |
| Windows services | 0 / 11 | 0.0% | 0.0–25.88% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 19 / 20 | 95.0% | 76.39–99.11% |
| COM | 4 / 20 | 20.0% | 8.07–41.6% |
| .NET native interop | 2 / 20 | 10.0% | 2.79–30.1% |
| Windows Shell | 2 / 20 | 10.0% | 2.79–30.1% |
| DirectX | 1 / 20 | 5.0% | 0.89–23.61% |
| WinRT | 1 / 20 | 5.0% | 0.89–23.61% |
| Windows Registry | 1 / 20 | 5.0% | 0.89–23.61% |
| Windows services | 0 / 20 | 0.0% | 0.0–16.11% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| WilliamHudspeth/institutional-alpha | success | Python | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| FS-GG/FS.GG.Templates | success | Python | Linux | No framework detected |  |  |
| Iridescent-Technologies/proposals | success | HTML | Web | No framework detected |  |  |
| MochiesCode/Mochies-Unity-Shaders | success | HLSL | Unknown | No framework detected |  |  |
| blaiseratcliffe/bitedj | partial | C++ | Multiple OS \(incl. Windows\) | Qt | Cross-platform: Qt, PowerShell script | COM, Win32 |
| papataku/honda\_ehev\_analyzer | success | Swift | Multiple OS \(no Windows\) | No framework detected |  |  |
| Demolinator/revit-mcp-server | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| thomas-maurice/hindlearn | success | JavaScript | Web | No framework detected |  |  |
| Bogzx/prop-firm-calendar | success | Python | Web | Next.js |  |  |
| gm64x/June | not\_applicable | GDScript | Unknown | No framework detected |  |  |
| eellison/better-benchmark | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| kiva/ui | success | JavaScript | Web | Vue |  |  |
| MvRens/ha-enever | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| OpenPLi/enigma2 | success | Python | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| pinobatch/rfk-nes | success | Assembly | Python runtime \(OS unspecified\) | No framework detected |  |  |
| TimmyTheTurtle/skills-copilot-10-agentic-workflows-that-read-the-room | success | Astro | Web | No framework detected |  |  |
| lawanmuk/hbn-parabolic-two-band-model | success | Jupyter Notebook | Python runtime \(OS unspecified\) | No framework detected |  |  |
| pjb0811/use-hooks | success | TypeScript | Web | React |  |  |
| fastcat/gdev | success | Go | Linux | No framework detected |  |  |
| rootxkit/uspace-ussp | success | Go | Web | Next.js |  |  |
| Lad-Company/superbloom | success | TypeScript | Web | React |  |  |
| ontripai/dorvia | partial | TypeScript | Web | Next.js |  |  |
| eliasmacielr/website | success | TypeScript | Web | Next.js |  |  |
| cyphylax/sungrow2mqtt | success | Python | Containers / Kubernetes | No framework detected |  |  |
| compucorp/civirules | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| 1Bnja/Typr | success | Python | Web | React |  |  |
| Nico6719/windhawk-mod-mobile-open-animation | success | C++ | Windows | No framework detected | Native / Win32 \(UI not proven\) | COM, Win32, Windows Shell |
| Tylervitale/munder-difflin | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| Igorjr19/last-month-recap | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| iggym/systems-bench | success | HTML | Web | Next.js |  |  |
| jangjunseo518-collab/springlog-Repetitive-learning | success | Java | Windows | Spring Boot | Native / Win32 \(UI not proven\) | Win32 |
| shnug/OSSRanking | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| kanywst/wtfi2 | success | Rust | Linux | No framework detected |  |  |
| pedrobtz/zuxml | success | R | Unknown | No framework detected |  |  |
| apache/james-mime4j | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| zenadell/Aethron | success | HTML | macOS | Next.js |  |  |
| Andrey31072/test-manager-library-3145555-page | success | HTML | Web | No framework detected |  |  |
| djbclark/plektra-djbclark | success | Kotlin | Android | No framework detected |  |  |
| GEUS-Glaciology-and-Climate/pypromice | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| PyAutoLabs/PyAutoMemory | success | TeX | Python runtime \(OS unspecified\) | No framework detected |  |  |
| turkmenos/tm-data | success | TSQL | Native code \(OS unspecified\) | No framework detected |  |  |
| protoledger/protoledger-backend | success | Rust | Web | No framework detected |  |  |
| Terminator364/BuildHub | success | C++ | Windows | No framework detected | Native / Win32 \(UI not proven\) | COM, Win32, Windows Shell |
| mirzatghayrat/mirzatghayrat.github.io | partial | HTML | Web | Next.js |  |  |
| hari2629-p/Sudoko | success | CSS | Web | No framework detected |  |  |
| MoaidHathot/Podium | success | C# | Linux | Vue | PowerShell script |  |
| Sharif2023/single-vendor | success | TypeScript | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| Fei-Away/Codex-Dream-Skin | success | JavaScript | Multiple OS \(incl. Windows\) | Windows Forms | PowerShell install script, PowerShell script, Windows Forms | .NET native interop, COM, Win32 |
| PlatformRelay/MKurator | success | Go | Linux | No framework detected |  |  |
| icreated/lumnik-site | success | HTML | Web | No framework detected |  |  |
| SoundMatt/c-RCP | success | C | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| lwz20210407/ZotWatch | success | HTML | Windows | Next.js | Native / Win32 \(UI not proven\), PowerShell install script, PowerShell script | Win32 |
| bettsLee/osaka\_lunch\_app | success | TypeScript | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| NereaV04/Restaurante | success | C# | .NET runtime \(OS unspecified\) | No framework detected |  |  |
| LouHeb/TrainingGitHubBAM | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| allenpiscitello/ducy | success | Rust | WebAssembly | No framework detected |  |  |
| Ncloclo/Ncloclo | success | Python | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| bradhermsen/TipIn | success | C++ | Windows | Windows Forms | Cross-platform: React Native, Windows Forms |  |
| telicent-oss/jwt-servlet-auth | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| gmargonato/HSInspired | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| corca-ai/wasmtex | success | TypeScript | Linux | No framework detected |  |  |
| robertguss/safe-c | success | C | Linux | No framework detected |  |  |
| astro-trove/trove | success | Python | Web | Next.js |  |  |
| Skiepy/Le-ptit-bot | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| mishan/mullion-gtk | success | C | Native code \(OS unspecified\) | No framework detected |  |  |
| onOffice-Web-Org/oo-wp-plugin | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| BeatrizJover/rail-punctuality-rag | success | Python | Server / backend | FastAPI |  |  |
| SnapPwd/snappwd-service | success | Rust | Containers / Kubernetes | No framework detected |  |  |
| spectonio/spectoncr | success | Rust | Web | React |  |  |
| psandhir/horustrace | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| evergage/mongodb\_exporter | failed |  |  |  |  |  |
| briandconnelly/codex-in-claude | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| jdwillmsen/dotfiles | success | Shell | Native code \(OS unspecified\) | No framework detected | PowerShell script |  |
| hinshiba/CostDropout | success | Rust | Native code \(OS unspecified\) | No framework detected |  |  |
| BryanChavesSalas/SodaYa | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| gsamuele78/RumblingStone | failed |  |  |  |  |  |
| babylonlabs-io/.github | not\_applicable | Python | Unknown | No framework detected |  |  |
| 2008monana/monana-financial | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| mirrorfolio-idea-labs/AEOS | success | TypeScript | Web | React |  |  |
| jo-fleck/Taxsim.jl | success | Julia | Unknown | No framework detected |  |  |
| Tsuchinoko0/neon-gate | success | HTML | Web | No framework detected |  |  |
| jejjohnson/vardax | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| caosuoming/InteSchool | success | TypeScript | Web | React | PowerShell script |  |
| Tramsey00/MathStart-Python | success | HTML | Web | React | PowerShell script |  |
| Domimueller85/guardian | success | TypeScript | Windows | Angular | Native / Win32 \(UI not proven\) | Win32 |
| atravis817/matchlatch | success | JavaScript | Web | No framework detected |  |  |
| shivaansh0610-LUFFY/RTI-Copilot | success | Python | Web | React |  |  |
| dennycrafter/tapedeck | success | TypeScript | Web | Next.js |  |  |
| exharmonic/gradeops | success | JavaScript | Web | React |  |  |
| rayrayraykk/CoPaw | success | Python | Multiple OS \(incl. Windows\) | Next.js | Native / Win32 \(UI not proven\), PowerShell install script, PowerShell script | .NET native interop, COM, DirectX, Win32, WinRT, Windows Registry |
| chrisrios-334/cafe-tacuba-frontend | success | JavaScript | Web | React |  |  |
| alexmathieu22-ops/home-ops | success | HCL | Cloud / infrastructure | No framework detected |  |  |
| jordanhubbard/webmux | success | TypeScript | Web | React | PowerShell module, PowerShell script, Service management |  |
| slashme/parliamentdiagram | success | JavaScript | Web | Flask |  |  |
| HorneroOS/greeter | success | Python | Linux | No framework detected |  |  |
| krystof-pilnacek-home/vtherm\_tpi\_hysteresis | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| cybrid-systems/aura | success | C++ | Native code \(OS unspecified\) | No framework detected |  |  |
| sonuKumar03/bundleradar | success | Go | Web | Angular |  |  |
| IBM/dra-node-sdk | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| mkny13/couch-tour | success | Kotlin | Multiple OS \(no Windows\) | No framework detected |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
