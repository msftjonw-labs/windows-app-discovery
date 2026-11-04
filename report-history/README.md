# Report history

Every successful weekly run on the default branch archives both PDFs here:

- GitHub: `report-yyyy-mm-dd.pdf` (preserving existing historical filenames).
- GitLab: `gitlab-report-yyyy-mm-dd.pdf`.

Each date comes from that report's `generated_at` value in UTC. Earlier reports are
kept; same-day reruns replace that source's PDF, never the other source's PDF.
The weekly email attaches these two reports together. Registry research PDFs are
not part of the workflow.
