# Git Merge Orchestrator 测试目录

这个目录专门用于Git Merge Orchestrator的测试和实验环境。提供独立、安全的测试空间，避免污染主项目代码。

## 📁 目录结构

```
git-merge-orchestrator-test/
├── README.md                    # 本说明文档
├── test-repos/                  # 测试仓库目录
│   ├── simple-repo/            # 简单测试仓库
│   ├── complex-repo/           # 复杂场景测试仓库
│   └── multi-branch-repo/      # 多分支测试仓库
├── test-scripts/               # 测试脚本和工具
│   ├── create_test_repo.py     # 测试仓库创建工具
│   ├── setup_scenarios.py     # 场景设置脚本
│   └── cleanup.py              # 清理工具
├── test-data/                  # 测试数据
│   ├── sample-files/           # 示例文件
│   └── configurations/         # 测试配置
└── logs/                       # 测试日志
```

## 🚀 快速开始

### 1. 基本测试仓库创建

```bash
cd /home/howie/Workspace/Project/tools/git-merge-orchestrator-test

# 创建简单测试仓库
python test-scripts/create_test_repo.py --type simple --name my-test

# 创建复杂测试仓库
python test-scripts/create_test_repo.py --type complex --name advanced-test
```

### 2. 运行测试场景

```bash
# 在测试目录中运行git-merge-orchestrator
cd test-repos/my-test
python ../../git-merge-orchestrator/main.py feature-branch main

# 或使用相对路径
python ../git-merge-orchestrator/main.py --repo-path ./test-repos/my-test
```

## 🧪 测试场景类型

### 1. 简单场景 (simple-repo)
- **用途**: 基本功能验证
- **特点**: 
  - 2-3个分支
  - 5-10个文件
  - 简单的合并冲突
  - 单一贡献者或少数贡献者

### 2. 复杂场景 (complex-repo)
- **用途**: 高级功能和性能测试
- **特点**:
  - 5-10个分支
  - 50-100个文件
  - 多层目录结构
  - 复杂的合并冲突
  - 多个贡献者

### 3. 多分支场景 (multi-branch-repo)
- **用途**: 分支管理和集成测试
- **特点**:
  - 10+个活跃分支
  - 模拟真实开发环境
  - 交叉合并需求
  - 长期分支历史

### 4. 大规模场景 (large-scale-repo)
- **用途**: 性能压力测试
- **特点**:
  - 数百个文件
  - 深层嵌套目录
  - 大量历史提交
  - 模拟企业级项目

## 🔧 测试工具使用

### 创建测试仓库工具

```bash
# 基本用法
python test-scripts/create_test_repo.py --help

# 创建指定类型的测试仓库
python test-scripts/create_test_repo.py \
  --type complex \
  --name project-x \
  --contributors "Alice,Bob,Charlie" \
  --files 50 \
  --branches "develop,feature-1,feature-2"
```

### 场景设置脚本

```bash
# 设置标准测试场景
python test-scripts/setup_scenarios.py --scenario merge-conflicts
python test-scripts/setup_scenarios.py --scenario file-level-processing
python test-scripts/setup_scenarios.py --scenario load-balancing
```

### 清理工具

```bash
# 清理所有测试仓库
python test-scripts/cleanup.py --all

# 清理特定仓库
python test-scripts/cleanup.py --repo my-test

# 清理日志文件
python test-scripts/cleanup.py --logs
```

## 📋 测试最佳实践

### 1. 测试前准备
- 确保测试目录独立于主项目
- 检查Git配置是否正确
- 备份重要的测试数据

### 2. 测试执行
- 每次测试使用独立的仓库
- 记录测试步骤和结果
- 注意观察性能指标

### 3. 测试后清理
- 及时清理临时文件
- 保存有价值的测试日志
- 更新测试文档

## 🎯 测试用例模板

### 基本功能测试

```bash
# 1. 创建测试环境
cd git-merge-orchestrator-test
python test-scripts/create_test_repo.py --type simple --name basic-test

# 2. 执行合并编排
cd test-repos/basic-test
python ../../git-merge-orchestrator/main.py feature main

# 3. 验证结果
git log --oneline
git status
```

### 文件级处理测试

```bash
# 1. 创建复杂测试环境
python test-scripts/create_test_repo.py --type complex --name file-level-test

# 2. 启用文件级处理模式
cd test-repos/file-level-test
python ../../git-merge-orchestrator/main.py \
  --processing-mode file_level \
  feature-branch main

# 3. 验证文件级分配
# 检查 .merge_work/merge_plan.json 中的文件级结构
```

### 性能压力测试

