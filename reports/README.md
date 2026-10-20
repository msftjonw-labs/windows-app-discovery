# Windows app discovery — latest report

Activity window (UTC): 2026-09-20T19:00:00Z → 2026-10-20T19:00:00Z
Generated: 2026-10-20T22:59:13Z  
Ruleset: pilot-3; Application Inspector: 1.10.2

Uniform random sample from 377954 public repositories with qualifying human activity.
Seed: 2026-10-20T19:00:00Z; archive hours: 720/720; qualifying events: 1264946; deleted/private replacements: 4.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.05 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 95 |
| Partial | 0 |
| Failed | 0 |
| No eligible source | 5 |
| Windows candidates (subset of complete scans) | 19 |
| Windows applications (subset of complete scans) | 12 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 33 / 95 | 34.74% | 25.92–44.74% |
| Multiple OS \(incl. Windows\) | 11 / 95 | 11.58% | 6.59–19.55% |
| Python runtime \(OS unspecified\) | 8 / 95 | 8.42% | 4.33–15.75% |
| Windows | 8 / 95 | 8.42% | 4.33–15.75% |
| Node.js tooling/runtime \(OS unspecified\) | 6 / 95 | 6.32% | 2.93–13.1% |
| Linux | 5 / 95 | 5.26% | 2.27–11.73% |
| Containers / Kubernetes | 3 / 95 | 3.16% | 1.08–8.88% |
| Server / backend | 3 / 95 | 3.16% | 1.08–8.88% |
| Shell / automation \(OS unspecified\) | 3 / 95 | 3.16% | 1.08–8.88% |
| WebAssembly | 3 / 95 | 3.16% | 1.08–8.88% |
| Android | 2 / 95 | 2.11% | 0.58–7.35% |
| Multiple OS \(no Windows\) | 2 / 95 | 2.11% | 0.58–7.35% |
| Smart contracts | 2 / 95 | 2.1% | 0.58–7.35% |
| Unknown | 2 / 95 | 2.1% | 0.58–7.35% |
| macOS | 2 / 95 | 2.1% | 0.58–7.35% |
| Native code \(OS unspecified\) | 1 / 95 | 1.05% | 0.19–5.72% |
| iOS | 1 / 95 | 1.05% | 0.19–5.72% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| TypeScript | 21 / 95 | 22.11% | 14.94–31.44% |
| Python | 18 / 95 | 18.95% | 12.33–27.97% |
| JavaScript | 11 / 95 | 11.58% | 6.59–19.55% |
| HTML | 7 / 95 | 7.37% | 3.61–14.44% |
| Go | 6 / 95 | 6.32% | 2.93–13.1% |
| Rust | 6 / 95 | 6.32% | 2.93–13.1% |
| C | 3 / 95 | 3.16% | 1.08–8.88% |
| Java | 3 / 95 | 3.16% | 1.08–8.88% |
| C# | 2 / 95 | 2.11% | 0.58–7.35% |
| Ruby | 2 / 95 | 2.11% | 0.58–7.35% |
| Unknown | 2 / 95 | 2.11% | 0.58–7.35% |
| Blade | 1 / 95 | 1.05% | 0.19–5.72% |
| C++ | 1 / 95 | 1.05% | 0.19–5.72% |
| CSS | 1 / 95 | 1.05% | 0.19–5.72% |
| Dart | 1 / 95 | 1.05% | 0.19–5.72% |
| Jupyter Notebook | 1 / 95 | 1.05% | 0.19–5.72% |
| Kotlin | 1 / 95 | 1.05% | 0.19–5.72% |
| MoonBit | 1 / 95 | 1.05% | 0.19–5.72% |
| PHP | 1 / 95 | 1.05% | 0.19–5.72% |
| PLpgSQL | 1 / 95 | 1.05% | 0.19–5.72% |
| Pep8 | 1 / 95 | 1.05% | 0.19–5.72% |
| PowerShell | 1 / 95 | 1.05% | 0.19–5.72% |
| R | 1 / 95 | 1.05% | 0.19–5.72% |
| Shell | 1 / 95 | 1.05% | 0.19–5.72% |
| Swift | 1 / 95 | 1.05% | 0.19–5.72% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 56 / 95 | 58.95% | 48.9–68.3% |
| Next.js | 12 / 95 | 12.63% | 7.38–20.79% |
| React | 12 / 95 | 12.63% | 7.38–20.79% |
| Electron | 2 / 95 | 2.11% | 0.58–7.35% |
| FastAPI | 2 / 95 | 2.11% | 0.58–7.35% |
| Flutter | 2 / 95 | 2.11% | 0.58–7.35% |
| React Native | 2 / 95 | 2.11% | 0.58–7.35% |
| Spring Boot | 2 / 95 | 2.1% | 0.58–7.35% |
| Express | 1 / 95 | 1.05% | 0.19–5.72% |
| Vue | 1 / 95 | 1.05% | 0.19–5.72% |
| WPF | 1 / 95 | 1.05% | 0.19–5.72% |
| WinUI / Windows App SDK | 1 / 95 | 1.05% | 0.19–5.72% |
| Windows Forms | 1 / 95 | 1.05% | 0.19–5.72% |

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 4 / 12 | 33.33% | 13.81–60.94% |
| Cross-platform: Flutter | 2 / 12 | 16.67% | 4.7–44.8% |
| Console / other / unknown | 1 / 12 | 8.33% | 1.49–35.39% |
| Cross-platform: .NET MAUI | 1 / 12 | 8.33% | 1.49–35.39% |
| Cross-platform: Electron | 1 / 12 | 8.33% | 1.49–35.39% |
| WPF | 1 / 12 | 8.33% | 1.49–35.39% |
| WinUI / Windows App SDK | 1 / 12 | 8.33% | 1.49–35.39% |
| Windows Forms | 1 / 12 | 8.33% | 1.49–35.39% |
| Windows service | 1 / 12 | 8.33% | 1.49–35.39% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 8 / 12 | 66.67% | 39.06–86.19% |
| .NET native interop | 3 / 12 | 25.0% | 8.89–53.23% |
| COM | 3 / 12 | 25.0% | 8.89–53.23% |
| WinRT | 1 / 12 | 8.33% | 1.49–35.39% |
| Windows Registry | 1 / 12 | 8.33% | 1.49–35.39% |
| Windows services | 1 / 12 | 8.33% | 1.49–35.39% |
| DirectX | 0 / 12 | 0.0% | 0.0–24.25% |
| Windows Shell | 0 / 12 | 0.0% | 0.0–24.25% |

