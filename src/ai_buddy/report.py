from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Literal
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import argparse

from .data_models import Activity, ChildProfile
from .loader import load_activities, load_profiles
from .session import SessionLog, ActivityAttempt
from .persist import load_history
from .recommender import recommend_activities, explain_recommendation

# -------------------------
# Data & helpers
# -------------------------

OutcomeScore = {"success": 1.0, "partial": 0.6, "struggle": 0.2, "skipped": 0.0}

HOME_TIPS = {
    "spelling": "Play quick word-family games (cat, bat, mat). 5 minutes a day builds confidence.",
    "pattern_recognition": "Look for patterns in nature or blocks at home. Ask: 'What comes next?'",
    "storytelling": "At dinner, take turns adding a sentence to a silly family story.",
    "reading_comprehension": "After reading, ask: 'Who was the main character? What changed?'",
    "addition": "Cook together and add ingredient counts (2 cups + 1 cup).",
    "subtraction": "Snack math: 'We had 6 grapes, you ate 2—how many left?'",
    "logic": "Play 'Odd One Out' with household items and explain the reason."
}

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _period_range(period: str) -> Tuple[datetime, datetime]:
    # Supported: "7d", "14d", "30d"
    units = {"d": "days"}
    n = int(period[:-1]); u = period[-1]
    if u not in units: raise ValueError("Use Nd where N is int and d=days")
    end = _now()
    start = end - timedelta(days=n)
    return start, end

def _load_all() -> Tuple[List[Activity], List[ChildProfile], List[SessionLog]]:
    activities = load_activities("data/activities.json")
    profiles = load_profiles("data/profiles.json")
    history = load_history("data/history.json")
    return activities, profiles, history

def _index_activities(activities: List[Activity]) -> Dict[str, Activity]:
    return {a.id: a for a in activities}

# -------------------------
# Aggregation
# -------------------------

@dataclass
class SkillStat:
    attempts: int = 0
    total_score: float = 0.0
    avg: float = 0.0

def _collect_attempts_for_child(history: List[SessionLog], child_id: str, start: datetime, end: datetime) -> List[ActivityAttempt]:
    rows: List[ActivityAttempt] = []
    for sess in history:
        if sess.child_id != child_id: continue
        for att in sess.attempts:
            # Convert naive datetime to timezone-aware if needed
            timestamp = att.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            if start <= timestamp <= end:
                rows.append(att)
    return rows

def _fallback_if_empty(period_attempts: List[ActivityAttempt], history: List[SessionLog], child_id: str) -> Tuple[List[ActivityAttempt], bool]:
    if period_attempts:
        return period_attempts, False
    # fallback to lifetime
    rows: List[ActivityAttempt] = []
    for sess in history:
        if sess.child_id != child_id: continue
        rows.extend(sess.attempts)
    return rows, True

def _skill_and_type_metrics(attempts: List[ActivityAttempt], idx: Dict[str, Activity]) -> Tuple[Dict[str, SkillStat], Dict[str, SkillStat]]:
    skills: Dict[str, SkillStat] = {}
    types: Dict[str, SkillStat] = {}
    for att in attempts:
        score = OutcomeScore.get(att.outcome, 0.0)
        aid = att.activity_id
        act = idx.get(aid)
        if not act: continue
        # skills
        for s in act.skills:
            st = skills.setdefault(s, SkillStat())
            st.attempts += 1
            st.total_score += score
        # types
        tt = types.setdefault(act.type, SkillStat())
        tt.attempts += 1
        tt.total_score += score
    # finalize avg
    for d in (skills, types):
        for st in d.values():
            st.avg = (st.total_score / st.attempts) if st.attempts else 0.0
    return skills, types

def _time_fit_share(attempts: List[ActivityAttempt], idx: Dict[str, Activity], attention_span_min: int) -> float:
    if not attempts: return 0.0
    ok = 0
    for att in attempts:
        act = idx.get(att.activity_id)
        if not act: continue
        if act.estimated_min <= attention_span_min:
            ok += 1
    return ok / max(1, len(attempts))

def _classify(skills: Dict[str, SkillStat]) -> Tuple[List[str], List[str]]:
    sparks, focus = [], []
    for name, st in skills.items():
        if st.attempts >= 2 and st.avg >= 0.75:
            sparks.append(name)
        if st.attempts >= 2 and st.avg <= 0.5:
            focus.append(name)
    # Top-2 each
    sparks.sort(key=lambda s: (-skills[s].avg, -skills[s].attempts))
    focus.sort(key=lambda s: (skills[s].avg, -skills[s].attempts))
    return sparks[:2], focus[:2]

# -------------------------
# Report generation
# -------------------------

def _interests_engaged(child: ChildProfile, attempts: List[ActivityAttempt], idx: Dict[str, Activity]) -> List[str]:
    hits = set()
    child_int = set(x.lower() for x in child.interests)
    for att in attempts:
        act = idx.get(att.activity_id)
        if not act: continue
        tokens = set([act.type.lower(), *[t.lower() for t in act.tags]])
        if child_int & tokens:
            hits.update(child_int & tokens)
    return sorted(hits)[:3]

def _tips_for_focus(skills: List[str]) -> List[str]:
    tips = []
    for s in skills:
        if s in HOME_TIPS:
            tips.append(f"- **{s.replace('_',' ').title()}** — {HOME_TIPS[s]}")
    return tips[:3]

