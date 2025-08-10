# Git Merge Orchestrator 测试环境 - 贡献指南

## 📋 版本管理策略

这个测试环境使用Git进行版本管理，但采用了精心设计的忽略策略，确保只管理必要的文件。

## 🎯 版本管理的文件

### ✅ 纳入版本管理的文件类型

1. **核心脚本和工具**
   - `batch_test.sh` - 批量测试脚本
   - `test-scripts/*.py` - 所有测试脚本
   - `README.md` - 项目说明文档

2. **静态配置和测试数据**
   - `test-data/configurations/` - 测试配置文件
   - `test-data/sample-files/` - 示例测试文件
   - `.gitignore` - Git忽略规则

3. **目录结构占位文件**
   - `logs/.gitkeep` - 保持日志目录
   - `scenarios/.gitkeep` - 保持场景目录
   - `test-repos/.gitkeep` - 保持测试仓库目录

### ❌ 不纳入版本管理的文件类型

1. **动态生成的内容**
   - `test-repos/*/` - 测试过程中动态创建的Git仓库
   - `logs/*.log` - 测试运行日志
   - `scenarios/*.json` - 运行时生成的场景配置

2. **临时和缓存文件**
   - `__pycache__/` - Python字节码
   - `*.pyc` - 编译文件
   - 各种临时文件和备份文件

3. **用户自定义内容**
   - 本地配置文件
   - 调试输出
   - 性能分析结果

## 🔄 开发工作流

### 1. 日常开发
```bash
# 检查当前状态
git status

# 添加新的脚本或配置文件
git add test-scripts/new_feature.py
git add test-data/configurations/new_config.json

# 提交更改
git commit -m "feat: 添加新功能测试脚本

- 实现xxx功能的测试用例
- 添加相应的配置文件
- 更新文档说明"

# 查看提交历史
git log --oneline -10
```

### 2. 添加新的测试脚本
```bash
# 创建新脚本
cp test-scripts/template.py test-scripts/new_test.py
# 编辑新脚本...

# 使脚本可执行
chmod +x test-scripts/new_test.py

# 添加到版本管理
git add test-scripts/new_test.py
git commit -m "feat: 添加新测试脚本 new_test.py"
```

### 3. 更新测试数据
```bash
# 添加新的测试配置
git add test-data/configurations/
git commit -m "data: 更新测试配置数据"

# 添加新的示例文件
git add test-data/sample-files/
git commit -m "data: 添加新的示例测试文件"
```

### 4. 文档维护
```bash
# 更新文档
git add README.md CONTRIBUTING.md
git commit -m "docs: 更新项目文档

- 完善使用说明
- 添加故障排除指南"
```

## 📊 分支管理

### 主要分支
- **`master`** - 主分支，稳定版本
- **`develop`** - 开发分支（可选）
- **`feature/*`** - 功能分支（可选）

### 分支策略示例
```bash
# 创建功能分支
git checkout -b feature/advanced-benchmarks

# 开发完成后合并
git checkout master
git merge feature/advanced-benchmarks
git branch -d feature/advanced-benchmarks
```

## 🧹 清理和维护

### 定期清理
```bash
# 清理所有动态生成的内容
./batch_test.sh --cleanup
python test-scripts/cleanup.py --all

# 检查Git状态（应该是clean）
git status
```

### 重置测试环境
```bash
# 完全重置（保持Git历史）
python test-scripts/cleanup.py --all
git status  # 应该显示 clean

# 如果需要，重新设置测试场景
python test-scripts/setup_scenarios.py --scenario all
```

## 🚀 发布和标签

### 创建版本标签
```bash
# 创建带注释的标签
git tag -a v1.0.0 -m "Git Merge Orchestrator 测试环境 v1.0.0

功能特性:
- 完整的自动化测试套件
- 8种预定义测试场景
- 性能基准测试工具
- 集成测试系统"

# 查看标签
git tag -l

# 显示标签详细信息
git show v1.0.0
```

### 版本发布
```bash
# 推送标签（如果有远程仓库）
git push origin v1.0.0

# 或推送所有标签
git push origin --tags
```

## 🔍 代码质量检查

### 提交前检查
```bash
# 格式化Python代码
black test-scripts/*.py

# 检查语法（如果安装了 flake8）
flake8 test-scripts/ --max-line-length=88

# 测试脚本功能
python test-scripts/integration_tests.py --quick
```

### 预提交钩子建议
创建 `.git/hooks/pre-commit` 文件：
```bash
#!/bin/bash
# 预提交钩子 - 格式化代码

echo "🔍 运行预提交检查..."

# 格式化Python文件
if command -v black >/dev/null 2>&1; then
    black test-scripts/*.py
    git add test-scripts/*.py
    echo "✅ 代码格式化完成"
fi

# 基本语法检查
python -m py_compile test-scripts/*.py
if [ $? -eq 0 ]; then
    echo "✅ Python语法检查通过"
else
    echo "❌ Python语法检查失败"
    exit 1
fi

echo "🎉 预提交检查完成"
```

## 📝 提交信息约定

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型说明
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **data**: 测试数据更新
- **perf**: 性能优化

### 示例
```bash
git commit -m "feat(benchmark): 添加内存使用监控功能

- 在性能基准测试中集成内存监控
- 添加内存使用趋势分析
- 更新相关文档和示例

Closes #123"
```

## 🤝 协作指南

### 多人协作
1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd git-merge-orchestrator-test-env
   ```

2. **设置开发环境**
   ```bash
   # 设置Git身份
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   
   # 验证环境
   ./batch_test.sh --health-only
   ```

3. **开始开发**
   ```bash
   # 同步最新代码
   git pull origin master
   
   # 创建功能分支
   git checkout -b feature/my-improvement
   
   # 开发并提交
   git add .
   git commit -m "feat: 我的改进功能"
   ```

### 代码审查
- 确保新增的脚本有执行权限
- 验证忽略规则正确工作
- 测试新功能在不同场景下的表现
- 检查文档是否同步更新

## 📞 问题报告

如果遇到Git管理相关的问题：

1. 检查 `.gitignore` 是否正确配置
2. 确认文件是否应该被版本管理
3. 查看Git状态和日志
4. 必要时重置或清理环境

### 常见问题解决
```bash
# 问题：意外提交了不应该管理的文件
git rm --cached unwanted-file.log
git commit -m "fix: 移除不应版本管理的文件"

# 问题：忽略规则不生效
git rm -r --cached .
git add .
git commit -m "fix: 重新应用忽略规则"
```

---

通过遵循这些指南，我们可以确保Git Merge Orchestrator测试环境的版本管理既高效又清晰！ 🚀
