# Windows app discovery — latest report

Activity window (UTC): 2026-09-22T10:00:00Z → 2026-10-22T10:00:00Z
Generated: 2026-10-22T14:02:34Z  
Ruleset: pilot-3; Application Inspector: 1.10.2

Uniform random sample from 373037 public repositories with qualifying human activity.
Seed: 2026-10-22T10:00:00Z; archive hours: 720/720; qualifying events: 1228737; deleted/private replacements: 6.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.22 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 92 |
| Partial | 6 |
| Failed | 0 |
| No eligible source | 2 |
| Windows candidates (subset of complete scans) | 15 |
| Windows applications (subset of complete scans) | 11 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 92 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 48 / 92 | 52.17% | 42.09–62.09% |
| Windows | 10 / 92 | 10.87% | 6.01–18.86% |
| Python runtime \(OS unspecified\) | 8 / 92 | 8.7% | 4.47–16.23% |
| Multiple OS \(incl. Windows\) | 5 / 92 | 5.44% | 2.34–12.1% |
| Unknown | 5 / 92 | 5.43% | 2.34–12.1% |
| Android | 3 / 92 | 3.26% | 1.12–9.15% |
| Containers / Kubernetes | 3 / 92 | 3.26% | 1.12–9.15% |
| Linux | 3 / 92 | 3.26% | 1.12–9.15% |
| Node.js tooling/runtime \(OS unspecified\) | 2 / 92 | 2.17% | 0.6–7.58% |
| Shell / automation \(OS unspecified\) | 2 / 92 | 2.17% | 0.6–7.58% |
| Native code \(OS unspecified\) | 1 / 92 | 1.09% | 0.19–5.9% |
| Smart contracts | 1 / 92 | 1.09% | 0.19–5.9% |
| macOS | 1 / 92 | 1.09% | 0.19–5.9% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 92 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| TypeScript | 26 / 92 | 28.26% | 20.08–38.19% |
| JavaScript | 15 / 92 | 16.3% | 10.14–25.17% |
| Python | 15 / 92 | 16.3% | 10.14–25.17% |
| Go | 10 / 92 | 10.87% | 6.01–18.86% |
| HTML | 5 / 92 | 5.43% | 2.34–12.1% |
| Rust | 3 / 92 | 3.26% | 1.12–9.15% |
| C | 2 / 92 | 2.17% | 0.6–7.58% |
| Java | 2 / 92 | 2.17% | 0.6–7.58% |
| Jupyter Notebook | 2 / 92 | 2.17% | 0.6–7.58% |
| Lua | 2 / 92 | 2.17% | 0.6–7.58% |
| C# | 1 / 92 | 1.09% | 0.19–5.9% |
| Go Template | 1 / 92 | 1.09% | 0.19–5.9% |
| Julia | 1 / 92 | 1.09% | 0.19–5.9% |
| Kotlin | 1 / 92 | 1.09% | 0.19–5.9% |
| Lean | 1 / 92 | 1.09% | 0.19–5.9% |
| Luau | 1 / 92 | 1.09% | 0.19–5.9% |
| PHP | 1 / 92 | 1.09% | 0.19–5.9% |
| PLpgSQL | 1 / 92 | 1.09% | 0.19–5.9% |
| PowerShell | 1 / 92 | 1.09% | 0.19–5.9% |
| Unknown | 1 / 92 | 1.09% | 0.19–5.9% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 92 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 43 / 92 | 46.74% | 36.88–56.86% |
| Next.js | 21 / 92 | 22.82% | 15.44–32.39% |
| React | 10 / 92 | 10.87% | 6.01–18.86% |
| FastAPI | 3 / 92 | 3.26% | 1.12–9.15% |
| Vue | 3 / 92 | 3.26% | 1.12–9.15% |
| Spring Boot | 2 / 92 | 2.17% | 0.6–7.58% |
| Svelte | 2 / 92 | 2.17% | 0.6–7.58% |
| Windows Forms | 2 / 92 | 2.17% | 0.6–7.58% |
| Angular | 1 / 92 | 1.09% | 0.19–5.9% |
| Django | 1 / 92 | 1.09% | 0.19–5.9% |
| Electron | 1 / 92 | 1.09% | 0.19–5.9% |
| Express | 1 / 92 | 1.09% | 0.19–5.9% |
| React Native | 1 / 92 | 1.09% | 0.19–5.9% |
| WinUI / Windows App SDK | 1 / 92 | 1.09% | 0.19–5.9% |

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 7 / 11 | 63.64% | 35.38–84.83% |
| Windows Forms | 2 / 11 | 18.18% | 5.14–47.7% |
| Console / other / unknown | 1 / 11 | 9.09% | 1.62–37.74% |
| Cross-platform: .NET MAUI | 1 / 11 | 9.09% | 1.62–37.74% |
| WinUI / Windows App SDK | 1 / 11 | 9.09% | 1.62–37.74% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 8 / 11 | 72.73% | 43.44–90.25% |
| .NET native interop | 3 / 11 | 27.27% | 9.75–56.56% |
| COM | 2 / 11 | 18.18% | 5.14–47.7% |
| DirectX | 0 / 11 | 0.0% | 0.0–25.88% |
| WinRT | 0 / 11 | 0.0% | 0.0–25.88% |
| Windows Registry | 0 / 11 | 0.0% | 0.0–25.88% |
| Windows Shell | 0 / 11 | 0.0% | 0.0–25.88% |
| Windows services | 0 / 11 | 0.0% | 0.0–25.88% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 12 / 15 | 80.0% | 54.81–92.95% |
| .NET native interop | 4 / 15 | 26.67% | 10.9–51.95% |
| COM | 2 / 15 | 13.33% | 3.74–37.88% |
| DirectX | 0 / 15 | 0.0% | 0.0–20.39% |
| WinRT | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows Registry | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows Shell | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows services | 0 / 15 | 0.0% | 0.0–20.39% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| mikelear/leartech-automated-agent | success | Python | Containers / Kubernetes | No framework detected |  |  |
| kaybenleroll/ai\_assisted\_research | success | HTML | Linux | No framework detected |  |  |
| mirai-construction-dx/Construction-Enterprise-OS | partial | HTML | Web | Next.js |  |  |
| Zubs/islamichub | success | JavaScript | Web | Next.js |  |  |
| BodyMaps/BodyMaps-website | success | TypeScript | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| eoko-dev/gideon | success | Python | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| tjstinso/simple-loop | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| Vasile07/ubb-events-backend | success | Java | Windows | Spring Boot | Native / Win32 \(UI not proven\) | Win32 |
| aaron996/kas\_shopee\_performance | success | JavaScript | Web | Svelte |  |  |
| Ticker-Events/whatomate | success | Go | Web | Next.js |  |  |
| briandenicola/Aurearia | success | Go | Web | Vue |  |  |
| gorillanobakaa-dot/Gorilla.Fieldkit | success | Python | Multiple OS \(incl. Windows\) | Windows Forms | Windows Forms | .NET native interop, COM |
| BintzGavin/lean-code-rust | success | Rust | Native code \(OS unspecified\) | No framework detected |  |  |
| raju-santhani/star-log | success | JavaScript | Web | No framework detected |  |  |
| andersonvazvieira/TechStore | success | C# | Multiple OS \(incl. Windows\) | WinUI / Windows App SDK | Cross-platform: .NET MAUI, WinUI / Windows App SDK |  |
| hilather/go-lab-netconf | success | Go | Web | React |  |  |
| JFETA/simple-sticky-notes-codex | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| inrupt/solid-client-access-grants-js | success | TypeScript | Web | Next.js |  |  |
| Tatsh/scenechange | success | C | macOS | No framework detected |  |  |
| tool-jx3/toolkit | success | TypeScript | Web | React |  |  |
| lvahost/hiveku-claude-plugin | success | JavaScript | Unknown | No framework detected |  |  |
| Fchery87/furrow | success | Lua | Python runtime \(OS unspecified\) | No framework detected |  |  |
| madebyjeffrey/sdl-stars | success | C | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| hehaize88-code/hehaize | success | HTML | Web | Next.js |  |  |
| Valorian0108/permanence-protocol | success | TypeScript | Smart contracts | Next.js |  |  |
| ch-holt/UDEs\_recovering\_functional\_forms | success | Julia | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| TheManoeuvre/StockSmith-App | success | Python | Web | React |  |  |
| unmango/go-gmk | success | Go | Unknown | No framework detected |  |  |
| PianoNic/ngx-prompt-kit | success | TypeScript | Web | Angular |  |  |
| henrymosk1011/tenelevenmedia-website | success | HTML | Web | No framework detected |  |  |
| j-grok/cockpit-kit | success | JavaScript | Web | No framework detected |  |  |
| ArloL/nvd-cves | partial | Shell | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| ianlintner/python-oauth2-server | success | Python | Web | FastAPI |  |  |
| aurora-silicon/mesa | partial | C | Multiple OS \(incl. Windows\) | Next.js | Native / Win32 \(UI not proven\) | DirectX, Win32, Windows Registry, Windows Shell |
| mrcjkb/haskell-tools.nvim | success | Lua | Unknown | No framework detected |  |  |
| seeker19110/hotel-manager | success | TypeScript | Web | Next.js |  |  |
| michealet/closet-app | success | TypeScript | Web | Next.js |  |  |
| accountinglms/accountinglms.github.io | success | JavaScript | Web | No framework detected |  |  |
| Let-s-intern/ogonggo-FE | success | TypeScript | Web | Next.js |  |  |
| olly-styles/logbook | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| MOTHblank/pokeidle-addons | success | Rust | Linux | No framework detected |  |  |
| thanhtantran/agents-radar | success | TypeScript | Web | No framework detected |  |  |
| sorrycc/Mayoi | success | Go | Web | Vue |  |  |
| manosliod/score-4 | success | TypeScript | Web | React |  |  |
| kj299/doze\_sec | success | PowerShell | Windows | No framework detected | Native / Win32 \(UI not proven\) | .NET native interop, Win32 |
| stumarti/Shopping-list | success | TypeScript | Web | React Native |  |  |
| HotCode2025/DebuggersUTN-Cuarto-Semestre | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| GiorgiKhorbaladze/PowerSim-repository | success | HTML | Windows | FastAPI | Console / other / unknown |  |
| fredibaques/salesmate | success | TypeScript | Web | Next.js |  |  |
| n8n-io/n8n-kiro-power | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| dipilo/Put-A-Plug-In-it- | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| Father-Pumpkin/ocr | success | TypeScript | Web | React |  |  |
| ashlrai/lexicon | success | TypeScript | Multiple OS \(incl. Windows\) | Windows Forms | Windows Forms | .NET native interop, COM, Win32 |
| ecmwf-projects/c3s2-eqc-quality-assessment | success | Jupyter Notebook | Python runtime \(OS unspecified\) | No framework detected |  |  |
| flashcatcloud/flashduty-cli | success | Go | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| CenterForOpenScience/helm-charts | success | Go Template | Web | Spring Boot |  |  |
| Gcango/equipa1\_plataforma\_pedagogica | success | JavaScript | Web | No framework detected |  |  |
| Oppulence-Engineering/paperless-check-if-email-exists | success | TypeScript | Multiple OS \(incl. Windows\) | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| leveret-dev/leveret | success | TypeScript | Android | Svelte |  |  |
| conda-forge/trove-classifiers-feedstock | success | Unknown | Python runtime \(OS unspecified\) | No framework detected |  |  |
| sdvp-3/poetic-random-generator-images | success | JavaScript | Web | No framework detected |  |  |
| Mpho6746/silent-killer-ai-cvd | success | Jupyter Notebook | Android | FastAPI |  |  |
| ROCm/roc-optiq | partial | C++ | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | Win32, Windows Shell |
| Pavithran030/Pambaram-Game-Development-Project | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| HansKristoffer/agentgate | success | TypeScript | Linux | React |  |  |
| muyuzhong/Featherlog | success | TypeScript | Web | Electron |  |  |
| lander16/voz-local | success | Kotlin | Android | No framework detected |  |  |
| lucacodorean/otel-for-agents | success | Python | Containers / Kubernetes | No framework detected |  |  |
| RedHatInsights/insights-operator-gathering-conditions-service | success | Go | Containers / Kubernetes | No framework detected |  |  |
| sucuklutank123456789-coder/Token-Panel | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| bgstratt/seriesmith | success | Python | Web | React |  |  |
| triade-prog/T-shirtclub.br | success | TypeScript | Web | Next.js |  |  |
| EvolvingAgentsLabs/lora-kernel | success | Python | Web | Next.js |  |  |
| Ju4mpizel/dev-idea | success | JavaScript | Web | Next.js |  |  |
| akshatn70-prog/Shop-Management-Storage-Test | success | PLpgSQL | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| pipecrew-ai/pipecrew | success | JavaScript | Web | No framework detected |  |  |
| BigJohnMoss/Pathfinder1e | success | JavaScript | Web | Next.js |  |  |
| rowan-franciscus/onus-health-application | success | JavaScript | Web | React |  |  |
| auspuru/pte-scoring-api | success | JavaScript | Web | Express |  |  |
| lazyoracle/isotropic-grover-proof | success | Lean | Unknown | No framework detected |  |  |
| ruip005/SD-2026-2027 | success | HTML | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| Azure/sonic-host-services.msft | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| phall1/opencode | partial | TypeScript | Multiple OS \(incl. Windows\) | Windows Forms | Cross-platform: Electron, Windows Forms | .NET native interop, Win32 |
| tawounfouet/pyaccountingkit | success | Python | Web | Django |  |  |
| proteus1208/talenttekpro.com | success | TypeScript | Web | Next.js |  |  |
| Rascal-Company/rascal-pages | success | TypeScript | Web | Next.js |  |  |
| MOdformazione/app-template-custom-shipping-rates | success | TypeScript | Web | Next.js |  |  |
| sadouninc/Sado-Investment-Lab | success | Python | Web | No framework detected |  |  |
| CoolHunter76/ivanllopis | success | Python | Web | Next.js |  |  |
| abrance/ptdoc | success | TypeScript | Web | No framework detected |  |  |
| AtlasRoX/kairos | success | TypeScript | Web | Next.js |  |  |
| bhavikbhoir/the-gooners-world | success | JavaScript | Web | React |  |  |
| fragoulis/pf-goapp | success | Go | Unknown | No framework detected |  |  |
| dirac1974/gavel-race | success | Luau | Python runtime \(OS unspecified\) | No framework detected |  |  |
| nlabrazi/riftvision | success | TypeScript | Web | Vue |  |  |
| julcapp/soft-ice-platform | partial | JavaScript | Web | React |  |  |
| jPurin-gg/fitlog | success | Go | Web | Next.js |  |  |
| zsoltacsai/wpcaregrid | success | PHP | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| ryanduguid/ryanduguid.github.io | success | Rust | Windows | No framework detected | Native / Win32 \(UI not proven\) | .NET native interop, Win32 |
| wmcbay13/ticket-platform | success | Go | Web | React |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
