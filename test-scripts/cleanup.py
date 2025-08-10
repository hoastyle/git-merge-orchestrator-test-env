#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Merge Orchestrator - 测试环境清理工具
清理测试仓库、日志文件和临时数据
"""

import os
import sys
import argparse
import shutil
import time
from datetime import datetime, timedelta


class TestCleanup:
    """测试环境清理工具"""

    def __init__(self, base_dir="."):
        self.base_dir = os.path.abspath(base_dir)
        self.test_repos_dir = os.path.join(self.base_dir, "test-repos")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.scenarios_dir = os.path.join(self.base_dir, "scenarios")

    def clean_all(self, force=False):
        """清理所有测试数据"""
        print("🧹 清理所有测试数据...")

        cleaned_items = []

        # 清理测试仓库
        if os.path.exists(self.test_repos_dir):
            repo_count = len(
                [
                    d
                    for d in os.listdir(self.test_repos_dir)
                    if os.path.isdir(os.path.join(self.test_repos_dir, d))
                ]
            )
            shutil.rmtree(self.test_repos_dir)
            os.makedirs(self.test_repos_dir)
            cleaned_items.append("测试仓库: {} 个".format(repo_count))

        # 清理日志
        if os.path.exists(self.logs_dir):
            log_count = len(
                [
                    f
                    for f in os.listdir(self.logs_dir)
                    if os.path.isfile(os.path.join(self.logs_dir, f))
                ]
            )
            shutil.rmtree(self.logs_dir)
            os.makedirs(self.logs_dir)
            cleaned_items.append("日志文件: {} 个".format(log_count))

        # 清理场景信息
        if os.path.exists(self.scenarios_dir):
            scenario_count = len(
                [
                    f
                    for f in os.listdir(self.scenarios_dir)
                    if os.path.isfile(os.path.join(self.scenarios_dir, f))
                ]
            )
            cleaned_items.append("场景文件: {} 个".format(scenario_count))

        if cleaned_items:
            print("✅ 清理完成:")
            for item in cleaned_items:
                print("   - {}".format(item))
        else:
            print("📋 没有需要清理的内容")

    def clean_repos(self, repo_names=None, force=False):
        """清理指定的测试仓库"""
        if not os.path.exists(self.test_repos_dir):
            print("📋 没有找到测试仓库目录")
            return

        all_repos = [
            d
            for d in os.listdir(self.test_repos_dir)
            if os.path.isdir(os.path.join(self.test_repos_dir, d))
        ]
        repos_to_clean = []

        if repo_names:
            # 清理指定仓库
            for repo_name in repo_names:
                repo_path = os.path.join(self.test_repos_dir, repo_name)
                if os.path.exists(repo_path):
                    repos_to_clean.append(repo_path)
                else:
                    print("⚠️ 仓库不存在: {}".format(repo_name))
        else:
            # 清理所有仓库
            repos_to_clean = [os.path.join(self.test_repos_dir, d) for d in all_repos]

        if not repos_to_clean:
            print("📋 没有需要清理的仓库")
            return

        if not force:
            print("⚠️ 将删除 {} 个测试仓库".format(len(repos_to_clean)))
            for repo in repos_to_clean:
                print("   - {}".format(os.path.basename(repo)))

            try:
                response = input("确认继续? (y/N): ").lower()
                if response != "y":
                    print("❌ 已取消")
                    return
            except:
                print("❌ 已取消")
                return

        print("🧹 清理 {} 个测试仓库...".format(len(repos_to_clean)))
        cleaned_count = 0

        for repo_path in repos_to_clean:
            try:
                shutil.rmtree(repo_path)
                print("   ✅ 已删除: {}".format(os.path.basename(repo_path)))
                cleaned_count += 1
            except Exception as e:
                print("   ❌ 删除失败: {} - {}".format(os.path.basename(repo_path), e))

        print("✅ 仓库清理完成: {} 个仓库已删除".format(cleaned_count))

    def clean_logs(self, older_than_days=7, force=False):
        """清理日志文件"""
        if not os.path.exists(self.logs_dir):
            print("📋 没有找到日志目录")
            return

        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        all_logs = [
            f
            for f in os.listdir(self.logs_dir)
            if os.path.isfile(os.path.join(self.logs_dir, f))
        ]
        files_to_clean = []

        for log_file in all_logs:
            log_path = os.path.join(self.logs_dir, log_file)
            try:
                mtime = os.path.getmtime(log_path)
                if mtime < cutoff_time:
                    files_to_clean.append(log_path)
            except:
                continue

        if not files_to_clean:
            print("📋 没有需要清理的日志文件")
            return

        if not force:
            print("🧹 清理超过 {} 天的日志文件...".format(older_than_days))
            print("⚠️ 将删除 {} 个日志文件".format(len(files_to_clean)))
            for log_file in files_to_clean:
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                print(
                    "   - {} ({})".format(
                        os.path.basename(log_file), mtime.strftime("%Y-%m-%d %H:%M")
                    )
                )

            try:
                response = input("确认继续? (y/N): ").lower()
                if response != "y":
                    print("❌ 已取消")
                    return
            except:
                print("❌ 已取消")
                return

        cleaned_count = 0

        for log_file in files_to_clean:
            try:
                os.remove(log_file)
                print("   ✅ 已删除: {}".format(os.path.basename(log_file)))
                cleaned_count += 1
            except Exception as e:
                print("   ❌ 删除失败: {} - {}".format(os.path.basename(log_file), e))

        print("✅ 日志清理完成: {} 个文件已删除".format(cleaned_count))

    def clean_temp(self, force=False):
        """清理临时文件"""
        print("🧹 清理临时文件...")

        cleaned_count = 0
        temp_patterns = ["*.pyc", "*.pyo", "*.tmp", ".DS_Store", "Thumbs.db"]

        # 清理临时文件
        for root, dirs, files in os.walk(self.base_dir):
            # 跳过.git目录
            if ".git" in root:
                continue

            # 清理__pycache__目录
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                try:
                    shutil.rmtree(pycache_path)
                    print(
                        "   ✅ 已删除: {}".format(pycache_path.replace(self.base_dir, "."))
                    )
                    cleaned_count += 1
                    dirs.remove("__pycache__")  # 不再遍历已删除的目录
                except Exception as e:
                    print("   ❌ 删除失败: {} - {}".format(pycache_path, e))

            # 清理匹配模式的文件
            for file in files:
                file_path = os.path.join(root, file)
                for pattern in temp_patterns:
                    if file.endswith(pattern.replace("*", "")):
                        try:
                            os.remove(file_path)
                            print(
                                "   ✅ 已删除: {}".format(
                                    file_path.replace(self.base_dir, ".")
                                )
                            )
                            cleaned_count += 1
                        except Exception as e:
                            print("   ❌ 删除失败: {} - {}".format(file_path, e))
                        break

        print("✅ 临时文件清理完成: {} 个项目已删除".format(cleaned_count))

    def show_status(self):
        """显示测试环境状态"""
        print("📊 测试环境状态概览")
        print("=" * 50)

        # 测试仓库信息
        if os.path.exists(self.test_repos_dir):
            repos = [
                d
                for d in os.listdir(self.test_repos_dir)
                if os.path.isdir(os.path.join(self.test_repos_dir, d))
            ]
            if repos:
                print("\\n📁 测试仓库 ({} 个):".format(len(repos)))
                for repo in repos[:10]:  # 只显示前10个
                    print("   - {}".format(repo))
                if len(repos) > 10:
                    print("   ... 还有 {} 个仓库".format(len(repos) - 10))

        # 日志文件信息
        if os.path.exists(self.logs_dir):
            logs = [
                f
                for f in os.listdir(self.logs_dir)
                if os.path.isfile(os.path.join(self.logs_dir, f))
            ]
            if logs:
                print("\\n📋 日志文件 ({} 个):".format(len(logs)))
                for log in logs[:10]:  # 只显示前10个
                    print("   - {}".format(log))
                if len(logs) > 10:
                    print("   ... 还有 {} 个日志文件".format(len(logs) - 10))

        # 场景信息
        if os.path.exists(self.scenarios_dir):
            scenarios = [
                f
                for f in os.listdir(self.scenarios_dir)
                if os.path.isfile(os.path.join(self.scenarios_dir, f))
            ]
            if scenarios:
                print("\\n🎯 场景信息 ({} 个):".format(len(scenarios)))
                for scenario in scenarios:
                    print("   - {}".format(scenario))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试环境清理工具")

    parser.add_argument("--all", action="store_true", help="清理所有测试数据")
    parser.add_argument("--repos", nargs="*", help="清理指定的测试仓库")
    parser.add_argument("--logs", action="store_true", help="清理日志文件")
    parser.add_argument("--temp", action="store_true", help="清理临时文件")
    parser.add_argument("--older-than", type=int, default=7, help="清理超过指定天数的文件")
    parser.add_argument("--list", "-l", action="store_true", help="列出测试数据概况")
    parser.add_argument("--force", "-f", action="store_true", help="强制执行，不询问确认")
    parser.add_argument("--base-dir", default=".", help="测试目录基础路径")

    args = parser.parse_args()

    # 创建清理器
    cleaner = TestCleanup(args.base_dir)

    try:
        if args.list:
            cleaner.show_status()
        elif args.all:
            cleaner.clean_all(force=args.force)
        elif args.repos is not None:
            cleaner.clean_repos(args.repos, force=args.force)
        elif args.logs:
            cleaner.clean_logs(older_than_days=args.older_than, force=args.force)
        elif args.temp:
            cleaner.clean_temp(force=args.force)
        else:
            # 默认显示状态
            cleaner.show_status()

    except KeyboardInterrupt:
        print("\\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print("❌ 清理过程中发生错误: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
