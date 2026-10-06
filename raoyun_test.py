#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""绕晕指数测试 —— 2026 中秋国庆调休节奏问卷。

致敬 2026-09-14 热搜第一："上5休1、上5休3、上3休7、上3休1，网友：已绕晕"。
7 道题，答对加分、答错扣分，总分 0-100 对应 5 档绕晕等级。
纯娱乐，无医学依据；调休数据依据 2026 年真实安排（已用 date -d 核验星期）。
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import date

# 依据 2026 年真实放假调休安排（星期已用 `date -d` 核验）：
# 中秋 9/25(周五)-9/27(周日) 休；国庆 10/1(周四)-10/7(周三) 休；
# 9/20(周日)、10/10(周六) 调休上班。
WORK_DAYS = frozenset({"2026-09-20", "2026-10-10"})


def days_to_new_year(today: date | None = None) -> int:
    """距离 2027 年元旦还有多少天（动态计算）。"""
    today = today or date.today()
    return (date(2027, 1, 1) - today).days


def build_questions(today: date | None = None) -> list[dict]:
    return [
        {
            "text": "【第 1 题】9月20日是周日，这天上不上班？（提示：中秋调休）\n输入 上班 / 不上班：",
            "kind": "bool",
            "answer": True,
            "explain": "9月20日（周日）调休上班——中秋假期是 9/25-9/27，这天是提前补班。",
        },
        {
            "text": "【第 2 题】10月10日是周六，这天上不上班？（提示：国庆调休）\n输入 上班 / 不上班：",
            "kind": "bool",
            "answer": True,
            "explain": "10月10日（周六）调休上班——国庆假期是 10/1-10/7，这天是补班。",
        },
        {
            "text": "【第 3 题】9月27日是中秋假期最后一天，这天上不上班？\n输入 上班 / 不上班：",
            "kind": "bool",
            "answer": False,
            "explain": "9月27日（周日）是中秋假期最后一天，放假，不上班。",
        },
        {
            "text": "【第 4 题】10月9日（周五，国庆收假第二天）上不上班？\n输入 上班 / 不上班：",
            "kind": "bool",
            "answer": True,
            "explain": "10月8日就收假了，10月9日正常上班——别做梦了。",
        },
        {
            "text": "【第 5 题】9月28/29/30（周一到周三）请 3 天年假，从 9月25日中秋假期算起，最多连休几天？（填数字）",
            "kind": "int",
            "answer": 13,
            "explain": "9/25-9/27 中秋休 3 天 + 请假 3 天 + 10/1-10/7 国庆休 7 天 = 请3休13，经典操作。",
        },
        {
            "text": "【第 6 题】国庆 10月1日到7日放 7 天，加上紧挨着的周末，最多连休几天？（填数字）",
            "kind": "int",
            "answer": 7,
            "explain": "陷阱！前面 9/28-9/30 要上班隔开，后面 10/10（周六）调休上班——紧挨的周末根本连不上，就是 7 天。",
        },
        {
            "text": "【第 7 题·陷阱】下一次法定放假是 2027 年元旦，距离今天还有多少天？（填数字）",
            "kind": "int",
            "answer": days_to_new_year(today),
            "explain": "动态计算：(2027-01-01 - 今天).days。这道题答对不代表清醒，只代表会算数。",
        },
    ]


WEIGHTS = [12, 12, 12, 12, 16, 16, 20]  # 合计 100
MAX_SCORE = sum(WEIGHTS)

TIERS = [
    (90, "人间清醒", "调休表倒背如流，建议去国务院办公厅兼职排班。"),
    (70, "轻微绕晕", "偶尔把周六当周日，多喝热水就好。"),
    (50, "晕头转向", "已经开始在日历上画圈圈了，正常，全国人民陪你。"),
    (30, "彻底绕晕", "上5休1、上5休3、上3休7、上3休1——你已经分不清自己在哪一天。"),
    (0, "调休受害者", "建议把本程序设为开机启动，每天默念三遍：今天上不上班。"),
]


def parse_answer(raw: str, kind: str):
    """解析用户输入；非法输入返回 None。"""
    raw = raw.strip()
    if kind == "bool":
        if raw in ("上班", "上", "是", "y", "Y", "yes"):
            return True
        if raw in ("不上班", "不上", "休", "不", "否", "n", "N", "no"):
            return False
        return None
    if kind == "int":
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def grade(questions: list[dict], answers: list) -> tuple[int, list[bool]]:
    """评分：答对加权，答错扣一半权重（非法输入按答错），总分钳在 0-100。"""
    score = 0
    flags: list[bool] = []
    for q, ans, w in zip(questions, answers, WEIGHTS):
        ok = ans == q["answer"]
        flags.append(ok)
        score += w if ok else -(w // 2)
    return max(0, min(100, score)), flags


def tier_of(score: int) -> tuple[str, str]:
    for bar, name, comment in TIERS:
        if score >= bar:
            return name, comment
    return TIERS[-1][1], TIERS[-1][2]


def run_interactive(questions: list[dict]) -> None:
    if not sys.stdin.isatty():
        print("交互模式需要终端输入；请用 --auto 模式自动演示。", file=sys.stderr)
        sys.exit(2)
    answers = []
    for q in questions:
        while True:
            raw = input(q["text"] + "\n> ")
            ans = parse_answer(raw, q["kind"])
            if ans is not None:
                answers.append(ans)
                break
            print("看不懂你的回答，再说一遍（上班/不上班，或数字）：")
    score, flags = grade(questions, answers)
    name, comment = tier_of(score)
    print(f"\n你的绕晕指数：{score} 分 ——【{name}】")
    print(comment)
    print("\n--- 逐题讲解 ---")
    for q, ok in zip(questions, flags):
        mark = "✔" if ok else "✘"
        print(f"{mark} {q['explain']}")


def run_auto(games: int, seed: int) -> None:
    rng = random.Random(seed)
    today = date.today()
    buckets: dict[str, int] = {}
    total = 0
    for _ in range(games):
        questions = build_questions(today)
        answers = []
        for q in questions:
            if q["kind"] == "bool":
                answers.append(rng.random() < 0.5)
            else:
                # AI 随机答题：50% 猜对，50% 在附近瞎猜
                if rng.random() < 0.5:
                    answers.append(q["answer"])
                else:
                    answers.append(q["answer"] + rng.choice([-3, -2, -1, 1, 2, 3]))
        score, _ = grade(questions, answers)
        name, _ = tier_of(score)
        buckets[name] = buckets.get(name, 0) + 1
        total += score
    print(f"虚拟用户 {games} 局（seed={seed}），平均分 {total / games:.1f}：")
    for name, _ in [(t[1], t[2]) for t in TIERS]:
        n = buckets.get(name, 0)
        bar = "█" * n
        print(f"  {name}：{bar} ({n})")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="绕晕指数测试：2026 调休节奏问卷")
    ap.add_argument("--auto", action="store_true", help="自动演示（AI 随机答题）")
    ap.add_argument("--games", type=int, default=10, help="自动演示局数")
    ap.add_argument("--seed", type=int, default=42, help="随机种子")
    args = ap.parse_args(argv)
    if args.auto:
        run_auto(args.games, args.seed)
    else:
        run_interactive(build_questions())


if __name__ == "__main__":
    main()
