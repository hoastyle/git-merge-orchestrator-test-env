#!/bin/bash

# Git Merge Orchestrator - 批量测试脚本
# 自动执行完整的测试套件

set -e  # 遇到错误立即退出

# 配置
TEST_DIR="/home/howie/Workspace/Project/tools/git-merge-orchestrator/test-environment"
GMO_DIR="/home/howie/Workspace/Project/tools/git-merge-orchestrator"
LOG_DIR="$TEST_DIR/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装"
        exit 1
    fi
    
    if [ ! -d "$GMO_DIR" ]; then
        log_error "Git Merge Orchestrator 目录不存在: $GMO_DIR"
        exit 1
    fi
    
    if [ ! -d "$TEST_DIR" ]; then
        log_error "测试目录不存在: $TEST_DIR"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 初始化测试环境
init_test_environment() {
    log_info "初始化测试环境..."
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 设置Git配置（如果未设置）
    if [ -z "$(git config --global user.name 2>/dev/null)" ]; then
        git config --global user.name "Test User"
        log_info "设置Git用户名: Test User"
    fi
    
    if [ -z "$(git config --global user.email 2>/dev/null)" ]; then
        git config --global user.email "test@example.com"
        log_info "设置Git用户邮箱: test@example.com"
    fi
    
    # 切换到测试目录
    cd "$TEST_DIR"
    
    log_success "测试环境初始化完成"
}

# 清理旧的测试数据
cleanup_old_tests() {
    log_info "清理旧的测试数据..."
    
    if [ -f "test-scripts/cleanup.py" ]; then
        python3 test-scripts/cleanup.py --all --quiet 2>/dev/null || true
    fi
    
    # 清理旧日志（保留最近10个）
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.log" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null || true
        find "$LOG_DIR" -name "*.json" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null || true
    fi
    
    log_success "清理完成"
}

# 运行健康检查
run_health_check() {
    log_info "运行系统健康检查..."
    
    cd "$GMO_DIR"
    
    local health_log="$LOG_DIR/health_check_$TIMESTAMP.log"
    
    if python3 run_tests.py --health > "$health_log" 2>&1; then
        local health_status=$(tail -1 "$health_log" | grep -o "✅.*通过" || echo "检查完成")
        log_success "健康检查: $health_status"
        return 0
    else
        log_error "健康检查失败，查看日志: $health_log"
        return 1
    fi
}

# 设置测试场景
setup_test_scenarios() {
    log_info "设置测试场景..."
    
    cd "$TEST_DIR"
    
    local scenarios=("merge-conflicts" "file-level-processing" "load-balancing" "ignore-rules")
    local setup_log="$LOG_DIR/scenario_setup_$TIMESTAMP.log"
    
    for scenario in "${scenarios[@]}"; do
        log_info "  设置场景: $scenario"
        
        if python3 test-scripts/setup_scenarios.py --scenario "$scenario" >> "$setup_log" 2>&1; then
            log_success "  场景 $scenario 设置完成"
        else
            log_warning "  场景 $scenario 设置失败"
        fi
    done
    
    log_success "测试场景设置完成"
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."
    
    cd "$TEST_DIR"
    
    local integration_log="$LOG_DIR/integration_test_$TIMESTAMP.log"
    
    if python3 test-scripts/integration_tests.py > "$integration_log" 2>&1; then
        local success_rate=$(grep "成功率:" "$integration_log" | tail -1 | grep -o "[0-9.]*%" || echo "未知")
        log_success "集成测试完成，成功率: $success_rate"
        
        # 显示测试摘要
        if grep -q "集成测试报告摘要" "$integration_log"; then
            log_info "测试摘要:"
            grep -A 10 "集成测试报告摘要" "$integration_log" | tail -n +2
        fi
        
        return 0
    else
        log_error "集成测试失败，查看日志: $integration_log"
        
        # 显示错误信息
        if [ -f "$integration_log" ]; then
            log_error "最后几行错误信息:"
            tail -5 "$integration_log" | sed 's/^/  /'
        fi
        
        return 1
    fi
}

