"""
Stage 1 — Locate a user-supplied HC-245 file.

This module does not download from AHRQ.

1. If a .dta file already exists in data/raw/, record provenance
   (name, size, sha256) into data/raw/provenance.json.
2. If nothing is there, print manual-download instructions and exit
   non-zero. The pipeline never continues with no data.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config

MANUAL_INSTRUCTIONS = f"""
No MEPS data file found in {config.DATA_RAW_DIR}.

This pipeline does not scrape or guess a download URL. Get the file yourself:

  1. Go to: {config.MEPS_SOURCE['doc_url']}
  2. Download the "{config.MEPS_SOURCE['stata_zip_hint']}"
  3. Unzip it and place the resulting .dta file into:
       {config.DATA_RAW_DIR}
  4. Re-run this pipeline.

Dataset: {config.MEPS_SOURCE['dataset_name']} ({config.MEPS_SOURCE['puf_id']}, {config.MEPS_SOURCE['coverage']})
"""


def _sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def find_raw_file() -> Path | None:
    config.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    candidates = sorted(config.DATA_RAW_DIR.glob("*.dta")) + sorted(config.DATA_RAW_DIR.glob("*.DTA"))
    return candidates[0] if candidates else None


def record_provenance(raw_file: Path) -> dict:
    record = {
        "dataset_name": config.MEPS_SOURCE["dataset_name"],
        "puf_id": config.MEPS_SOURCE["puf_id"],
        "coverage": config.MEPS_SOURCE["coverage"],
        "source_doc_url": config.MEPS_SOURCE["doc_url"],
        "file_name": raw_file.name,
        "file_size_bytes": raw_file.stat().st_size,
        "sha256": _sha256(raw_file),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "User-supplied file; not fetched automatically by this pipeline.",
    }
    out_path = config.DATA_RAW_DIR / "provenance.json"
    out_path.write_text(json.dumps(record, indent=2))
    return record


def main() -> Path:
    raw_file = find_raw_file()
    if raw_file is None:
        print(MANUAL_INSTRUCTIONS)
        sys.exit(1)
    record = record_provenance(raw_file)
    print(f"Found raw file: {raw_file.name} ({record['file_size_bytes']:,} bytes, sha256={record['sha256'][:12]}...)")
    return raw_file


if __name__ == "__main__":
    main()
