# Windows app discovery — latest report

Activity window (UTC): 2026-09-24T19:00:00Z → 2026-10-24T19:00:00Z
Generated: 2026-10-24T22:53:29Z  
Ruleset: pilot-5; Application Inspector: 1.10.2

Uniform random sample from 369917 public repositories with qualifying human activity.
Seed: 2026-10-24T19:00:00Z; archive hours: 720/720; qualifying events: 1197515; deleted/private replacements: 11.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.16 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 93 |
| Partial | 1 |
| Failed | 0 |
| No eligible source | 6 |
| Windows candidates (subset of complete scans) | 10 |
| Windows applications (subset of complete scans) | 8 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 45 / 93 | 48.39% | 38.5–58.4% |
| Python runtime \(OS unspecified\) | 12 / 93 | 12.9% | 7.54–21.21% |
| Linux | 6 / 93 | 6.45% | 2.99–13.37% |
| Containers / Kubernetes | 5 / 93 | 5.38% | 2.32–11.97% |
| Multiple OS \(incl. Windows\) | 5 / 93 | 5.38% | 2.32–11.97% |
| Windows | 5 / 93 | 5.38% | 2.32–11.97% |
| Multiple OS \(no Windows\) | 3 / 93 | 3.23% | 1.1–9.06% |
| Node.js tooling/runtime \(OS unspecified\) | 3 / 93 | 3.23% | 1.1–9.06% |
| Native code \(OS unspecified\) | 2 / 93 | 2.15% | 0.59–7.51% |
| .NET runtime \(OS unspecified\) | 1 / 93 | 1.08% | 0.19–5.84% |
| Android | 1 / 93 | 1.08% | 0.19–5.84% |
| BSD | 1 / 93 | 1.07% | 0.19–5.84% |
| Cloud / infrastructure | 1 / 93 | 1.07% | 0.19–5.84% |
| JVM \(OS unspecified\) | 1 / 93 | 1.07% | 0.19–5.84% |
| Shell / automation \(OS unspecified\) | 1 / 93 | 1.07% | 0.19–5.84% |
| iOS | 1 / 93 | 1.07% | 0.19–5.84% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Python | 22 / 93 | 23.66% | 16.17–33.23% |
| TypeScript | 19 / 93 | 20.43% | 13.49–29.72% |
| JavaScript | 10 / 93 | 10.75% | 5.95–18.67% |
| Rust | 8 / 93 | 8.6% | 4.42–16.07% |
| Java | 5 / 93 | 5.38% | 2.32–11.97% |
| C# | 4 / 93 | 4.3% | 1.69–10.54% |
| Go | 4 / 93 | 4.3% | 1.69–10.54% |
| HTML | 3 / 93 | 3.23% | 1.1–9.06% |
| Blade | 2 / 93 | 2.15% | 0.59–7.51% |
| C++ | 2 / 93 | 2.15% | 0.59–7.51% |
| Jupyter Notebook | 2 / 93 | 2.15% | 0.59–7.51% |
| Kotlin | 2 / 93 | 2.15% | 0.59–7.51% |
| PowerShell | 2 / 93 | 2.15% | 0.59–7.51% |
| AL | 1 / 93 | 1.08% | 0.19–5.84% |
| CSS | 1 / 93 | 1.08% | 0.19–5.84% |
| Go Template | 1 / 93 | 1.08% | 0.19–5.84% |
| HCL | 1 / 93 | 1.08% | 0.19–5.84% |
| Haxe | 1 / 93 | 1.07% | 0.19–5.84% |
| MDX | 1 / 93 | 1.07% | 0.19–5.84% |
| Makefile | 1 / 93 | 1.07% | 0.19–5.84% |
| Ruby | 1 / 93 | 1.07% | 0.19–5.84% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 93 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 52 / 93 | 55.91% | 45.79–65.57% |
| React | 23 / 93 | 24.73% | 17.08–34.38% |
| Next.js | 5 / 93 | 5.38% | 2.32–11.97% |
| Electron | 2 / 93 | 2.15% | 0.59–7.51% |
| Vue | 2 / 93 | 2.15% | 0.59–7.51% |
| Windows Forms | 2 / 93 | 2.15% | 0.59–7.51% |
| FastAPI | 1 / 93 | 1.08% | 0.19–5.84% |
| Flask | 1 / 93 | 1.08% | 0.19–5.84% |
| Flutter | 1 / 93 | 1.08% | 0.19–5.84% |
| Qt | 1 / 93 | 1.08% | 0.19–5.84% |
| Spring Boot | 1 / 93 | 1.07% | 0.19–5.84% |
| Svelte | 1 / 93 | 1.07% | 0.19–5.84% |
| WPF | 1 / 93 | 1.07% | 0.19–5.84% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Types are identified from source patterns and project metadata, not inferred from OS or language. Repositories without sufficient type evidence remain in the denominator and are reported in the classification coverage note, not as application types. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web frontend | 52 / 93 | 55.91% | 45.79–65.57% |
| Python application / script | 47 / 93 | 50.54% | 40.56–60.47% |
| Command-line tool | 46 / 93 | 49.46% | 39.53–59.44% |
| Shell / batch automation | 46 / 93 | 49.46% | 39.53–59.44% |
| Container / orchestration configuration | 28 / 93 | 30.11% | 21.73–40.07% |
| Backend / API | 23 / 93 | 24.73% | 17.08–34.38% |
| Executable application | 23 / 93 | 24.73% | 17.08–34.38% |
| Library / SDK | 18 / 93 | 19.35% | 12.61–28.53% |
| Build automation | 17 / 93 | 18.28% | 11.74–27.34% |
| PowerShell | 7 / 93 | 7.53% | 3.69–14.73% |
| Notebook / data analysis | 6 / 93 | 6.45% | 2.99–13.37% |
| Mobile app | 4 / 93 | 4.3% | 1.69–10.54% |
| Windows desktop app | 3 / 93 | 3.23% | 1.1–9.06% |
| Cross-platform: Electron | 2 / 93 | 2.15% | 0.59–7.51% |
| Windows Forms app | 2 / 93 | 2.15% | 0.59–7.51% |
| Cross-platform: Flutter | 1 / 93 | 1.08% | 0.19–5.84% |
| Cross-platform: Qt | 1 / 93 | 1.08% | 0.19–5.84% |
| Infrastructure as code | 1 / 93 | 1.08% | 0.19–5.84% |
| Service management | 1 / 93 | 1.08% | 0.19–5.84% |
| Smart contract | 1 / 93 | 1.08% | 0.19–5.84% |
| WPF app | 1 / 93 | 1.08% | 0.19–5.84% |
| macOS app | 1 / 93 | 1.08% | 0.19–5.84% |
| UWP app | 0 / 93 | 0.0% | 0.0–3.97% |
| WinUI app | 0 / 93 | 0.0% | 0.0–3.97% |
| Windows service | 0 / 93 | 0.0% | 0.0–3.97% |

