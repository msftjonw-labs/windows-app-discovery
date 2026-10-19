"use strict";

let report;
const $ = (id) => document.getElementById(id);
const element = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

function githubLink(text, url) {
  const link = element("a", text);
  const parsed = new URL(url);
  if (parsed.protocol !== "https:" || parsed.hostname !== "github.com") {
    throw new Error("Unexpected repository link");
  }
  link.href = parsed.href;
  return link;
}

function bars(id, values) {
  const container = $(id);
  container.replaceChildren();
  if (values === undefined) {
    container.append(element("p", "Not collected by this report's ruleset.", "muted"));
    return;
  }
  if (!values.length || values.every((value) => value.denominator === 0)) {
    container.append(element("p", "N/A — no eligible repositories in this cohort.", "muted"));
    return;
  }
  for (const value of values) {
    const row = element("div", undefined, "bar-row");
    const label = element("div", undefined, "bar-label");
    label.append(element("span", value.label), element("span", `${value.percent}% · ${value.count}/${value.denominator}`));
    const track = element("div", undefined, "track");
    track.setAttribute("aria-hidden", "true");
    const fill = element("div", undefined, "fill");
    fill.style.width = `${Math.max(0, Math.min(100, value.percent))}%`;
    track.append(fill);
    row.append(label, track);
    container.append(row);
  }
}

function renderRows() {
  const filter = $("filter").value.toLowerCase();
  const status = $("scan-status").value;
  const records = report.repositories.filter((repo) => {
    const text = [repo.name, ...(repo.platforms || []), ...(repo.frameworks || []),
      ...(repo.components || []), repo.primary_language || "", repo.purpose || ""].join(" ").toLowerCase();
    return text.includes(filter) && (!status || repo.status === status);
  });
  $("repository-count").textContent = `${records.length} of ${report.repositories.length} selected repositories`;
  $("rows").replaceChildren();
  for (const repo of records) {
    const row = element("tr");
    const name = element("td");
    name.append(githubLink(repo.name, `https://github.com/${repo.name}`));
    name.append(element("div", `${repo.fork ? "Fork · " : ""}${repo.archived ? "Archived · " : ""}${repo.last_activity}`, "muted"));
    name.append(githubLink("Activity evidence", repo.activity_evidence));
    const targets = element("td", `${(repo.platforms || []).join(", ") || "Not analyzed"}`);
    targets.append(element("div", repo.primary_language || "Unknown", "muted"));
    const framework = element("td", (repo.frameworks || []).join(", ") || "Not analyzed");
    framework.append(element("div", repo.purpose || "Unknown", "muted"));
    const components = element("td", repo.windows_scan === "success"
      ? (repo.components.length ? repo.components.join(", ") : "No selected component patterns detected")
      : "Not analyzed");
    const scan = element("td");
    scan.append(element("span", repo.status, `badge ${repo.status}`));
    if (repo.error) scan.append(element("p", repo.error));
    if (repo.note) scan.append(element("p", repo.note));
    if (repo.inspector_incomplete && Object.keys(repo.inspector_incomplete).length) {
      scan.append(element("p", `Inspector incomplete: ${JSON.stringify(repo.inspector_incomplete)}`, "muted"));
    }
    if (repo.sha) {
      scan.append(element("div", `${repo.files_scanned} files · ${repo.scanned_at}`, "muted"));
      scan.append(element("div", `Source retrieval: ${repo.source_method || "not recorded"}`, "muted"));
      scan.append(githubLink(`SHA ${repo.sha.slice(0, 10)}`, `${repo.url}/tree/${repo.sha}`));
    }
    if (repo.evidence && repo.evidence.length) {
      const details = element("details");
      details.append(element("summary", `Evidence (${repo.evidence.length} shown, max 200)`));
      const list = element("ul");
      for (const evidence of repo.evidence) {
        const item = element("li");
        const path = evidence.path.split("/").map(encodeURIComponent).join("/");
        item.append(githubLink(`${evidence.label} · ${evidence.path}:${evidence.line}`,
          `${repo.url}/blob/${repo.sha}/${path}#L${evidence.line}`));
        item.append(element("div", evidence.engine, "muted"));
        list.append(item);
      }
      details.append(list);
      scan.append(details);
    }
    if (repo.excluded && Object.keys(repo.excluded).length) {
      scan.append(element("p", `Skipped: ${Object.entries(repo.excluded).map(([key, count]) => `${key}: ${count}`).join("; ")}`, "muted"));
    }
    row.append(name, targets, framework, components, scan);
    $("rows").append(row);
  }
}

