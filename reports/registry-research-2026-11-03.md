# Cross-OS public-source research - 2026-11-03

Collected (UTC): 2026-11-03T21:16:04.767045+00:00  
Evidence window (UTC): **2026-10-03T20:00:00Z <= timestamp < 2026-11-02T20:00:00Z**  
Population: the same 100 repositories in [the existing discovery assessments](cross-os-assessments.json).

## Findings

**Two projects have verified recent macOS/Linux Homebrew bottle updates. One additional project published Rust source containing explicit Windows/macOS/Linux branches.** These are different evidence tiers: packaging activity and shipped source indicators, not proof of successful cross-OS development or runtime compatibility.

The audit found 18 identity-matched registry packages across nine projects and 576 in-window package versions. None of the matched npm/PyPI/NuGet releases supplied qualifying multi-OS artifact evidence under the checks performed. That is a coverage-limited observation, **not evidence that the projects are single-OS**.

This preserves the original cohort's 30-day window for comparison; it is not a rolling 30 days ending at collection time. Existing GitHub classifications are unchanged. No population prevalence estimate or confidence interval is calculated: package discovery was bounded, coverage differs by ecosystem, and several sources were unavailable.

### Dated cross-OS evidence

| Project | Latest qualifying evidence (UTC) | OS families | Interpretation | Source |
| --- | --- | --- | --- | --- |
| percona/percona-server | 2026-10-24T23:12:38Z | Linux, macOS | Homebrew 9.7.1-1_3: new bottle checksums for both OS families in the same commit; packaging evidence only | [Commit](https://github.com/Homebrew/homebrew-core/commit/b1d421f537e8018b776186ccf2b572a9186c4e40); [formula](https://github.com/Homebrew/homebrew-core/blob/b1d421f537e8018b776186ccf2b572a9186c4e40/Formula/p/percona-server.rb) |
| runkids/skillshare | 2026-10-31T14:47:56Z | Linux, macOS | Homebrew 0.28.2: new bottle checksums for both OS families in the same commit; packaging evidence only | [Commit](https://github.com/Homebrew/homebrew-core/commit/75b5435c2eca6c10f7839044e957e33aaf59d873); [formula](https://github.com/Homebrew/homebrew-core/blob/75b5435c2eca6c10f7839044e957e33aaf59d873/Formula/s/skillshare.rb) |
| OpenVTC/verifiable-git-infrastructure | 2026-11-02T07:48:45.863841Z | Windows, macOS, Linux | `did-git-sign` 0.30.0: published source contains explicit OS branches; not independently built or tested | [Version metadata](https://crates.io/api/v1/crates/did-git-sign/0.30.0); [published archive](https://static.crates.io/crates/did-git-sign/did-git-sign-0.30.0.crate) |

The Rust archive's `src/store.rs:77-86` selects platform-specific credential-store names; `Cargo.toml:152` declares a Linux-only dependency. This is an explicit source indicator, not independent verification of the credential backends. In the same repository, [`vgi-bridge` 0.30.0](https://static.crates.io/crates/vgi-bridge/vgi-bridge-0.30.0.crate) was published at 2026-11-02T07:48:58.377294Z; `src/setup.rs:73-84` selects launchd on macOS and systemd on Linux. Both archives' SHA-256 digests were checked against crates.io version metadata. They count as **one repository**, not two.

For Percona, the newest formula commit on October 30 only added `compatibility_version`; it was **not** counted as a release. The October 24 bottle diff supplies the qualifying evidence. Homebrew's `vhs` formula also lists macOS and Linux bottles, but its latest path change before the window end was September 24, so it is excluded from recent evidence.

### Registry release inventory

Versions include prereleases. Counts are package versions, not commits, projects, or developer activity. Different packages from one repository are not independent projects.

| Project | Registry / packages | In-window versions | Latest timestamp (UTC) | OS evidence from inspected releases |
| --- | --- | ---: | --- | --- |
| ai-ecoverse/slicc-agent | [npm: @ai-ecoverse/slicc-agent](https://registry.npmjs.org/%40ai-ecoverse%2Fslicc-agent) | 279 | 2026-11-02T17:06:54.686Z | No OS allowlist or platform optional dependencies in the collected version metadata |
| anza-xyz/xtask | [crates.io: anza-xtask](https://crates.io/api/v1/crates/anza-xtask) | 1 | 2026-10-27T17:24:44.515437Z | No explicit multi-OS indicators in the latest inspected source archives |
| argmend/argmend | [crates.io: argmend](https://crates.io/api/v1/crates/argmend) | 9 | 2026-10-27T10:29:30.040084Z | No explicit multi-OS indicators in the latest inspected source archives |
| baekenough/oh-my-customcode | [npm: oh-my-customcode](https://registry.npmjs.org/oh-my-customcode) | 22 | 2026-10-26T04:59:34.492Z | No OS allowlist or platform optional dependencies in the collected version metadata |
| Calhooon/bsv-overlay-cloudflare | [crates.io: bsv-low-proof-replay](https://crates.io/api/v1/crates/bsv-low-proof-replay); [crates.io: bsv-overlay-cloudflare](https://crates.io/api/v1/crates/bsv-overlay-cloudflare); [crates.io: bsv-overlay-discovery](https://crates.io/api/v1/crates/bsv-overlay-discovery); [crates.io: bsv-overlay-engine](https://crates.io/api/v1/crates/bsv-overlay-engine) | 80 | 2026-10-19T22:40:27.822806Z | No explicit multi-OS indicators in the latest inspected source archives |
| OpenVTC/verifiable-git-infrastructure | [crates.io: did-git-sign](https://crates.io/api/v1/crates/did-git-sign); [crates.io: verify-trust](https://crates.io/api/v1/crates/verify-trust); [crates.io: vgi-bridge](https://crates.io/api/v1/crates/vgi-bridge); [crates.io: vgi-cli](https://crates.io/api/v1/crates/vgi-cli); [crates.io: vgi-core](https://crates.io/api/v1/crates/vgi-core); [crates.io: vgi-forge-forgejo](https://crates.io/api/v1/crates/vgi-forge-forgejo); [crates.io: vgi-forge-github](https://crates.io/api/v1/crates/vgi-forge-github) | 151 | 2026-11-02T07:48:58.377294Z | Explicit OS source indicators; no multi-OS binary validation |
| OSInside/kiwi | [PyPI: kiwi](https://pypi.org/pypi/kiwi/json) | 5 | 2026-10-27T09:23:29.888600Z | Source distributions only; no platform wheels in the window |
| xiajiajun516/dsh-config-manager | [npm: dsh-config-manager](https://registry.npmjs.org/dsh-config-manager) | 25 | 2026-11-02T19:17:39.762Z | No OS allowlist or platform optional dependencies in the collected version metadata |
| zksecurity/wasmati | [npm: wasmati](https://registry.npmjs.org/wasmati) | 4 | 2026-10-07T15:41:03.629Z | No OS allowlist or platform optional dependencies in the collected version metadata |

## Source coverage

| Source | Candidate queries | Projects queried | Verified package matches | In-window versions | Result / limitation |
| --- | ---: | ---: | ---: | ---: | --- |
| npm | 50 | 42 | 4 | 330 | No OS allowlists or optional dependencies on matched recent versions; generic JS is not OS proof. |
| PyPI | 41 | 25 | 1 | 5 | Only `kiwi` matched; its five recent versions contained source distributions, not OS-tagged wheels. |
| NuGet | 5 | 5 | 0 | 0 | Exact repository-slug package-ID search returned no matching candidates; .csproj PackageId extraction was not performed. |
| crates.io | 41 | 12 | 13 | 241 | 13 matched packages; latest recent archive for each inspected (13 total), not all 241 archives. |
| Maven Central | 12 | 3 | 0 | 0 | Pinned POM coordinates searched; at most 100 indexed versions per coordinate. No verified in-window match; classifiers not inspected. |

Homebrew: scanned current official core/cask file trees for cohort repository-name candidates, plus `mongodb-compass`. Eight candidates were found, three had repository identity links, and two had verified in-window multi-OS bottle diffs. The public JSON host failed DNS resolution, so official Homebrew catalog files and commit history on GitHub were used. This is an external packaging source hosted on GitHub, not an independent non-GitHub transport. The MongoDB Compass cask remained identity-unconfirmed under the exact-repository-link rule.

winget: product-path access returned HTTP 403 with organization SAML enforcement; code search supplied no usable results. No winget findings or negative conclusions are reported.

OSV and NVD: connectivity checks failed DNS resolution. No cohort advisory research was completed. Even when available, advisory publication/modification dates would provide security context, not evidence of development or release activity.

## Method and interpretation

1. Preserve all 100 cohort identities and their original pinned SHAs. Query pinned repository trees for package manifests; inspect at most eight eligible files per repository, ordered by depth/name. Use manifest package names plus primary-language repository-slug candidates. Private npm packages and Cargo packages explicitly marked unpublished are not added as manifest candidates.
2. Require registry repository metadata to identify the exact cohort repository, ignoring case and accepting standard `.git` suffixes. Same-name packages, forks pointing at another upstream, and unrelated dependencies are not accepted as project identities. Registry metadata is publisher-declared, not independently authenticated ownership.
3. Select timestamps within the half-open UTC window. npm uses version publish times; PyPI uses individual file uploads; crates.io uses version creation times. NuGet publication dates and Maven index timestamps would retain their distinct meanings, but produced no verified recent matches.
4. Treat Windows/macOS/Linux as distinct OS families, not architectures. Generic Python wheels, portable languages, missing npm restrictions, generic TFMs and `cfg(unix)` do not prove support for two OS families. Rust textual matches are retained only as source indicators, separately from OS-specific wheel/RID/bottle artifact evidence.
5. Inspect the newest in-window source archive per matched crate, without executing project code. Read `.rs` files and Cargo.toml, excluding test/example/bench/vendor/target directories; limit each file to 1 MB and aggregate source to 5 MB per archive. Inline test code, comments, negative conditions and unbuilt branches can still produce textual matches; contextual review was performed for the cited positive indicators.
6. For accepted Homebrew candidates, inspect path history and the newest in-window bottle commit. Require that the actual added checksum lines include both macOS and Linux; a recent metadata edit alone is insufficient. Bottle metadata was not followed by installing or running bottles.

## Coverage gaps

This is a bounded cohort audit, not an exhaustive registry-wide search. Packages with different names, missing repository links, dynamically computed identities, custom release channels or unsupported manifest formats can be missed. Homebrew name matching can miss aliases or removed formulae. Registry metadata was collected now and can change after publication; source archives and Homebrew revisions provide stronger pinned provenance where available.

Registry queries were made for 78 of 100 projects. Projects without discovered candidates remain unassessed by the registry pass. The original GitHub assessment's ten Cross-OS projects measured documented support, not recent releases; that number must not be added to or replaced by this audit's evidence counts.

Manifest-discovery failures or explicit discovery bounds:

| Project | Limitation |
| --- | --- |
| 0ladymt/mt-pack-organizer-releases | Manifest discovery: HTTPError: HTTP Error 404: Not Found |
| Azure/azure-cli-extensions | Manifest discovery: HTTPError: HTTP Error 403: Forbidden |
| baekenough/oh-my-customcode | Manifest limit: inspected 8 of 9 eligible paths |
| Calhooon/bsv-overlay-cloudflare | Manifest limit: inspected 8 of 10 eligible paths |
| deepmsg/deepmsg | Manifest limit: inspected 8 of 20 eligible paths |
| HHS/simpler-grants-gov | Manifest limit: inspected 8 of 9 eligible paths |
| houraniiiii/Renulus | Manifest limit: inspected 8 of 24 eligible paths |
| Leonn190/PokeTactics | Manifest discovery: ValueError: Response exceeds 12000000 bytes: https://api.github.com/repos/Leonn190/PokeTactics/git/trees/0d2982e8b972b4df44f5ede42e3c1a73313331d0?recursive=1 |
| manwar/perlweeklychallenge-club | Manifest discovery: ValueError: Response exceeds 12000000 bytes: https://api.github.com/repos/manwar/perlweeklychallenge-club/git/trees/3d1fb627ec911dac2eda6bca3bca434990c0ea9f?recursive=1 |
| mongodb-js/compass | Manifest limit: inspected 8 of 77 eligible paths |
| OpenVTC/verifiable-git-infrastructure | Manifest limit: inspected 8 of 9 eligible paths |
| PennyLaneAI/demos | Manifest discovery: ValueError: No pinned SHA in original assessment; manifest discovery unavailable |
| percona/percona-server | Manifest discovery: ValueError: Response exceeds 12000000 bytes: https://api.github.com/repos/percona/percona-server/git/trees/727a975feefe7bcdd796d03e87d0801d5f11f8ca?recursive=1 |
| PostHog/trino | Manifest limit: inspected 8 of 117 eligible paths; Maven io.trino:trino-cli: results limited to 100 indexed versions; Maven io.trino:trino-client: results limited to 100 indexed versions; Maven io.trino:trino-docs: results limited to 100 indexed versions; Maven io.trino:trino-jdbc: results limited to 100 indexed versions; Maven io.trino:trino-main: results limited to 100 indexed versions; Maven io.trino:trino-parser: results limited to 100 indexed versions; Maven io.trino:trino-root: results limited to 100 indexed versions |
| Statsify/statsify | Manifest limit: inspected 8 of 18 eligible paths |
| thiagodmont/greeg | Manifest limit: inspected 8 of 11 eligible paths |

## Audit trail

[Machine-readable evidence](registry-research-2026-11-03.json) includes all 100 cohort entries, pinned SHAs, attempted package names and outcomes, matched identity URLs, recent versions and timestamps, archive checksums, cited source lines, catalog revisions/diffs, source failures and collection bounds. `qualifies` on individual registry releases refers only to the initial multi-OS artifact check; source/archive reviews and Homebrew outcomes are stored separately. No OpenAI API was used.

The table below distinguishes queried-but-unconfirmed entries from entries without candidates; neither means single-OS.

| Project | Registry pass |
| --- | --- |
| 0ladymt/mt-pack-organizer-releases | No registry candidates discovered; discovery gap/bound recorded above |
| aboodmoh724-svg/halqa-followup | Candidates queried; no verified match |
| ai-ecoverse/slicc-agent | Matched registry identity and recent versions |
| ajare/vulkan-poly-pusher | No registry candidates discovered |
| amitmohapatra/agent-memory-service | Candidates queried; no verified match |
| anotherpanacea-eng/apodictic-tauri | Candidates queried; no verified match |
| anthropics/prompt-eng-interactive-tutorial | No registry candidates discovered |
| anza-xyz/xtask | Matched registry identity and recent versions |
| approoveapp/approove | Candidates queried; no verified match |
| argmend/argmend | Matched registry identity and recent versions |
| Austin-Ellefson/Wargame | No registry candidates discovered |
| Azure/azure-cli-extensions | Candidates queried; no verified match; discovery gap/bound recorded above |
| baekenough/oh-my-customcode | Matched registry identity and recent versions; discovery gap/bound recorded above |
| Bambale0/banano_kling | Candidates queried; no verified match |
| basher83/tailnet-microservices | Candidates queried; no verified match |
| BestTeam-MosipDecode/face-liveness-pad | Candidates queried; no verified match |
| Calhooon/bsv-overlay-cloudflare | Matched registry identity and recent versions; discovery gap/bound recorded above |
| Carlos-39/multimodal_presenter | Candidates queried; no verified match |
| CharitonMedia/Tremelay | No registry candidates discovered |
| charmbracelet/vhs | No registry candidates discovered |
| chewtoo22-rgb/SoundMesh | No registry candidates discovered |
| ClarionLive/multiterminal | Candidates queried; no verified match |
| culturesofknowledge/site-front-2 | Candidates queried; no verified match |
| DanielAmah/ai-dev-quiz-app | Candidates queried; no verified match |
| deankim77/jsolution-ai-plm-postgres | Candidates queried; no verified match |
| deepmsg/deepmsg | Candidates queried; no verified match; discovery gap/bound recorded above |
| developerz-ai/multi-ai-router | Candidates queried; no verified match |
| duongcongcao-0312/duannhom5-main | Candidates queried; no verified match |
| eepstein201/jev-mcp | Candidates queried; no verified match |
| EFForg/privacybadger-website | No registry candidates discovered |
| ejb1123/teleport | Candidates queried; no verified match |
| eom-tae-in/ticket-on | No registry candidates discovered |
| faizal97/realm-of-loner | Candidates queried; no verified match |
| farhananwarghumman/TippSend | No registry candidates discovered |
| felipeaugusantos/erpzetech | Candidates queried; no verified match |
| flytiger-eco/TransformerEngine-for-sail | Candidates queried; no verified match |
| GeneralKnowledge/Good-Dog-Book | No registry candidates discovered |
| Gloria-GK-406/DNF-JP-86-Server | Candidates queried; no verified match |
| guruoshan/Paid-Due | No registry candidates discovered |
| HHS/simpler-grants-gov | Candidates queried; no verified match; discovery gap/bound recorded above |
| hockeybuggy/hockeybuggy.com | Candidates queried; no verified match |
| houraniiiii/Renulus | Candidates queried; no verified match; discovery gap/bound recorded above |
| iFixit/govinor | Candidates queried; no verified match |
| jiya-m/capstone | Candidates queried; no verified match |
| johnhenry/workflows | Candidates queried; no verified match |
| julienld/ha-mcp-native | Candidates queried; no verified match |
| justinhunt/moodle-repository_cloudpoodll | No registry candidates discovered |
| karagemop466-tech/LOLHOTSPAWN2 | Candidates queried; no verified match |
| konstelasi/StarDustDocs | Candidates queried; no verified match |
| KrzysztofMarciniak/scjson | No registry candidates discovered |
| Leonn190/PokeTactics | Candidates queried; no verified match; discovery gap/bound recorded above |
| manh-vv/docb | Candidates queried; no verified match |
| manwar/perlweeklychallenge-club | No registry candidates discovered; discovery gap/bound recorded above |
| mathildekw/mathildekw | No registry candidates discovered |
| michael-bachmann/lineitem | Candidates queried; no verified match |
| MichaelUserBro/SeaBattle | No registry candidates discovered |
| misospace/pr-reviewer-action | Candidates queried; no verified match |
| miszyszka/Epcido-Terminal | Candidates queried; no verified match |
| Mitchk1995/dragonbound | Candidates queried; no verified match |
| mlengse/orthos | Candidates queried; no verified match |
| mongodb-js/compass | Candidates queried; no verified match; discovery gap/bound recorded above |
| Ndegwa4943/Merstat-FrontEnd | No registry candidates discovered |
| nextcloud/logreader | Candidates queried; no verified match |
| OpenVTC/verifiable-git-infrastructure | Matched registry identity and recent versions; discovery gap/bound recorded above |
| OSInside/kiwi | Matched registry identity and recent versions |
| PenguinMod/PenguinMod-ExtensionsGallery | Candidates queried; no verified match |
| PennyLaneAI/demos | No registry candidates discovered; discovery gap/bound recorded above |
| percona/percona-server | No registry candidates discovered; discovery gap/bound recorded above |
| pingvis/Nida-Windows | Candidates queried; no verified match |
| pontago/otenki-live | Candidates queried; no verified match |
| PostHog/trino | Candidates queried; no verified match; discovery gap/bound recorded above |
| Prekzursil/fractal-darkroom | Candidates queried; no verified match |
| Project-Colony/Xion | Candidates queried; no verified match |
| protoLabsAI/protobanana-plugin | Candidates queried; no verified match |
| Quimia-br/quimia-web-crud | Candidates queried; no verified match |
| rafs2006/optimus | Candidates queried; no verified match |
| rckearns/sitescan-frontend | Candidates queried; no verified match |
| RestartDK/dotfiles | Candidates queried; no verified match |
| richardpowellus/invisible_playwright_mcp | Candidates queried; no verified match |
| robert-koch-institut/mex-backend | Candidates queried; no verified match |
| robot-pesg/NavSR | No registry candidates discovered |
| rootscripts/riff | Candidates queried; no verified match |
| Rufics/fpv-radio-map | Candidates queried; no verified match |
| runkids/skillshare | Candidates queried; no verified match |
| sandeepkumarkrprabhu/ZYRAHRM-Backend | Candidates queried; no verified match |
| sebrandon1/imagecertinfo-operator | No registry candidates discovered |
| solaranoir/pocketsat-testlab | Candidates queried; no verified match |
| Statsify/statsify | Candidates queried; no verified match; discovery gap/bound recorded above |
| stavroskasidis/codalus-ide | Candidates queried; no verified match |
| Stiftelsen-Hulen/hulen.no | Candidates queried; no verified match |
| TandemVector-Labs/.github | Candidates queried; no verified match |
| thiagodmont/greeg | Candidates queried; no verified match; discovery gap/bound recorded above |
| ThreeMonth03/Conjugate-Gradient-Method-library | Candidates queried; no verified match |
| tnt007tarun/StreamCast | Candidates queried; no verified match |
| TurnGui/catchlog-api | Candidates queried; no verified match |
| twhitelow1/anthony-insurance-services-forms | Candidates queried; no verified match |
| vegekyd-sys/v-nightshift | Candidates queried; no verified match |
| xex-ken-xex/ai-gm-bridge | Candidates queried; no verified match |
| xiajiajun516/dsh-config-manager | Matched registry identity and recent versions |
| zksecurity/wasmati | Matched registry identity and recent versions |

## Independent discovery results

The table summarizes bounded, source-first discovery for the same 30-day window above. These searches were not seeded from the existing 100-project cohort. Counts are source-specific packages, formulae, or sampled candidates, not a deduplicated count of projects. “Unavailable” and “inconclusive” do not mean no cross-OS activity.

| Source | Candidates inspected | Multi-OS evidence found | High-level result |
| --- | ---: | ---: | --- |
| npm | 100 | 1 package | Dated optional platform packages for Windows, macOS, and Linux |
| PyPI | 95 | 7 packages | In-window wheels tagged for at least two OS families |
| NuGet | 100 | 0 | No multi-OS runtime-identifier assets in this bounded sample |
| crates.io | 100 | 17 crates | Published source contains explicit OS-specific branches; 14 distinct declared repository URLs, not build verification |
| Maven Central | 0 | Inconclusive | Search index returned no in-window entries; its freshness check was stale |
| Homebrew | 100 commits | 36 formulae | In-window bottle updates added macOS and Linux checksums |
| winget | Unavailable | Not assessed | Public API access blocked by organization SAML enforcement |
| OSV | Unavailable | Not assessed | Source access unavailable; advisories indicate security context, not development activity |
| NVD | Unavailable | Not assessed | Source access unavailable; advisories indicate security context, not development activity |

Package and formula metadata are evidence of platform-specific distribution or source intent, not proof of successful builds or runtime compatibility. The bounded feeds are not exhaustive or representative; package names may not map one-to-one to upstream projects. No combined total or prevalence estimate is calculated. Machine-readable collection evidence remains available separately in [the source-first audit data](registry-research-2026-11-03-independent.json).
