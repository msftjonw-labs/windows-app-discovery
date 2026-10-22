"""Collect bounded GitHub evidence and summarize identified Windows applications."""

from html import unescape
import logging
import re

LOG = logging.getLogger(__name__)

QUERY = """
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    description
    readme: object(expression:"HEAD:README.md") {
      ... on Blob { text }
    }
    readmeRoot: object(expression:"HEAD:README") {
      ... on Blob { text }
    }
    readmeRst: object(expression:"HEAD:README.rst") {
      ... on Blob { text }
    }
    issues(first:5, orderBy:{field:UPDATED_AT,direction:DESC}) {
      nodes {
        title body url state labels(first:20) { nodes { name } }
        comments { totalCount } reactions { totalCount }
      }
    }
    featureIssues: issues(first:5, labels:["feature"], orderBy:{field:UPDATED_AT,direction:DESC}) {
      nodes {
        title body url state labels(first:20) { nodes { name } }
        comments { totalCount } reactions { totalCount }
      }
    }
    pullRequests(first:5, orderBy:{field:UPDATED_AT,direction:DESC}) {
      nodes {
        title body url state merged
        comments { totalCount } reactions { totalCount }
      }
    }
  }
}"""

SECTION_HEADINGS = ("how it works", "usage", "features", "architecture", "getting started")


def _plain_text(value):
    value = re.sub(r"```.*?```", " ", value or "", flags=re.S)
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<[^>]*>", " ", value)
    value = re.sub(r"^\s{0,3}#{1,6}\s*", "", value, flags=re.M)
    value = re.sub(r"^\s*[-*+]\s+", "", value, flags=re.M)
    value = re.sub(r"[*_`~]", "", value)
    return " ".join(unescape(value).split())


def _first_sentence(value):
    value = _plain_text(value)
    if not value:
        return ""
    match = re.search(r"[.!?](?:\s|$)", value)
    return value[:match.start()].strip() if match else value


def _readme_paragraph(readme):
    content = re.sub(r"```.*?```", "", readme or "", flags=re.S)
    content = re.sub(r"(?m)^\s{0,3}#{1,6}\s+.*$", "", content)
    for paragraph in re.split(r"\n\s*\n", content):
        value = _first_sentence(paragraph)
        if value and not re.fullmatch(r"[\W_]+", value):
            return value[:280].rstrip()
    return ""


def _readme_approach(readme):
    lines = (readme or "").splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading or not any(key in heading.group(1).lower() for key in SECTION_HEADINGS):
            continue
        section = []
        for following in lines[index + 1:]:
            if re.match(r"^\s{0,3}#{1,6}\s+", following):
                break
            section.append(following)
        phrase = _first_sentence("\n".join(section))
        if phrase:
            return heading.group(1).strip(), phrase[:280].rstrip()
    return None, ""


def _nodes(connection):
    return ((connection or {}).get("nodes") or [])


def _issue_feature(issue):
    labels = (issue.get("labels") or {}).get("nodes") or []
    return any((label.get("name") or "").casefold() == "feature" for label in labels)


def _count(item, key):
    return ((item.get(key) or {}).get("totalCount") or 0)


def _record_summary(item):
    return (_first_sentence(item.get("body") or "")
            or _first_sentence(item.get("title") or "a change"))[:280]


def _analysis(repository, readme, issues, feature_issues, pull_requests):
    purpose = _readme_paragraph(readme)
    if purpose:
        first = f"The README presents the application as {purpose}."
    elif repository.get("description"):
        description = _first_sentence(repository["description"])
        first = f"The repository description presents the application as {description}."
    else:
        first = "The README and repository metadata do not state the application's purpose."

    approach_heading, approach = _readme_approach(readme)
    features = [issue for issue in feature_issues if _issue_feature(issue)]
    feature = features[0] if features else None
    pull_request = pull_requests[0] if pull_requests else None
    details = []
    if approach:
        details.append(f"The README's {approach_heading} section states: {approach}")
    if feature:
        details.append(f"a feature issue requests {_record_summary(feature)}")
    if pull_request:
        details.append(f"a recent pull request proposes {_record_summary(pull_request)}")
    if details:
        sentence = "; ".join(details)
        second = sentence[0].upper() + sentence[1:] + "."
    else:
        second = "The available README and recent GitHub records do not explain how the application works."

    if issues or pull_requests:
        open_issues = sum(issue.get("state") == "OPEN" for issue in issues)
        merged = sum(bool(pr.get("merged")) for pr in pull_requests)
        comments = sum(_count(item, "comments") for item in [*issues, *pull_requests])
        reactions = sum(_count(item, "reactions") for item in [*issues, *pull_requests])
        issue_noun = "issue" if len(issues) == 1 else "issues"
        pr_noun = "pull request" if len(pull_requests) == 1 else "pull requests"
        open_noun = "issue is" if open_issues == 1 else "issues are"
        merged_noun = "pull request is" if merged == 1 else "pull requests are"
        third = (f"Among {len(issues)} recent {issue_noun} and {len(pull_requests)} recent {pr_noun}, "
                 f"{open_issues} {open_noun} open and {merged} {merged_noun} merged; "
                 f"the reviewed items have {comments} comments and {reactions} reactions.")
    else:
        third = "No recent issues or pull requests were returned, so community reception could not be assessed."
    return " ".join((first, second, third))


def unavailable_analysis():
    return ("The README and repository metadata could not be collected to establish the application's purpose. "
            "GitHub issue and pull-request details could not be collected to explain how it works. "
            "Community reception could not be assessed because GitHub activity data was unavailable.")


def is_windows_application(record):
    return (record.get("status") == "success" and "Windows" in record.get("platforms", [])
            and record.get("purpose") == "Application" and record.get("windows_scan") == "success")


def enrich_windows_applications(records, fetch):
    """Attach an evidence-based, three-sentence summary to each fully scanned Windows application."""
    for record in records:
        if not is_windows_application(record):
            continue
        try:
            owner, name = record["name"].split("/", 1)
            result = fetch(QUERY, owner=owner, name=name)["repository"]
            if result is None:
                raise ValueError("repository no longer available")
            readme = next((
                (result.get(key) or {}).get("text")
                for key in ("readme", "readmeRoot", "readmeRst")
                if (result.get(key) or {}).get("text")
            ), "")
            issues = _nodes(result.get("issues"))
            feature_issues = _nodes(result.get("featureIssues"))
            pull_requests = _nodes(result.get("pullRequests"))
            record["analysis"] = _analysis(
                result, readme, issues, feature_issues, pull_requests)
        except Exception as error:
            LOG.warning("Could not collect application insights for %s: %s", record.get("name"), error)
            record["analysis"] = unavailable_analysis()
