"""Dump the spoken text of each cut lesson (kept words within the EDL ranges,
in range order) for human review of coherence + leftover hesitations.

Writes one .txt per lesson into <plan_dir>/review/ and prints a summary with
any leftover "é..."/standalone-"é" hesitations still present.

Usage:
    python helpers/lesson_text.py <lessons.json>
"""
import json, re, sys
from pathlib import Path


def main():
    plan_path = Path(sys.argv[1]).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    transcript = json.loads(Path(plan["transcript"]).read_text(encoding="utf-8"))
    W = [w for w in transcript["words"] if w.get("type") == "word"
         and float(w["end"]) > float(w["start"])]
    outdir = plan_path.parent / "review"
    outdir.mkdir(exist_ok=True)

    def words_in(ranges):
        out = []
        for r in ranges:
            a, b = float(r["start"]), float(r["end"])
            seg = [w["text"] for w in W if float(w["start"]) >= a - 0.02 and float(w["end"]) <= b + 0.02]
            out.append(" ".join(seg))
        return out

    print(f"{'lesson':40} words  é-hesit")
    for L in plan["lessons"]:
        slug = L["slug"]
        edl_path = plan_path.parent / f"edl_{slug}.json"
        if not edl_path.exists():
            continue
        ranges = json.loads(edl_path.read_text(encoding="utf-8"))["ranges"]
        blocks = words_in(ranges)
        text = "\n\n— — —\n\n".join(blocks)
        # count leftover hesitations: token "é..." or standalone/short "é" surrounded by breaks
        hes = len(re.findall(r"\bé\.\.\.", text)) + len(re.findall(r"(?:^|\s)é(?:\s|$)", text))
        (outdir / f"{slug}.txt").write_text(
            f"# {L['title']}\n# ranges: {len(ranges)}\n\n{text}\n", encoding="utf-8")
        nwords = sum(len(b.split()) for b in blocks)
        print(f"{slug:40} {nwords:5}  {hes}")
    print(f"\nwrote {len(plan['lessons'])} files to {outdir}")


if __name__ == "__main__":
    main()
