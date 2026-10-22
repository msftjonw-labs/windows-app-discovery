# Windows app discovery — latest report

Activity window (UTC): 2026-09-22T17:00:00Z → 2026-10-22T17:00:00Z
Generated: 2026-10-22T20:39:47Z  
Ruleset: pilot-4; Application Inspector: 1.10.2

Uniform random sample from 371908 public repositories with qualifying human activity.
Seed: 2026-10-22T17:00:00Z; archive hours: 720/720; qualifying events: 1222282; deleted/private replacements: 6.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.16 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 93 |
| Partial | 4 |
| Failed | 0 |
| No eligible source | 3 |
| Windows candidates (subset of complete scans) | 9 |
| Windows applications (subset of complete scans) | 4 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 41 / 93 | 44.09% | 34.43–54.21% |
| Python runtime \(OS unspecified\) | 8 / 93 | 8.6% | 4.42–16.07% |
| Containers / Kubernetes | 7 / 93 | 7.53% | 3.69–14.73% |
| Windows | 7 / 93 | 7.53% | 3.69–14.73% |
| Android | 5 / 93 | 5.38% | 2.32–11.97% |
| Unknown | 5 / 93 | 5.38% | 2.32–11.97% |
| Node.js tooling/runtime \(OS unspecified\) | 3 / 93 | 3.23% | 1.1–9.06% |
| macOS | 3 / 93 | 3.23% | 1.1–9.06% |
| Cloud / infrastructure | 2 / 93 | 2.15% | 0.59–7.51% |
| Linux | 2 / 93 | 2.15% | 0.59–7.51% |
| Multiple OS \(incl. Windows\) | 2 / 93 | 2.15% | 0.59–7.51% |
| Smart contracts | 2 / 93 | 2.15% | 0.59–7.51% |
| WebAssembly | 2 / 93 | 2.15% | 0.59–7.51% |
| Multiple OS \(no Windows\) | 1 / 93 | 1.07% | 0.19–5.84% |
| Native code \(OS unspecified\) | 1 / 93 | 1.07% | 0.19–5.84% |
| Server / backend | 1 / 93 | 1.07% | 0.19–5.84% |
| Shell / automation \(OS unspecified\) | 1 / 93 | 1.07% | 0.19–5.84% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| TypeScript | 30 / 93 | 32.26% | 23.62–42.3% |
| Python | 18 / 93 | 19.35% | 12.61–28.53% |
| JavaScript | 11 / 93 | 11.83% | 6.73–19.95% |
| HTML | 5 / 93 | 5.38% | 2.32–11.97% |
| Rust | 4 / 93 | 4.3% | 1.69–10.54% |
| Go | 3 / 93 | 3.23% | 1.1–9.06% |
| Java | 3 / 93 | 3.23% | 1.1–9.06% |
| Jupyter Notebook | 2 / 93 | 2.15% | 0.59–7.51% |
| PHP | 2 / 93 | 2.15% | 0.59–7.51% |
| Scala | 2 / 93 | 2.15% | 0.59–7.51% |
| Swift | 2 / 93 | 2.15% | 0.59–7.51% |
| Unknown | 2 / 93 | 2.15% | 0.59–7.51% |
| Astro | 1 / 93 | 1.08% | 0.19–5.84% |
| C | 1 / 93 | 1.08% | 0.19–5.84% |
| C# | 1 / 93 | 1.08% | 0.19–5.84% |
| C++ | 1 / 93 | 1.08% | 0.19–5.84% |
| Dart | 1 / 93 | 1.07% | 0.19–5.84% |
| GDScript | 1 / 93 | 1.07% | 0.19–5.84% |
| HCL | 1 / 93 | 1.07% | 0.19–5.84% |
| Kotlin | 1 / 93 | 1.07% | 0.19–5.84% |
| Shell | 1 / 93 | 1.07% | 0.19–5.84% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 54 / 93 | 58.06% | 47.91–67.58% |
| Next.js | 12 / 93 | 12.9% | 7.54–21.21% |
| React | 12 / 93 | 12.9% | 7.54–21.21% |
| React Native | 4 / 93 | 4.3% | 1.69–10.54% |
| Angular | 2 / 93 | 2.15% | 0.59–7.51% |
| Electron | 2 / 93 | 2.15% | 0.59–7.51% |
| FastAPI | 2 / 93 | 2.15% | 0.59–7.51% |
| Vue | 2 / 93 | 2.15% | 0.59–7.51% |
| Flutter | 1 / 93 | 1.08% | 0.19–5.84% |
| Svelte | 1 / 93 | 1.08% | 0.19–5.84% |
| Windows Forms | 1 / 93 | 1.08% | 0.19–5.84% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Unknown / no findings | 84 / 93 | 90.32% | 82.62–94.82% |
| Cross-platform: React Native | 5 / 93 | 5.38% | 2.32–11.97% |
| Cross-platform: Electron | 2 / 93 | 2.15% | 0.59–7.51% |
| PowerShell | 2 / 93 | 2.15% | 0.59–7.51% |
| Cross-platform: Flutter | 1 / 93 | 1.08% | 0.19–5.84% |
| Windows Forms app | 1 / 93 | 1.08% | 0.19–5.84% |
| Windows desktop app | 1 / 93 | 1.08% | 0.19–5.84% |
| Service management | 0 / 93 | 0.0% | 0.0–3.97% |
| UWP app | 0 / 93 | 0.0% | 0.0–3.97% |
| WPF app | 0 / 93 | 0.0% | 0.0–3.97% |
| WinUI app | 0 / 93 | 0.0% | 0.0–3.97% |
| Windows service | 0 / 93 | 0.0% | 0.0–3.97% |

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 3 / 4 | 75.0% | 30.06–95.44% |
| PowerShell script | 2 / 4 | 50.0% | 15.0–85.0% |
| Cross-platform: React Native | 1 / 4 | 25.0% | 4.56–69.94% |
| PowerShell install script | 1 / 4 | 25.0% | 4.56–69.94% |
| Windows Forms | 1 / 4 | 25.0% | 4.56–69.94% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 4 / 4 | 100.0% | 51.01–100.0% |
| .NET native interop | 0 / 4 | 0.0% | 0.0–48.99% |
| COM | 0 / 4 | 0.0% | 0.0–48.99% |
| DirectX | 0 / 4 | 0.0% | 0.0–48.99% |
| WinRT | 0 / 4 | 0.0% | 0.0–48.99% |
| Windows Registry | 0 / 4 | 0.0% | 0.0–48.99% |
| Windows Shell | 0 / 4 | 0.0% | 0.0–48.99% |
| Windows services | 0 / 4 | 0.0% | 0.0–48.99% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 9 / 9 | 100.0% | 70.09–100.0% |
| .NET native interop | 0 / 9 | 0.0% | 0.0–29.91% |
| COM | 0 / 9 | 0.0% | 0.0–29.91% |
| DirectX | 0 / 9 | 0.0% | 0.0–29.91% |
| WinRT | 0 / 9 | 0.0% | 0.0–29.91% |
| Windows Registry | 0 / 9 | 0.0% | 0.0–29.91% |
| Windows Shell | 0 / 9 | 0.0% | 0.0–29.91% |
| Windows services | 0 / 9 | 0.0% | 0.0–29.91% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| cositools/cosipy | success | Jupyter Notebook | Python runtime \(OS unspecified\) | No framework detected |  |  |
| peteknowsai/ship | success | HTML | Web | No framework detected |  |  |
| adeelahmad/lense | success | Python | Multiple OS \(incl. Windows\) | Next.js | Native / Win32 \(UI not proven\), PowerShell install script, PowerShell script | Win32 |
| CodexVeritas/ai-env-handler | success | Python | Web | No framework detected |  |  |
| j769chen/overclock | success | TypeScript | Web | React Native | Cross-platform: React Native |  |
| AIAshinze/meditationApp | success | JavaScript | Web | React Native | Cross-platform: React Native |  |
| z-tyner/Assignment-1 | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| nailkhmrn/nimay-studio | success | TypeScript | Web | Next.js |  |  |
| daniele21/cineo | success | Python | macOS | No framework detected |  |  |
| Vanderbilt-VR-2026/EscapeGranny | success | C# | Android | No framework detected |  |  |
| hmrc/ioss-intermediary-registration-stub | success | Scala | Unknown | No framework detected |  |  |
| miaoziguan/obsidian-chinese-plugin-market | success | TypeScript | Web | No framework detected |  |  |
| isabelasiilva/meu-projeto-elastech | success | Java | Unknown | No framework detected |  |  |
| robertodelfranco/ft\_transcendence | success | Python | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| natleewhee/papartfolio | success | Python | Web | Next.js |  |  |
| coport-uni/SpinCoaterAutomation\_I2C | success | C++ | Python runtime \(OS unspecified\) | No framework detected |  |  |
| mohanpennabadi/JavaScript\_Assignment | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| estengel07-ui/Entrainement-Matu-Post-Technique | success | JavaScript | Web | No framework detected |  |  |
| zheref/kro-pwa | success | TypeScript | Web | Next.js |  |  |
| SaurabhX99/b2b-connect | success | JavaScript | Web | React |  |  |
| oroszgy/gitlab-pipelines-for-openchamber | success | TypeScript | Web | No framework detected |  |  |
| containers/crun | success | C | Containers / Kubernetes | No framework detected |  |  |
| repinw/yamt | success | Dart | Multiple OS \(no Windows\) | Flutter | Cross-platform: Flutter |  |
| MionKit/multifront | success | TypeScript | WebAssembly | Svelte |  |  |
| zigflow/zigflow | success | Go | Containers / Kubernetes | No framework detected |  |  |
| mz00m/ai-labor-predictions | success | TypeScript | Web | Next.js |  |  |
| gahnejennifer/Kraftly\_Watt | success | JavaScript | Web | Vue |  |  |
| alex1989hu/kubelet-serving-cert-approver | success | Go | Containers / Kubernetes | No framework detected |  |  |
| OrbitalCommons/rizzma | success | Rust | WebAssembly | No framework detected |  |  |
| sowdm/cp-car-gen | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| thenuggetapp/nuggetapp | success | TypeScript | Web | Next.js |  |  |
| veracindarella/votechain-contracts | success | TypeScript | Smart contracts | React |  |  |
| wichtelimwald/ada | success | Python | Containers / Kubernetes | No framework detected |  |  |
| Tatiwel/electron-multi-window | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| Fatima-Ashnehdar/Zihome | success | TypeScript | Web | Next.js |  |  |
| shepcx3/holisticallyhip | success | JavaScript | Web | No framework detected |  |  |
| matchmoments-admin/quillo | success | TypeScript | Android | React |  |  |
| championai70-debug/bonwise | success | Python | Android | No framework detected |  |  |
| larai-w/carequest | success | TypeScript | Web | Next.js |  |  |
| gemmadanks/hebog | success | Python | Containers / Kubernetes | No framework detected |  |  |
| powersync-ja/CSQLite | partial | C | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| risu729/biwa | success | Rust | Linux | No framework detected |  |  |
| loopcompany/backend-laravel | success | PHP | Windows | Vue | Native / Win32 \(UI not proven\) | Win32 |
| dxuanhai2908-ship-it/SCM---Report-v2 | success | HTML | Web | No framework detected |  |  |
| grafana/opensouthcode-2026-k6-workshop | success | JavaScript | Containers / Kubernetes | No framework detected |  |  |
| thitapafocus/HBDtoMylove | success | HTML | Web | No framework detected |  |  |
| Thomas-Boudin/devis-ACJ | success | JavaScript | Web | No framework detected |  |  |
| boterop/proyecto\_software\_2 | success | Java | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| Jack-Pettersson/logmon-ui | success | TypeScript | Web | React |  |  |
| cloudposse-terraform-components/aws-github-oidc-role | success | HCL | Cloud / infrastructure | No framework detected |  |  |
| symfony/symfony | partial | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| BiomSharp/BiomSharp | partial | C# | Windows | Windows Forms | Windows Forms | .NET native interop |
| byteMara/sub-rosa-issue | success | TypeScript | Smart contracts | React |  |  |
| navikt/watson-sak-frontend | success | TypeScript | Web | React |  |  |
| DogeTennant/dTournaments | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| AudiopodAI/claude-plugin | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| GRIDAPPSD/ieee-2030\_5-client-go | success | Go | Native code \(OS unspecified\) | No framework detected |  |  |
| dondon3109/Budget-and-expense-analysis-tool | success | TypeScript | Android | React Native | Cross-platform: React Native |  |
| ustclhx/saas-template | success | TypeScript | Web | React |  |  |
| kuxiaowo/TechX-Shude-Mood-Barometer | success | Python | Web | FastAPI |  |  |
| rsitech-ai/space\_lens | success | Swift | macOS | No framework detected |  |  |
| EfinZhao/hermes | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| dondakeshimo/dotfiles | success | Shell | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| P4PER/revelio | success | TypeScript | Web | Next.js |  |  |
| ArturoMGuerrero/xr18-ai-controller | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| parabirb/freeremote-server | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| Priya-T-S/task-manager-api | success | Python | Server / backend | FastAPI |  |  |
| oficina-dev/deco-apps | success | TypeScript | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| photon-hq/buildspace | success | JavaScript | Unknown | No framework detected |  |  |
| chrisgen19/Pocket | success | TypeScript | Web | Next.js |  |  |
| YARAHQ/yara-forge | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| abdullahnettoor/p2p-games | success | TypeScript | Web | Next.js |  |  |
| TrongDang1511/Skipli-Canvas | success | TypeScript | Web | React |  |  |
| ericwalisko/memware | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| QuantEcon/test-actions-lecture-intro | success | Jupyter Notebook | Unknown | No framework detected |  |  |
| mathmaster0824/mnm-academy | success | HTML | Web | No framework detected |  |  |
| dev-protocol/community | success | Unknown | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| hajrix01-star/abroj-baseer-production | success | Python | Multiple OS \(incl. Windows\) | Windows Forms | Cross-platform: React Native, PowerShell script, Windows Forms | Win32 |
| Marcosariasglez/diana | success | TypeScript | Web | React Native | Cross-platform: React Native |  |
| sgentzen/vibe-dash | success | TypeScript | Web | React |  |  |
| grimoire-codex/.github | success | Unknown | Unknown | No framework detected |  |  |
| overcuriousity/pdf2epub | success | Python | Containers / Kubernetes | No framework detected |  |  |
| nationalarchives/dr2-ingest | success | Scala | Cloud / infrastructure | No framework detected |  |  |
| appstrax/time-tracker | success | TypeScript | Windows | Angular | Native / Win32 \(UI not proven\) | Win32 |
| joomla-projects/Joomla-Extension-Directory | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| alexcosta97/livesplit-asr-bridge | success | Rust | Linux | No framework detected |  |  |
| action-state-group/capsule-viewer | success | HTML | Web | No framework detected |  |  |
| StoryTime-Productions/st-tools | success | TypeScript | Web | Next.js |  |  |
| rami-nava/PF-PLAG-OUT-26 | success | Kotlin | Android | No framework detected |  |  |
| TheStich-T/SistemaDeGesti-nAutomotriz | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| vicotrbb/positron | success | Rust | Web | No framework detected |  |  |
| mmvolkov/invest-project-eval | success | JavaScript | Web | No framework detected |  |  |
| otomata-tech/oto-archive | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| owner8b-droid/structura | success | Astro | Web | No framework detected |  |  |
| llvm-mos/llvm-mos | partial | LLVM | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | .NET native interop, Win32 |
| Nana-04-art/beesagono | success | TypeScript | Web | Angular |  |  |
| Ryuta-Miyamoto/Vela | success | Swift | macOS | No framework detected |  |  |
| Koaieus/skill-tree-of-life | success | GDScript | Web | No framework detected |  |  |
| 0rce-Labs/roe-guard | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| MrFixITslu/V79Tiquet | success | JavaScript | Web | React |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
