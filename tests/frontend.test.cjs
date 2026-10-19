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
    };
  }
  const context = vm.createContext({
    URL,
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
      platforms: [], languages: [], frameworks: [], application_types: [], components: [], candidate_components: [] },
    repositories: [] };
  run(`fetch = async () => ({ ok: true, json: async () => (${JSON.stringify(data)}) }); document.getElementById("filter").addEventListener = () => {}; document.getElementById("scan-status").addEventListener = () => {}; document.getElementById("csv").addEventListener = () => {};`);
  await run("load()");
  assert.deepEqual(run('$("cards").children.map((c) => c.children[1].textContent)'),
    ["Selected repositories", "Complete scans", "Partial scans", "Failed scans", "No eligible source (N/A)"]);
  assert.equal(run('$("windows-cards").children.length'), 2);
  assert.equal(run('$("windows-cards").children[0].className'), "card subset");
  assert.equal(run('$("windows-cards").children[1].children[2].textContent'), "of 93 complete scans");
  assert.match(run('$("platforms-note").textContent'), /only from the 93 complete scans, excluding 4 partial scans, 1 failed scans.*100%/);
});

test("repository filters preserve N/A notes and partial Inspector counters", () => {
  const run = app();
  run(`report = ${JSON.stringify({ repositories: [
    { name: "o/empty", status: "not_applicable", note: "No eligible source", activity_evidence: "https://github.com/o/empty/issues/1" },
    { name: "o/partial", status: "partial", inspector_incomplete: { filesSkipped: 2 }, activity_evidence: "https://github.com/o/partial/issues/1" },
  ] })}`);
  run('$("scan-status").value = "not_applicable"; renderRows()');
  assert.equal(run('$("rows").children.length'), 1);
  assert.equal(run('$("repository-count").textContent'), "1 of 2 selected repositories");
  assert.equal(run('$("rows").children[0].children[4].children[1].textContent'), "No eligible source");
  run('$("scan-status").value = "partial"; renderRows()');
  assert.match(run('$("rows").children[0].children[4].children[1].textContent'), /filesSkipped.*2/);
});
