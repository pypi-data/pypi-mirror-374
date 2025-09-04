# judge_markday

Utility for marking daily results with judge integration.
## Usage

Install:

```bash
pip install judge-markday

Run:

```bash
mark-day --metrics metrics.json --log day_log.txt --date 2025-08-26

cat <<'EOF' >> README.md
## Usage

Install:

pip install judge-markday

Run:

mark-day --metrics metrics.json --log day_log.txt --date 2025-08-26

This will append a record to day_log.txt using data from metrics.json.