```bash
# 1. 创建大规模测试环境
python test-scripts/create_test_repo.py \
  --type large-scale \
  --name performance-test \
  --files 200 \
  --contributors "Dev1,Dev2,Dev3,Dev4,Dev5"

# 2. 执行性能测试
cd test-repos/performance-test
time python ../../git-merge-orchestrator/main.py feature main

# 3. 分析性能数据
# 检查 .merge_work/performance.log
```

## 🛠️ 故障排查

### 常见问题

1. **Git仓库初始化失败**
   ```bash
   # 解决方案
   git config --global user.name "Test User"
   git config --global user.email "test@example.com"
   ```

2. **权限问题**
   ```bash
   # 确保脚本可执行
   chmod +x test-scripts/*.py
   ```

3. **路径问题**
   ```bash
   # 使用绝对路径
   export GMO_TEST_DIR="/home/howie/Workspace/Project/tools/git-merge-orchestrator-test"
   ```

### 调试模式

```bash
# 启用详细输出
export GIT_MERGE_DEBUG=1

# 启用性能监控
export ENABLE_PERFORMANCE_MONITORING=true

# 设置日志级别
export LOG_LEVEL=DEBUG
```

## 📊 测试报告

### 自动测试报告生成

```bash
# 运行完整测试套件并生成报告
python ../git-merge-orchestrator/run_tests.py --full --report-dir ./logs
```

### 性能基准测试

```bash
# 基准性能测试
python test-scripts/benchmark.py \
  --scenarios "simple,complex,large-scale" \
  --iterations 3 \
  --output ./logs/benchmark_$(date +%Y%m%d_%H%M%S).json
```

## 🔄 持续集成集成

### GitHub Actions 示例

```yaml
name: Git Merge Orchestrator Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Test Environment
        run: |
          cd git-merge-orchestrator-test
          python test-scripts/setup_scenarios.py --all
      
      - name: Run Core Tests
        run: |
          cd git-merge-orchestrator
          python run_tests.py --full
      
      - name: Run Integration Tests
        run: |
          cd git-merge-orchestrator-test
          python test-scripts/integration_tests.py
```

## 📝 贡献测试用例

### 添加新测试场景

1. 在 `test-scripts/` 中创建场景脚本
2. 更新 `setup_scenarios.py` 添加新场景
3. 在本文档中记录使用方法
4. 提供测试验证步骤

### 测试数据提交

- 不要提交实际的Git仓库到版本控制
- 只提交测试脚本和配置文件
- 使用 `.gitignore` 排除临时文件

## 🎯 测试覆盖目标

- **功能覆盖**: 90%+ 的核心功能
- **场景覆盖**: 涵盖常见使用场景
- **性能覆盖**: 各种规模的仓库测试
- **错误覆盖**: 边界条件和异常情况

## 🧰 高级测试工具

### 集成测试套件
```bash
# 运行完整的集成测试
python test-scripts/integration_tests.py

# 查看集成测试报告
ls logs/integration_test_report_*.json
```

### 性能基准测试
```bash
# 运行性能基准测试
python test-scripts/benchmark.py --scenarios "simple,complex" --iterations 3

# 自定义基准测试
python test-scripts/benchmark.py \
  --scenarios "large-scale" \
  --iterations 5 \
  --output ./my_benchmark.json
```

### 批量自动化测试
```bash
# 运行完整的批量测试
./batch_test.sh

# 快速测试模式（跳过性能测试）
./batch_test.sh --quick

# 仅运行健康检查
./batch_test.sh --health-only

# 仅设置测试场景
./batch_test.sh --scenarios-only
```

### 结果验证工具
```bash
# 验证所有测试场景结果
python test-scripts/verify_results.py

# 验证特定场景
python test-scripts/verify_results.py --scenario merge-conflicts-test
```

## 🔄 完整测试工作流

### 新用户快速体验
```bash
# 1. 进入测试目录
cd /home/howie/Workspace/Project/tools/git-merge-orchestrator-test

# 2. 运行快速批量测试
./batch_test.sh --quick

# 3. 查看测试报告
ls logs/batch_test_report_*.md
```

### 开发者完整测试
```bash
# 1. 设置所有测试场景
python test-scripts/setup_scenarios.py --scenario all

# 2. 运行集成测试
python test-scripts/integration_tests.py

# 3. 运行性能基准测试
python test-scripts/benchmark.py

# 4. 验证测试结果
python test-scripts/verify_results.py

# 5. 生成综合报告
./batch_test.sh
```

### 持续集成测试
```bash
# CI环境中的测试命令
./batch_test.sh --quick --ci-mode 2>&1 | tee ci_test.log
```

## 📊 测试报告系统

### 自动生成的报告类型

1. **集成测试报告** (`integration_test_report_*.json`)
   - 各场景测试结果
   - 成功率统计
   - 详细错误信息

