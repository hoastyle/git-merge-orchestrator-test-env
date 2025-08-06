#!/usr/bin/env python3
"""
Git Merge Orchestrator - 性能基准测试脚本
测试不同规模和场景下的性能表现
"""

import os
import sys
import json
import subprocess
import time
import statistics
from pathlib import Path
from datetime import datetime
from create_test_repo import TestRepoCreator


class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(self, test_base_dir):
        self.test_base_dir = Path(test_base_dir)
        self.gmo_path = self.test_base_dir.parent / "git-merge-orchestrator"
        self.creator = TestRepoCreator(str(test_base_dir))
        self.benchmark_results = {}
        
    def run_benchmark_suite(self, scenarios=None, iterations=3):
        """运行基准测试套件"""
        if scenarios is None:
            scenarios = ["simple", "complex", "large-scale"]
            
        print("🚀 开始Git Merge Orchestrator性能基准测试")
        print(f"🔄 每个场景运行 {iterations} 次迭代")
        print("=" * 60)
        
        for scenario in scenarios:
            print(f"\n📊 基准测试场景: {scenario}")
            print("-" * 40)
            
            try:
                results = self._benchmark_scenario(scenario, iterations)
                self.benchmark_results[scenario] = results
                self._print_scenario_summary(scenario, results)
                
            except Exception as e:
                print(f"❌ 场景 {scenario} 基准测试失败: {e}")
                
        self._generate_benchmark_report()

    def _benchmark_scenario(self, scenario, iterations):
        """对单个场景进行基准测试"""
        scenario_configs = {
            "simple": {
                "type": "simple",
                "files": 20,
                "contributors": ["Dev1", "Dev2"],
                "branches": ["feature"]
            },
            "complex": {
                "type": "complex", 
                "files": 100,
                "contributors": ["Dev1", "Dev2", "Dev3", "Dev4", "Dev5"],
                "branches": ["feature-1", "feature-2"]
            },
            "large-scale": {
                "type": "large-scale",
                "files": 500,
                "contributors": [f"Dev{i}" for i in range(1, 11)],
                "branches": ["feature-main"]
            }
        }
        
        if scenario not in scenario_configs:
            raise ValueError(f"未知场景: {scenario}")
            
        config = scenario_configs[scenario]
        repo_name = f"benchmark-{scenario}"
        
        # 创建测试仓库
        repo_path = self._create_benchmark_repo(repo_name, config)
        if not repo_path:
            raise RuntimeError(f"创建基准测试仓库失败: {repo_name}")
            
        # 进行多次迭代测试
        iteration_results = []
        
        for i in range(iterations):
            print(f"  🔄 迭代 {i+1}/{iterations}")
            result = self._run_single_benchmark(repo_path, scenario)
            iteration_results.append(result)
            
            # 清理工作目录以确保一致的测试环境
            self._cleanup_work_dir(repo_path)
            
        return self._analyze_iteration_results(iteration_results, config)

    def _create_benchmark_repo(self, repo_name, config):
        """创建基准测试仓库"""
        # 先清理可能存在的旧仓库
        old_repo_path = self.test_base_dir / "test-repos" / repo_name
        if old_repo_path.exists():
            import shutil
            shutil.rmtree(old_repo_path)
            
        # 创建新的测试仓库
        repo_path = self.creator.create_repo(
            repo_name,
            config["type"],
            contributors=config["contributors"],
            files=config["files"],
            branches=config["branches"]
        )
        
        return repo_path

    def _run_single_benchmark(self, repo_path, scenario):
        """运行单次基准测试"""
        os.chdir(repo_path)
        
        # 测试不同的处理模式
        modes = ["file_level", "group_based"]
        mode_results = {}
        
        for mode in modes:
            print(f"    📋 测试模式: {mode}")
            
            # 确定要测试的分支
            branches = self._get_test_branches(repo_path)
            if not branches:
                continue
                
            source_branch, target_branch = branches[0], "master"
            
            # 执行性能测试
            start_time = time.time()
            
            cmd = [
                "python", str(self.gmo_path / "main.py"),
                "--processing-mode", mode,
                source_branch, target_branch,
                "--auto-analyze", "--quiet"
            ]
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300  # 5分钟超时
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # 收集性能指标
                metrics = self._collect_performance_metrics(repo_path, duration, result)
                mode_results[mode] = metrics
                
                print(f"      ⏱️ 耗时: {duration:.2f}秒")
                
            except subprocess.TimeoutExpired:
                print(f"      ⚠️ 超时 (>300秒)")
                mode_results[mode] = {"timeout": True, "duration": 300}
                
            except Exception as e:
                print(f"      ❌ 错误: {e}")
                mode_results[mode] = {"error": str(e)}
                
            # 清理工作目录
            self._cleanup_work_dir(repo_path)
            
        return mode_results

    def _get_test_branches(self, repo_path):
        """获取可用的测试分支"""
        try:
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                branches = []
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().replace('origin/', '')
                    if branch and branch != 'master' and not branch.startswith('HEAD'):
                        branches.append(branch)
                return branches
                
        except Exception:
            pass
            
        return ["feature"]  # 默认分支

    def _collect_performance_metrics(self, repo_path, duration, result):
        """收集性能指标"""
        metrics = {
            "duration": duration,
            "success": result.returncode == 0,
            "memory_usage": "N/A"  # 可以扩展添加内存监控
        }
        
        # 检查生成的文件
        merge_work_dir = repo_path / ".merge_work"
        if merge_work_dir.exists():
            plan_file = merge_work_dir / "merge_plan.json"
            if plan_file.exists():
                try:
                    with open(plan_file) as f:
                        plan_data = json.load(f)
                    
                    # 分析处理的数据量
                    if plan_data.get("processing_mode") == "file_level":
                        metrics["processed_files"] = len(plan_data.get("files", []))
                        metrics["processing_mode"] = "file_level"
                    else:
                        groups = plan_data.get("groups", [])
                        metrics["processed_groups"] = len(groups)
                        metrics["processed_files"] = sum(len(g.get("files", [])) for g in groups)
                        metrics["processing_mode"] = "group_based"
                        
                    metrics["contributors_analyzed"] = len(plan_data.get("contributors", {}))
                    
                except json.JSONDecodeError:
                    pass
        
        # 分析脚本生成情况
        scripts_dir = merge_work_dir / "scripts" if merge_work_dir.exists() else None
        if scripts_dir and scripts_dir.exists():
            script_count = len(list(scripts_dir.glob("*.sh")))
            metrics["generated_scripts"] = script_count
            
        return metrics

    def _cleanup_work_dir(self, repo_path):
        """清理工作目录"""
        merge_work_dir = repo_path / ".merge_work"
        if merge_work_dir.exists():
            import shutil
            shutil.rmtree(merge_work_dir)

    def _analyze_iteration_results(self, iteration_results, config):
        """分析迭代结果"""
        analysis = {
            "config": config,
            "iterations": len(iteration_results),
            "modes": {}
        }
        
        # 分析每种模式的结果
        for mode in ["file_level", "group_based"]:
            mode_data = []
            
            for iteration in iteration_results:
                if mode in iteration and "duration" in iteration[mode]:
                    mode_data.append(iteration[mode])
            
            if mode_data:
                durations = [d["duration"] for d in mode_data if "duration" in d]
                
                if durations:
                    analysis["modes"][mode] = {
                        "avg_duration": statistics.mean(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                        "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0,
                        "success_rate": sum(1 for d in mode_data if d.get("success", False)) / len(mode_data),
                        "sample_metrics": mode_data[0]  # 使用第一次迭代的详细指标
                    }
        
        return analysis

    def _print_scenario_summary(self, scenario, results):
        """打印场景摘要"""
        print(f"\n📊 场景 {scenario} 基准测试结果:")
        
        for mode, data in results["modes"].items():
            print(f"\n  🔧 {mode} 模式:")
            print(f"    ⏱️ 平均耗时: {data['avg_duration']:.2f}秒")
            print(f"    📊 耗时范围: {data['min_duration']:.2f}s - {data['max_duration']:.2f}s")
            print(f"    📈 标准差: {data['std_deviation']:.2f}秒")
            print(f"    ✅ 成功率: {data['success_rate']*100:.1f}%")
            
            sample = data["sample_metrics"]
            if "processed_files" in sample:
                print(f"    📁 处理文件数: {sample['processed_files']}")
            if "contributors_analyzed" in sample:
                print(f"    👥 分析贡献者: {sample['contributors_analyzed']}")

    def _generate_benchmark_report(self):
        """生成基准测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self._generate_summary(),
            "scenarios": self.benchmark_results,
            "system_info": self._collect_system_info()
        }
        
        # 保存详细报告
        report_file = self.test_base_dir / "logs" / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印摘要报告
        self._print_benchmark_summary(report)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        return report

    def _generate_summary(self):
        """生成摘要统计"""
        summary = {
            "total_scenarios": len(self.benchmark_results),
            "mode_comparison": {},
            "performance_grades": {}
        }
        
        # 比较不同模式的性能
        for mode in ["file_level", "group_based"]:
            mode_durations = []
            for scenario_results in self.benchmark_results.values():
                if mode in scenario_results["modes"]:
                    mode_durations.append(scenario_results["modes"][mode]["avg_duration"])
            
            if mode_durations:
                summary["mode_comparison"][mode] = {
                    "avg_duration": statistics.mean(mode_durations),
                    "scenarios_tested": len(mode_durations)
                }
        
        # 性能等级评估
        for scenario, results in self.benchmark_results.items():
            grades = {}
            for mode, data in results["modes"].items():
                avg_time = data["avg_duration"]
                success_rate = data["success_rate"]
                
                # 基于时间和成功率的简单评级
                if success_rate >= 0.9:
                    if avg_time <= 10:
                        grade = "优秀"
                    elif avg_time <= 30:
                        grade = "良好"
                    elif avg_time <= 60:
                        grade = "一般"
                    else:
                        grade = "需优化"
                else:
                    grade = "不稳定"
                    
                grades[mode] = grade
                
            summary["performance_grades"][scenario] = grades
        
        return summary

    def _collect_system_info(self):
        """收集系统信息"""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
                "git_version": self._get_git_version()
            }
        except ImportError:
            return {
                "platform": "未知",
                "note": "需要安装 psutil 库获取详细系统信息"
            }

    def _get_git_version(self):
        """获取Git版本"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "未知"
        except Exception:
            return "未知"

    def _print_benchmark_summary(self, report):
        """打印基准测试摘要"""
        print("\n" + "=" * 60)
        print("📊 性能基准测试摘要报告")
        print("=" * 60)
        
        summary = report["summary"]
        
        print(f"测试场景数: {summary['total_scenarios']}")
        print(f"测试时间: {report['timestamp'][:19]}")
        
        # 模式对比
        if summary.get("mode_comparison"):
            print("\n🔧 处理模式性能对比:")
            for mode, data in summary["mode_comparison"].items():
                print(f"  {mode}: 平均 {data['avg_duration']:.2f}秒 ({data['scenarios_tested']} 个场景)")
        
        # 性能等级
        print("\n🏆 性能等级评估:")
        for scenario, grades in summary["performance_grades"].items():
            print(f"  📋 {scenario}:")
            for mode, grade in grades.items():
                print(f"    {mode}: {grade}")
        
        # 系统信息
        if report.get("system_info"):
            print(f"\n💻 测试环境: {report['system_info'].get('platform', '未知')}")
            if "cpu_count" in report["system_info"]:
                print(f"    CPU: {report['system_info']['cpu_count']} 核心")
                print(f"    内存: {report['system_info']['memory_total']}")

        print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 性能基准测试")
    parser.add_argument(
        "--scenarios",
        default="simple,complex,large-scale",
        help="测试场景，逗号分隔"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="每个场景的迭代次数"
    )
    parser.add_argument(
        "--output",
        help="输出报告文件路径（可选）"
    )
    parser.add_argument(
        "--test-dir",
        default="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test",
        help="测试目录路径"
    )
    
    args = parser.parse_args()
    
    # 解析场景列表
    scenarios = [s.strip() for s in args.scenarios.split(",")]
    
    # 确保在正确的目录
    original_dir = os.getcwd()
    
    try:
        benchmark = PerformanceBenchmark(args.test_dir)
        benchmark.run_benchmark_suite(scenarios, args.iterations)
        
        # 如果指定了输出文件，复制报告
        if args.output:
            import shutil
            # 找到最新的报告文件
            logs_dir = Path(args.test_dir) / "logs"
            if logs_dir.exists():
                report_files = list(logs_dir.glob("benchmark_report_*.json"))
                if report_files:
                    latest_report = max(report_files, key=os.path.getctime)
                    shutil.copy2(latest_report, args.output)
                    print(f"📋 报告已复制到: {args.output}")
        
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    main()