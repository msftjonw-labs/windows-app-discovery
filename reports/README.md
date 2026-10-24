# Windows app discovery — latest report

Activity window (UTC): 2026-09-24T14:00:00Z → 2026-10-24T14:00:00Z
Generated: 2026-10-24T18:19:09Z  
Ruleset: pilot-4; Application Inspector: 1.10.2

Uniform random sample from 370179 public repositories with qualifying human activity.
Seed: 2026-10-24T14:00:00Z; archive hours: 720/720; qualifying events: 1200787; deleted/private replacements: 5.
95% Wilson confidence intervals; worst-case margin for complete scans: ±10.05 percentage points.

| Metric | Repositories |
| --- | ---: |
| Sampled | 100 |
| Complete scans | 95 |
| Partial | 2 |
| Failed | 0 |
| No eligible source | 3 |
| Windows candidates (subset of complete scans) | 15 |
| Windows applications (subset of complete scans) | 11 |

## Target platform

One primary platform per repository: an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last.

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Target platform](platforms.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Web | 41 / 95 | 43.16% | 33.66–53.19% |
| Windows | 12 / 95 | 12.63% | 7.38–20.79% |
| Python runtime \(OS unspecified\) | 11 / 95 | 11.58% | 6.59–19.55% |
| Node.js tooling/runtime \(OS unspecified\) | 5 / 95 | 5.26% | 2.27–11.73% |
| Native code \(OS unspecified\) | 4 / 95 | 4.21% | 1.65–10.33% |
| Unknown | 4 / 95 | 4.21% | 1.65–10.33% |
| Containers / Kubernetes | 3 / 95 | 3.16% | 1.08–8.88% |
| Multiple OS \(incl. Windows\) | 3 / 95 | 3.16% | 1.08–8.88% |
| Multiple OS \(no Windows\) | 2 / 95 | 2.11% | 0.58–7.35% |
| Server / backend | 2 / 95 | 2.11% | 0.58–7.35% |
| iOS | 2 / 95 | 2.11% | 0.58–7.35% |
| .NET runtime \(OS unspecified\) | 1 / 95 | 1.05% | 0.19–5.72% |
| Android | 1 / 95 | 1.05% | 0.19–5.72% |
| Cloud / infrastructure | 1 / 95 | 1.05% | 0.19–5.72% |
| Shell / automation \(OS unspecified\) | 1 / 95 | 1.05% | 0.19–5.72% |
| Smart contracts | 1 / 95 | 1.05% | 0.19–5.72% |
| WebAssembly | 1 / 95 | 1.05% | 0.19–5.72% |

## Primary programming language

GitHub's primary language per repository.

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Primary programming language](languages.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| TypeScript | 26 / 95 | 27.37% | 19.41–37.08% |
| Python | 17 / 95 | 17.89% | 11.48–26.8% |
| JavaScript | 11 / 95 | 11.58% | 6.59–19.55% |
| C++ | 7 / 95 | 7.37% | 3.61–14.44% |
| HTML | 5 / 95 | 5.26% | 2.27–11.73% |
| Go | 4 / 95 | 4.21% | 1.65–10.33% |
| C | 3 / 95 | 3.16% | 1.08–8.88% |
| Java | 3 / 95 | 3.16% | 1.08–8.88% |
| Swift | 3 / 95 | 3.16% | 1.08–8.88% |
| C# | 2 / 95 | 2.11% | 0.58–7.35% |
| Kotlin | 2 / 95 | 2.11% | 0.58–7.35% |
| PHP | 2 / 95 | 2.11% | 0.58–7.35% |
| Rust | 2 / 95 | 2.11% | 0.58–7.35% |
| Astro | 1 / 95 | 1.05% | 0.19–5.72% |
| CSS | 1 / 95 | 1.05% | 0.19–5.72% |
| Elixir | 1 / 95 | 1.05% | 0.19–5.72% |
| PLpgSQL | 1 / 95 | 1.05% | 0.19–5.72% |
| PowerShell | 1 / 95 | 1.05% | 0.19–5.72% |
| Ruby | 1 / 95 | 1.05% | 0.19–5.72% |
| Shell | 1 / 95 | 1.05% | 0.19–5.72% |
| Zig | 1 / 95 | 1.05% | 0.19–5.72% |

## Framework evidence

Most specific detected framework per repository (e.g. Next.js before React).

Each repository belongs to one category; shares total 100% across the 95 complete scans only. Partial, failed, and no-eligible-source repositories are excluded.

![Framework evidence](frameworks.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| No framework detected | 53 / 95 | 55.79% | 45.77–65.36% |
| Next.js | 17 / 95 | 17.9% | 11.48–26.8% |
| React | 13 / 95 | 13.69% | 8.17–22.02% |
| Express | 3 / 95 | 3.16% | 1.08–8.88% |
| Electron | 2 / 95 | 2.11% | 0.58–7.35% |
| Angular | 1 / 95 | 1.05% | 0.19–5.72% |
| Django | 1 / 95 | 1.05% | 0.19–5.72% |
| Flask | 1 / 95 | 1.05% | 0.19–5.72% |
| React Native | 1 / 95 | 1.05% | 0.19–5.72% |
| Spring Boot | 1 / 95 | 1.05% | 0.19–5.72% |
| WPF | 1 / 95 | 1.05% | 0.19–5.72% |
| Windows Forms | 1 / 95 | 1.05% | 0.19–5.72% |

## Project application and automation types

Share of complete repository scans with collected project findings, including libraries/tools and non-Windows PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project findings are excluded. Static indicators do not prove executable or runtime behavior.

![Project application and automation types](project_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| PowerShell | 11 / 95 | 11.58% | 6.59–19.55% |
| Cross-platform: Electron | 2 / 95 | 2.11% | 0.58–7.35% |
| WPF app | 2 / 95 | 2.11% | 0.58–7.35% |
| Windows desktop app | 2 / 95 | 2.11% | 0.58–7.35% |
| Cross-platform: React Native | 1 / 95 | 1.05% | 0.19–5.72% |
| Windows Forms app | 1 / 95 | 1.05% | 0.19–5.72% |
| Service management | 0 / 95 | 0.0% | 0.0–3.89% |
| UWP app | 0 / 95 | 0.0% | 0.0–3.89% |
| WinUI app | 0 / 95 | 0.0% | 0.0–3.89% |
| Windows service | 0 / 95 | 0.0% | 0.0–3.89% |

Classification coverage: 81 repositories had no recognized application type under
the original `pilot-4` rules. They remain in the denominator. The broader
source-based application and automation classification requires a fresh scan with
`pilot-5`; platform labels alone cannot establish these application types.

## Windows application types

Complete Windows application scans; types can overlap.

![Windows application types](application_types.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Native / Win32 \(UI not proven\) | 7 / 11 | 63.64% | 35.38–84.83% |
| PowerShell script | 3 / 11 | 27.27% | 9.75–56.56% |
| WPF | 2 / 11 | 18.18% | 5.14–47.7% |
| Console / other / unknown | 1 / 11 | 9.09% | 1.62–37.74% |
| Cross-platform: Electron | 1 / 11 | 9.09% | 1.62–37.74% |
| Windows Forms | 1 / 11 | 9.09% | 1.62–37.74% |

## Windows component adoption

Complete Windows application scans; components overlap.

![Windows component adoption](components.svg)

| Category | Count / denominator | Share | CI |
| --- | ---: | ---: | --- |
| Win32 | 9 / 11 | 81.82% | 52.3–94.86% |
| .NET native interop | 3 / 11 | 27.27% | 9.75–56.56% |
| COM | 1 / 11 | 9.09% | 1.62–37.74% |
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
| Win32 | 13 / 15 | 86.67% | 62.12–96.26% |
| .NET native interop | 3 / 15 | 20.0% | 7.05–45.19% |
| COM | 1 / 15 | 6.67% | 1.19–29.82% |
| DirectX | 0 / 15 | 0.0% | 0.0–20.39% |
| WinRT | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows Registry | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows Shell | 0 / 15 | 0.0% | 0.0–20.39% |
| Windows services | 0 / 15 | 0.0% | 0.0–20.39% |

## Sampled repositories

| Repository | Scan | Language | Platform | Framework | Windows app types | Components |
| --- | --- | --- | --- | --- | --- | --- |
| YaoYang-123456/NLP-2026-Team08-Structured-Memory | success | Python | Python runtime \(OS unspecified\) | No framework detected | PowerShell script |  |
| juancabernal/software4-SIGRA-frontend | success | TypeScript | Web | Angular |  |  |
| im-herald/aiwf-sandbox | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| bakdata/streams-bootstrap | success | Java | Containers / Kubernetes | No framework detected |  |  |
| swift-ros2/swift-ros2-rosidl | success | Swift | Python runtime \(OS unspecified\) | No framework detected |  |  |
| displaycoffee/portfolio | success | TypeScript | Web | React |  |  |
| Silk-Nodes/tx-silknodes | success | TypeScript | Web | Next.js |  |  |
| mauriziofonte/chat-dump-bookmarklet | success | JavaScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| FedeOlivares/wordcraft | success | Rust | Multiple OS \(incl. Windows\) | Next.js | Console / other / unknown, PowerShell script |  |
| runethorbek/deals | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| saurick/plush-toy-erp | partial | JavaScript | Windows | Next.js | Native / Win32 \(UI not proven\) | .NET native interop, Win32 |
| 2026-2-NCC2/Projeto1 | success | JavaScript | Web | React |  |  |
| Hyperbog/RLOFT | success | C++ | Windows | WPF | PowerShell script, WPF | .NET native interop |
| cosmic-utils/web-apps | success | Rust | Web | No framework detected |  |  |
| lfnovo/open-notebook | success | TypeScript | Web | Next.js |  |  |
| grycap/oscar-hub | success | JavaScript | Web | No framework detected |  |  |
| ARPA-SIMC/arkimaps | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| ESSENTIA-Science/ICAROS-web | success | TypeScript | Web | Next.js |  |  |
| Daemon-Labs-Co/agent-commonroom | success | Go | Web | No framework detected | PowerShell install script, PowerShell script |  |
| jagjitphull/wharf | success | TypeScript | Web | Electron | Cross-platform: Electron |  |
| tans/jack-cases | success | TypeScript | Web | React |  |  |
| wouthh/hardcore-radio-logger | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| tia8910/Walletlens | success | JavaScript | Multiple OS \(incl. Windows\) | React | Native / Win32 \(UI not proven\) | Win32 |
| jamjet-labs/jamjet-policy | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| ryandens/agents | success | Python | Web | Next.js |  |  |
| aws-greengrass/aws-greengrass-component-sdk | success | C | Native code \(OS unspecified\) | No framework detected |  |  |
| gnachman/iTerm2 | success | Swift | Multiple OS \(no Windows\) | No framework detected |  |  |
| alleyinteractive/create-wordpress-project | success | PHP | Web | React |  |  |
| OCIOStateOfNebraska/stateofnebraska-aem | success | JavaScript | Web | No framework detected |  |  |
| jvondermarck/dinosaur-exploder | success | Java | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| zenithloh1016/zhenli-unified-dms | success | JavaScript | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| Jeanwong1222/JingsHomePage | success | HTML | Web | No framework detected |  |  |
| reppiks490/icarus-owner-actions | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| oracle-samples/oracle-aidp-samples | success | Python | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| amariner/logic2b-ui | success | TypeScript | iOS | Next.js |  |  |
| wgtechlabs/build-flow-action | success | Python | Web | No framework detected |  |  |
| lumertzg/zlap | success | Zig | Unknown | No framework detected |  |  |
| johann-han/bsmp | success | TypeScript | Web | Next.js |  |  |
| zeus22ru/wiki\_4 | success | Python | Web | Flask | PowerShell script |  |
| sailfishos/sailfish-browser | success | C++ | Unknown | No framework detected |  |  |
| IronFill/grantplan | success | Astro | Web | No framework detected |  |  |
| codelibs/fess-themes | success | JavaScript | Web | No framework detected |  |  |
| iobroker-community-adapters/ioBroker.mydlink | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| KeibaAI-developer/mykeibadb-python | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| haxeko/ESP32-IoT-Project | success | C++ | Native code \(OS unspecified\) | No framework detected |  |  |
| cavack/WaterfallHunter | success | Python | Web | Next.js |  |  |
| Copinance/copinance-os | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| gryadav7/APNA-BAZAR | success | JavaScript | Server / backend | Express |  |  |
| rebus-org/Rebus.RabbitMq | success | C# | .NET runtime \(OS unspecified\) | No framework detected |  |  |
| mukhamorov95/mglass-app | success | TypeScript | Web | Next.js |  |  |
| coronalabs/corona | partial | C++ | Multiple OS \(incl. Windows\) | WPF | PowerShell script, UWP, WPF | COM, DirectX, Win32, WinRT, Windows Registry, Windows Shell |
| bahaeAether/Marchica-Trips | success | HTML | Web | No framework detected |  |  |
| JetnipitKaewsup/Dormitory-Maintenance-Request-System | success | Java | Windows | Spring Boot | Native / Win32 \(UI not proven\) | Win32 |
| logiclrd/Mesher | success | C++ | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| vf7y0agts7/containers\_\_kubernetes-mcp-server.fcd9bbe6 | success | Go | Containers / Kubernetes | No framework detected |  |  |
| massmedi-cpu/Finanzas-3.0 | success | TypeScript | Web | Next.js |  |  |
| dismanisiao/HISABIYA | success | CSS | Web | React |  |  |
| JensPytlichPersonal/eReader | success | JavaScript | Web | Express |  |  |
| devMuntazirmehdi007/PF\_LAB\_TASK1C | success | C | Unknown | No framework detected |  |  |
| Wedeueis/pyguara | success | Python | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| dhananjay1405/tally-mcp-server | success | TypeScript | Web | Express |  |  |
| AIAllTheThingz/Engineering-Standards | success | PowerShell | Python runtime \(OS unspecified\) | No framework detected | PowerShell install script, PowerShell module, PowerShell script |  |
| mongodb-industry-solutions/snomed-ct-on-mongodb | success | JavaScript | Web | Next.js |  |  |
| Imergent-Technology/flow-life-commons | success | PHP | Windows | React | Native / Win32 \(UI not proven\) | Win32 |
| toanaz-ops/rta-tool | success | C++ | Native code \(OS unspecified\) | No framework detected |  |  |
| Y-0JI/buat-web-screening | success | Python | Windows | Next.js | Native / Win32 \(UI not proven\) | Win32 |
| meringtonupdate-coder/wwq | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| miguns/stelli-website | success | HTML | Web | No framework detected |  |  |
| ragomes102030-cpu/plataforma-obras | success | TypeScript | Web | React |  |  |
| golang-migrate/migrate | success | Go | Containers / Kubernetes | No framework detected |  |  |
| SMozaff/Watermelon-MediaPlayer | success | Kotlin | Android | No framework detected |  |  |
| jwang9228/cwong-art-portfolio | success | TypeScript | Web | Next.js |  |  |
| AmedeoBiolatti/kin | success | C++ | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| Twingate/terraform-provider-twingate | success | Go | Native code \(OS unspecified\) | No framework detected |  |  |
| heathrampazis/loot-wars | success | Swift | iOS | No framework detected |  |  |
| shardapps/clippboard | success | C# | Windows | Windows Forms | PowerShell script, WPF, Windows Forms | .NET native interop, COM, Win32 |
| Azure/azure-functions-skills | success | TypeScript | Cloud / infrastructure | No framework detected | PowerShell script |  |
| lokaliseAutomation/e2e-check-stage | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| CodingGita-Hackathon-Commitee/PixelRush-Team\_Brothers\_SU | success | HTML | Web | No framework detected |  |  |
| Danny-Carvajal/kredian | success | TypeScript | Smart contracts | Next.js |  |  |
| TheAyushTandon/Innovate-Test-Repo | not\_applicable | Unknown | Unknown | No framework detected |  |  |
| simp/pupmod-simp-postfix | success | Ruby | Unknown | No framework detected |  |  |
| SKhousing-co-Ltd/Test | success | PLpgSQL | Web | React | PowerShell script |  |
| hraness/build-governance | success | TypeScript | Web | Next.js |  |  |
| autoguru-au/overdrive | success | TypeScript | Web | React |  |  |
| Galactic717/halo-bot | success | TypeScript | Multiple OS \(incl. Windows\) | Electron | Cross-platform: Electron | .NET native interop, Win32 |
| canhassancode/skills | success | Shell | Shell / automation \(OS unspecified\) | No framework detected |  |  |
| MasayukiYamakura/video-generator-ui | success | JavaScript | Web | No framework detected |  |  |
| Project-Hatchet/Interaction-Framework | success | C++ | Python runtime \(OS unspecified\) | No framework detected |  |  |
| Tami-Mendelman/twitter-app | success | TypeScript | Node.js tooling/runtime \(OS unspecified\) | No framework detected |  |  |
| rickethyo/TurnHub | success | Kotlin | Multiple OS \(no Windows\) | No framework detected | PowerShell script |  |
| ahmedali5530/restaurant-pos | success | TypeScript | Web | React | PowerShell install script, PowerShell script |  |
| jonwilliams84/cli-anything-zigbee2mqtt | success | Python | Python runtime \(OS unspecified\) | No framework detected |  |  |
| techfoundrynz/Pubmote | success | C | WebAssembly | React |  |  |
| azedler/roadplanner | success | Python | Web | React |  |  |
| elixirnaijacommunity/enc\_recipe\_app | success | Elixir | Web | No framework detected |  |  |
| YishenTu/claudian | success | TypeScript | Windows | No framework detected | Native / Win32 \(UI not proven\) | Win32 |
| dimagi-internal/ace | success | TypeScript | Server / backend | Django |  |  |
| suphiozdedee/projenicdesign.com | success | Python | Web | React Native | Cross-platform: React Native |  |
| amoghu26/stat432-fall2026 | success | HTML | Web | No framework detected |  |  |

Static source-level evidence is not proof of runtime use or OS compatibility. Component and application-type categories can overlap. Partial and failed scans are nonresponse; their exclusion can bias estimates. Sampling intervals do not measure classification error or nonresponse bias.

See the [methodology and full metric definitions](../README.md#metric-definitions).