2. **性能基准报告** (`benchmark_report_*.json`)  
   - 不同场景的性能对比
   - 处理模式性能分析
   - 系统环境信息

3. **批量测试报告** (`batch_test_report_*.md`)
   - 完整测试流程摘要
   - 所有步骤执行状态
   - 问题诊断建议

### 报告查看工具
```bash
# 查看最新的测试报告
ls -t logs/*.md logs/*.json | head -5

# 简化的报告摘要
grep -E "(✅|❌|⚠️)" logs/batch_test_report_*.md | tail -10
```

## 🎯 测试场景扩展

### 添加自定义测试场景

1. **创建场景脚本**
   ```python
   # 在 setup_scenarios.py 中添加新方法
   def _setup_my_custom_scenario(self):
       # 实现自定义场景设置逻辑
       pass
   ```

2. **注册场景**
   ```python
   # 在 setup_scenario 方法中添加
   scenarios = {
       # 现有场景...
       "my-custom": self._setup_my_custom_scenario,
   }
   ```

3. **添加验证逻辑**
   ```python
   # 在 verify_results.py 中添加验证方法
   def _verify_my_custom_scenario(self, repo_path):
       # 实现验证逻辑
       pass
   ```

### 自定义仓库生成
```bash
# 使用自定义参数创建测试仓库
python test-scripts/create_test_repo.py \
  --name "enterprise-simulation" \
  --type "large-scale" \
  --contributors "TeamA-Lead,TeamA-Dev1,TeamA-Dev2,TeamB-Lead,TeamB-Dev1" \
  --files 200 \
  --branches "release/v2.0,feature/user-auth,feature/payment,hotfix/security"
```

## 🔧 故障诊断指南

### 常见问题及解决方案

#### 测试环境问题
```bash
# Git配置问题
git config --global user.name "Test User"
git config --global user.email "test@example.com"

# Python路径问题  
export PYTHONPATH="/home/howie/Workspace/Project/tools/git-merge-orchestrator:$PYTHONPATH"

# 权限问题
chmod +x test-scripts/*.py
chmod +x *.sh
```

#### 性能测试问题
```bash
# 内存不足
python test-scripts/benchmark.py --scenarios "simple" --iterations 1

# 超时问题
timeout 300s python test-scripts/integration_tests.py
```

#### 场景设置失败
```bash
# 清理后重试
python test-scripts/cleanup.py --all
python test-scripts/setup_scenarios.py --scenario all

# 单独设置problematic场景
python test-scripts/setup_scenarios.py --scenario merge-conflicts --debug
```

### 调试模式
```bash
# 启用详细输出
export GIT_MERGE_DEBUG=1
export LOG_LEVEL=DEBUG

# 保留中间文件
export KEEP_TEMP_FILES=1

# 单步调试
python -u test-scripts/integration_tests.py 2>&1 | tee debug.log
```

## 📈 性能基准参考

### 不同规模的预期性能

| 场景类型 | 文件数量 | 贡献者数 | 预期时间 | 内存使用 |
|---------|---------|---------|---------|---------|
| Simple | 10-20 | 2-3 | < 10秒 | < 100MB |
| Complex | 50-100 | 5-8 | < 30秒 | < 200MB |  
| Large-scale | 200-500 | 8-15 | < 120秒 | < 500MB |

### 性能评级标准

- **优秀**: 在预期时间内完成，成功率 ≥ 95%
- **良好**: 在预期时间1.5倍内完成，成功率 ≥ 90%  
- **一般**: 在预期时间2倍内完成，成功率 ≥ 80%
- **需优化**: 超过预期时间2倍或成功率 < 80%

## 📞 获取帮助

### 日志文件位置
- 集成测试日志: `logs/integration_test_*.log`
- 性能基准日志: `logs/benchmark_*.log`  
- 批量测试日志: `logs/batch_test_report_*.md`
- 场景设置日志: `logs/scenario_setup_*.log`

### 支持渠道
1. 查看 `logs/` 目录中的详细日志
2. 运行 `./batch_test.sh --help` 了解批量测试选项
3. 检查主项目的 `TESTING_GUIDE.md` 文档  
4. 使用 `python test-scripts/verify_results.py` 验证结果
5. 在项目仓库中提交issue报告问题

### 快速问题排查
```bash
# 一键问题诊断
./batch_test.sh --health-only

# 检查测试环境状态
python test-scripts/integration_tests.py --check-env

# 重置测试环境
python test-scripts/cleanup.py --all
python test-scripts/setup_scenarios.py --scenario all
```

---

**🚀 通过系统化的测试工具和流程，确保 Git Merge Orchestrator 的稳定性和可靠性！**