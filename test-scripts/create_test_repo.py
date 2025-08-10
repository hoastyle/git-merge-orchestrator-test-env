#!/usr/bin/env python3
"""
Git Merge Orchestrator - 测试仓库创建工具
自动创建各种类型的测试Git仓库，支持不同的复杂度和场景
"""

import os
import sys
import argparse
import subprocess
import random
import json
from pathlib import Path
from datetime import datetime, timedelta


class TestRepoCreator:
    """测试仓库创建工具"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.test_repos_dir = self.base_dir / "test-repos"
        self.test_data_dir = self.base_dir / "test-data"

        # 确保目录存在
        self.test_repos_dir.mkdir(exist_ok=True)
        self.test_data_dir.mkdir(exist_ok=True)

    def create_repo(self, repo_name, repo_type="simple", **kwargs):
        """创建测试仓库"""
        repo_path = self.test_repos_dir / repo_name

        if repo_path.exists():
            print(f"⚠️ 仓库 {repo_name} 已存在，是否覆盖？(y/N): ", end="")
            if input().lower() != "y":
                print("❌ 取消创建")
                return None

            # 删除现有仓库
            import shutil

            shutil.rmtree(repo_path)

        print(f"🚀 创建 {repo_type} 类型的测试仓库: {repo_name}")

        # 创建基础仓库结构
        repo_path.mkdir(parents=True)

        # 初始化Git仓库
        self._run_git_command("git init", repo_path)
        self._setup_git_config(repo_path)

        # 根据类型创建不同的仓库结构
        if repo_type == "simple":
            self._create_simple_repo(repo_path, **kwargs)
        elif repo_type == "complex":
            self._create_complex_repo(repo_path, **kwargs)
        elif repo_type == "multi-branch":
            self._create_multi_branch_repo(repo_path, **kwargs)
        elif repo_type == "large-scale":
            self._create_large_scale_repo(repo_path, **kwargs)
        else:
            raise ValueError(f"不支持的仓库类型: {repo_type}")

        print(f"✅ 测试仓库创建完成: {repo_path}")
        return repo_path

    def _setup_git_config(self, repo_path):
        """设置Git配置"""
        self._run_git_command('git config user.name "Test User"', repo_path)
        self._run_git_command('git config user.email "test@example.com"', repo_path)

    def _run_git_command(self, cmd, repo_path):
        """执行Git命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git命令失败: {cmd}")
            print(f"错误: {e.stderr}")
            return None

    def _create_file(self, repo_path, file_path, content):
        """创建文件"""
        full_path = repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _commit_changes(self, repo_path, message, author=None):
        """提交更改"""
        self._run_git_command("git add .", repo_path)

        if author:
            # 临时更改作者
            self._run_git_command(f'git config user.name "{author}"', repo_path)
            self._run_git_command(
                f'git config user.email "{author.lower().replace(" ", ".")}@example.com"',
                repo_path,
            )

        self._run_git_command(f'git commit -m "{message}"', repo_path)

        if author:
            # 恢复默认配置
            self._setup_git_config(repo_path)

    def _create_simple_repo(self, repo_path, **kwargs):
        """创建简单测试仓库"""
        contributors = kwargs.get("contributors", ["Alice", "Bob"])

        # 主分支初始提交
        self._create_file(
            repo_path, "README.md", "# Simple Test Repository\\n\\n这是一个简单的测试仓库。"
        )
        self._create_file(
            repo_path,
            "main.py",
            """#!/usr/bin/env python3
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""",
        )
        self._create_file(
            repo_path, "config.json", '{"version": "1.0", "debug": false}'
        )

        self._commit_changes(repo_path, "Initial commit", contributors[0])

        # 创建feature分支
        self._run_git_command("git checkout -b feature", repo_path)

        # 在feature分支添加功能
        self._create_file(
            repo_path,
            "utils.py",
            """def helper_function():
    return "This is a helper function"

def another_helper():
    return "Another helper"
""",
        )

        self._create_file(
            repo_path,
            "main.py",
            """#!/usr/bin/env python3
from utils import helper_function

def main():
    print("Hello, World!")
    print(helper_function())

if __name__ == "__main__":
    main()
""",
        )

        self._commit_changes(
            repo_path,
            "Add utility functions",
            contributors[1] if len(contributors) > 1 else contributors[0],
        )

        # 添加更多提交
        self._create_file(
            repo_path,
            "tests.py",
            """import unittest
from main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # 简单测试
        pass

if __name__ == '__main__':
    unittest.main()
""",
        )

        self._commit_changes(
            repo_path,
            "Add basic tests",
            contributors[1] if len(contributors) > 1 else contributors[0],
        )

        # 回到主分支 (使用master，Git默认分支名)
        self._run_git_command("git checkout master", repo_path)

    def _create_complex_repo(self, repo_path, **kwargs):
        """创建复杂测试仓库"""
        contributors = kwargs.get("contributors", ["Alice", "Bob", "Charlie", "David"])
        files_count = kwargs.get("files", 50)
        branches = kwargs.get(
            "branches", ["develop", "feature-1", "feature-2", "hotfix-1"]
        )

        # 创建目录结构
        directories = [
            "src/core",
            "src/utils",
            "src/ui",
            "src/api",
            "tests/unit",
            "tests/integration",
            "docs",
            "config",
            "scripts",
            "data",
        ]

        for directory in directories:
            (repo_path / directory).mkdir(parents=True, exist_ok=True)

        # 主分支初始结构
        self._create_file(
            repo_path,
            "README.md",
            """# Complex Test Repository

这是一个复杂的测试仓库，模拟真实项目结构。

## 项目结构

- `src/` - 源代码
- `tests/` - 测试文件
- `docs/` - 文档
- `config/` - 配置文件
- `scripts/` - 脚本文件
- `data/` - 数据文件
""",
        )

        # 创建核心文件
        core_files = [
            ("src/core/__init__.py", "# Core module"),
            (
                "src/core/main.py",
                "class MainApplication:\\n    def __init__(self):\\n        self.version = '1.0'",
            ),
            (
                "src/core/database.py",
                "class Database:\\n    def connect(self):\\n        pass",
            ),
            ("src/utils/__init__.py", "# Utilities"),
            ("src/utils/helpers.py", "def format_data(data):\\n    return str(data)"),
            (
                "src/utils/validators.py",
                "def validate_email(email):\\n    return '@' in email",
            ),
            ("src/ui/__init__.py", "# UI module"),
            (
                "src/ui/components.py",
                "class Button:\\n    def __init__(self, text):\\n        self.text = text",
            ),
            ("src/api/__init__.py", "# API module"),
            ("src/api/routes.py", "def get_users():\\n    return []"),
        ]

        for file_path, content in core_files:
            self._create_file(repo_path, file_path, content)

        self._commit_changes(repo_path, "Initial project structure", contributors[0])

        # 创建多个分支和提交
        for i, branch in enumerate(branches):
            self._run_git_command(f"git checkout -b {branch}", repo_path)

            # 在每个分支添加特定功能
            if branch.startswith("feature-"):
                self._add_feature_changes(
                    repo_path, branch, contributors[i % len(contributors)]
                )
            elif branch.startswith("hotfix-"):
                self._add_hotfix_changes(
                    repo_path, branch, contributors[i % len(contributors)]
                )
            elif branch == "develop":
                self._add_development_changes(
                    repo_path, contributors[i % len(contributors)]
                )

            # 回到主分支
            self._run_git_command("git checkout master", repo_path)

        # 添加更多文件以达到指定数量
        self._add_additional_files(repo_path, files_count - 20, contributors)

    def _add_feature_changes(self, repo_path, branch, author):
        """添加功能分支更改"""
        feature_num = branch.split("-")[-1]

        # 添加新功能文件
        self._create_file(
            repo_path,
            f"src/features/feature_{feature_num}.py",
            f"""class Feature{feature_num}:
    def __init__(self):
        self.name = "Feature {feature_num}"
        self.enabled = True
    
    def execute(self):
        return f"Executing {{self.name}}"
""",
        )

        # 更新主文件
        main_content = f"""# Updated for {branch}
from features.feature_{feature_num} import Feature{feature_num}

class MainApplication:
    def __init__(self):
        self.version = '1.{feature_num}'
        self.feature_{feature_num} = Feature{feature_num}()
"""
        self._create_file(repo_path, "src/core/main.py", main_content)

        self._commit_changes(repo_path, f"Add {branch} functionality", author)

        # 添加测试
        self._create_file(
            repo_path,
            f"tests/unit/test_feature_{feature_num}.py",
            f"""import unittest
from src.features.feature_{feature_num} import Feature{feature_num}

class TestFeature{feature_num}(unittest.TestCase):
    def test_execute(self):
        feature = Feature{feature_num}()
        result = feature.execute()
        self.assertIn("Feature {feature_num}", result)
""",
        )

        self._commit_changes(repo_path, f"Add tests for {branch}", author)

    def _add_hotfix_changes(self, repo_path, branch, author):
        """添加热修复分支更改"""
        # 修复一些"bug"
        self._create_file(
            repo_path,
            "src/utils/validators.py",
            """def validate_email(email):
    # Hotfix: Better email validation
    return '@' in email and '.' in email and len(email) > 5
""",
        )

        self._commit_changes(repo_path, f"Hotfix: Improve email validation", author)

    def _add_development_changes(self, repo_path, author):
        """添加开发分支更改"""
        # 添加开发工具
        self._create_file(
            repo_path,
            "scripts/dev_setup.py",
            """#!/usr/bin/env python3
import os

def setup_dev_environment():
    print("Setting up development environment...")
    # 模拟开发环境设置
    pass

if __name__ == "__main__":
    setup_dev_environment()
""",
        )

        self._create_file(
            repo_path,
            "config/development.json",
            """{
    "debug": true,
    "log_level": "DEBUG",
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "test_db"
    }
}""",
        )

        self._commit_changes(repo_path, "Add development configuration", author)

    def _add_additional_files(self, repo_path, count, contributors):
        """添加额外文件以达到指定数量"""
        file_types = [
            ("py", "# Python file\\nprint('Hello World')"),
            ("js", "// JavaScript file\\nconsole.log('Hello World');"),
            ("css", "/* CSS file */\\nbody { margin: 0; }"),
            ("html", "<!-- HTML file -->\\n<html><body><h1>Test</h1></body></html>"),
            ("json", '{"test": "data"}'),
            ("md", "# Test Document\\n\\nThis is a test."),
        ]

        for i in range(count):
            file_type, content = random.choice(file_types)
            file_name = f"generated_file_{i:03d}.{file_type}"
            directory = random.choice(["src/generated", "data", "docs/generated"])

            self._create_file(repo_path, f"{directory}/{file_name}", content)

            if (i + 1) % 10 == 0:  # 每10个文件提交一次
                author = random.choice(contributors)
                self._commit_changes(
                    repo_path, f"Add generated files batch {(i//10)+1}", author
                )

    def _create_multi_branch_repo(self, repo_path, **kwargs):
        """创建多分支测试仓库"""
        # 基于复杂仓库，但创建更多分支
        self._create_complex_repo(repo_path, **kwargs)

        # 添加更多分支
        additional_branches = [
            "feature/user-auth",
            "feature/api-v2",
            "feature/frontend-redesign",
            "bugfix/login-issue",
            "bugfix/performance",
            "refactor/database",
            "experimental/new-algo",
            "release/v2.0",
        ]

        contributors = kwargs.get(
            "contributors", ["Alice", "Bob", "Charlie", "David", "Eve"]
        )

        for branch in additional_branches:
            self._run_git_command(f"git checkout -b {branch}", repo_path)

            # 添加分支特定的更改
            branch_type = branch.split("/")[0]
            if branch_type == "feature":
                self._add_random_feature(repo_path, branch, random.choice(contributors))
            elif branch_type == "bugfix":
                self._add_random_bugfix(repo_path, branch, random.choice(contributors))

            self._run_git_command("git checkout master", repo_path)

    def _add_random_feature(self, repo_path, branch, author):
        """添加随机功能"""
        feature_name = branch.split("/")[-1].replace("-", "_")

        self._create_file(
            repo_path,
            f"src/features/{feature_name}.py",
            f"""class {feature_name.title()}:
    def __init__(self):
        self.name = "{feature_name}"
    
    def run(self):
        return f"Running {{self.name}}"
""",
        )

        self._commit_changes(repo_path, f"Implement {feature_name} feature", author)

    def _add_random_bugfix(self, repo_path, branch, author):
        """添加随机bug修复"""
        fix_description = branch.split("/")[-1].replace("-", " ")

        # 随机选择一个文件进行"修复"
        files_to_fix = ["src/core/main.py", "src/utils/helpers.py", "src/api/routes.py"]
        file_to_fix = random.choice(files_to_fix)

        # 读取现有内容并添加注释
        try:
            with open(repo_path / file_to_fix, "r") as f:
                content = f.read()
        except:
            content = "# Fixed file"

        fixed_content = f"# Fixed: {fix_description}\\n{content}"
        self._create_file(repo_path, file_to_fix, fixed_content)

        self._commit_changes(repo_path, f"Fix {fix_description}", author)

    def _create_large_scale_repo(self, repo_path, **kwargs):
        """创建大规模测试仓库"""
        files_count = kwargs.get("files", 200)
        contributors = kwargs.get(
            "contributors", ["Dev1", "Dev2", "Dev3", "Dev4", "Dev5", "Dev6"]
        )

        # 基于复杂仓库
        # 移除contributors和files避免重复传递
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["contributors", "files"]
        }
        self._create_complex_repo(
            repo_path, files=files_count, contributors=contributors, **filtered_kwargs
        )

        # 添加大量历史提交
        self._add_commit_history(repo_path, contributors, 50)

    def _add_commit_history(self, repo_path, contributors, commit_count):
        """添加大量历史提交"""
        import time

        for i in range(commit_count):
            # 随机修改文件
            file_num = random.randint(1, 20)
            file_path = f"src/history/history_file_{file_num:03d}.py"

            content = f"""# History file {file_num}
# Modified at commit {i+1}
import datetime

def get_timestamp():
    return datetime.datetime.now()

def process_data_{i}():
    return "Processing data at commit {i+1}"
"""

            self._create_file(repo_path, file_path, content)
            author = random.choice(contributors)
            self._commit_changes(
                repo_path, f"Update history file {file_num} (commit {i+1})", author
            )

            # 模拟时间间隔
            if i % 10 == 0:
                time.sleep(0.1)  # 短暂延迟


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试仓库创建工具")

    parser.add_argument("--name", "-n", required=True, help="仓库名称")
    parser.add_argument(
        "--type",
        "-t",
        choices=["simple", "complex", "multi-branch", "large-scale"],
        default="simple",
        help="仓库类型",
    )
    parser.add_argument("--contributors", "-c", help="贡献者列表，逗号分隔，如：Alice,Bob,Charlie")
    parser.add_argument(
        "--files", "-f", type=int, help="文件数量（对complex和large-scale类型有效）"
    )
    parser.add_argument(
        "--branches", "-b", help="分支列表，逗号分隔，如：develop,feature-1,feature-2"
    )
    parser.add_argument("--base-dir", default=".", help="测试目录基础路径")

    args = parser.parse_args()

    # 解析参数
    kwargs = {}
    if args.contributors:
        kwargs["contributors"] = [c.strip() for c in args.contributors.split(",")]
    if args.files:
        kwargs["files"] = args.files
    if args.branches:
        kwargs["branches"] = [b.strip() for b in args.branches.split(",")]

    # 创建测试仓库
    try:
        creator = TestRepoCreator(args.base_dir)
        repo_path = creator.create_repo(args.name, args.type, **kwargs)

        if repo_path:
            print(f"\\n📋 测试仓库信息:")
            print(f"   路径: {repo_path}")
            print(f"   类型: {args.type}")
            print(f"   分支数: ", end="")

            # 获取分支信息
            result = subprocess.run(
                "git branch -a",
                shell=True,
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                branches = [
                    b.strip().replace("* ", "")
                    for b in result.stdout.split("\\n")
                    if b.strip()
                ]
                print(len(branches))
                print(f"   分支列表: {', '.join(branches)}")
            else:
                print("未知")

            print(f"\\n🚀 使用方法:")
            print(f"   cd {repo_path}")
            print(f"   python ../../../main.py feature master")

    except Exception as e:
        print(f"❌ 创建失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
