const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

function app() {
  const nodes = new Map();
  function node(tag) {
    return {
      tag, children: [], style: {}, value: "",
      append(...children) { this.children.push(...children); },
      replaceChildren(...children) { this.children = children; },
      setAttribute(name, value) { this[name] = value; },
      click() {},
    };
  }
  const context = vm.createContext({
    URL,
    Blob,
    setTimeout: () => {},
    document: {
      createElement: node,
      getElementById: (id) => {
        if (!nodes.has(id)) nodes.set(id, node("div"));
        return nodes.get(id);
      },
    },
    fetch: () => new Promise(() => {}),
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, "..", "site", "app.js"), "utf8"), context);
  return (expression) => vm.runInContext(expression, context);
}

test("CSV quotes values and neutralizes spreadsheet formulas", () => {
  const run = app();
  assert.equal(run('csvCell(\'a"b\')'), '"a""b"');
  assert.equal(run('csvCell("=HYPERLINK(1)")'), '"\'=HYPERLINK(1)"');
  assert.equal(run('csvCell("  +123")'), '"\'  +123"');
  assert.equal(run("csvCell(null)"), '""');
});

test("repository links reject non-GitHub and script URLs", () => {
  const run = app();
  assert.equal(run('githubLink("repo", "https://github.com/o/r").href'), "https://github.com/o/r");
  for (const url of ["javascript:alert(1)", "https://evil.example", "https://github.com.evil.example/o/r"]) {
    assert.throws(() => run(`githubLink("repo", ${JSON.stringify(url)})`), /Unexpected repository link/);
  }
});

test("untrusted labels are assigned as text, not HTML", () => {
  const run = app();
  assert.equal(run('element("span", "<img src=x onerror=alert(1)>").textContent'),
    "<img src=x onerror=alert(1)>");
});

test("charts distinguish older reports and empty eligible populations", () => {
  const run = app();
  run('bars("os-targets", undefined)');
  assert.equal(run('$("os-targets").children[0].textContent'), "Not collected by this report's ruleset.");
  run('bars("os-targets", [{label: "Windows", count: 0, denominator: 0, percent: null}])');
  assert.match(run('$("os-targets").children[0].textContent'), /N\/A/);
});

test("charts display the measured percentage and exact complete-scan denominator", () => {
  const run = app();
  run('bars("platforms", [{label: "Unknown", count: 2, denominator: 86, percent: 2.33}])');
  assert.equal(run('$("platforms").children[0].children[0].children[1].textContent'), "2.33% · 2/86");
  assert.equal(run('$("platforms").children[0].children[1].children[0].style.width'), "2.33%");
});

test("charts show confidence intervals for random samples", () => {
  const run = app();
  run('bars("platforms", [{label: "Windows", count: 19, denominator: 95, percent: 20, ci_low: 13.2, ci_high: 29.1}])');
  assert.equal(run('$("platforms").children[0].children[0].children[1].textContent'), "20% (CI 13.2–29.1%) · 19/95");
  assert.equal(run('$("platforms").children[0].children[1].children[1].style.left'), "13.2%");
  assert.match(run('$("platforms").children[0].children[1].children[1].style.width'), /^15\.9\d*%$/);
});

test("coverage text distinguishes random samples from GraphQL fallback", () => {
  const run = app();
  const sampled = run(`describeCoverage(${JSON.stringify({ representative_sample: true, population_size: 1234567, seed: "s",
    hours_processed: 720, hours_expected: 720, qualifying_events: 10, events_scanned: 20, excluded_after_sampling: [{}] })},
    {selected: 100, confidence_level: 0.95, margin_of_error: 10.05})`);
  assert.match(sampled[0][0], /1,234,567.*95% Wilson.*±10\.05/);
  assert.match(sampled[1][0], /1 sampled repositories were deleted or private/);
  const fallback = run(`describeCoverage(${JSON.stringify({ representative_sample: false, items_examined: 5,
    eligible_repositories: 3, truncated_connections: 0, fallback_reason: "archive down", searches: [] })}, {})`);
  assert.match(fallback[1][0], /fallback reason: archive down/);
});