function csvCell(value) {
  const text = String(value ?? "");
  // Prefix spreadsheet formula cells, including those with leading whitespace.
  const safe = /^\s*[=+\-@]/.test(text) ? `'${text}` : text;
  return `"${safe.replaceAll('"', '""')}"`;
}

function downloadCsv() {
  const fields = ["name", "status", "last_activity", "primary_language", "platforms",
    "frameworks", "purpose", "application_types", "components", "os_targets", "sha", "source_method", "files_scanned", "note", "error"];
  const lines = [fields.map(csvCell).join(",")];
  for (const repo of report.repositories) {
    lines.push(fields.map((field) => csvCell(Array.isArray(repo[field]) ? repo[field].join("; ") : repo[field])).join(","));
  }
  const url = URL.createObjectURL(new Blob([lines.join("\r\n")], { type: "text/csv;charset=utf-8" }));
  const link = element("a");
  link.href = url;
  link.download = "repository-analysis.csv";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function load() {
  try {
    const response = await fetch("data/latest.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`Analysis data returned HTTP ${response.status}`);
    report = await response.json();
    if (report.schema_version !== 1 || !Array.isArray(report.repositories)) {
      throw new Error("Unsupported analysis data format");
    }
    $("status").textContent = `Generated ${report.generated_at}`;
    $("window").textContent = `${report.window.start} inclusive → ${report.window.end} exclusive (UTC)`;
    const metrics = report.metrics;
    const cards = [
      ["Selected repositories", metrics.selected], ["Complete scans", metrics.successful],
      ["Partial scans", metrics.partial], ["Failed scans", metrics.failed],
      ["Windows candidates", metrics.windows_repositories], ["Windows applications", metrics.windows_applications],
    ];
    if ("not_applicable" in metrics) cards.splice(4, 0, ["No eligible source (N/A)", metrics.not_applicable]);
    for (const [label, value] of cards) {
      const card = element("div", undefined, "card");
      card.append(element("strong", value), element("span", label));
      $("cards").append(card);
    }
    $("coverage").append(element("p",
      `${report.coverage.items_examined} issue/PR items examined; ${report.coverage.eligible_repositories} unique qualifying repositories before selection; ${report.coverage.truncated_connections} truncated comment/review connections.`));
    if (report.coverage.rerun) {
      $("coverage").append(element("p",
        `Rescanned the cohort from ${report.coverage.source_generated_at}; discovery/activity evidence was not refreshed.`));
    }
    for (const search of report.coverage.searches) {
      $("coverage").append(element("p", `${search.query} · examined ${search.items_examined} of ${search.matching_items} matches${search.bounded ? " · bounded/truncated" : ""}`, "muted"));
    }
    for (const field of ["platforms", "os_targets", "languages", "frameworks", "application_types", "components", "candidate_components"]) {
      bars(field, metrics[field]);
    }
    $("versions").textContent = `Ruleset ${report.ruleset_version}; Microsoft Application Inspector ${report.inspector_version}. Cached scans retain their original scan timestamps.`;
    $("filter").addEventListener("input", renderRows);
    $("scan-status").addEventListener("change", renderRows);
    $("csv").disabled = false;
    $("csv").addEventListener("click", downloadCsv);
    renderRows();
  } catch (error) {
    $("status").className = "error";
    $("status").textContent = `Cannot display analysis: ${error.message}. Run the collector first, then serve the site over HTTP. No sample statistics are substituted.`;
    console.error(error);
  }
}

load();
