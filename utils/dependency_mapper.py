"""
Control-M XML -> static JSON dependency config, plus on-demand lookup.

Step 1 (run once, or whenever the XML export changes):
    python ctm_dependency_mapper.py build ctm_data.xml -o dependency_map.json

Step 2 (any time you need a lookup - reads the JSON file at that moment, nothing kept in memory):
    python ctm_dependency_mapper.py query dependency_map.json JOBNAME

From your agent:
    from ctm_dependency_mapper import lookup
    lookup("dependency_map.json", "DBARRT_FIN_RDM_DAILY_VNM")

Static file shape (keyed by job name):
    { "<JOB>": { "predecessors": [...], "successors": [...] }, ... }
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict


def build_map(xml_path):
    """Parse the XML and return {job: {predecessors, successors}}."""
    root = ET.parse(xml_path).getroot()
    adders, waiters, names = defaultdict(list), defaultdict(list), []

    for job in root.iter("JOB"):
        name = job.get("JOBNAME")
        if not name:
            continue
        names.append(name)
        for c in job:
            if c.tag == "OUTCOND" and c.get("SIGN", "+") == "+":
                adders[c.get("NAME")].append(name)
            elif c.tag == "INCOND":
                waiters[c.get("NAME")].append(name)

    preds, succs = defaultdict(set), defaultdict(set)
    for cond, consumers in waiters.items():
        for consumer in consumers:
            for producer in adders.get(cond, []):
                if producer != consumer:
                    preds[consumer].add(producer)
                    succs[producer].add(consumer)

    return {
        n: {"predecessors": sorted(preds[n]), "successors": sorted(succs[n])}
        for n in names
    }


def lookup(json_path, name):
    """Read the static JSON file and return the job, its predecessors and successors."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for job, deps in data.items():
        if job.lower() == name.lower():
            return {"job": job, **deps}

    low = name.lower()
    return {
        "job": name,
        "found": False,
        "suggestions": [j for j in data if low in j.lower()][:10],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("xml")
    b.add_argument("-o", "--output", default="dependency_map.json")
    q = sub.add_parser("query")
    q.add_argument("json_file")
    q.add_argument("job")
    a = ap.parse_args()

    if a.cmd == "build":
        m = build_map(a.xml)
        with open(a.output, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2)
        print(f"{len(m)} jobs -> {a.output}")
    else:
        print(json.dumps(lookup(a.json_file, a.job), indent=2))


if __name__ == "__main__":
    sys.exit(main())