test("Windows tiles render as a separate complete-scan subset with denominator notes", async () => {
  const run = app();
  const data = { schema_version: 1, generated_at: "g", window: { start: "s", end: "e" }, ruleset_version: "r", inspector_version: "i",
    coverage: { representative_sample: false, items_examined: 1, eligible_repositories: 1, truncated_connections: 0, searches: [] },
    metrics: { selected: 100, successful: 93, partial: 4, failed: 1, not_applicable: 2, windows_repositories: 15, windows_applications: 6,
      platforms: [], languages: [], frameworks: [], application_types: [], components: [], candidate_components: [],
      project_types_unclassified: 3,
      project_types: [{label: "PowerShell", count: 11, denominator: 93, percent: 11.83},
        {label: "Backend / API", count: 1, denominator: 93, percent: 1.08}] },
    repositories: [] };
  run(`fetch = async () => ({ ok: true, json: async () => (${JSON.stringify(data)}) }); document.getElementById("filter").addEventListener = () => {}; document.getElementById("scan-status").addEventListener = () => {}; document.getElementById("csv").addEventListener = () => {};`);
  await run("load()");
  assert.deepEqual(run('$("cards").children.map((c) => c.children[1].textContent)'),
    ["Selected repositories", "Complete scans", "Partial scans", "Failed scans", "No eligible source (N/A)"]);
  assert.equal(run('$("windows-cards").children.length'), 2);
  assert.equal(run('$("windows-cards").children[0].className'), "card subset");
  assert.equal(run('$("windows-cards").children[1].children[2].textContent'), "of 93 complete scans");
  assert.match(run('$("platforms-note").textContent'), /only from the 93 complete scans, excluding 4 partial scans, 1 failed scans.*100%/);
  assert.equal(run('$("project_types").children[0].children[0].children[0].textContent'), "PowerShell");
  assert.equal(run('$("project_types").children[0].children[0].children[1].textContent'), "11.83% · 11/93");
  assert.equal(run('$("project_types").children[1].children[0].children[0].textContent'), "Backend / API");
  assert.match(run('$("project-types-coverage").textContent'), /3 repositories have insufficient application-type evidence/);
});

test("repository explorer only lists complete Windows candidates and preserves filters and diagnostics", () => {
  const run = app();
  run(`report = ${JSON.stringify({ repositories: [
    { name: "o/windows", status: "success", platforms: ["Windows"], note: "Scan note", activity_evidence: "https://github.com/o/windows/issues/1" },
    { name: "o/mixed", status: "success", platforms: ["Linux", "Windows"], inspector_incomplete: { filesSkipped: 2 }, activity_evidence: "https://github.com/o/mixed/issues/1" },
    { name: "o/cross", sha: "abc", status: "success", platforms: ["Linux", "Windows"],
      cross_os: { status: "success", sha: "abc", decision: { cross_os: true } } },
    { name: "o/linux", status: "success", platforms: ["Linux"], activity_evidence: "https://github.com/o/linux/issues/1" },
    { name: "o/unknown", status: "success", activity_evidence: "https://github.com/o/unknown/issues/1" },
    { name: "o/empty", status: "not_applicable", note: "No eligible source", activity_evidence: "https://github.com/o/empty/issues/1" },
    { name: "o/partial", status: "partial", platforms: ["Windows"], activity_evidence: "https://github.com/o/partial/issues/1" },
    { name: "o/failed", status: "failed", platforms: ["Windows"], activity_evidence: "https://github.com/o/failed/issues/1" },
  ] })}`);
  run("renderRows()");
  assert.equal(run('$("rows").children.length'), 2);
  assert.equal(run('$("repository-count").textContent'), "2 of 2 Windows candidates");
  assert.equal(run('$("rows").children[0].children[0].children[0].textContent'), "o/windows");
  assert.equal(run('$("rows").children[1].children[0].children[0].textContent'), "o/mixed");
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).children[2].textContent'), "Scan note");
  assert.match(run('$("rows").children[1].children[4].children.at(-1).children[2].textContent'), /filesSkipped.*2/);
  run('$("filter").value = "mixed"; $("scan-status").value = "success"; renderRows()');
  assert.equal(run('$("rows").children.length'), 1);
  assert.equal(run('$("repository-count").textContent'), "1 of 2 Windows candidates");
  run('$("filter").value = ""; $("scan-status").value = "partial"; renderRows()');
  assert.equal(run('$("rows").children.length'), 0);
  assert.equal(run('$("repository-count").textContent'), "0 of 2 Windows candidates");
  run('$("scan-status").value = ""; $("filter").value = "linux"; renderRows()');
  assert.equal(run('$("rows").children.length'), 1);
  run('report.repositories = []; $("filter").value = ""; renderRows()');
  assert.equal(run('$("rows").children.length'), 0);
  assert.equal(run('$("repository-count").textContent'), "0 of 0 Windows candidates");
});