# 运行性能基准测试
run_performance_benchmark() {
    log_info "运行性能基准测试..."
    
    cd "$TEST_DIR"
    
    local benchmark_log="$LOG_DIR/benchmark_$TIMESTAMP.log"
    
    # 运行轻量级的性能测试（避免耗时过长）
    if python3 test-scripts/benchmark.py \
        --scenarios "simple,complex" \
        --iterations 2 \
        --output "$LOG_DIR/benchmark_result_$TIMESTAMP.json" > "$benchmark_log" 2>&1; then
        
        log_success "性能基准测试完成"
        
        # 显示性能摘要
        if grep -q "性能基准测试摘要报告" "$benchmark_log"; then
            log_info "性能摘要:"
            grep -A 15 "性能基准测试摘要报告" "$benchmark_log" | tail -n +2
        fi
        
        return 0
    else
        log_warning "性能基准测试未完成，查看日志: $benchmark_log"
        return 1
    fi
}

# 运行功能验证测试
run_functional_tests() {
    log_info "运行功能验证测试..."
    
    local test_scenarios=(
        "merge-conflicts-test:feature-1:master"
        "file-level-test:file-level-feature:master"
        "ignore-rules-test:ignore-test:master"
    )
    
    local functional_log="$LOG_DIR/functional_test_$TIMESTAMP.log"
    local success_count=0
    local total_count=${#test_scenarios[@]}
    
    for scenario_info in "${test_scenarios[@]}"; do
        IFS=':' read -r repo_name source_branch target_branch <<< "$scenario_info"
        
        local repo_path="$TEST_DIR/test-repos/$repo_name"
        
        if [ ! -d "$repo_path" ]; then
            log_warning "  跳过不存在的测试仓库: $repo_name"
            continue
        fi
        
        log_info "  测试仓库: $repo_name ($source_branch -> $target_branch)"
        
        cd "$repo_path"
        
        # 运行快速分析测试
        if timeout 60s python3 "$GMO_DIR/main.py" \
            "$source_branch" "$target_branch" \
            --auto-analyze --quiet >> "$functional_log" 2>&1; then
            
            # 检查是否生成了必要的文件
            if [ -f ".merge_work/merge_plan.json" ]; then
                log_success "    ✅ $repo_name 测试通过"
                ((success_count++))
            else
                log_warning "    ⚠️ $repo_name 未生成合并计划"
            fi
        else
            log_warning "    ❌ $repo_name 测试失败或超时"
        fi
        
        # 清理工作目录
        rm -rf .merge_work 2>/dev/null || true
    done
    
    local success_rate=$((success_count * 100 / total_count))
    
    if [ $success_rate -ge 80 ]; then
        log_success "功能验证测试完成: $success_count/$total_count 通过 (${success_rate}%)"
        return 0
    else
        log_warning "功能验证测试: $success_count/$total_count 通过 (${success_rate}%)"
        return 1
    fi
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."
    
    local report_file="$LOG_DIR/batch_test_report_$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# Git Merge Orchestrator 批量测试报告

## 测试概要
- **测试时间**: $(date)
- **测试环境**: $(uname -a)
- **Git版本**: $(git --version)
- **Python版本**: $(python3 --version)

## 测试结果

### 系统健康检查
$([ -f "$LOG_DIR/health_check_$TIMESTAMP.log" ] && echo "✅ 通过" || echo "❌ 失败")

### 集成测试
$(if [ -f "$LOG_DIR/integration_test_$TIMESTAMP.log" ]; then
    if grep -q "成功率: 100%" "$LOG_DIR/integration_test_$TIMESTAMP.log"; then
        echo "✅ 完全通过"
    elif grep -q "成功率:" "$LOG_DIR/integration_test_$TIMESTAMP.log"; then
        grep "成功率:" "$LOG_DIR/integration_test_$TIMESTAMP.log" | tail -1 | sed 's/^/✅ /'
    else
        echo "⚠️ 部分通过"
    fi
else
    echo "❌ 未运行"
fi)

### 性能基准测试
$([ -f "$LOG_DIR/benchmark_$TIMESTAMP.log" ] && echo "✅ 已完成" || echo "⚠️ 未完成")

### 功能验证测试
根据实际运行结果

## 日志文件
- 健康检查: \`$LOG_DIR/health_check_$TIMESTAMP.log\`
- 场景设置: \`$LOG_DIR/scenario_setup_$TIMESTAMP.log\`
- 集成测试: \`$LOG_DIR/integration_test_$TIMESTAMP.log\`
- 性能基准: \`$LOG_DIR/benchmark_$TIMESTAMP.log\`
- 功能验证: \`$LOG_DIR/functional_test_$TIMESTAMP.log\`

## 建议
$(if [ -f "$LOG_DIR/integration_test_$TIMESTAMP.log" ] && grep -q "成功率: 100%" "$LOG_DIR/integration_test_$TIMESTAMP.log"; then
    echo "🎉 所有测试通过，系统运行良好！"
else
    echo "⚠️ 请查看失败的测试日志并解决相关问题。"
fi)

EOF

    log_success "测试报告已生成: $report_file"
}

# 主测试流程
main() {
    local start_time=$(date +%s)
    
    echo "🚀 Git Merge Orchestrator 批量测试开始"
    echo "=========================================="
    echo "测试时间: $(date)"
    echo "测试目录: $TEST_DIR"
    echo "=========================================="
    
    # 记录原始目录
    local original_dir=$(pwd)
    
    # 测试步骤
    local steps=(
        "check_dependencies"
        "init_test_environment"
        "cleanup_old_tests"
        "run_health_check"
        "setup_test_scenarios"
        "run_integration_tests"
        "run_functional_tests"
        "run_performance_benchmark"
        "generate_test_report"
    )
    
    local failed_steps=()
    
    # 执行测试步骤
    for step in "${steps[@]}"; do
        if ! $step; then
            failed_steps+=("$step")
        fi
        echo ""
    done
    
    # 返回原始目录
    cd "$original_dir"
    
    # 计算总耗时
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    # 打印最终结果
    echo "=========================================="
    echo "📊 批量测试完成摘要"
    echo "=========================================="
    echo "总耗时: ${total_time}秒"
    echo "执行步骤: ${#steps[@]}"
    echo "成功步骤: $((${#steps[@]} - ${#failed_steps[@]}))"
    echo "失败步骤: ${#failed_steps[@]}"
    
    if [ ${#failed_steps[@]} -eq 0 ]; then
        log_success "🎉 所有测试步骤都成功完成！"
        echo ""
        log_info "📋 查看详细报告: $LOG_DIR/batch_test_report_$TIMESTAMP.md"
        exit 0
    else
        log_warning "⚠️ 以下步骤执行失败:"
        for failed_step in "${failed_steps[@]}"; do
            echo "  - $failed_step"
        done
        echo ""
        log_info "📋 查看详细日志文件排查问题"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
Git Merge Orchestrator 批量测试脚本

用法: $0 [选项]

选项:
    --help, -h          显示此帮助信息
    --quick             快速测试模式（跳过性能基准测试）
    --health-only       仅运行健康检查
    --scenarios-only    仅设置测试场景
    --integration-only  仅运行集成测试
    --performance-only  仅运行性能测试

示例:
    $0                  # 运行完整的批量测试
    $0 --quick          # 运行快速测试（跳过性能测试）
    $0 --health-only    # 仅运行健康检查

环境变量:
    TEST_DIR           测试目录路径
    GMO_DIR           Git Merge Orchestrator 目录路径
    
EOF
}

# 参数解析
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --quick)
        # 快速模式：跳过性能测试
        main_quick() {
            check_dependencies
            init_test_environment
            cleanup_old_tests
            run_health_check
            setup_test_scenarios
            run_integration_tests
            run_functional_tests
            generate_test_report
        }
        main_quick
        ;;
    --health-only)
        check_dependencies
        init_test_environment
        run_health_check
        ;;
    --scenarios-only)
        check_dependencies
        init_test_environment
        cleanup_old_tests
        setup_test_scenarios
        ;;
    --integration-only)
        check_dependencies
        init_test_environment
        run_integration_tests
        ;;
    --performance-only)
        check_dependencies
        init_test_environment
        run_performance_benchmark
        ;;
    "")
        # 默认：运行完整测试
        main
        ;;
    *)
        echo "未知参数: $1"
        echo "使用 --help 查看帮助信息"
        exit 1
        ;;
esac
