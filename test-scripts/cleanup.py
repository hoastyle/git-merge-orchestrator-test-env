#!/usr/bin/env python3
"""
Git Merge Orchestrator - 测试环境清理工具
清理测试仓库、日志文件和临时数据
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
import json
from datetime import datetime


class TestCleanupTool:
    """测试清理工具"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.test_repos_dir = self.base_dir / "test-repos"
        self.logs_dir = self.base_dir / "logs"
        self.scenarios_dir = self.base_dir / "scenarios"

    def cleanup_all(self, confirm=True):
        """清理所有测试数据"""
        if confirm:
            print("⚠️ 这将删除所有测试仓库、日志和场景数据！")
            response = input("确认继续？(yes/NO): ")
            if response.lower() not in ["yes", "y"]:
                print("❌ 取消清理操作")
                return

        print("🧹 开始清理所有测试数据...")

        cleaned_items = []

        # 清理测试仓库
        if self.test_repos_dir.exists():
            repo_count = len([d for d in self.test_repos_dir.iterdir() if d.is_dir()])
            shutil.rmtree(self.test_repos_dir)
            self.test_repos_dir.mkdir()
            cleaned_items.append(f"测试仓库: {repo_count} 个")

        # 清理日志
        if self.logs_dir.exists():
            log_count = len([f for f in self.logs_dir.iterdir() if f.is_file()])
            shutil.rmtree(self.logs_dir)
            self.logs_dir.mkdir()
            cleaned_items.append(f"日志文件: {log_count} 个")

        # 清理场景信息
        if self.scenarios_dir.exists():
            scenario_count = len(
                [f for f in self.scenarios_dir.iterdir() if f.is_file()]
            )
            shutil.rmtree(self.scenarios_dir)
            self.scenarios_dir.mkdir()
            cleaned_items.append(f"场景文件: {scenario_count} 个")

        print("✅ 清理完成:")
        for item in cleaned_items:
            print(f"   - {item}")

    def cleanup_repos(self, repo_names=None, confirm=True):
        """清理指定的测试仓库"""
        if not self.test_repos_dir.exists():
            print("📋 没有找到测试仓库目录")
            return

        if repo_names is None:
            # 清理所有仓库
            repos_to_clean = [d for d in self.test_repos_dir.iterdir() if d.is_dir()]
            if confirm:
                print(f"⚠️ 将删除 {len(repos_to_clean)} 个测试仓库")
                response = input("确认继续？(yes/NO): ")
                if response.lower() not in ["yes", "y"]:
                    print("❌ 取消清理操作")
                    return
        else:
            # 清理指定仓库
            repos_to_clean = []
            for repo_name in repo_names:
                repo_path = self.test_repos_dir / repo_name
                if repo_path.exists():
                    repos_to_clean.append(repo_path)
                else:
                    print(f"⚠️ 仓库不存在: {repo_name}")

        if not repos_to_clean:
            print("📋 没有找到要清理的仓库")
            return

        print(f"🧹 清理 {len(repos_to_clean)} 个测试仓库...")

        cleaned_count = 0
        for repo_path in repos_to_clean:
            try:
                repo_size = self._get_directory_size(repo_path)
                shutil.rmtree(repo_path)
                cleaned_count += 1
                print(f"   ✅ 已删除: {repo_path.name} ({self._format_size(repo_size)})")
            except Exception as e:
                print(f"   ❌ 删除失败: {repo_path.name} - {e}")

        print(f"✅ 仓库清理完成: {cleaned_count} 个仓库已删除")

    def cleanup_logs(self, older_than_days=None, confirm=True):
        """清理日志文件"""
        if not self.logs_dir.exists():
            print("📋 没有找到日志目录")
            return

        log_files = [f for f in self.logs_dir.iterdir() if f.is_file()]

        if older_than_days:
            # 只清理超过指定天数的日志
            cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
            files_to_clean = [f for f in log_files if f.stat().st_mtime < cutoff_time]
            print(f"🧹 清理超过 {older_than_days} 天的日志文件...")
        else:
            # 清理所有日志
            files_to_clean = log_files
            if confirm:
                print(f"⚠️ 将删除 {len(files_to_clean)} 个日志文件")
                response = input("确认继续？(yes/NO): ")
                if response.lower() not in ["yes", "y"]:
                    print("❌ 取消清理操作")
                    return

        if not files_to_clean:
            print("📋 没有找到要清理的日志文件")
            return

        cleaned_count = 0
        total_size = 0
        for log_file in files_to_clean:
            try:
                file_size = log_file.stat().st_size
                log_file.unlink()
                cleaned_count += 1
                total_size += file_size
                print(f"   ✅ 已删除: {log_file.name} ({self._format_size(file_size)})")
            except Exception as e:
                print(f"   ❌ 删除失败: {log_file.name} - {e}")

        print(f"✅ 日志清理完成: {cleaned_count} 个文件已删除 (共 {self._format_size(total_size)})")

    def cleanup_temp_files(self):
        """清理临时文件"""
        print("🧹 清理临时文件...")

        temp_patterns = [
            "**/*.pyc",
            "**/__pycache__",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.tmp",
            "**/*.temp",
            "**/*.log.bak",
        ]

        cleaned_count = 0
        total_size = 0

        for pattern in temp_patterns:
            for item in self.base_dir.rglob(pattern):
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        total_size += size
                    elif item.is_dir():
                        size = self._get_directory_size(item)
                        shutil.rmtree(item)
                        total_size += size

                    cleaned_count += 1
                    print(f"   ✅ 已删除: {item.relative_to(self.base_dir)}")
                except Exception as e:
                    print(f"   ❌ 删除失败: {item.relative_to(self.base_dir)} - {e}")

        if cleaned_count == 0:
            print("📋 没有找到临时文件")
        else:
            print(
                f"✅ 临时文件清理完成: {cleaned_count} 个项目已删除 (共 {self._format_size(total_size)})"
            )

    def list_test_data(self):
        """列出测试数据概况"""
        print("📊 测试数据概况:")
        print("=" * 60)

        # 测试仓库
        if self.test_repos_dir.exists():
            repos = [d for d in self.test_repos_dir.iterdir() if d.is_dir()]
            if repos:
                print(f"\\n📁 测试仓库 ({len(repos)} 个):")
                total_repo_size = 0
                for repo in sorted(repos):
                    repo_size = self._get_directory_size(repo)
                    total_repo_size += repo_size
                    print(f"   {repo.name:30} {self._format_size(repo_size):>10}")
                print(f"   {'总计':30} {self._format_size(total_repo_size):>10}")
            else:
                print("\\n📁 测试仓库: 无")

        # 日志文件
        if self.logs_dir.exists():
            logs = [f for f in self.logs_dir.iterdir() if f.is_file()]
            if logs:
                print(f"\\n📋 日志文件 ({len(logs)} 个):")
                total_log_size = 0
                for log in sorted(logs, key=lambda x: x.stat().st_mtime, reverse=True):
                    log_size = log.stat().st_size
                    total_log_size += log_size
                    mod_time = datetime.fromtimestamp(log.stat().st_mtime).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    print(
                        f"   {log.name:30} {self._format_size(log_size):>10} {mod_time}"
                    )
                print(f"   {'总计':30} {self._format_size(total_log_size):>10}")
            else:
                print("\\n📋 日志文件: 无")

        # 场景信息
        if self.scenarios_dir.exists():
            scenarios = [f for f in self.scenarios_dir.iterdir() if f.is_file()]
            if scenarios:
                print(f"\\n🎯 场景信息 ({len(scenarios)} 个):")
                for scenario in sorted(scenarios):
                    scenario_name = scenario.stem
                    try:
                        with open(scenario, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            scenario_type = data.get("type", "unknown")
                            print(f"   {scenario_name:30} {scenario_type}")
                    except:
                        print(f"   {scenario_name:30} (无法读取)")
            else:
                print("\\n🎯 场景信息: 无")

        print("=" * 60)

    def _get_directory_size(self, path):
        """获取目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except (OSError, PermissionError):
            pass
        return total_size

    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"

        size_units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(size_units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.1f} {size_units[unit_index]}"

    def vacuum_git_repos(self):
        """优化Git仓库，减少磁盘占用"""
        print("🔧 优化Git仓库...")

        if not self.test_repos_dir.exists():
            print("📋 没有找到测试仓库目录")
            return

        repos = [
            d
            for d in self.test_repos_dir.iterdir()
            if d.is_dir() and (d / ".git").exists()
        ]

        if not repos:
            print("📋 没有找到Git仓库")
            return

        optimized_count = 0
        total_saved = 0

        for repo in repos:
            try:
                # 获取优化前的大小
                before_size = self._get_directory_size(repo)

                # 执行Git优化命令
                import subprocess

                subprocess.run(
                    ["git", "gc", "--prune=now"], cwd=repo, capture_output=True
                )
                subprocess.run(["git", "repack", "-ad"], cwd=repo, capture_output=True)

                # 获取优化后的大小
                after_size = self._get_directory_size(repo)
                saved = before_size - after_size

                if saved > 0:
                    total_saved += saved
                    print(f"   ✅ {repo.name}: 节省 {self._format_size(saved)}")
                else:
                    print(f"   📋 {repo.name}: 已优化")

                optimized_count += 1

            except Exception as e:
                print(f"   ❌ 优化失败 {repo.name}: {e}")

        if optimized_count > 0:
            print(
                f"✅ Git仓库优化完成: {optimized_count} 个仓库，共节省 {self._format_size(total_saved)}"
            )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试环境清理工具")

    parser.add_argument("--all", action="store_true", help="清理所有测试数据")
    parser.add_argument("--repos", nargs="*", help="清理指定的测试仓库")
    parser.add_argument("--logs", action="store_true", help="清理日志文件")
    parser.add_argument("--temp", action="store_true", help="清理临时文件")
    parser.add_argument("--older-than", type=int, help="清理超过指定天数的文件")
    parser.add_argument("--list", "-l", action="store_true", help="列出测试数据概况")
    parser.add_argument("--vacuum", action="store_true", help="优化Git仓库")
    parser.add_argument("--force", "-f", action="store_true", help="强制执行，不询问确认")
    parser.add_argument(
        "--base-dir",
        default="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test",
        help="测试目录基础路径",
    )

    args = parser.parse_args()

    cleanup = TestCleanupTool(args.base_dir)
    confirm = not args.force

    if args.list:
        cleanup.list_test_data()
        return

    if args.all:
        cleanup.cleanup_all(confirm=confirm)
        return

    if args.repos is not None:
        if len(args.repos) == 0:
            # 清理所有仓库
            cleanup.cleanup_repos(confirm=confirm)
        else:
            # 清理指定仓库
            cleanup.cleanup_repos(args.repos, confirm=confirm)

    if args.logs:
        cleanup.cleanup_logs(older_than_days=args.older_than, confirm=confirm)

    if args.temp:
        cleanup.cleanup_temp_files()

    if args.vacuum:
        cleanup.vacuum_git_repos()

    # 如果没有指定任何操作，显示帮助
    if not any([args.all, args.repos is not None, args.logs, args.temp, args.vacuum]):
        print("请指定要执行的清理操作，使用 --help 查看帮助")
        cleanup.list_test_data()


if __name__ == "__main__":
    main()