test("project findings retain multiple labels, confidence and pinned evidence links", () => {
  const run = app();
  run(`report = {repositories: [{
    name: "o/mixed", url: "https://github.com/o/mixed", sha: "abc123", status: "success", platforms: ["Windows"],
    activity_evidence: "https://github.com/o/mixed/issues/1",
    projects: [{path: "desktop/App.csproj", kind: "dotnet",
      labels: ["Windows Forms", "Windows service"], confidence: "high",
      evidence: [{label: "Windows Forms", path: "desktop/a b.cs", line: 7,
        engine: "project metadata", confidence: "high"}]}]
  }]}`);
  run('$("filter").value = "windows service"; renderRows()');
  assert.equal(run('$("rows").children.length'), 1);
  const details = '$("rows").children[0].children[4].children.at(-1).children[2]';
  assert.equal(run(`${details}.children[0].textContent`), "Project findings (1)");
  assert.match(run(`${details}.children[1].textContent`), /not statistical/);
  assert.equal(run(`${details}.children[3].textContent`), "Windows Forms, Windows service · high confidence");
  assert.equal(run(`${details}.children[4].children[0].children[0].href`),
    "https://github.com/o/mixed/blob/abc123/desktop/a%20b.cs#L7");
  assert.match(run(`${details}.children[4].children[0].children[1].textContent`), /high confidence/);
  run('$("filter").value = "desktop/app.csproj"; renderRows()');
  assert.equal(run('$("rows").children.length'), 1);
});

test("project findings render untrusted project names as text", () => {
  const run = app();
  assert.equal(run(`projectFindings({projects: [{
    path: "<img src=x>", kind: "script", labels: ["PowerShell automation"],
    confidence: "medium", evidence: []
  }]}).children[2].textContent`), "<img src=x> · script");
});

test("project findings distinguish per-label confidence and association limitations", () => {
  const run = app();
  run(`let findings = projectFindings({projects: [{
    path: ".", kind: "shared", labels: ["PowerShell module", "Windows service"],
    confidence: "high", label_confidence: {"PowerShell module": "high", "Windows service": "low"},
    notes: ["No unique project ownership"], evidence: []
  }]});`);
  assert.equal(run("findings.children[3].textContent"),
    "PowerShell module (high), Windows service (low) · high confidence");
  assert.equal(run("findings.children[4].textContent"), "No unique project ownership");
});

test("supplemental tool failures are visible without hiding completed scans", () => {
  const run = app();
  run(`report = {repositories: [{
    name: "o/r", status: "success", platforms: ["Windows"], activity_evidence: "https://github.com/o/r/issues/1",
    semgrep: {status: "partial", reason: "Semgrep timeout"}
  }]}; renderRows();`);
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).children[1].textContent'), "success");
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).children[2].textContent'),
    "Supplemental Semgrep: partial · Semgrep timeout");
  run('report.repositories[0].semgrep = {status: "partial", errors: 2, rejected_findings: 1}; renderRows()');
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).children[2].textContent'),
    "Supplemental Semgrep: partial · 2 errors · 1 rejected findings");
});

test("CSV preserves structured project labels and evidence instead of object strings", async () => {
  const run = app();
  const projects = [{
    path: "scripts/install.ps1", kind: "powershell", labels: ["PowerShell automation", "Installation script"],
    confidence: "medium", evidence: [{path: "scripts/install.ps1", line: 1, label: "Installation script",
      engine: "PowerShell heuristic", confidence: "medium"}],
  }];
  run(`report = {repositories: [{name: "o/r", projects: ${JSON.stringify(projects)}}]};
    let capturedCsv; URL = {createObjectURL(blob) {capturedCsv = blob; return "blob:test";}, revokeObjectURL() {}};
    downloadCsv();`);
  const csv = await run("capturedCsv.text()");
  assert.match(csv.split("\r\n")[0], /"projects"/);
  assert.ok(csv.includes(run(`csvCell(${JSON.stringify(JSON.stringify(projects))})`)));
  assert.ok(!csv.includes("[object Object]"));
});

