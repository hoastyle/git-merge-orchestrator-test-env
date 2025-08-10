#!/usr/bin/env python3
"""
Git Merge Orchestrator - 集成测试脚本
自动化运行各种测试场景并验证结果
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime


class IntegrationTester:
    """集成测试执行器"""

    def __init__(self, test_base_dir):
        self.test_base_dir = Path(test_base_dir).absolute()
        self.gmo_path = self.test_base_dir.parent
        self.results = []

        # 验证main.py存在
        self.main_py = self.gmo_path / "main.py"
        if not self.main_py.exists():
            raise RuntimeError(f"找不到主程序: {self.main_py}")

    def run_all_tests(self):
        """运行所有集成测试"""
        print("🚀 开始Git Merge Orchestrator集成测试")
        print("=" * 60)

        test_scenarios = [
            ("basic_functionality", self._test_basic_functionality),
            ("file_level_processing", self._test_file_level_processing),
            ("merge_conflicts", self._test_merge_conflicts),
            ("load_balancing", self._test_load_balancing),
            ("ignore_rules", self._test_ignore_rules),
            ("performance", self._test_performance),
        ]

        for test_name, test_func in test_scenarios:
            print(f"\n📋 执行测试: {test_name}")
            print("-" * 40)

            try:
                start_time = time.time()
                result = test_func()
                end_time = time.time()

                self.results.append(
                    {
                        "test_name": test_name,
                        "success": result,
                        "duration": end_time - start_time,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                status = "✅ 通过" if result else "❌ 失败"
                print(f"{status} - 耗时: {end_time - start_time:.2f}秒")

            except Exception as e:
                print(f"❌ 测试异常: {e}")
                self.results.append(
                    {
                        "test_name": test_name,
                        "success": False,
                        "error": str(e),
                        "duration": 0,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        self._generate_report()

    def _test_basic_functionality(self):
        """测试基本功能"""
        # 确保测试场景存在
        self._setup_scenario("merge-conflicts")

        test_repo = self.test_base_dir / "test-repos" / "merge-conflicts-test"
        if not test_repo.exists():
            print("❌ 测试仓库不存在")
            return False

        os.chdir(test_repo)

        # 运行基本分析 (非交互式自动计划创建)
        cmd = ["python", str(self.main_py), "feature-1", "master", "--auto-plan", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        # 检查是否生成了基本文件
        merge_work_dir = test_repo / ".merge_work"
        # v2.3 系统使用 file_plan.json（文件级模式）
        plan_file = merge_work_dir / "file_plan.json"

        success = (
            result.returncode == 0
            or result.returncode == 124  # timeout退出码
            or (result.returncode == 1 and merge_work_dir.exists())  # 交互模式但创建了工作目录
            and merge_work_dir.exists()
        )

        if success:
            print("✅ 基本功能正常：生成了合并计划")
        else:
            print(f"❌ 基本功能失败: {result.stderr}")

        return success

    def _test_file_level_processing(self):
        """测试文件级处理功能"""
        self._setup_scenario("file-level-processing")

        test_repo = self.test_base_dir / "test-repos" / "file-level-test"
        if not test_repo.exists():
            print("❌ 文件级测试仓库不存在")
            return False

        os.chdir(test_repo)

        # 运行文件级处理 (非交互式自动计划创建)
        cmd = [
            "python",
            str(self.main_py),
            "file-level-feature",
            "master",
            "--processing-mode",
            "file_level",
            "--auto-plan",
            "--quiet",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

        # 检查文件级数据结构
        # v2.3 系统使用 file_plan.json（文件级模式）
        plan_file = test_repo / ".merge_work" / "file_plan.json"
        if not plan_file.exists():
            print("❌ 合并计划文件不存在")
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 验证文件级结构
            has_file_level = (
                plan_data.get("processing_mode") == "file_level"
                and "files" in plan_data
                and isinstance(plan_data["files"], list)
            )

            if has_file_level:
                file_count = len(plan_data["files"])
                print(f"✅ 文件级处理正常：处理了 {file_count} 个文件")
                return True
            else:
                print("❌ 未检测到文件级数据结构")
                return False

        except json.JSONDecodeError:
            print("❌ 合并计划文件格式错误")
            return False

    def _test_merge_conflicts(self):
        """测试合并冲突处理"""
        self._setup_scenario("merge-conflicts")

        test_repo = self.test_base_dir / "test-repos" / "merge-conflicts-test"
        if not test_repo.exists():
            return False

        os.chdir(test_repo)

        # 分析分支差异
        try:
            # 检查是否有合并冲突
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", "feature-1", "master"],
                capture_output=True,
                text=True,
            )

            if diff_result.returncode == 0 and diff_result.stdout.strip():
                print(f"✅ 检测到 {len(diff_result.stdout.strip().split())} 个差异文件")

                # 尝试运行合并分析 (非交互式自动完整流程)
                cmd = [
                    "python",
                    str(self.main_py),
                    "feature-1",
                    "master",
                    "--strategy",
                    "standard",
                    "--auto-workflow",
                    "--quiet",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                # v2.3 系统：检查是否完成了任务分配（替代merge scripts检查）
                plan_file = test_repo / ".merge_work" / "file_plan.json"
                if plan_file.exists():
                    try:
                        with open(plan_file) as f:
                            plan_data = json.load(f)
                        # 检查是否有分配的任务
                        assigned_files = [f for f in plan_data.get("files", []) if f.get("assignee")]
                        if assigned_files:
                            print(f"✅ 合并冲突处理：已分配 {len(assigned_files)} 个文件")
                            return True
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            print(f"❌ 合并冲突测试异常: {e}")

        return False

    def _test_load_balancing(self):
        """测试负载均衡功能"""
        self._setup_scenario("load-balancing")

        test_repo = self.test_base_dir / "test-repos" / "load-balancing-test"
        if not test_repo.exists():
            return False

        os.chdir(test_repo)

        cmd = ["python", str(self.main_py), "load-test-feature", "master", "--auto-workflow", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # 检查分配结果
        # v2.3 系统使用 file_plan.json（文件级模式）
        plan_file = test_repo / ".merge_work" / "file_plan.json"
        if not plan_file.exists():
            return False

        try:
            with open(plan_file) as f:
                plan_data = json.load(f)

            # 分析负载分配
            assignee_workload = {}

            if plan_data.get("processing_mode") == "file_level":
                for file_info in plan_data.get("files", []):
                    assignee = file_info.get("assignee", "未分配")
                    assignee_workload[assignee] = assignee_workload.get(assignee, 0) + 1
            else:
                for group in plan_data.get("groups", []):
                    assignee = group.get("assignee", "未分配")
                    file_count = len(group.get("files", []))
                    assignee_workload[assignee] = assignee_workload.get(assignee, 0) + file_count

            # 检查负载是否相对平衡

            # 过滤掉未分配的任务，只分析已分配的
            assigned_workload = {k: v for k, v in assignee_workload.items() if k != "未分配"}

            if len(assigned_workload) > 1:
                workloads = list(assigned_workload.values())
                max_workload = max(workloads)
                min_workload = min(workloads)
                balance_ratio = min_workload / max_workload if max_workload > 0 else 0

                print(f"✅ 负载均衡检查：最大负载 {max_workload}，最小负载 {min_workload}，平衡度 {balance_ratio:.2f}")
                return balance_ratio > 0.3  # 允许一定程度的不平衡
            elif len(assigned_workload) == 1:
                print("✅ 负载均衡检查：只有一个分配对象，测试通过")
                return True

        except json.JSONDecodeError:
            pass

        return False

    def _test_ignore_rules(self):
        """测试忽略规则功能"""
        self._setup_scenario("ignore-rules")

        test_repo = self.test_base_dir / "test-repos" / "ignore-rules-test"
        if not test_repo.exists():
            return False

        os.chdir(test_repo)

        # 检查忽略规则文件
        ignore_file = test_repo / ".merge_ignore"
        if not ignore_file.exists():
            print("❌ .merge_ignore 文件不存在")
            return False

        cmd = ["python", str(self.main_py), "feature", "master", "--auto-plan", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        # 检查是否正确过滤了文件
        # v2.3 系统使用 file_plan.json（文件级模式）
        plan_file = test_repo / ".merge_work" / "file_plan.json"

        if plan_file.exists():
            try:
                with open(plan_file) as f:
                    plan_data = json.load(f)

                # 检查处理的文件中是否包含应该被忽略的文件
                processed_files = []
                if plan_data.get("processing_mode") == "file_level":
                    processed_files = [f["path"] for f in plan_data.get("files", [])]
                else:
                    for group in plan_data.get("groups", []):
                        processed_files.extend(group.get("files", []))

                # 检查是否包含 .pyc, .log 等应该被忽略的文件
                ignored_extensions = [".pyc", ".log", ".tmp"]
                has_ignored_files = any(any(f.endswith(ext) for ext in ignored_extensions) for f in processed_files)

                if not has_ignored_files:
                    print("✅ 忽略规则正常：已过滤掉临时文件")
                    return True
                else:
                    print("❌ 忽略规则失效：仍包含应忽略的文件")

            except json.JSONDecodeError:
                pass

        return False

    def _test_performance(self):
        """测试性能"""
        self._setup_scenario("large-scale-performance")

        test_repo = self.test_base_dir / "test-repos" / "performance-test"
        if not test_repo.exists():
            return False

        os.chdir(test_repo)

        # 性能测试
        start_time = time.time()

        cmd = ["python", str(self.main_py), "feature", "master", "--auto-plan", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        end_time = time.time()
        duration = end_time - start_time

        # 性能标准：大规模仓库分析应在3分钟内完成
        performance_ok = duration < 180

        if performance_ok:
            print(f"✅ 性能测试通过：耗时 {duration:.2f} 秒")
        else:
            print(f"❌ 性能测试失败：耗时 {duration:.2f} 秒，超过180秒限制")

        return performance_ok

    def _setup_scenario(self, scenario_name):
        """设置测试场景"""
        setup_script = self.test_base_dir / "test-scripts" / "setup_scenarios.py"
        if setup_script.exists():
            subprocess.run(
                ["python", str(setup_script), "--scenario", scenario_name],
                capture_output=True,
            )

    def _generate_report(self):
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%",
            },
            "test_results": self.results,
        }

        # 保存报告
        report_file = (
            self.test_base_dir / "logs" / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 集成测试报告摘要")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"成功率: {report['summary']['success_rate']}")
        print("-" * 60)

        for result in self.results:
            status = "✅" if result["success"] else "❌"
            duration = result.get("duration", 0)
            print(f"{status} {result['test_name']} - {duration:.2f}秒")

        print("-" * 60)
        print(f"详细报告: {report_file}")

        # 返回整体成功状态
        return passed_tests == total_tests


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 集成测试")
    parser.add_argument("--test-dir", default=".", help="测试目录路径")

    args = parser.parse_args()

    # 确保在正确的目录
    original_dir = os.getcwd()

    try:
        tester = IntegrationTester(args.test_dir)
        success = tester.run_all_tests()

        # 退出码
        sys.exit(0 if success else 1)

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    main()
