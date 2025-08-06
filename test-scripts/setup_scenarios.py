#!/usr/bin/env python3
"""
Git Merge Orchestrator - 测试场景设置脚本
提供预定义的测试场景，快速设置各种测试环境
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from create_test_repo import TestRepoCreator


class ScenarioSetup:
    """测试场景设置工具"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.creator = TestRepoCreator(base_dir)
        self.scenarios_dir = self.base_dir / "scenarios"
        self.scenarios_dir.mkdir(exist_ok=True)

    def setup_scenario(self, scenario_name):
        """设置指定的测试场景"""
        scenarios = {
            "merge-conflicts": self._setup_merge_conflicts_scenario,
            "file-level-processing": self._setup_file_level_scenario,
            "load-balancing": self._setup_load_balancing_scenario,
            "large-scale-performance": self._setup_performance_scenario,
            "multi-contributor": self._setup_multi_contributor_scenario,
            "complex-directory-structure": self._setup_complex_directory_scenario,
            "branch-management": self._setup_branch_management_scenario,
            "ignore-rules": self._setup_ignore_rules_scenario,
        }

        if scenario_name == "all":
            print("🚀 设置所有测试场景...")
            for name, setup_func in scenarios.items():
                print(f"\\n📋 设置场景: {name}")
                try:
                    setup_func()
                    print(f"✅ 场景 {name} 设置完成")
                except Exception as e:
                    print(f"❌ 场景 {name} 设置失败: {e}")
            return

        if scenario_name not in scenarios:
            print(f"❌ 未知场景: {scenario_name}")
            print(f"可用场景: {', '.join(scenarios.keys())}, all")
            return

        print(f"🚀 设置测试场景: {scenario_name}")
        try:
            scenarios[scenario_name]()
            print(f"✅ 场景 {scenario_name} 设置完成")
        except Exception as e:
            print(f"❌ 场景设置失败: {e}")

    def _setup_merge_conflicts_scenario(self):
        """设置合并冲突测试场景"""
        repo_name = "merge-conflicts-test"
        repo_path = self.creator.create_repo(
            repo_name, "complex",
            contributors=["Alice", "Bob", "Charlie"],
            branches=["feature-1", "feature-2"]
        )

        if not repo_path:
            return

        # 创建冲突的更改
        self._run_git_command("git checkout feature-1", repo_path)
        
        # 在feature-1中修改文件
        conflict_content_1 = """# Main Application
class Application:
    def __init__(self):
        self.version = "2.0-feature1"
        self.feature_1_enabled = True
        
    def start(self):
        print("Starting application v2.0 with feature 1")
        return "feature-1-version"
"""
        self._create_file(repo_path, "src/core/main.py", conflict_content_1)
        self._commit_changes(repo_path, "Add feature-1 changes", "Alice")

        # 切换到feature-2并创建冲突
        self._run_git_command("git checkout feature-2", repo_path)
        
        conflict_content_2 = """# Main Application
class Application:
    def __init__(self):
        self.version = "2.0-feature2"
        self.feature_2_enabled = True
        
    def start(self):
        print("Starting application v2.0 with feature 2")
        return "feature-2-version"
"""
        self._create_file(repo_path, "src/core/main.py", conflict_content_2)
        self._commit_changes(repo_path, "Add feature-2 changes", "Bob")

        # 回到master分支
        self._run_git_command("git checkout master", repo_path)

        # 保存场景信息
        self._save_scenario_info(repo_name, {
            "type": "merge-conflicts",
            "description": "测试合并冲突处理",
            "conflicts": ["src/core/main.py"],
            "branches": ["feature-1", "feature-2"],
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py feature-1 master"
        })

    def _setup_file_level_scenario(self):
        """设置文件级处理测试场景"""
        repo_name = "file-level-test"
        repo_path = self.creator.create_repo(
            repo_name, "complex",
            contributors=["Dev1", "Dev2", "Dev3", "Dev4"],
            files=30
        )

        if not repo_path:
            return

        # 创建更多分散的文件变更
        self._run_git_command("git checkout -b file-level-feature", repo_path)

        # 创建各种类型的文件变更
        file_changes = [
            ("src/models/user.py", "class User:\\n    def __init__(self, name):\\n        self.name = name", "Dev1"),
            ("src/models/product.py", "class Product:\\n    def __init__(self, id):\\n        self.id = id", "Dev2"),
            ("src/services/auth.py", "def authenticate(user):\\n    return True", "Dev3"),
            ("src/services/payment.py", "def process_payment(amount):\\n    return 'success'", "Dev4"),
            ("src/utils/encryption.py", "def encrypt(data):\\n    return 'encrypted'", "Dev1"),
            ("config/database.json", '{"host": "localhost", "port": 5432}', "Dev2"),
            ("docs/api.md", "# API Documentation\\n\\n## Endpoints", "Dev3"),
        ]

        for file_path, content, author in file_changes:
            self._create_file(repo_path, file_path, content)
            self._commit_changes(repo_path, f"Update {file_path}", author)

        self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "file-level-processing",
            "description": "测试文件级处理和分配",
            "files_count": len(file_changes),
            "contributors": 4,
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py --processing-mode file_level file-level-feature master"
        })

    def _setup_load_balancing_scenario(self):
        """设置负载均衡测试场景"""
        repo_name = "load-balancing-test"
        repo_path = self.creator.create_repo(
            repo_name, "large-scale",
            contributors=["TeamLead", "Senior1", "Senior2", "Junior1", "Junior2", "Intern1"],
            files=100
        )

        if not repo_path:
            return

        # 创建不均衡的贡献历史
        self._run_git_command("git checkout -b load-test-feature", repo_path)

        # 模拟某些开发者贡献更多
        heavy_contributors = ["TeamLead", "Senior1"]
        light_contributors = ["Junior1", "Junior2", "Intern1"]

        # 重点贡献者提交更多
        for i in range(20):
            file_path = f"src/heavy_work/file_{i:03d}.py"
            content = f"# Heavy work file {i}\\ndef process_{i}():\\n    return {i}"
            self._create_file(repo_path, file_path, content)
            author = heavy_contributors[i % len(heavy_contributors)]
            self._commit_changes(repo_path, f"Heavy work: file {i}", author)

        # 轻度贡献者少量提交
        for i in range(5):
            file_path = f"src/light_work/file_{i:03d}.py"
            content = f"# Light work file {i}\\ndef simple_{i}():\\n    return {i}"
            self._create_file(repo_path, file_path, content)
            author = light_contributors[i % len(light_contributors)]
            self._commit_changes(repo_path, f"Light work: file {i}", author)

        self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "load-balancing",
            "description": "测试负载均衡分配算法",
            "heavy_contributors": heavy_contributors,
            "light_contributors": light_contributors,
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py load-test-feature master"
        })

    def _setup_performance_scenario(self):
        """设置性能测试场景"""
        repo_name = "performance-test"
        repo_path = self.creator.create_repo(
            repo_name, "large-scale",
            contributors=["Perf1", "Perf2", "Perf3", "Perf4", "Perf5"],
            files=500
        )

        if not repo_path:
            return

        self._save_scenario_info(repo_name, {
            "type": "performance",
            "description": "大规模性能压力测试",
            "files_count": 500,
            "contributors": 5,
            "usage": f"cd {repo_path} && time python ../../git-merge-orchestrator/main.py feature master"
        })

    def _setup_multi_contributor_scenario(self):
        """设置多贡献者测试场景"""
        repo_name = "multi-contributor-test"
        contributors = [
            "Frontend-Dev", "Backend-Dev", "DevOps-Engineer", 
            "QA-Tester", "Product-Manager", "UI-Designer",
            "Data-Scientist", "Security-Expert"
        ]
        
        repo_path = self.creator.create_repo(
            repo_name, "complex",
            contributors=contributors,
            files=80
        )

        if not repo_path:
            return

        # 创建不同专业领域的文件
        self._run_git_command("git checkout -b multi-team-feature", repo_path)

        specialization_files = [
            ("frontend/components/", "Frontend-Dev", ["button.js", "modal.js", "form.js"]),
            ("backend/api/", "Backend-Dev", ["users.py", "products.py", "orders.py"]),
            ("infrastructure/", "DevOps-Engineer", ["docker-compose.yml", "kubernetes.yaml"]),
            ("tests/", "QA-Tester", ["integration_tests.py", "e2e_tests.py"]),
            ("docs/requirements/", "Product-Manager", ["features.md", "roadmap.md"]),
            ("design/", "UI-Designer", ["mockups.md", "style-guide.css"]),
            ("analytics/", "Data-Scientist", ["metrics.py", "reports.py"]),
            ("security/", "Security-Expert", ["audit.py", "permissions.py"]),
        ]

        for directory, specialist, files in specialization_files:
            for filename in files:
                file_path = f"{directory}{filename}"
                content = f"# {specialist} work\\n# {filename} implementation"
                self._create_file(repo_path, file_path, content)
            
            self._commit_changes(repo_path, f"Add {specialist} components", specialist)

        self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "multi-contributor",
            "description": "多专业团队协作测试",
            "contributors": contributors,
            "specializations": len(specialization_files),
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py multi-team-feature master"
        })

    def _setup_complex_directory_scenario(self):
        """设置复杂目录结构测试场景"""
        repo_name = "complex-directory-test"
        repo_path = self.creator.create_repo(
            repo_name, "complex",
            contributors=["Architect", "Developer1", "Developer2"],
            files=60
        )

        if not repo_path:
            return

        # 创建深层嵌套的目录结构
        self._run_git_command("git checkout -b complex-structure", repo_path)

        deep_structure = [
            "src/main/java/com/company/project/core/",
            "src/main/java/com/company/project/services/impl/",
            "src/main/java/com/company/project/controllers/api/v1/",
            "src/main/resources/config/environments/production/",
            "src/test/java/com/company/project/integration/",
            "docs/architecture/diagrams/sequence/",
            "docs/api/v1/endpoints/",
            "scripts/deployment/environments/staging/",
        ]

        for directory in deep_structure:
            # 在每个深层目录创建文件
            for i in range(3):
                file_path = f"{directory}file_{i}.txt"
                content = f"Deep directory file {i} in {directory}"
                self._create_file(repo_path, file_path, content)
            
            author = ["Architect", "Developer1", "Developer2"][hash(directory) % 3]
            self._commit_changes(repo_path, f"Add files to {directory}", author)

        self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "complex-directory",
            "description": "复杂深层目录结构测试",
            "max_depth": 8,
            "directories": len(deep_structure),
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py complex-structure master"
        })

    def _setup_branch_management_scenario(self):
        """设置分支管理测试场景"""
        repo_name = "branch-management-test"
        repo_path = self.creator.create_repo(
            repo_name, "multi-branch",
            contributors=["Release-Manager", "Feature-Dev1", "Feature-Dev2", "Hotfix-Dev"],
            branches=["develop", "release/v1.0", "hotfix/urgent-fix"]
        )

        if not repo_path:
            return

        # 创建更复杂的分支结构
        complex_branches = [
            ("feature/user-management", "Feature-Dev1"),
            ("feature/payment-integration", "Feature-Dev2"),
            ("bugfix/login-issue", "Hotfix-Dev"),
            ("refactor/database-layer", "Feature-Dev1"),
            ("experimental/ml-integration", "Feature-Dev2"),
        ]

        for branch, developer in complex_branches:
            self._run_git_command(f"git checkout -b {branch}", repo_path)
            
            # 为每个分支添加特定更改
            branch_type = branch.split('/')[0]
            feature_name = branch.split('/')[-1].replace('-', '_')
            
            file_path = f"src/{branch_type}/{feature_name}.py"
            content = f"""# {branch} implementation
class {feature_name.title()}:
    def __init__(self):
        self.branch = "{branch}"
        self.developer = "{developer}"
    
    def execute(self):
        return f"Executing {self.branch} by {self.developer}"
"""
            self._create_file(repo_path, file_path, content)
            self._commit_changes(repo_path, f"Implement {feature_name}", developer)
            
            self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "branch-management",
            "description": "复杂分支管理测试",
            "branches": [b[0] for b in complex_branches],
            "developers": list(set(b[1] for b in complex_branches)),
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py develop master"
        })

    def _setup_ignore_rules_scenario(self):
        """设置忽略规则测试场景"""
        repo_name = "ignore-rules-test"
        repo_path = self.creator.create_repo(
            repo_name, "simple",
            contributors=["Developer", "Tester"]
        )

        if not repo_path:
            return

        # 创建应该被忽略的文件
        self._run_git_command("git checkout -b ignore-test", repo_path)

        # 创建各种类型的文件，包括应该被忽略的
        files_to_create = [
            ("src/important.py", "重要的源文件"),
            ("src/cache.pyc", "编译的Python文件"),
            ("logs/application.log", "日志文件"),
            ("temp/temp_data.tmp", "临时文件"),
            (".vscode/settings.json", "IDE设置"),
            ("node_modules/package/index.js", "依赖包文件"),
            ("build/output.exe", "构建文件"),
            ("docs/readme.md", "重要文档"),
            (".DS_Store", "系统文件"),
            ("__pycache__/module.cpython-39.pyc", "Python缓存"),
        ]

        for file_path, description in files_to_create:
            content = f"# {description}\\nThis is a {description.lower()}"
            self._create_file(repo_path, file_path, content)

        self._commit_changes(repo_path, "Add various file types including ignorable ones", "Developer")

        # 创建忽略规则文件
        ignore_rules = """# Git Merge Orchestrator 忽略规则测试
*.pyc
*.log
*.tmp
.vscode/
node_modules/
build/
.DS_Store
__pycache__/
"""
        self._create_file(repo_path, ".merge_ignore", ignore_rules)
        self._commit_changes(repo_path, "Add merge ignore rules", "Developer")

        self._run_git_command("git checkout master", repo_path)

        self._save_scenario_info(repo_name, {
            "type": "ignore-rules",
            "description": "忽略规则功能测试",
            "total_files": len(files_to_create),
            "ignore_patterns": ignore_rules.count('\\n') - 1,
            "usage": f"cd {repo_path} && python ../../git-merge-orchestrator/main.py ignore-test master"
        })

    def _run_git_command(self, cmd, repo_path):
        """执行Git命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=repo_path,
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git命令失败: {cmd} - {e.stderr}")
            return None

    def _create_file(self, repo_path, file_path, content):
        """创建文件"""
        full_path = repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _commit_changes(self, repo_path, message, author):
        """提交更改"""
        self._run_git_command("git add .", repo_path)
        
        if author:
            self._run_git_command(f'git config user.name "{author}"', repo_path)
            self._run_git_command(f'git config user.email "{author.lower().replace(" ", ".")}@example.com"', repo_path)
        
        self._run_git_command(f'git commit -m "{message}"', repo_path)

    def _save_scenario_info(self, scenario_name, info):
        """保存场景信息"""
        info_file = self.scenarios_dir / f"{scenario_name}.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    def list_scenarios(self):
        """列出可用的测试场景"""
        scenarios = {
            "merge-conflicts": "合并冲突处理测试",
            "file-level-processing": "文件级处理和分配测试", 
            "load-balancing": "负载均衡算法测试",
            "large-scale-performance": "大规模性能压力测试",
            "multi-contributor": "多专业团队协作测试",
            "complex-directory-structure": "复杂深层目录结构测试",
            "branch-management": "复杂分支管理测试",
            "ignore-rules": "忽略规则功能测试",
        }

        print("📋 可用的测试场景:")
        print("-" * 60)
        for name, description in scenarios.items():
            print(f"  {name:30} - {description}")
        print("-" * 60)
        print("  all                          - 设置所有场景")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试场景设置工具")
    
    parser.add_argument(
        "--scenario", "-s",
        help="要设置的场景名称，或使用'all'设置所有场景"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用的测试场景"
    )
    parser.add_argument(
        "--base-dir",
        default="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test",
        help="测试目录基础路径"
    )

    args = parser.parse_args()
    
    setup = ScenarioSetup(args.base_dir)
    
    if args.list:
        setup.list_scenarios()
        return
    
    if not args.scenario:
        print("请指定要设置的场景名称，使用 --list 查看可用场景")
        setup.list_scenarios()
        return

    setup.setup_scenario(args.scenario)


if __name__ == "__main__":
    main()