test("Analysis shows problems, development status, measured issue counts, feedback and source links", () => {
  const run = app();
  const analysis = {
    status: "success", problem: "<img src=x> Automates desktop tasks.",
    development: "Experimental <not stable>; archive status is false.",
    community: "Sampled comments report startup problems, not community-wide dissatisfaction.",
    issues_opened: 15, issues_sampled: 2, comments_sampled: 3,
    problem_sources: ["S1"], development_sources: ["S3"], community_sources: ["S2"],
    sources: [
      {id: "S1", kind: "readme", url: "https://github.com/o/r/blob/abc/README.md"},
      {id: "S2", kind: "comment", url: "https://github.com/o/r/issues/1#issuecomment-2"},
      {id: "S3", kind: "repository_status", url: "https://github.com/o/r"},
    ],
    window: {start: "2026-10-01T00:00:00Z", end: "2026-10-31T00:00:00Z"},
    limitations: "Bounded sample, not community-wide sentiment.", model: "gpt-4o", generated_at: "now",
  };
  run(`let cell = analysisCell({analysis: ${JSON.stringify(analysis)}})`);
  assert.equal(run("cell.children[0].textContent"), "Problems solved");
  assert.equal(run("cell.children[1].textContent"), analysis.problem);
  assert.equal(run("cell.children[2].children[0].href"), analysis.sources[0].url);
  assert.equal(run("cell.children[3].textContent"), "Development status");
  assert.equal(run("cell.children[4].textContent"), analysis.development);
  assert.equal(run("cell.children[5].children[0].href"), analysis.sources[2].url);
  assert.equal(run("cell.children[6].textContent"), "Community response");
  assert.equal(run("cell.children[7].textContent"),
    "15 issues opened in the report window (excluding PRs). Feedback sample: 2 issues, 3 human comments.");
  assert.equal(run("cell.children[8].textContent"), analysis.community);
  assert.equal(run("cell.children[9].children[0].href"), analysis.sources[1].url);
  assert.equal(run("cell.children[10].tag"), "details");
  assert.match(run("cell.children[10].children[2].textContent"), /Bounded sample/);
  delete analysis.development;
  delete analysis.development_sources;
  run(`cell = analysisCell({analysis: ${JSON.stringify(analysis)}})`);
  assert.equal(run("cell.children[4].textContent"), "Not collected. Rerun the AI analysis step.");
});

test("Analysis explicitly distinguishes uncollected and failed summaries and collapses scan evidence", () => {
  const run = app();
  assert.match(run("analysisCell({}).children[0].textContent"), /Analysis not collected/);
  assert.equal(run('analysisCell({analysis: {status: "failed", error: "OpenAI HTTP 401"}}).children[0].textContent'),
    "Analysis unavailable: OpenAI HTTP 401");
  run(`report = {repositories: [{
    name: "o/r", status: "success", platforms: ["Windows"],
    activity_evidence: "https://github.com/o/r/issues/1"
  }]}; renderRows();`);
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).tag'), "details");
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).children[0].textContent'), "Scan / evidence");
  assert.equal(run('$("rows").children[0].children[4].children.at(-1).open'), undefined);
});

test("CSV retains structured AI analysis", async () => {
  const run = app();
  const analysis = {status: "success", problem: "Task automation", issues_opened: 2, sources: []};
  run(`report = {repositories: [{name: "o/r", analysis: ${JSON.stringify(analysis)}}]};
    let capturedCsv; URL = {createObjectURL(blob) {capturedCsv = blob; return "blob:test";}, revokeObjectURL() {}};
    downloadCsv();`);
  const csv = await run("capturedCsv.text()");
  assert.match(csv.split("\r\n")[0], /"analysis"/);
  assert.ok(csv.includes(run(`csvCell(${JSON.stringify(JSON.stringify(analysis))})`)));
});