Classification coverage: 4 repositories have insufficient application-type evidence in the scanned source. They remain in the denominator but are not assigned an application type.

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 4 / 8 | 50.0% | 21.52–78.48% |
| Cross-platform: Flutter | 1 / 8 | 12.5% | 2.24–47.09% |
| Cross-platform: Qt | 1 / 8 | 12.5% | 2.24–47.09% |
| PowerShell install script | 1 / 8 | 12.5% | 2.24–47.09% |
| PowerShell script | 1 / 8 | 12.5% | 2.24–47.09% |
| WPF | 1 / 8 | 12.5% | 2.24–47.09% |
| Windows Forms | 1 / 8 | 12.5% | 2.24–47.09% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 7 / 8 | 87.5% | 52.91–97.76% |
| .NET native interop | 1 / 8 | 12.5% | 2.24–47.09% |
| COM | 1 / 8 | 12.5% | 2.24–47.09% |
| DirectX | 0 / 8 | 0.0% | 0.0–32.44% |
| WinRT | 0 / 8 | 0.0% | 0.0–32.44% |
| Windows Registry | 0 / 8 | 0.0% | 0.0–32.44% |
| Windows Shell | 0 / 8 | 0.0% | 0.0–32.44% |
| Windows services | 0 / 8 | 0.0% | 0.0–32.44% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 8 / 10 | 80.0% | 49.02–94.33% |
| .NET native interop | 1 / 10 | 10.0% | 1.79–40.42% |
| COM | 1 / 10 | 10.0% | 1.79–40.42% |
| DirectX | 0 / 10 | 0.0% | 0.0–27.75% |
| WinRT | 0 / 10 | 0.0% | 0.0–27.75% |
| Windows Registry | 0 / 10 | 0.0% | 0.0–27.75% |
| Windows Shell | 0 / 10 | 0.0% | 0.0–27.75% |
| Windows services | 0 / 10 | 0.0% | 0.0–27.75% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| ShravanSunder/sunstack-tools | success | Rust | Linux | No framework detected |  |  |
| bytedance/UI-TARS-desktop | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| NVIDIA/daqiri | success | C++ | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| datastax/release-notes | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| n0-computer/iroh | success | Rust | Multiple OS \(no Windows\) | No framework detected |  |  |
| RamsesMartinez/el-gato-bobah-pos | success | Go | Web | React |  |  |
| Elten-huanghuang/rs\_integration | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| nmcitra/kil | success | Python | Containers / Kubernetes | No framework detected |  |  |
| kydecker/genderswap.fm | success | TypeScript | Web | Svelte |  |  |
| ryba-22/product-engineering-os | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| missing-semester/missing-semester | success | CSS | Web | No framework detected |  |  |
| fogrew/bb-plugin-project-icons | success | TypeScript | Web | React |  |  |
| atum-platform/atum-drive-companion | partial | C++ | Multiple OS \(incl. Windows\) | Qt | Cross-platform: Qt, PowerShell script | Win32, WinRT |
| bailey-lab/MIPTools | success | Jupyter Notebook | Python runtime \(OS unspecified\) | No framework detected |  |  |
| M4K4TT4CK/OmniEngineering | success | Python | Web | FastAPI |  |  |
| kilaslab/ccprovider | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| Tunaxa/tunaxa-crm | success | JavaScript | Web | React |  |  |
| tenalisriharsha/deploy-oracle | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| jlogicsoftware/prudent | success | Java | Multiple OS \(incl. Windows\) | Flutter | Cross-platform: Flutter | COM, Win32 |
| CoderLambert/translateflow-dictionary-builder | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| eli-jordan/etsy-listing-automation | success | Python | Web | React |  |  |
| sae-space-ai/midi-engine-core | success | TypeScript | Web | React |  |  |
| PittsCraft/control-surface | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| CarsonBurke/cosmicbar | success | Rust | Native code \(OS unspecified\) | No framework detected |  |  |
| Startrek1977/Webiks-Home-Exercise | success | C# | Windows | WPF | WPF |  |
| paketo-buildpacks/java-memory-assistant | success | Go | Native code \(OS unspecified\) | No framework detected |  |  |
| AVinaFB/Photographer\_Assistant | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| HansKristoffer/agentgate | success | TypeScript | Linux | React |  |  |
| businesscentralal/bc-origo-bifrost-inventory | success | AL | Python runtime \(OS unspecified\) | No framework detected | PowerShell script |  |
| taqelah/checkout-app | success | HTML | Web | No framework detected |  |  |
| megzin777-arch/reinos-de-eter-apk | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| stuttgart-things/argocd | success | Go Template | Containers / Kubernetes | No framework detected |  |  |
| maniator/verticopolis | success | TypeScript | Linux | No framework detected |  |  |
| grafana/grafana-influxdb-datasource | success | TypeScript | Web | React |  |  |
| bdbch/inksane | success | TypeScript | Web | React |  |  |
| carmelo-schepis/S6\_CUT | success | TypeScript | Linux | React | PowerShell install script, PowerShell script |  |
| Flazened/laravel-sistem-sekolah | success | Blade | Web | No framework detected |  |  |
| ZigmaSoftware/iwms-backend | success | Python | Web | Next.js |  |  |
| MeguminBOT/hxscript | success | Haxe | Python runtime \(OS unspecified\) | No framework detected |  |  |
| shiyan688/dsh-novel-craft | success | JavaScript | Web | React |  |  |
| rome-protocol/rome-dex | success | Rust | Linux | Next.js |  |  |
| kunobi-ninja/kunobi-daemon | success | Rust | BSD | No framework detected |  |  |
| joaovitordev9/controle-de-acesso | success | JavaScript | Web | React |  |  |
| djuvinall/collection | success | PowerShell | Web | No framework detected | PowerShell module, PowerShell script, Service management |  |
| euanmsm/devkit | success | JavaScript | Web | No framework detected |  |  |
| sondresjolyst/si-dotnet-packages | success | C# | .NET runtime \(OS unspecified\) | No framework detected |  |  |
| sebastha93-pixel/http-localhost-8502-shopify | success | Python | Web | Next.js | PowerShell script |  |
| Ataraxy-Labs/sem | success | Rust | Multiple OS \(no Windows\) | Vue |  |  |
| daviddossou/spens | success | Ruby | Web | No framework detected |  |  |
| aklaus1287-cloud/aklaus1287-cloud.github.io | success | TypeScript | Web | Next.js |  |  |
| spacetelescope/notebook-ci-testing | success | Jupyter Notebook | Web | No framework detected |  |  |
| jorgegv/jnext | success | C++ | Multiple OS \(incl. Windows\) | Qt | Cross-platform: Qt | Win32 |
| Adolanium/hermes-resetwatch | success | Python | Python runtime \(OS unspecified\) | React |  |  |
| cybozu-go/cke | success | Go | Linux | No framework detected |  |  |
| henriquebrites/gitscope | success | TypeScript | Web | React |  |  |
| timvink/mkdocs-git-revision-date-localized-plugin | success | Python | Web | No framework detected |  |  |
| m1m2m3m4m5m6m700-afk/FLIXO\_Hub | success | TypeScript | Web | React |  |  |
| spacetelescope/jdaviz | success | Python | Web | Vue |  |  |
| netbooee/makeithappen | success | TypeScript | Web | React |  |  |
| escoffier-labs/skillet | success | JavaScript | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| MidnightsFX/Valheim-Community-Patch | success | C# | Windows | Windows Forms | PowerShell script, Windows Forms |  |
| accuknox/accuknox-jobs | success | Python | Containers / Kubernetes | No framework detected |  |  |
| tasta-skolekorps/tilsynsvakt | success | C# | Web | No framework detected | PowerShell script |  |
| mcofirty/Darijapp | success | TypeScript | Web | React |  |  |
| FactumID/sealsign-docs | success | TypeScript | Web | React |  |  |
| RealityBending/RealityBending.github.io | success | JavaScript | Web | No framework detected |  |  |
| Jumpmaster2/Shutter-Assistant | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| Azure/terraform-azurerm-avm-ptn-odaa | success | HCL | Cloud / infrastructure | No framework detected |  |  |
| scheduleonce/help-center | success | MDX | Web | No framework detected |  |  |
| phatblat/conventional-docs | success | Rust | Web | No framework detected |  |  |
| AhmedDR200/dev-notes | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| recomp-code/street-recomp-v3 | success | PowerShell | Multiple OS \(incl. Windows\) | Windows Forms | PowerShell install script, PowerShell script, Windows Forms | .NET native interop, Win32 |
| nurdsaga16/kzt-converter | success | Python | Containers / Kubernetes | No framework detected |  |  |
| lucypham4/R-L | success | JavaScript | iOS | React |  |  |
| deepika-91/CodeGuardian | success | Python | Web | No framework detected |  |  |
| build-extensions-oss/gradle-helm-plugin | success | Kotlin | JVM \(OS unspecified\) | No framework detected |  |  |
| muleysayali875-ui/LoopLearn | success | JavaScript | Web | React |  |  |
| usa4148/cme-mdp3-sim | success | Python | Web | Flask |  |  |
| route4me/route4me-python-sdk | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| bengeraci14/data-structures-portfolio | success | HTML | Web | No framework detected |  |  |
| ietf-rats-wg/draft-ietf-rats-multi-verifier | success | Makefile | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| UsernameMP/English | success | Java | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| CartoDB/agent-skills | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| astudilloalex/company-registry-service | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| DMANDAVIYA/strategic-private-assets-management | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| redhat-cne/downstream-ptp-operator-monorepo | success | Go | Containers / Kubernetes | No framework detected |  |  |
| Hiosdra/hReader | success | Kotlin | Android | No framework detected |  |  |
| duksunghcg-ship-it/sentinel | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| clayvanderburg/geometry-survivor | success | JavaScript | Web | No framework detected |  |  |
| tiriana/repo-template | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| Mozilla-Campus-Club-Cummins/cybersecurity-incident-dashboard-HacktoberFest-2026 | success | JavaScript | Web | React |  |  |
| SCORELabUS/SPHERE | success | HTML | Web | React |  |  |
| PakhomovAlexander/afactory | success | Rust | Multiple OS \(no Windows\) | No framework detected |  |  |
| funkelab/funlib.persistence | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| msqd/harp | success | Python | Web | React |  |  |
| karinalfrida/advanced-r-lab04 | not\_applicable | R | Unknown | No framework detected |  |  |
| SkshieldusRookies06/UDT-Used\_Device\_Trade\_BackEnd | success | Java | Windows | Spring Boot | Native / Win32 \(UI not proven\) | Win32 |
| snsm-uptime/finance-dashboard | success | Python | Web | Next.js |  |  |
| yosima050/simple-pos-kelompok-04 | success | Blade | Web | No framework detected |  |  |
| Team-Hanmaum/hanmaum-frontend | success | TypeScript | Web | React |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
