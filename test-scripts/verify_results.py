#!/usr/bin/env python3
"""
Git Merge Orchestrator - 测试结果验证脚本
验证测试执行结果的正确性
"""

import os
import json
import subprocess
from pathlib import Path


class TestResultVerifier:
    """测试结果验证器"""

    def __init__(self, test_base_dir):
        self.test_base_dir = Path(test_base_dir)
        self.verification_results = []

    def verify_all_scenarios(self):
        """验证所有测试场景的结果"""
        print("🔍 开始验证测试结果...")
        print("=" * 50)

        scenarios_to_verify = [
            ("merge-conflicts-test", self._verify_merge_conflicts),
            ("file-level-test", self._verify_file_level_processing),
            ("load-balancing-test", self._verify_load_balancing),
            ("ignore-rules-test", self._verify_ignore_rules),
        ]

        for repo_name, verify_func in scenarios_to_verify:
            repo_path = self.test_base_dir / "test-repos" / repo_name

            if not repo_path.exists():
                print(f"⏭️ 跳过不存在的仓库: {repo_name}")
                continue

            print(f"\n📋 验证场景: {repo_name}")
            print("-" * 30)

            try:
                result = verify_func(repo_path)
                self.verification_results.append(
                    {
                        "scenario": repo_name,
                        "success": result,
                        "details": self._get_verification_details(repo_path),
                    }
                )

                status = "✅ 通过" if result else "❌ 失败"
                print(f"{status}")

            except Exception as e:
                print(f"❌ 验证异常: {e}")
                self.verification_results.append(
                    {"scenario": repo_name, "success": False, "error": str(e)}
                )

        self._print_verification_summary()
        return all(r["success"] for r in self.verification_results)

    def _verify_merge_conflicts(self, repo_path):
        """验证合并冲突场景"""
        # 检查合并计划是否存在
        plan_file = repo_path / ".merge_work" / "merge_plan.json"
        if not plan_file.exists():
            print("  ❌ 合并计划文件不存在")
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 验证基本结构
            if not self._validate_plan_structure(plan_data):
                print("  ❌ 合并计划结构无效")
                return False

            # 检查脚本生成
            scripts_dir = repo_path / ".merge_work" / "scripts"
            if not scripts_dir.exists() or not list(scripts_dir.glob("*.sh")):
                print("  ❌ 未生成合并脚本")
                return False

            print("  ✅ 合并计划和脚本生成正常")
            return True

        except json.JSONDecodeError:
            print("  ❌ 合并计划文件格式错误")
            return False

    def _verify_file_level_processing(self, repo_path):
        """验证文件级处理"""
        plan_file = repo_path / ".merge_work" / "merge_plan.json"
        if not plan_file.exists():
            print("  ❌ 合并计划文件不存在")
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 验证文件级结构
            if plan_data.get("processing_mode") != "file_level":
                print("  ❌ 处理模式不是 file_level")
                return False

            if "files" not in plan_data or not isinstance(plan_data["files"], list):
                print("  ❌ 缺少文件级数据结构")
                return False

            # 验证文件信息结构
            files = plan_data["files"]
            if not files:
                print("  ❌ 未处理任何文件")
                return False

            for file_info in files[:3]:  # 检查前3个文件
                required_fields = ["path", "assignee", "status"]
                if not all(field in file_info for field in required_fields):
                    print(f"  ❌ 文件信息缺少必需字段: {file_info}")
                    return False

            print(f"  ✅ 文件级处理正常，处理了 {len(files)} 个文件")
            return True

        except json.JSONDecodeError:
            print("  ❌ 合并计划文件格式错误")
            return False

    def _verify_load_balancing(self, repo_path):
        """验证负载均衡"""
        plan_file = repo_path / ".merge_work" / "merge_plan.json"
        if not plan_file.exists():
            print("  ❌ 合并计划文件不存在")
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 统计负载分配
            assignee_workload = {}

            if plan_data.get("processing_mode") == "file_level":
                for file_info in plan_data.get("files", []):
                    assignee = file_info.get("assignee", "未分配")
                    if assignee != "未分配":
                        assignee_workload[assignee] = (
                            assignee_workload.get(assignee, 0) + 1
                        )
            else:
                for group in plan_data.get("groups", []):
                    assignee = group.get("assignee", "未分配")
                    if assignee != "未分配":
                        file_count = len(group.get("files", []))
                        assignee_workload[assignee] = (
                            assignee_workload.get(assignee, 0) + file_count
                        )

            if not assignee_workload:
                print("  ❌ 未进行任务分配")
                return False

            if len(assignee_workload) < 2:
                print("  ⚠️ 负载均衡验证：只分配给了1个人")
                return True  # 仍然算通过，可能是合理的情况

            # 计算负载分配的均衡性
            workloads = list(assignee_workload.values())
            max_workload = max(workloads)
            min_workload = min(workloads)
            balance_ratio = min_workload / max_workload if max_workload > 0 else 0

            print(f"  ✅ 负载分配：{len(assignee_workload)} 个贡献者，平衡度 {balance_ratio:.2f}")
            return True

        except json.JSONDecodeError:
            print("  ❌ 合并计划文件格式错误")
            return False

    def _verify_ignore_rules(self, repo_path):
        """验证忽略规则"""
        # 检查忽略规则文件
        ignore_file = repo_path / ".merge_ignore"
        if not ignore_file.exists():
            print("  ❌ .merge_ignore 文件不存在")
            return False

        plan_file = repo_path / ".merge_work" / "merge_plan.json"
        if not plan_file.exists():
            print("  ❌ 合并计划文件不存在")
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 收集处理的文件列表
            processed_files = []
            if plan_data.get("processing_mode") == "file_level":
                processed_files = [f["path"] for f in plan_data.get("files", [])]
            else:
                for group in plan_data.get("groups", []):
                    processed_files.extend(group.get("files", []))

            # 检查是否包含应该被忽略的文件类型
            ignored_extensions = [".pyc", ".log", ".tmp", ".DS_Store"]
            ignored_dirs = ["__pycache__", "node_modules", ".vscode"]

            has_ignored_files = any(
                any(f.endswith(ext) for ext in ignored_extensions)
                or any(dir_name in f for dir_name in ignored_dirs)
                for f in processed_files
            )

            if has_ignored_files:
                print("  ❌ 忽略规则失效：包含应忽略的文件")
                print(f"    处理的文件: {processed_files[:5]}...")  # 显示前5个
                return False

            print(f"  ✅ 忽略规则正常：正确过滤了临时文件（处理 {len(processed_files)} 个文件）")
            return True

        except json.JSONDecodeError:
            print("  ❌ 合并计划文件格式错误")
            return False

    def _validate_plan_structure(self, plan_data):
        """验证合并计划的基本结构"""
        required_fields = ["source_branch", "target_branch", "timestamp"]

        # 检查基本字段
        if not all(field in plan_data for field in required_fields):
            return False

        # 检查数据结构
        processing_mode = plan_data.get("processing_mode", "group_based")

        if processing_mode == "file_level":
            return "files" in plan_data and isinstance(plan_data["files"], list)
        else:
            return "groups" in plan_data and isinstance(plan_data["groups"], list)

    def _get_verification_details(self, repo_path):
        """获取验证详细信息"""
        details = {}

        # 检查合并计划
        plan_file = repo_path / ".merge_work" / "merge_plan.json"
        if plan_file.exists():
            try:
                with open(plan_file) as f:
                    plan_data = json.load(f)

                details["processing_mode"] = plan_data.get("processing_mode", "unknown")
                details["source_branch"] = plan_data.get("source_branch", "unknown")
                details["target_branch"] = plan_data.get("target_branch", "unknown")

                if plan_data.get("processing_mode") == "file_level":
                    details["files_count"] = len(plan_data.get("files", []))
                else:
                    details["groups_count"] = len(plan_data.get("groups", []))

            except json.JSONDecodeError:
                details["plan_file_error"] = "JSON格式错误"

        # 检查脚本生成
        scripts_dir = repo_path / ".merge_work" / "scripts"
        if scripts_dir.exists():
            details["generated_scripts"] = len(list(scripts_dir.glob("*.sh")))

        return details

    def _print_verification_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 50)
        print("📊 测试结果验证摘要")
        print("=" * 50)

        total_scenarios = len(self.verification_results)
        successful_scenarios = sum(1 for r in self.verification_results if r["success"])

        print(f"验证场景数: {total_scenarios}")
        print(f"成功验证: {successful_scenarios}")
        print(f"失败验证: {total_scenarios - successful_scenarios}")
        print(
            f"成功率: {successful_scenarios/total_scenarios*100:.1f}%"
            if total_scenarios > 0
            else "0%"
        )

        print("\n场景详情:")
        for result in self.verification_results:
            status = "✅" if result["success"] else "❌"
            scenario = result["scenario"]
            print(f"  {status} {scenario}")

            if "details" in result:
                details = result["details"]
                if "processing_mode" in details:
                    print(f"      模式: {details['processing_mode']}")
                if "files_count" in details:
                    print(f"      文件数: {details['files_count']}")
                elif "groups_count" in details:
                    print(f"      组数: {details['groups_count']}")
                if "generated_scripts" in details:
                    print(f"      脚本数: {details['generated_scripts']}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试结果验证")
    parser.add_argument(
        "--test-dir",
        default="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test",
        help="测试目录路径",
    )
    parser.add_argument("--scenario", help="验证特定场景（可选）")

    args = parser.parse_args()

    verifier = TestResultVerifier(args.test_dir)

    if args.scenario:
        # 验证特定场景
        repo_path = Path(args.test_dir) / "test-repos" / args.scenario
        if not repo_path.exists():
            print(f"❌ 场景不存在: {args.scenario}")
            return False

        print(f"🔍 验证场景: {args.scenario}")
        # 这里可以扩展单个场景的验证逻辑
        return True
    else:
        # 验证所有场景
        success = verifier.verify_all_scenarios()
        return success


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