def _markdown_report(child: ChildProfile, period_label: str, lifetime_fallback: bool, skills: Dict[str, SkillStat], types: Dict[str, SkillStat], interests: List[str], time_fit_share: float, picks: List[Activity], idx: Dict[str, Activity]) -> str:
    sparks, focus = _classify(skills)
    def fmt_pct(x: float) -> str:
        return f"{round(x*100)}%"
    type_lines = [f"- **{t}** — {v.attempts} attempts, avg {fmt_pct(v.avg)}" for t,v in sorted(types.items(), key=lambda kv: (-kv[1].attempts, -kv[1].avg))]
    skill_lines = [f"- **{s.replace('_',' ').title()}** — {skills[s].attempts} attempts, avg {fmt_pct(skills[s].avg)}" for s in sorted(skills.keys(), key=lambda k: (-skills[k].attempts, -skills[k].avg))[:6]]
    pick_lines = [f"- **{a.title}** (_{a.id} · {a.type} · {a.level}_) " for a in picks]
    tips = _tips_for_focus(focus)

    header = f"# Parent Report — {child.name}\n\n**Period:** {period_label}" + (" (lifetime snapshot)" if lifetime_fallback else "") + "\n"
    highlights = f"## Highlights\n- **Sparks:** {', '.join(s.replace('_',' ').title() for s in sparks) if sparks else '—'}\n- **Growth areas:** {', '.join(s.replace('_',' ').title() for s in focus) if focus else '—'}\n- **Interests engaged:** {', '.join(interests) if interests else '—'}\n- **Time fit:** {round(time_fit_share*100)}% of activities matched attention span\n"
    snapshot = "## This Week's Activity Snapshot\n**By Type**\n" + ("\n".join(type_lines) if type_lines else "_No activity in period_") + "\n\n**By Skill**\n" + ("\n".join(skill_lines) if skill_lines else "_No skill data_") + "\n"
    next_up = "## Recommended Next Activities\n" + ("\n".join(pick_lines) if pick_lines else "_No picks_") + "\n"
    home = "## Try at Home\n" + ("\n".join(tips) if tips else "- Keep sessions short and fun. Let your child explain their thinking out loud.")

    return "\n".join([header, highlights, snapshot, next_up, home]) + "\n"

def _json_metrics(child_id: str, period_label: str, lifetime_fallback: bool, skills: Dict[str, SkillStat], types: Dict[str, SkillStat], interests: List[str], time_fit_share: float, picks: List[Activity]) -> Dict[str, Any]:
    return {
        "child_id": child_id,
        "period": period_label,
        "lifetime_fallback": lifetime_fallback,
        "skills": {k: {"attempts": v.attempts, "avg": v.avg} for k,v in skills.items()},
        "types": {k: {"attempts": v.attempts, "avg": v.avg} for k,v in types.items()},
        "interests_engaged": interests,
        "time_fit_share": time_fit_share,
        "recommended": [a.id for a in picks]
    }

def generate_parent_report(child: ChildProfile, activities: List[Activity], history: List[SessionLog], period: str = "7d", out_dir: str = "reports", fmt: Literal["md","json","both"]="md") -> List[Path]:
    start, end = _period_range(period)
    idx = _index_activities(activities)
    attempts = _collect_attempts_for_child(history, child.id, start, end)
    attempts, lifetime = _fallback_if_empty(attempts, history, child.id)

    skill_stats, type_stats = _skill_and_type_metrics(attempts, idx)
    interests = _interests_engaged(child, attempts, idx)
    time_share = _time_fit_share(attempts, idx, getattr(child, "attention_span_min", 10))

    # next picks
    picks = recommend_activities(child, activities, history, k=3)[:3]

    # build outputs
    period_label = f"{start.date().isoformat()} → {end.date().isoformat()}"
    md = _markdown_report(child, period_label, lifetime, skill_stats, type_stats, interests, time_share, picks, idx)
    js = _json_metrics(child.id, period_label, lifetime, skill_stats, type_stats, interests, time_share, picks)

    # save
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    stamp = _now().date().isoformat()
    paths: List[Path] = []
    if fmt in ("md","both"):
        p = out / f"{child.id}_{stamp}.md"
        p.write_text(md, encoding="utf-8")
        paths.append(p)
    if fmt in ("json","both"):
        p = out / f"{child.id}_{stamp}.json"
        p.write_text(json.dumps(js, indent=2), encoding="utf-8")
        paths.append(p)
    return paths

# -------------------------
# CLI
# -------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate parent reports")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--child", type=str, help="Child ID like C001")
    g.add_argument("--all", action="store_true", help="All children")
    parser.add_argument("--period", type=str, default="7d", help="e.g., 7d")
    parser.add_argument("--format", type=str, default="md", choices=["md","json","both"])
    args = parser.parse_args()

    activities, profiles, history = _load_all()
    targets = profiles if args.all else [p for p in profiles if p.id == args.child]
    if not targets:
        raise SystemExit("No matching child")

    written: List[Path] = []
    for child in targets:
        written.extend(generate_parent_report(child, activities, history, args.period, "reports", args.format))

    print("Wrote:")
    for p in written:
        print(" -", p.as_posix())

if __name__ == "__main__":
    main()