## Exploratory: all Windows candidates

Includes libraries/tools; not an application metric.

![Exploratory: all Windows candidates](candidate_components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 15 / 19 | 78.95% | 56.67–91.49% |
| .NET native interop | 3 / 19 | 15.79% | 5.52–37.57% |
| COM | 3 / 19 | 15.79% | 5.52–37.57% |
| WinRT | 1 / 19 | 5.26% | 0.94–24.64% |
| Windows Registry | 1 / 19 | 5.26% | 0.94–24.64% |
| Windows services | 1 / 19 | 5.26% | 0.94–24.64% |
| DirectX | 0 / 19 | 0.0% | 0.0–16.82% |
| Windows Shell | 0 / 19 | 0.0% | 0.0–16.82% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| suitenumerique/meet-whisperx | success | Python | Server / backend | FastAPI |  |  |
| kelesb/SeturMairnas\_tekneciler | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| ekmigasari/sticker | success | TypeScript | Web | React |  |  |
| hardisgroupcom/sfdx-hardis-training | success | JavaScript | Web | No framework detected |  |  |
| taooceros/llm-d | success | Shell | Linux | No framework detected |  |  |
| dae0064-boop/seonggeul-content-hub | success | JavaScript | Windows | Windows Forms | Windows Forms |  |
| mattjowen1991-hue/the-paranormal-pad | success | HTML | Web | No framework detected |  |  |
| sandbaseai/cli | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| neomjs/neo-agent-skills | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| Chris-Wolfgang/ICollection-Extensions | success | PowerShell | Multiple OS \(incl. Windows\) | No framework detected | Console / other / unknown |  |
| mercurial0416-lgtm/moto | success | Unknown | Unknown | No framework detected |  |  |
| mccomercialtda-code/candia-webhook | success | JavaScript | Server / backend | Express |  |  |
| verastack-labs/origan | success | TypeScript | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| jedisherpa/grok-build-tauri-control-panel | success | Rust | Web | No framework detected |  |  |
| FabrizioT04/olimpiadas-innova-2026 | success | TypeScript | Web | React |  |  |
| yuhevita-wq/keirin-market-analysis- | success | Python | Web | Next.js |  |  |
| larsbx/tiling-theory-research | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| ha-homelab/ha-echo-dot | success | Python | macOS | Next.js |  |  |
| edohenik99/courtvision-ai | success | Python | Web | No framework detected |  |  |
| K25043/2026-oop2-github-task3 | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| leandergrech/Mizien | success | Python | Web | No framework detected |  |  |
| fintrack-labs/be-ai-ocr-service | success | JavaScript | Server / backend | No framework detected |  |  |
| kazetani-SE/Arashyn-Project | success | TypeScript | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| Arcade-IFES/Fliperama- | success | TypeScript | Web | React |  |  |
| Horizon-OpenSource/report | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| zidudu/dudu.github.io | success | HTML | Web | No framework detected |  |  |
| temporalio/samples-python | success | Python | Linux | No framework detected |  |  |
| projectpas/PAS\_DB | not\_applicable | TSQL | Unknown | No framework detected |  |  |
| 0xmhha/indexer-go | success | Go | Smart contracts | No framework detected |  |  |
| powell-FCC/medspend | success | TypeScript | Web | React |  |  |
| stackabletech/spark-k8s-operator | success | Rust | Linux | No framework detected |  |  |
| elastic/eui | success | TypeScript | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| jinchenma94/bazi-skill | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| moonbit-community/tonyfettes-unicode | success | MoonBit | Native code \(OS unspecified\) | No framework detected |  |  |
| jeffvato/forgewarden | success | Python | Web | No framework detected |  |  |
| FrancislaineLima/Fsystem-Automa-o-em-python- | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| cafe333/curso-git-practica | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| jaugustodafranca/myprs | success | Swift | macOS | No framework detected |  |  |
| snuhcs-course/swpp-2026-project-team-09 | success | TypeScript | iOS | React Native |  |  |
| riscv-non-isa/riscv-iopmp | success | C | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| Sebastian906/Prescripto-Fullstack | success | TypeScript | Web | Vue |  |  |
| alphagov/whitehall | success | Ruby | Web | No framework detected |  |  |
| Alfredd43/Warehousing-model | success | Python | Web | No framework detected |  |  |
| lovitus/mdd-sim-gateway | success | Go | Multiple OS \(incl. Windows\) | React | Windows service | COM, Win32, Windows services |
| NF-Software-Inc/zkteco-attendance-api | success | C# | Multiple OS \(incl. Windows\) | WinUI / Windows App SDK | Cross-platform: .NET MAUI, WinUI / Windows App SDK |  |
| EdgeApp/edge-core-js | success | TypeScript | Multiple OS \(incl. Windows\) | React Native | Cross-platform: React Native | Win32 |
| KooshaPari/KCode | success | Rust | Multiple OS \(incl. Windows\) | No framework detected | Native / Win32 \(UI not proven\) | .NET native interop, Win32 |
| ChatchaiSornkarn/asmat-saima | success | JavaScript | Web | No framework detected |  |  |
| duindorpdoet/platform | success | PLpgSQL | Web | Next.js |  |  |
| dkam/clinch | success | Ruby | Linux | No framework detected |  |  |
| pep-lang/pepper | success | Pep8 | Multiple OS \(no Windows\) | No framework detected |  |  |
| BD-Chess/bd-chessdb | success | HTML | WebAssembly | Next.js |  |  |
| Team-FINCH/finch-docs | success | HTML | Web | No framework detected |  |  |
| VonNekyia/heroic-map-renderer-plugin | success | Java | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| tk-ud/PrimitiveAppEditer | success | TypeScript | Multiple OS \(incl. Windows\) | Electron | Cross-platform: Electron | .NET native interop, Win32 |
| gentleeduck/duck-ui | success | TypeScript | Web | Next.js |  |  |
| agrorithms/destiny-public | success | TypeScript | Web | Next.js |  |  |
| MrGezz/mrgezz.github.io | success | HTML | Web | No framework detected |  |  |
| KotMatrosk1n/KM-Editor | success | C# | Multiple OS \(incl. Windows\) | WPF | WPF | .NET native interop, Win32 |
| chrispayneseo/alfred | success | Python | Web | React |  |  |
| btcpayserver/woocommerce-greenfield-plugin | success | PHP | Multiple OS \(incl. Windows\) | React | Native / Win32 \(UI not proven\) | Win32 |
| pratikbhadane24/ferro-ta | success | Rust | Multiple OS \(incl. Windows\) | Flutter | Cross-platform: Flutter |  |
| zaventorian/Packs.Ink | success | HTML | Android | Next.js |  |  |
| NatLabRockies/OpenOA | success | Jupyter Notebook | Web | No framework detected |  |  |
| ConductorOne/baton-sumo-logic | success | Go | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| TheNovasoft/Qoute-Match | success | Blade | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| astrogilda/tsbootstrap | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| jniebuhr/gaggimate | success | C | Multiple OS \(incl. Windows\) | React | Native / Win32 \(UI not proven\) | Win32 |
| vtrbraga/pgloupe | success | Rust | Linux | No framework detected |  |  |
| aajll/tickms | success | C | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| frpboy/NahThatsFake | success | HTML | Web | FastAPI |  |  |
| ammerallj/verisimilitude | success | CSS | Web | No framework detected |  |  |
| Mega32K/revelationfix | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| BlockedPath/pi-agent-plugins | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| artisam-heypay/heypay | success | TypeScript | Smart contracts | Next.js |  |  |
| finerreceiver/wg-lo-filter | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| mattermost/mattermost-cloud | success | Go | Containers / Kubernetes | No framework detected |  |  |
| danihrndzld/worship-deck-builder | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| ahiram1701/overdrive | success | JavaScript | Web | No framework detected |  |  |
| corelli18512/kraki | success | TypeScript | Multiple OS \(no Windows\) | Electron |  |  |
| FNGarvin/d3recipes | success | JavaScript | WebAssembly | No framework detected |  |  |
| AnayDhawan/tourneyradar | success | TypeScript | Web | Next.js |  |  |
| virgilelliswade/seshat | success | Kotlin | Android | No framework detected |  |  |
| Revengestyle6/ctcMKWIIstatswebsite | success | Python | Web | React |  |  |
| chrischall/schoolpass-mcp | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| 0mjs/zinc | success | Go | Web | No framework detected |  |  |
| jubiep/CSTU-NEXUS | success | Java | Windows | Spring Boot | Native / Win32 \(UI not proven\) | Win32 |
| czerudla/OpenVideoMapping | success | JavaScript | Web | No framework detected |  |  |
| webees/immich-cn | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| machinachristi/machina-christi | success | JavaScript | Web | Next.js |  |  |
| reveer-ai/jen-cli | success | TypeScript | Containers / Kubernetes | No framework detected |  |  |
| takahashim/dommy-js-zipp | success | Rust | WebAssembly | No framework detected |  |  |
| spiceai/terraform-provider-spiceai | success | Go | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| CDCgov/wastewater-informed-covid-forecasting | success | R | Containers / Kubernetes | No framework detected |  |  |
| afrizahrp/medcal | success | TypeScript | Web | Next.js |  |  |
| animatek/G1-Emu | success | C++ | Windows | No framework detected | Native / Win32 \(UI not proven\) | COM, Win32, WinRT |
| kewrybyun0119/agent\_board | success | Java | Web | Spring Boot |  |  |
| lfit/releng-reusable-workflows | success | Unknown | Unknown | No framework detected |  |  |
| qmediat/cursor-mcp | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| StillMisty/molia | success | Dart | Multiple OS \(incl. Windows\) | Flutter | Cross-platform: Flutter | COM, Win32, Windows Registry |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
