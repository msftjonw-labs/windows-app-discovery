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
