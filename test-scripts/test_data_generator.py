#!/usr/bin/env python3
"""
Git Merge Orchestrator - 测试数据生成工具
生成各种类型的测试数据文件和配置
"""

import os
import sys
import argparse
import json
import random
import string
from pathlib import Path
from datetime import datetime, timedelta


class TestDataGenerator:
    """测试数据生成工具"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.sample_files_dir = self.base_dir / "test-data" / "sample-files"
        self.configurations_dir = self.base_dir / "test-data" / "configurations"
        
        # 确保目录存在
        self.sample_files_dir.mkdir(parents=True, exist_ok=True)
        self.configurations_dir.mkdir(parents=True, exist_ok=True)

    def generate_sample_files(self, count=50, file_types=None):
        """生成示例文件"""
        if file_types is None:
            file_types = ["python", "javascript", "css", "html", "json", "markdown", "config"]

        print(f"🎲 生成 {count} 个示例文件...")
        
        generated_count = 0
        for i in range(count):
            file_type = random.choice(file_types)
            file_name, content = self._generate_file_content(file_type, i)
            
            # 创建子目录
            type_dir = self.sample_files_dir / file_type
            type_dir.mkdir(exist_ok=True)
            
            file_path = type_dir / file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            generated_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"   生成了 {i + 1} 个文件...")

        print(f"✅ 示例文件生成完成: {generated_count} 个文件")

    def generate_configurations(self):
        """生成测试配置文件"""
        print("⚙️ 生成测试配置文件...")
        
        configurations = [
            ("basic_config.json", self._generate_basic_config()),
            ("advanced_config.json", self._generate_advanced_config()),
            ("performance_config.json", self._generate_performance_config()),
            ("team_config.json", self._generate_team_config()),
            ("ignore_patterns.json", self._generate_ignore_patterns()),
            ("test_scenarios.json", self._generate_test_scenarios_config()),
        ]
        
        for config_name, config_data in configurations:
            config_path = self.configurations_dir / config_name
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"   ✅ 已生成: {config_name}")

        print(f"✅ 配置文件生成完成: {len(configurations)} 个配置")

    def generate_mock_git_history(self, output_file="mock_git_history.json"):
        """生成模拟的Git历史数据"""
        print("📊 生成模拟Git历史数据...")
        
        contributors = [
            "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince",
            "Eve Wilson", "Frank Miller", "Grace Lee", "Henry Ford"
        ]
        
        files = [
            "src/core/main.py", "src/utils/helpers.py", "src/api/routes.py",
            "src/models/user.py", "src/services/auth.py", "tests/test_main.py",
            "docs/README.md", "config/settings.py", "scripts/deploy.sh"
        ]
        
        # 生成历史提交数据
        history_data = {
            "contributors": {},
            "files": {},
            "commits": []
        }
        
        # 初始化贡献者数据
        for contributor in contributors:
            history_data["contributors"][contributor] = {
                "total_commits": 0,
                "recent_commits": 0,
                "files_touched": [],
                "activity_score": 0
            }
        
        # 初始化文件数据
        for file_path in files:
            history_data["files"][file_path] = {
                "contributors": {},
                "total_commits": 0,
                "last_modified": None
            }
        
        # 生成提交历史
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(200):  # 生成200个提交
            commit_date = base_date + timedelta(days=random.randint(0, 365))
            contributor = random.choice(contributors)
            affected_files = random.sample(files, random.randint(1, 3))
            
            commit_data = {
                "id": f"commit_{i:04d}",
                "author": contributor,
                "date": commit_date.isoformat(),
                "files": affected_files,
                "message": self._generate_commit_message()
            }
            
            history_data["commits"].append(commit_data)
            
            # 更新贡献者统计
            history_data["contributors"][contributor]["total_commits"] += 1
            if commit_date > datetime.now() - timedelta(days=90):
                history_data["contributors"][contributor]["recent_commits"] += 1
            
            # 更新文件统计
            for file_path in affected_files:
                if contributor not in history_data["files"][file_path]["contributors"]:
                    history_data["files"][file_path]["contributors"][contributor] = 0
                history_data["files"][file_path]["contributors"][contributor] += 1
                history_data["files"][file_path]["total_commits"] += 1
                history_data["files"][file_path]["last_modified"] = commit_date.isoformat()
                
                if file_path not in history_data["contributors"][contributor]["files_touched"]:
                    history_data["contributors"][contributor]["files_touched"].append(file_path)
        
        # 计算活动分数
        for contributor, data in history_data["contributors"].items():
            data["activity_score"] = data["recent_commits"] * 3 + data["total_commits"]
        
        # 保存数据
        output_path = self.configurations_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 模拟Git历史数据已生成: {output_path}")

    def _generate_file_content(self, file_type, index):
        """生成文件内容"""
        if file_type == "python":
            return self._generate_python_file(index)
        elif file_type == "javascript":
            return self._generate_javascript_file(index)
        elif file_type == "css":
            return self._generate_css_file(index)
        elif file_type == "html":
            return self._generate_html_file(index)
        elif file_type == "json":
            return self._generate_json_file(index)
        elif file_type == "markdown":
            return self._generate_markdown_file(index)
        elif file_type == "config":
            return self._generate_config_file(index)
        else:
            return f"file_{index:03d}.txt", f"Test file {index}\\nGenerated content"

    def _generate_python_file(self, index):
        """生成Python文件"""
        class_name = f"TestClass{index:03d}"
        function_name = f"test_function_{index}"
        
        content = f'''#!/usr/bin/env python3
"""
Test module {index}
Generated for testing purposes
"""

import os
import sys
from datetime import datetime


class {class_name}:
    """Test class {index}"""
    
    def __init__(self, name="test_{index}"):
        self.name = name
        self.created_at = datetime.now()
        self.version = "{random.randint(1, 10)}.{random.randint(0, 9)}"
    
    def {function_name}(self):
        """Test function {index}"""
        return f"{{self.name}} executed at {{self.created_at}}"
    
    def process_data(self, data):
        """Process test data"""
        if not data:
            return None
        
        processed = []
        for item in data:
            if isinstance(item, str):
                processed.append(item.upper())
            elif isinstance(item, (int, float)):
                processed.append(item * 2)
            else:
                processed.append(str(item))
        
        return processed


def main():
    """Main function for test module {index}"""
    test_obj = {class_name}()
    print(test_obj.{function_name}())
    
    test_data = ["hello", 42, 3.14, True]
    result = test_obj.process_data(test_data)
    print(f"Processed data: {{result}}")


if __name__ == "__main__":
    main()
'''
        return f"test_module_{index:03d}.py", content

    def _generate_javascript_file(self, index):
        """生成JavaScript文件"""
        content = f'''/**
 * Test JavaScript module {index}
 * Generated for testing purposes
 */

class TestClass{index:03d} {{
    constructor(name = 'test_{index}') {{
        this.name = name;
        this.createdAt = new Date();
        this.version = '{random.randint(1, 10)}.{random.randint(0, 9)}';
    }}
    
    testFunction{index}() {{
        return `${{this.name}} executed at ${{this.createdAt}}`;
    }}
    
    processData(data) {{
        if (!data || !Array.isArray(data)) {{
            return null;
        }}
        
        return data.map(item => {{
            if (typeof item === 'string') {{
                return item.toUpperCase();
            }} else if (typeof item === 'number') {{
                return item * 2;
            }} else {{
                return String(item);
            }}
        }});
    }}
}}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = TestClass{index:03d};
}}

// Example usage
const testObj = new TestClass{index:03d}();
console.log(testObj.testFunction{index}());

const testData = ['hello', 42, 3.14, true];
const result = testObj.processData(testData);
console.log('Processed data:', result);
'''
        return f"test_module_{index:03d}.js", content

    def _generate_css_file(self, index):
        """生成CSS文件"""
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#6c5ce7", "#fd79a8"]
        color = random.choice(colors)
        
        content = f'''/*
 * Test CSS module {index}
 * Generated for testing purposes
 */

.test-component-{index:03d} {{
    background-color: {color};
    padding: 20px;
    margin: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    font-family: 'Arial', sans-serif;
}}

.test-component-{index:03d} h1 {{
    color: #333;
    font-size: 24px;
    margin-bottom: 16px;
    text-align: center;
}}

.test-component-{index:03d} p {{
    color: #666;
    line-height: 1.6;
    margin-bottom: 12px;
}}

.test-component-{index:03d} .button {{
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease;
}}

.test-component-{index:03d} .button:hover {{
    background-color: #0056b3;
}}

@media (max-width: 768px) {{
    .test-component-{index:03d} {{
        padding: 15px;
        margin: 5px;
    }}
    
    .test-component-{index:03d} h1 {{
        font-size: 20px;
    }}
}}
'''
        return f"test_styles_{index:03d}.css", content

    def _generate_html_file(self, index):
        """生成HTML文件"""
        content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page {index:03d}</title>
    <link rel="stylesheet" href="test_styles_{index:03d}.css">
</head>
<body>
    <div class="test-component-{index:03d}">
        <h1>Test Page {index}</h1>
        <p>This is a generated test page for component {index}.</p>
        <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="content">
            <h2>Features</h2>
            <ul>
                <li>Responsive design</li>
                <li>Modern CSS styling</li>
                <li>Interactive elements</li>
                <li>Cross-browser compatibility</li>
            </ul>
            
            <button class="button" onclick="handleClick()">Test Button {index}</button>
        </div>
    </div>
    
    <script>
        function handleClick() {{
            alert('Button {index} clicked!');
            console.log('Test component {index} interaction');
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Test page {index} loaded');
        }});
    </script>
</body>
</html>
'''
        return f"test_page_{index:03d}.html", content

    def _generate_json_file(self, index):
        """生成JSON文件"""
        data = {
            "id": index,
            "name": f"test_data_{index:03d}",
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "description": f"Test data file {index} for testing purposes",
            "created_at": datetime.now().isoformat(),
            "config": {
                "debug": random.choice([True, False]),
                "max_items": random.randint(10, 100),
                "timeout": random.randint(1000, 5000),
                "retries": random.randint(1, 5)
            },
            "features": [
                f"feature_{i}" for i in range(random.randint(2, 6))
            ],
            "metadata": {
                "author": random.choice(["Alice", "Bob", "Charlie", "Diana"]),
                "priority": random.choice(["low", "medium", "high"]),
                "tags": [f"tag_{i}" for i in range(random.randint(1, 4))]
            }
        }
        
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return f"test_data_{index:03d}.json", content

    def _generate_markdown_file(self, index):
        """生成Markdown文件"""
        content = f'''# Test Document {index:03d}

This is a generated test document for testing purposes.

## Overview

Document ID: {index}
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: {random.randint(1, 5)}.{random.randint(0, 9)}

## Features

- **Feature A**: Advanced functionality for testing
- **Feature B**: Enhanced user experience
- **Feature C**: Improved performance metrics
- **Feature D**: Better error handling

## Code Examples

### Python Example

```python
def test_function_{index}():
    print("Hello from test document {index}")
    return True
```

### JavaScript Example

```javascript
function testFunction{index}() {{
    console.log('Hello from test document {index}');
    return true;
}}
```

## Configuration

| Setting | Value | Description |
|---------|--------|-------------|
| Debug | {random.choice(['true', 'false'])} | Enable debug mode |
| Max Items | {random.randint(10, 100)} | Maximum number of items |
| Timeout | {random.randint(1000, 5000)}ms | Request timeout |

## Tasks

- [x] Create basic structure
- [x] Add configuration options
- [ ] Implement advanced features
- [ ] Add comprehensive tests
- [ ] Update documentation

## Notes

> This is a test document generated for the Git Merge Orchestrator testing system.
> It contains sample content to simulate real documentation files.

## Links

- [Main Project](../README.md)
- [Configuration Guide](config/settings.md)
- [API Documentation](api/index.md)

---

*Generated by Test Data Generator v1.0*
'''
        return f"test_doc_{index:03d}.md", content

    def _generate_config_file(self, index):
        """生成配置文件"""
        config_formats = ["ini", "yaml", "env"]
        format_type = random.choice(config_formats)
        
        if format_type == "ini":
            content = f'''# Test configuration file {index}
# Generated for testing purposes

[general]
app_name = test_app_{index}
version = {random.randint(1, 5)}.{random.randint(0, 9)}
debug = {random.choice(['true', 'false'])}

[database]
host = localhost
port = {random.choice([3306, 5432, 27017])}
name = test_db_{index}
user = test_user
password = test_pass

[cache]
enabled = {random.choice(['true', 'false'])}
ttl = {random.randint(300, 3600)}
max_size = {random.randint(100, 1000)}

[logging]
level = {random.choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'])}
file = logs/test_{index}.log
max_size = {random.randint(10, 100)}MB
'''
            return f"test_config_{index:03d}.ini", content
            
        elif format_type == "yaml":
            content = f'''# Test YAML configuration {index}
# Generated for testing purposes

general:
  app_name: test_app_{index}
  version: "{random.randint(1, 5)}.{random.randint(0, 9)}"
  debug: {random.choice(['true', 'false'])}

database:
  host: localhost
  port: {random.choice([3306, 5432, 27017])}
  name: test_db_{index}
  user: test_user
  password: test_pass

cache:
  enabled: {random.choice(['true', 'false'])}
  ttl: {random.randint(300, 3600)}
  max_size: {random.randint(100, 1000)}

logging:
  level: {random.choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'])}
  file: logs/test_{index}.log
  max_size: {random.randint(10, 100)}MB
'''
            return f"test_config_{index:03d}.yaml", content
            
        else:  # env
            content = f'''# Test environment configuration {index}
# Generated for testing purposes

APP_NAME=test_app_{index}
VERSION={random.randint(1, 5)}.{random.randint(0, 9)}
DEBUG={random.choice(['true', 'false'])}

DB_HOST=localhost
DB_PORT={random.choice([3306, 5432, 27017])}
DB_NAME=test_db_{index}
DB_USER=test_user
DB_PASSWORD=test_pass

CACHE_ENABLED={random.choice(['true', 'false'])}
CACHE_TTL={random.randint(300, 3600)}
CACHE_MAX_SIZE={random.randint(100, 1000)}

LOG_LEVEL={random.choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'])}
LOG_FILE=logs/test_{index}.log
LOG_MAX_SIZE={random.randint(10, 100)}MB
'''
            return f"test_config_{index:03d}.env", content

    def _generate_commit_message(self):
        """生成提交消息"""
        prefixes = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        actions = ["add", "update", "fix", "remove", "improve", "implement", "optimize"]
        subjects = [
            "user authentication", "api endpoints", "database queries", "error handling",
            "unit tests", "documentation", "configuration", "performance", "security",
            "logging", "validation", "caching", "monitoring", "deployment"
        ]
        
        prefix = random.choice(prefixes)
        action = random.choice(actions)
        subject = random.choice(subjects)
        
        return f"{prefix}: {action} {subject}"

    def _generate_basic_config(self):
        """生成基础配置"""
        return {
            "name": "basic_test_config",
            "version": "1.0.0",
            "description": "基础测试配置",
            "settings": {
                "max_files_per_group": 5,
                "max_tasks_per_person": 50,
                "active_months": 3,
                "analysis_months": 12
            },
            "contributors": [
                "TestUser1",
                "TestUser2",
                "TestUser3"
            ],
            "ignore_patterns": [
                "*.pyc",
                "*.log",
                ".DS_Store"
            ]
        }

    def _generate_advanced_config(self):
        """生成高级配置"""
        return {
            "name": "advanced_test_config",
            "version": "2.0.0",
            "description": "高级测试配置",
            "processing_mode": "file_level",
            "settings": {
                "max_files_per_group": 10,
                "max_tasks_per_person": 200,
                "active_months": 6,
                "analysis_months": 24,
                "enable_caching": True,
                "cache_expiry_hours": 48,
                "max_worker_threads": 8
            },
            "contributors": [
                "SeniorDev1", "SeniorDev2", "JuniorDev1", 
                "JuniorDev2", "TeamLead", "Architect"
            ],
            "ignore_patterns": [
                "*.pyc", "*.pyo", "*.pyd", "__pycache__/",
                "*.log", "*.tmp", ".DS_Store", "node_modules/",
                "build/", "dist/", ".vscode/", ".idea/"
            ],
            "branch_patterns": {
                "feature_prefix": "feat/",
                "bugfix_prefix": "fix/",
                "hotfix_prefix": "hotfix/",
                "integration_template": "integration-{source}-{target}"
            },
            "load_balancing": {
                "enabled": True,
                "max_imbalance_ratio": 2.0,
                "prefer_recent_contributors": True
            }
        }

    def _generate_performance_config(self):
        """生成性能测试配置"""
        return {
            "name": "performance_test_config",
            "version": "1.0.0",
            "description": "性能测试专用配置",
            "performance": {
                "target_files": 1000,
                "max_contributors": 20,
                "max_branches": 50,
                "timeout_seconds": 300,
                "memory_limit_mb": 512
            },
            "benchmarks": {
                "file_analysis_time_ms": 100,
                "contributor_analysis_time_ms": 500,
                "task_assignment_time_ms": 200,
                "script_generation_time_ms": 50
            },
            "monitoring": {
                "enable_profiling": True,
                "log_performance_stats": True,
                "track_memory_usage": True
            }
        }

    def _generate_team_config(self):
        """生成团队配置"""
        return {
            "name": "team_collaboration_config",
            "version": "1.0.0",
            "description": "团队协作测试配置",
            "teams": {
                "frontend": {
                    "members": ["Frontend-Dev1", "Frontend-Dev2", "UI-Designer"],
                    "specialization": ["*.js", "*.jsx", "*.css", "*.html", "*.vue"],
                    "max_tasks": 30
                },
                "backend": {
                    "members": ["Backend-Dev1", "Backend-Dev2", "API-Dev"],
                    "specialization": ["*.py", "*.java", "*.go", "*.rs"],
                    "max_tasks": 40
                },
                "devops": {
                    "members": ["DevOps-Engineer", "SRE"],
                    "specialization": ["*.yml", "*.yaml", "*.sh", "Dockerfile", "*.tf"],
                    "max_tasks": 20
                },
                "qa": {
                    "members": ["QA-Tester1", "QA-Tester2"],
                    "specialization": ["*test*.py", "*spec*.js", "*.feature"],
                    "max_tasks": 25
                }
            },
            "collaboration_rules": {
                "cross_team_review": True,
                "require_team_lead_approval": False,
                "auto_assign_by_expertise": True
            }
        }

    def _generate_ignore_patterns(self):
        """生成忽略模式配置"""
        return {
            "name": "ignore_patterns_config",
            "version": "1.0.0",
            "description": "文件忽略模式配置",
            "patterns": {
                "build_artifacts": [
                    "build/", "dist/", "out/", "target/",
                    "*.o", "*.obj", "*.exe", "*.dll", "*.so"
                ],
                "dependencies": [
                    "node_modules/", "vendor/", ".yarn/",
                    "site-packages/", "Pods/"
                ],
                "cache_files": [
                    "*.pyc", "*.pyo", "*.pyd", "__pycache__/",
                    "*.class", "*.jar", ".gradle/"
                ],
                "temporary_files": [
                    "*.tmp", "*.temp", "*.swp", "*.swo", "*~",
                    ".DS_Store", "Thumbs.db"
                ],
                "log_files": [
                    "*.log", "*.log.*", "logs/", "log/"
                ],
                "ide_files": [
                    ".vscode/", ".idea/", "*.sublime-*",
                    ".eclipse/", ".settings/"
                ],
                "version_control": [
                    ".git/", ".svn/", ".hg/", ".bzr/"
                ]
            },
            "rules": {
                "apply_global_patterns": True,
                "respect_gitignore": True,
                "case_sensitive": False
            }
        }

    def _generate_test_scenarios_config(self):
        """生成测试场景配置"""
        return {
            "name": "test_scenarios_config",
            "version": "1.0.0",
            "description": "测试场景配置定义",
            "scenarios": {
                "merge_conflicts": {
                    "description": "合并冲突测试",
                    "files_count": 20,
                    "contributors": 3,
                    "conflict_probability": 0.3,
                    "branches": ["feature-1", "feature-2"]
                },
                "file_level_processing": {
                    "description": "文件级处理测试",
                    "files_count": 50,
                    "contributors": 5,
                    "processing_mode": "file_level",
                    "directory_depth": 4
                },
                "load_balancing": {
                    "description": "负载均衡测试",
                    "files_count": 100,
                    "contributors": 8,
                    "imbalance_ratio": 3.0,
                    "heavy_contributors": 2
                },
                "performance": {
                    "description": "性能压力测试",
                    "files_count": 500,
                    "contributors": 10,
                    "commit_history": 1000,
                    "timeout_limit": 60
                }
            },
            "validation": {
                "max_execution_time": 300,
                "max_memory_usage": "1GB",
                "success_criteria": {
                    "completion_rate": 0.95,
                    "error_rate": 0.05
                }
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git Merge Orchestrator 测试数据生成工具")
    
    parser.add_argument("--files", "-f", type=int, default=50, help="生成示例文件数量")
    parser.add_argument("--configs", "-c", action="store_true", help="生成配置文件")
    parser.add_argument("--history", "--hist", action="store_true", help="生成模拟Git历史")
    parser.add_argument("--all", "-a", action="store_true", help="生成所有类型的测试数据")
    parser.add_argument(
        "--types", "-t",
        nargs="+",
        choices=["python", "javascript", "css", "html", "json", "markdown", "config"],
        help="指定要生成的文件类型"
    )
    parser.add_argument(
        "--base-dir",
        default="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test",
        help="测试目录基础路径"
    )

    args = parser.parse_args()
    
    generator = TestDataGenerator(args.base_dir)
    
    if args.all:
        print("🚀 生成所有测试数据...")
        generator.generate_sample_files(args.files, args.types)
        generator.generate_configurations()
        generator.generate_mock_git_history()
        print("✅ 所有测试数据生成完成")
        return
    
    if args.files > 0:
        generator.generate_sample_files(args.files, args.types)
    
    if args.configs:
        generator.generate_configurations()
    
    if args.history:
        generator.generate_mock_git_history()
    
    if not any([args.files > 0, args.configs, args.history]):
        print("请指定要生成的数据类型，使用 --help 查看帮助")
        return


if __name__ == "__main__":
    main()