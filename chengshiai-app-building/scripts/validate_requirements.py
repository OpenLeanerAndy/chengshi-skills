#!/usr/bin/env python3
"""Validate chengshiai-app-building requirement-state stage gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def validate(data: dict[str, Any], phase: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    project = data.get("project", {})
    users = data.get("users_access", {})
    scope = data.get("scope", {})
    modules = scope.get("modules", [])
    current = [m for m in modules if m.get("in_current_scope", True)]

    for key, label in (
        ("wanted_app", "想做什么应用"),
        ("current_method", "当前处理方式"),
        ("pain_points", "当前痛点"),
        ("final_outputs", "最终输出"),
    ):
        if not present(project.get(key)):
            errors.append(f"缺少：{label}")

    for key, label in (
        ("users", "使用人员"),
        ("access_scope", "访问范围"),
        ("data_sharing", "数据共享方式"),
        ("app_form", "应用形态"),
    ):
        if not present(users.get(key)):
            errors.append(f"缺少：{label}")

    if users.get("app_form") == "local" and len(users.get("users", [])) > 1:
        if users.get("local_app_tradeoff_accepted") is not True:
            errors.append("多人使用本地应用，但尚未确认接受安装、更新和数据分散代价")

    if not scope.get("module_boundaries_confirmed"):
        errors.append("大模块边界尚未确认")
    if not modules:
        errors.append("尚未定义大模块")
    if len(modules) >= 3 and not scope.get("phasing_confirmed"):
        errors.append("大模块不少于 3 个，但分期范围尚未确认")
    if not current:
        errors.append("本期范围中没有模块")

    for index, module in enumerate(current, start=1):
        name = module.get("name") or f"模块{index}"
        for key, label in (
            ("things_to_do", "要做的事情"),
            ("workflow", "正常流程"),
            ("data", "数据及来源"),
            ("rules", "业务规则"),
            ("pages", "页面或输出"),
        ):
            if not present(module.get(key)):
                errors.append(f"{name}缺少：{label}")
        if module.get("normal_confirmed") is not True:
            errors.append(f"{name}的正常需求尚未确认")
        if phase in {"prd", "development", "deployment"}:
            if not present(module.get("exceptions")):
                errors.append(f"{name}尚未记录异常情况或明确不适用原因")
            if module.get("exceptions_confirmed") is not True:
                errors.append(f"{name}的异常处理尚未确认")

    if phase in {"prd", "development", "deployment"}:
        design = data.get("design", {})
        for key, label in (
            ("theme_color", "主题色"),
            ("logo", "Logo 决定"),
            ("mockups", "页面效果图"),
        ):
            if not present(design.get(key)):
                errors.append(f"缺少：{label}")
        if design.get("mockups_confirmed") is not True:
            errors.append("页面效果图尚未确认")

        prd = data.get("prd", {})
        if Path(str(prd.get("path", ""))).name != "产品需求说明书.html":
            errors.append("PRD 文件名必须为《产品需求说明书.html》")
        if prd.get("complete") is not True:
            errors.append("HTML PRD 尚未标记为完整")

    if phase in {"development", "deployment"}:
        if data.get("prd", {}).get("confirmed") is not True:
            errors.append("用户尚未明确确认 HTML PRD，不能开发")
        delivery = data.get("delivery", {})
        if delivery.get("target_os") not in {"windows", "macos"}:
            errors.append("未确认双击运行程序的目标操作系统")
        if delivery.get("launcher_required") is not True:
            errors.append("默认双击运行程序未纳入交付")
        required_controls = {"status", "url", "start", "stop"}
        actual_controls = set(delivery.get("launcher_panel", []))
        missing = required_controls - actual_controls
        if missing:
            errors.append("运行面板缺少：" + ", ".join(sorted(missing)))

    if phase == "deployment":
        tests = data.get("testing", {})
        required_tests = (
            "syntax",
            "dependencies",
            "startup",
            "functions",
            "ui_match",
            "launcher",
            "cleanup",
        )
        for key in required_tests:
            if tests.get(key) is not True:
                errors.append(f"测试未通过：{key}")
        if tests.get("apis") is not True:
            warnings.append("API 测试未标记通过；若不适用，请在测试证据中写明原因")

    return errors, warnings


def self_test() -> int:
    invalid = {"project": {}, "users_access": {}, "scope": {"modules": []}}
    errors, _ = validate(invalid, "prd")
    if not errors:
        print("SELF-TEST FAILED: invalid fixture passed")
        return 1

    valid = {
        "project": {
            "wanted_app": "培训管理应用",
            "current_method": "Excel",
            "pain_points": ["重复整理"],
            "final_outputs": ["课程页面"],
        },
        "users_access": {
            "users": ["管理员"],
            "access_scope": "lan",
            "data_sharing": "共享",
            "app_form": "lan_web",
        },
        "scope": {
            "module_boundaries_confirmed": True,
            "phasing_confirmed": True,
            "modules": [
                {
                    "name": "课程管理",
                    "in_current_scope": True,
                    "things_to_do": ["新增课程"],
                    "workflow": ["填写", "发布"],
                    "data": [{"name": "课程名", "source": "人工", "current_acquisition": "填写"}],
                    "rules": ["课程名必填"],
                    "pages": ["课程列表"],
                    "normal_confirmed": True,
                    "exceptions": ["缺少课程名时提示"],
                    "exceptions_confirmed": True,
                }
            ],
        },
        "design": {
            "theme_color": "蓝色",
            "logo": "none",
            "mockups": [{"page": "课程列表", "path": "mockups/courses.png"}],
            "mockups_confirmed": True,
        },
        "delivery": {
            "target_os": "windows",
            "launcher_required": True,
            "launcher_panel": ["status", "url", "start", "stop"],
        },
        "prd": {"path": "产品需求说明书.html", "complete": True, "confirmed": True},
        "testing": {
            "syntax": True,
            "dependencies": True,
            "startup": True,
            "functions": True,
            "apis": True,
            "ui_match": True,
            "launcher": True,
            "cleanup": True,
        },
    }
    errors, warnings = validate(valid, "deployment")
    if errors or warnings:
        print("SELF-TEST FAILED:", json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=False))
        return 1
    print("SELF-TEST PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", nargs="?", type=Path)
    parser.add_argument(
        "--phase",
        choices=("interview", "prd", "development", "deployment"),
        default="interview",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.state is None:
        parser.error("state is required unless --self-test is used")

    try:
        data = json.loads(args.state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)], "warnings": []}, ensure_ascii=False, indent=2))
        return 2

    errors, warnings = validate(data, args.phase)
    print(json.dumps({"ok": not errors, "phase": args.phase, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
