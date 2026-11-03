# Cross-OS public-source research - 2026-11-03

Collected (UTC): 2026-11-03T21:16:04.767045+00:00  
Evidence window (UTC): **2026-10-03T20:00:00Z <= timestamp < 2026-11-02T20:00:00Z**  
Population: the same 100 repositories in [the existing discovery assessments](cross-os-assessments.json).

This report has two separate scopes: the original cohort audit below, followed by
[independent discovery from each source](#independent-discovery-from-each-source).
The independent section is not restricted to those 100 repositories and has its own
candidate counts, findings and audit evidence.

## Cohort audit findings

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

## Independent discovery from each source

Appended (UTC): 2026-11-03T21:47:07.484409+00:00. This is **source-first discovery**, not additional scanning of the 100-project cohort. No cohort repository names, languages or manifests were used as discovery inputs. Repository URLs are optional descriptive metadata, not an eligibility requirement.

The evidence window remains **2026-10-03T20:00:00Z <= timestamp < 2026-11-02T20:00:00Z**. The bound is at most 100 root candidates per source, not 100 positive projects. Historical feeds were used where available; current-feed/search seeds are explicitly identified below. Dependencies and version-history lookups enrich those root candidates rather than enlarge the root sample.

OS checks in this audit cover Windows, macOS and Linux. Android, iOS and other
operating systems were not systematically classified.

**Results:** one npm package has dated multi-OS optional-package metadata; seven PyPI packages have in-window wheels for multiple OS families; 17 Rust packages have textual multi-OS source indicators (14 distinct declared GitHub repositories); and 36 Homebrew formulae have in-window macOS/Linux bottle-checksum updates. These evidence tiers must not be added together as a unique-project count or interpreted as verified runtime support.

### Independent source coverage

| Source | Root candidates | Positive package/formula IDs | Evidence / outcome |
| --- | ---: | ---: | --- |
| npm | 100 | 1 | Dated platform optional-package metadata; relevance-ranked cross-platform search, not a random sample |
| PyPI | 95 | 7 | Multi-OS wheel metadata; current RSS seeds, historical file-upload dates |
| NuGet | 100 | 0 | No multi-OS RID asset evidence in this catalog slice; not proof of no cross-OS packages |
| crates.io | 100 | 17 | Textual source indicators only; not build/runtime validation |
| Maven Central | 0 | 0 | Search returned no in-window entries; index freshness concern, not zero ecosystem activity |
| Homebrew | 100 | 36 | 41 qualifying commit events across 36 distinct formula paths; packaging metadata, not upstream coding |
| winget | 0 | Not assessed | Unavailable: organization SAML enforcement (HTTP 403) |
| OSV | 0 | Not assessed | Unavailable: bulk-index access failed; advisory context only |
| NVD | 0 | Not assessed | Unavailable: DNS failure; advisory context only |

No confidence intervals, ecosystem prevalence percentages or combined cohort denominator are appropriate. Candidate units differ (packages, versions and commits), current feeds favor projects active at collection time, and multiple packages can belong to one upstream project.

### Independent discovery: npm

Discovery endpoint: [npm feed/search](https://registry.npmjs.org/-/v1/search?text=cross-platform&size=100).

**Selection:** First 100 relevance-ranked results for cross-platform; theme-biased, not chronological or representative.

**Limits:** Replication feed DNS failed. Inspect all in-window root versions; at most 20 optional dependencies per version, exact versions only. Dependencies are not asserted to be the root project's own code. Metadata only; binaries not downloaded.

The npm replication-feed host failed DNS resolution, so discovery used the first 100 relevance-ranked `cross-platform` search results. 32 root packages had in-window version publications. This intentionally theme-biased search can overrepresent advertised portability and misses packages with no matching search terms.

| Package | Root version | Root publication (UTC) | Dated dependency targets | Evidence |
| --- | --- | --- | --- | --- |
| `@crowecawcaw/xa11y` | 0.15.4 | 2026-10-24T13:00:12.350Z | Linux, Windows, macOS | [Root metadata](https://registry.npmjs.org/%40crowecawcaw%2Fxa11y) |

`@crowecawcaw/xa11y` versions 0.15.3 and 0.15.4 reference exact-version optional packages whose metadata declares macOS, Linux and Windows targets and whose publication timestamps also fall in the window. Individual dependency timestamps and tarball URLs are in the audit file. This proves a declared multi-OS package arrangement, not that those tarballs contain working binaries or that all dependency code is authored by the root project.

### Independent discovery: PyPI

Discovery endpoint: [PyPI feed/search](https://pypi.org/rss/updates.xml).

**Selection:** Up to 100 items from the current recent-updates RSS feed, deduplicated by project; inspect those projects' historical in-window files.

**Limits:** RSS is a short current feed, not an archive of the window; projects absent from today's feed are missed. Wheel metadata inspected; archives not executed.

The current RSS snapshot supplied 100 events and 95 distinct project candidates; 74 had file uploads inside the historical window. The feed itself is not a complete history of the window. Positive rows require non-yanked OS-tagged wheels for the same version, each uploaded within the window; `*-none-any.whl` does not qualify.

| Package | Latest qualifying version | Latest in-window file upload (UTC) | OS families | Evidence |
| --- | --- | --- | --- | --- |
| `fs-assets` | 0.2.2 | 2026-11-02T19:11:06.279983Z | Linux, Windows, macOS | [Version files](https://pypi.org/pypi/fs-assets/0.2.2/json) |
| `geode-common` | 33.27.1 | 2026-10-31T00:40:32.021732Z | Linux, Windows | [Version files](https://pypi.org/pypi/geode-common/33.27.1/json) |
| `luminamoon` | 1.0.8.post1 | 2026-10-29T21:06:28.376266Z | Linux, Windows, macOS | [Version files](https://pypi.org/pypi/luminamoon/1.0.8.post1/json) |
| `managed-deepagents` | 0.10.2.dev2 | 2026-11-02T17:56:16.438973Z | Linux, Windows, macOS | [Version files](https://pypi.org/pypi/managed-deepagents/0.10.2.dev2/json) |
| `pqbench` | 0.0.10 | 2026-11-01T09:57:44.045763Z | Linux, macOS | [Version files](https://pypi.org/pypi/pqbench/0.0.10/json) |
| `pyblanket` | 0.2.0 | 2026-10-28T20:40:17.377805Z | Linux, macOS | [Version files](https://pypi.org/pypi/pyblanket/0.2.0/json) |
| `pynesys-pynecore` | 6.12.0 | 2026-10-30T15:36:44.613195Z | Linux, Windows, macOS | [Version files](https://pypi.org/pypi/pynesys-pynecore/6.12.0/json) |

Wheel filenames, OS tags, per-file timestamps, hashes, yanked flags and download URLs are recorded. These establish platform-specific distribution declarations; installation and runtime behavior were not tested. Prerelease/dev versions are included.

### Independent discovery: NuGet

Discovery endpoint: [NuGet feed/search](https://api.nuget.org/v3/catalog0/index.json).

**Selection:** 100 distinct in-window package/version catalog events, newest first, from up to five pages, including the boundary-straddling page.

**Limits:** Catalog commit dates select candidates; actual publication dates select evidence. Edit events can describe old publications. Version events are not 100 distinct projects. Catalog entry filenames are inspected, not installed.

The selected catalog page supplied 100 distinct package/version events and 100 distinct package IDs; 94 had actual publication timestamps inside the window. Catalog commit timestamps select candidates; actual `published` timestamps determine in-window releases. Catalog detail `packageEntries[].fullName` fields were inspected for real `runtimes/win*`, `runtimes/linux-*` and `runtimes/osx-*` assets, excluding `_._` placeholders. No candidate had qualifying assets for two families.

This does not inspect related packages or platform-specific TFMs, so packages using those distribution patterns can be missed. Catalog detail URLs and exact version IDs are preserved in the evidence file; generic .NET TFMs are not counted as multi-OS proof.

### Independent discovery: crates.io

Discovery endpoint: [crates.io feed/search](https://crates.io/api/v1/crates?sort=recent-updates&per_page=100&page=1).

**Selection:** 100 crates from the current recently-updated feed; inspect their historical in-window versions.

**Limits:** Current feed is not a historical census. Latest non-yanked in-window source archive per candidate inspected; positive textual cfg indicators are not build/runtime proof. 12 MB archive, 1 MB/file, 5 MB total source bounds.

100 independent candidates came from `sort=recent-updates`; 79 had non-yanked versions inside the historical window. For each of those, the newest eligible archive was downloaded and its SHA-256 checked against registry metadata. No project code was executed. The positive rows below are **textual source indicators**, not confirmed cross-OS applications.

| Crate | Version | Publication (UTC) | OS mentions | One cited source location per OS | Evidence |
| --- | --- | --- | --- | --- | --- |
| `aither-agent` | 0.11.0 | 2026-10-29T08:25:38.377568Z | Linux, Windows, macOS | Linux: `aither-agent-0.11.0/src/terminal_agent.rs:1139`; Windows: `aither-agent-0.11.0/src/terminal_agent.rs:360`; macOS: `aither-agent-0.11.0/src/terminal_agent.rs:585` | [Archive](https://static.crates.io/crates/aither-agent/aither-agent-0.11.0.crate) |
| `aither-sandbox` | 0.11.0 | 2026-10-29T08:24:31.210660Z | Linux, Windows, macOS | Linux: `aither-sandbox-0.11.0/src/jobserver.rs:35`; Windows: `aither-sandbox-0.11.0/src/bollard_exec.rs:475`; macOS: `aither-sandbox-0.11.0/src/stdin_watch.rs:597` | [Archive](https://static.crates.io/crates/aither-sandbox/aither-sandbox-0.11.0.crate) |
| `claude-history` | 0.1.81 | 2026-10-27T22:54:46.885372Z | Linux, macOS | Linux: `claude-history-0.1.81/src/daemon/power.rs:30`; macOS: `claude-history-0.1.81/src/bench.rs:137` | [Archive](https://static.crates.io/crates/claude-history/claude-history-0.1.81.crate) |
| `decapod` | 0.121.2 | 2026-11-01T06:36:36.292136Z | Linux, Windows, macOS | Linux: `decapod-0.121.2/src/decapod/core/bounded_process/signal.rs:222`; Windows: `decapod-0.121.2/src/decapod/core/dactyl.rs:220`; macOS: `decapod-0.121.2/assets/tools/vega_infer.rs:1234` | [Archive](https://static.crates.io/crates/decapod/decapod-0.121.2.crate) |
| `hotpath` | 0.30.3 | 2026-10-31T10:07:05.570606Z | Linux, Windows, macOS | Linux: `hotpath-0.30.3/Cargo.toml:760`; Windows: `hotpath-0.30.3/src/lib_on/threads/collector_windows.rs:322`; macOS: `hotpath-0.30.3/src/instant.rs:4` | [Archive](https://static.crates.io/crates/hotpath/hotpath-0.30.3.crate) |
| `hotpath-meta` | 0.30.3 | 2026-10-31T10:06:51.386385Z | Linux, Windows, macOS | Linux: `hotpath-meta-0.30.3/Cargo.toml:328`; Windows: `hotpath-meta-0.30.3/src/lib_on/threads/collector_windows.rs:322`; macOS: `hotpath-meta-0.30.3/src/instant.rs:4` | [Archive](https://static.crates.io/crates/hotpath-meta/hotpath-meta-0.30.3.crate) |
| `mitts` | 0.3.18 | 2026-11-02T18:20:20.211033Z | Linux, Windows, macOS | Linux: `mitts-0.3.18/src/adapter/rust/build_script_keys.rs:255`; Windows: `mitts-0.3.18/src/cli/coverage_tools.rs:66`; macOS: `mitts-0.3.18/src/adapter/rust/build_script_keys.rs:251` | [Archive](https://static.crates.io/crates/mitts/mitts-0.3.18.crate) |
| `n11-deadbolt` | 2.0.0 | 2026-10-12T23:53:44.574511Z | Linux, Windows, macOS | Linux: `n11-deadbolt-2.0.0/src/private_state.rs:240`; Windows: `n11-deadbolt-2.0.0/src/private_state.rs:166`; macOS: `n11-deadbolt-2.0.0/src/private_state.rs:200` | [Archive](https://static.crates.io/crates/n11-deadbolt/n11-deadbolt-2.0.0.crate) |
| `oneharness-core` | 0.29.1 | 2026-10-23T01:43:13.907712Z | Linux, Windows, macOS | Linux: `oneharness-core-0.29.1/src/io/app_server.rs:909`; Windows: `oneharness-core-0.29.1/src/io/cancel.rs:168`; macOS: `oneharness-core-0.29.1/src/domain/control.rs:1120` | [Archive](https://static.crates.io/crates/oneharness-core/oneharness-core-0.29.1.crate) |
| `onepipeline` | 0.98.2 | 2026-11-02T12:45:39.221559Z | Linux, Windows | Linux: `onepipeline-0.98.2/src/driver.rs:3976`; Windows: `onepipeline-0.98.2/src/driver.rs:5473` | [Archive](https://static.crates.io/crates/onepipeline/onepipeline-0.98.2.crate) |
| `rete-cli` | 0.5.0 | 2026-11-02T13:45:55.403385Z | Linux, Windows | Linux: `rete-cli-0.5.0/src/commands/range_source.rs:517`; Windows: `rete-cli-0.5.0/src/commands/range_source.rs:424` | [Archive](https://static.crates.io/crates/rete-cli/rete-cli-0.5.0.crate) |
| `rete-core` | 0.5.0 | 2026-11-02T13:44:10.331823Z | Linux, Windows | Linux: `rete-core-0.5.0/src/sysmem.rs:262`; Windows: `rete-core-0.5.0/src/extbuild_v06.rs:138` | [Archive](https://static.crates.io/crates/rete-core/rete-core-0.5.0.crate) |
| `rightkit-fs` | 0.4.9 | 2026-11-01T12:33:59.966771Z | Linux, Windows, macOS | Linux: `rightkit-fs-0.4.9/src/atomic.rs:695`; Windows: `rightkit-fs-0.4.9/src/app_dirs.rs:513`; macOS: `rightkit-fs-0.4.9/src/acl.rs:51` | [Archive](https://static.crates.io/crates/rightkit-fs/rightkit-fs-0.4.9.crate) |
| `songrec` | 0.8.0 | 2026-10-27T11:09:36.150601Z | Linux, Windows | Linux: `songrec-0.8.0/Cargo.toml:230`; Windows: `songrec-0.8.0/src/gui/main_window.rs:40` | [Archive](https://static.crates.io/crates/songrec/songrec-0.8.0.crate) |
| `text-typeset` | 3.0.0 | 2026-10-29T10:17:15.248262Z | Windows, macOS | Windows: `text-typeset-3.0.0/src/font/script_fallback.rs:110`; macOS: `text-typeset-3.0.0/src/font/script_fallback.rs:112` | [Archive](https://static.crates.io/crates/text-typeset/text-typeset-3.0.0.crate) |
| `vivida` | 0.2.5 | 2026-10-20T20:13:09.653073Z | Linux, Windows, macOS | Linux: `vivida-0.2.5/src/chrome.rs:38`; Windows: `vivida-0.2.5/build.rs:1`; macOS: `vivida-0.2.5/Cargo.toml:82` | [Archive](https://static.crates.io/crates/vivida/vivida-0.2.5.crate) |
| `vvmux` | 0.5.5 | 2026-10-20T20:49:34.944580Z | Linux, Windows, macOS | Linux: `vvmux-0.5.5/src/agent.rs:2034`; Windows: `vvmux-0.5.5/src/agent.rs:91`; macOS: `vvmux-0.5.5/src/agent.rs:84` | [Archive](https://static.crates.io/crates/vvmux/vvmux-0.5.5.crate) |

Multiple crates can share an upstream: `rete-cli`/`rete-core`, `hotpath`/`hotpath-meta`, and `aither-agent`/`aither-sandbox` each share a declared repository. Thus 17 package matches map to 14 distinct declared GitHub repositories, without verifying ownership or successful builds. Source matches can occur in inline tests, diagnostic names or unbuilt branches. Simple negated cfg lines and comment-only lines were excluded; this is not semantic Rust analysis.

### Independent discovery: Maven Central

Discovery endpoint: [Maven Central feed/search](https://search.maven.org/solrsearch/select?q=timestamp%3A%5B1791057600000+TO+1793649599999%5D&core=gav&rows=100&wt=json).

**Selection:** Up to 100 indexed artifact versions whose index timestamps fall in the window; server ranking retained.

**Limits:** Index timestamps are not guaranteed publication dates. No returned artifacts means no classifier evidence; not proof of no Central publications.

The version-index query restricted `timestamp` to the exact window and returned zero entries. A [separate unfiltered freshness probe](https://search.maven.org/solrsearch/select?q=%2A%3A%2A&core=gav&rows=1&wt=json) returned an artifact indexed at **2026-06-10T12:52:21+00:00**, well before this window. This is a warning about the accessible search index, not proof that Central had no recent releases. The alternative Central browse API host also failed DNS resolution.

No artifacts or classifiers were available to inspect from this time-filtered result, so independent Maven cross-OS discovery remains **inconclusive**.

### Independent discovery: Homebrew

Discovery endpoints: [official catalog commit feed 1](https://api.github.com/repos/Homebrew/homebrew-core/commits?path=Formula&since=2026-10-03T20%3A00%3A00Z&until=2026-11-02T20%3A00%3A00Z&per_page=50); [official catalog commit feed 2](https://api.github.com/repos/Homebrew/homebrew-cask/commits?path=Casks&since=2026-10-03T20%3A00%3A00Z&until=2026-11-02T20%3A00%3A00Z&per_page=50).

**Selection:** 50 newest in-window commits each from official core and cask paths; one alphabetical eligible file per commit.

**Limits:** 100 commit candidates, not 100 distinct products. Multi-file commits inspect only the first eligible file. Only added macOS/Linux bottle checksum lines qualify. JSON API DNS failed; catalogs are external packaging evidence hosted on GitHub.

The two independent commit feeds supplied 100 commit candidates, covering 73 distinct inspected formula/cask paths. 41 commits added both macOS and Linux bottle checksums, covering 36 formula paths. Repeated commits for the same formula are deduplicated below, retaining the newest qualifying event. Cask-only macOS activity does not establish cross-OS support.

| Formula | Latest qualifying packaging commit (UTC) | OS families | Evidence |
| --- | --- | --- | --- |
| `Formula/a/air.rb` | 2026-11-02T18:48:48Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/1dc10eaaddfcec795c2402f5bec05f85da04d2e2); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/1dc10eaaddfcec795c2402f5bec05f85da04d2e2/Formula/a/air.rb) |
| `Formula/a/aube.rb` | 2026-11-02T18:49:28Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/a32deb7c4d91e273daef73ed98a65933f43a1bb7); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/a32deb7c4d91e273daef73ed98a65933f43a1bb7/Formula/a/aube.rb) |
| `Formula/a/auditbeat.rb` | 2026-11-02T18:51:24Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/4fff8f4182de245e9dcc087bce94fc88aac97d14); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/4fff8f4182de245e9dcc087bce94fc88aac97d14/Formula/a/auditbeat.rb) |
| `Formula/b/bazel-diff.rb` | 2026-11-02T18:48:57Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/44b2b0805abe5574033aa8b86b684ac55ab7da3c); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/44b2b0805abe5574033aa8b86b684ac55ab7da3c/Formula/b/bazel-diff.rb) |
| `Formula/b/bitrise.rb` | 2026-11-02T18:49:34Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/ed6a684647b37017c47530e1a36c2d6344b7cd9a); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/ed6a684647b37017c47530e1a36c2d6344b7cd9a/Formula/b/bitrise.rb) |
| `Formula/b/bump-my-version.rb` | 2026-11-02T18:48:28Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/5962a839a5187899fea67095a1bb442099e8e3ab); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/5962a839a5187899fea67095a1bb442099e8e3ab/Formula/b/bump-my-version.rb) |
| `Formula/d/docker-agent.rb` | 2026-11-02T18:48:31Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/0f2fa504582f1e7f8d16cd21d44202a2560adf35); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/0f2fa504582f1e7f8d16cd21d44202a2560adf35/Formula/d/docker-agent.rb) |
| `Formula/d/dua-cli.rb` | 2026-11-02T19:59:22Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/4765edd4b1bc894c062696b914a0f11c6242f5dc); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/4765edd4b1bc894c062696b914a0f11c6242f5dc/Formula/d/dua-cli.rb) |
| `Formula/e/elio.rb` | 2026-11-02T19:58:58Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/30712f86c68eec56b06a15b25e80d103125755a2); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/30712f86c68eec56b06a15b25e80d103125755a2/Formula/e/elio.rb) |
| `Formula/e/expat.rb` | 2026-11-02T18:50:31Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/f8d3c2f3bcadff5891deaa3e87f7fe2eb3def61e); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/f8d3c2f3bcadff5891deaa3e87f7fe2eb3def61e/Formula/e/expat.rb) |
| `Formula/f/flowrs.rb` | 2026-11-02T18:48:29Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/9983ae53cf1d1826ffdb207af66bd453efe4263f); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/9983ae53cf1d1826ffdb207af66bd453efe4263f/Formula/f/flowrs.rb) |
| `Formula/i/imgproxy.rb` | 2026-11-02T18:49:07Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/21270dff5b62fb22d9ac8a1eb82fed0273f177ec); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/21270dff5b62fb22d9ac8a1eb82fed0273f177ec/Formula/i/imgproxy.rb) |
| `Formula/i/infisical.rb` | 2026-11-02T18:48:25Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/6265fa8cbd9b7b7e43de5282a1b31d6420fea458); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/6265fa8cbd9b7b7e43de5282a1b31d6420fea458/Formula/i/infisical.rb) |
| `Formula/k/krakend.rb` | 2026-11-02T18:48:43Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/9b102af43f0b00f6b7b34821d1b9df2235c00ba5); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/9b102af43f0b00f6b7b34821d1b9df2235c00ba5/Formula/k/krakend.rb) |
| `Formula/l/ldcli.rb` | 2026-11-02T18:48:39Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/90dd990639b6c2a7b93806c7394649f0b5911b0e); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/90dd990639b6c2a7b93806c7394649f0b5911b0e/Formula/l/ldcli.rb) |
| `Formula/l/lexicon.rb` | 2026-11-02T18:49:12Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/61d69a48d9cdd90a49164c881c83923ff38b34c7); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/61d69a48d9cdd90a49164c881c83923ff38b34c7/Formula/l/lexicon.rb) |
| `Formula/lib/libnghttp2.rb` | 2026-11-02T19:26:10Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/36ab4d6eeda6468e049c392757629ab3474a9dbd); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/36ab4d6eeda6468e049c392757629ab3474a9dbd/Formula/lib/libnghttp2.rb) |
| `Formula/lib/libnghttp3.rb` | 2026-11-02T19:58:59Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/6b046f08cbb5cd8da2c1a8ee72d607a239e1a8c2); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/6b046f08cbb5cd8da2c1a8ee72d607a239e1a8c2/Formula/lib/libnghttp3.rb) |
| `Formula/lib/libvirt-python.rb` | 2026-11-02T19:58:44Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/dc85bbb353b8fd5cb0dee7a2df533224b926a269); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/dc85bbb353b8fd5cb0dee7a2df533224b926a269/Formula/lib/libvirt-python.rb) |
| `Formula/n/nak.rb` | 2026-11-02T18:52:33Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/92ab8214ecebee57dbe63eec69afccc87f936e17); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/92ab8214ecebee57dbe63eec69afccc87f936e17/Formula/n/nak.rb) |
| `Formula/n/nghttp2.rb` | 2026-11-02T19:19:24Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/add0f3116959df9d8d1e56ba10ddb7e1326590fb); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/add0f3116959df9d8d1e56ba10ddb7e1326590fb/Formula/n/nghttp2.rb) |
| `Formula/n/ntfy.rb` | 2026-11-02T19:51:48Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/796855ff19e4b42ee7d0fdcb005214e2ddcc6d80); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/796855ff19e4b42ee7d0fdcb005214e2ddcc6d80/Formula/n/ntfy.rb) |
| `Formula/o/open-code-review.rb` | 2026-11-02T18:48:32Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/c67818f08bddc7d3a28f3e9cd3fd3128e6b7fccd); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/c67818f08bddc7d3a28f3e9cd3fd3128e6b7fccd/Formula/o/open-code-review.rb) |
| `Formula/o/opencode.rb` | 2026-11-02T19:27:41Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/55dd4aa68d52d30f5bd8a2a79624203871ce01b2); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/55dd4aa68d52d30f5bd8a2a79624203871ce01b2/Formula/o/opencode.rb) |
| `Formula/p/pipenv.rb` | 2026-11-02T18:48:45Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/706b50a1b6d59b9c11fe0cf4138da6394ca7a227); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/706b50a1b6d59b9c11fe0cf4138da6394ca7a227/Formula/p/pipenv.rb) |
| `Formula/q/qdl.rb` | 2026-11-02T19:04:24Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/3e9f9684d544039f23bb8a53dbdf6d7726859ca3); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/3e9f9684d544039f23bb8a53dbdf6d7726859ca3/Formula/q/qdl.rb) |
| `Formula/q/qobine-tui.rb` | 2026-11-02T18:50:43Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/0f582b5045e1b2963b7bb3944e82b8c2239d57da); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/0f582b5045e1b2963b7bb3944e82b8c2239d57da/Formula/q/qobine-tui.rb) |
| `Formula/q/qobine-web.rb` | 2026-11-02T18:49:57Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/92c9fe789388a98ecab99989ecafd43c8150a074); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/92c9fe789388a98ecab99989ecafd43c8150a074/Formula/q/qobine-web.rb) |
| `Formula/r/rulesync.rb` | 2026-11-02T18:48:38Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/350e10cb340b2a496cac9b414840a2733caf6863); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/350e10cb340b2a496cac9b414840a2733caf6863/Formula/r/rulesync.rb) |
| `Formula/s/schemathesis.rb` | 2026-11-02T18:48:25Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/679281d9fb58d2dc40828d9db57dc3bb55d80f0d); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/679281d9fb58d2dc40828d9db57dc3bb55d80f0d/Formula/s/schemathesis.rb) |
| `Formula/s/specify.rb` | 2026-11-02T18:50:28Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/f24a732cdcf4a61263fb4261600fe93c1107f397); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/f24a732cdcf4a61263fb4261600fe93c1107f397/Formula/s/specify.rb) |
| `Formula/s/syft.rb` | 2026-11-02T18:49:27Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/83d945ff4d13df8bb38c9a90e8d1f2bb231db43e); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/83d945ff4d13df8bb38c9a90e8d1f2bb231db43e/Formula/s/syft.rb) |
| `Formula/t/tele.rb` | 2026-11-02T19:50:00Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/415bd7008e07bcebfc895275b61118466b714899); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/415bd7008e07bcebfc895275b61118466b714899/Formula/t/tele.rb) |
| `Formula/t/telegraf.rb` | 2026-11-02T18:49:30Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/06e7f5fbd750c9f1fd0fec8f2fe9c206d7ea5e28); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/06e7f5fbd750c9f1fd0fec8f2fe9c206d7ea5e28/Formula/t/telegraf.rb) |
| `Formula/t/translate-toolkit.rb` | 2026-11-02T19:18:15Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/43b35ef499eeb3b20192a10ff6eb5a8a746df1f6); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/43b35ef499eeb3b20192a10ff6eb5a8a746df1f6/Formula/t/translate-toolkit.rb) |
| `Formula/v/vcluster.rb` | 2026-11-02T18:48:55Z | Linux, macOS | [Diff](https://github.com/Homebrew/homebrew-core/commit/059b5021f8bb5d1565c89e18e3d703532c59d399); [pinned formula](https://github.com/Homebrew/homebrew-core/blob/059b5021f8bb5d1565c89e18e3d703532c59d399/Formula/v/vcluster.rb) |

Only added OS-specific checksum lines in the actual diff qualify; metadata-only edits do not. Formula source URLs, pinned contents URLs and diffs are retained. The official Homebrew catalogs are hosted on GitHub, but discovery was seeded by their own packaging activity, not by the original GitHub repository sample. Bottles were not downloaded or executed.

### Independent discovery: winget

Discovery endpoint: [winget feed/search](https://api.github.com/repos/microsoft/winget-pkgs/commits?since=2026-10-03T20%3A00%3A00Z&until=2026-11-02T20%3A00%3A00Z&per_page=100).

**Selection:** Source-first recent changes/advisory endpoint; not seeded by the cohort.

**Limits:** No findings collected; missing access is not a negative result. OSV/NVD dates concern advisories, not development.

**Not assessed:** HTTPError: HTTP Error 403: Forbidden. No projects are counted as absent or single-OS because of this failure.

### Independent discovery: OSV

Discovery endpoint: [OSV feed/search](https://osv-vulnerabilities.storage.googleapis.com/PyPI/modified_id.csv).

**Selection:** Source-first recent changes/advisory endpoint; not seeded by the cohort.

**Limits:** No findings collected; missing access is not a negative result. OSV/NVD dates concern advisories, not development.

**Not assessed:** URLError: <urlopen error [Errno -5] No address associated with hostname>. No projects are counted as absent or single-OS because of this failure.

The alternate Google Storage bulk-index URL also returned HTTP 403. No package names from the original cohort were substituted to manufacture an independent result. Advisory modification dates would not establish recent development even with access.

### Independent discovery: NVD

Discovery endpoint: [NVD feed/search](https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate=2026-10-03T20%3A00%3A00.000&pubEndDate=2026-11-02T19%3A59%3A59.999&resultsPerPage=100).

**Selection:** Source-first recent changes/advisory endpoint; not seeded by the cohort.

**Limits:** No findings collected; missing access is not a negative result. OSV/NVD dates concern advisories, not development.

**Not assessed:** URLError: <urlopen error [Errno -5] No address associated with hostname>. No projects are counted as absent or single-OS because of this failure.

The alternate NVD modified-feed host also failed DNS resolution. A future result would require inspecting affected CPE configurations; advisory dates alone are not OS support or release evidence.

### Independent discovery audit trail

[Independent discovery evidence](registry-research-2026-11-03-independent.json) records every root candidate, source query, selection rule, timestamp meaning, positive evidence tier, relevant file/source metadata and access failure. It is separate from the original cohort audit and does not change that cohort's classifications or totals. Sources without usable access are explicitly unassessed.
