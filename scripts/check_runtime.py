"""CPU check for a built vica-laya runner.

Runs fixed decisions with the published model and times the email preset. With --reference,
the same runs use a second binary; any changed decision fails the check, and the largest
probability difference is reported.
"""
import argparse
import json
import re
import subprocess
import sys

STATES = [
    {"title": "OpenAI releases new reasoning model", "description": "The model improves math benchmarks and agent tool use."},
    {"title": "PostgreSQL 18 adds async I/O", "description": "Database engineers get faster sequential scans."},
    {"title": "엔비디아 분기 매출 사상 최대", "description": "데이터센터 수요로 매출이 크게 늘었다."},
    {"title": "랜섬웨어 공격으로 병원 시스템 마비", "description": "공격자가 환자 기록을 암호화했다."},
]


def decide(exe, model, args):
    out = subprocess.run([exe, "decide", model, "--json", "--device", "cpu", *args],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(out[out.index("{"):])["answers"]


def values(answer):
    return [answer.get("confidence", 0), answer.get("noul", 0), answer.get("score", 0), *answer.get("probabilities", {}).values()]


def decision(answer):
    if "choice" in answer:
        return answer["choice"]
    if "score" in answer:
        return round(answer["score"])
    return answer.get("noul", 0) >= 0.5


def compare(ours, ref):
    diff, changed = 0.0, 0
    for a, b in zip(ours, ref):
        for k in a:
            diff = max(diff, *(abs(x - y) for x, y in zip(values(a[k]), values(b[k]))))
            changed += decision(a[k]) != decision(b[k])
    return diff, changed


def bench(exe, model):
    out = subprocess.run([exe, "bench", model, "--device", "cpu", "--preset", "email", "--warmup", "3", "--runs", "20"],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    m = re.search(r"mean ([\d.]+)\s+p50 ([\d.]+)\s+best ([\d.]+) ms", out)
    return {"mean_ms": float(m[1]), "p50_ms": float(m[2]), "best_ms": float(m[3])}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("exe")
    p.add_argument("model")
    p.add_argument("state_file")
    p.add_argument("questions_file")
    p.add_argument("output")
    p.add_argument("--reference")
    a = p.parse_args()

    states = [open(a.state_file, encoding="utf-8").read()] + [json.dumps(s, ensure_ascii=False) for s in STATES]
    cases = [["--state", s, "--questions-file", a.questions_file] for s in states]
    cases += [["--state", s, "--preset", "guard"] for s in states]
    result = {"answers": [decide(a.exe, a.model, c) for c in cases], "bench_cpu_email": bench(a.exe, a.model)}
    if a.reference:
        ref = [decide(a.reference, a.model, c) for c in cases]
        result["reference_bench_cpu_email"] = bench(a.reference, a.model)
        result["reference_answers"] = ref
        result["identical_to_reference"] = sum(x == y for x, y in zip(result["answers"], ref))
        result["cases"] = len(cases)
        result["max_abs_diff"], result["decision_changes"] = compare(result["answers"], ref)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("answers")}, indent=1))
    if a.reference and result["decision_changes"]:
        sys.exit("decisions differ from the reference build")


main()
