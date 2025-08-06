#!/bin/bash

# Git Merge Orchestrator 测试环境 - Git维护脚本
# 提供常见的Git管理操作

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 显示帮助
show_help() {
    cat << EOF
Git Merge Orchestrator 测试环境 - Git维护脚本

用法: $0 [命令]

可用命令:
  status          显示详细的Git状态
  cleanup         清理所有动态生成的文件
  commit-check    检查是否有需要提交的更改
  format-code     格式化Python代码
  create-tag      创建版本标签
  reset-test      重置测试环境（保持Git历史）
  health-check    检查仓库健康状态
  help            显示此帮助信息

示例:
  $0 status              # 查看详细状态
  $0 cleanup             # 清理环境
  $0 commit-check        # 检查是否有待提交内容
  $0 create-tag v1.1.0   # 创建标签

EOF
}

# 显示详细状态
show_status() {
    log_info "Git仓库状态检查"
    echo "===================="
    
    echo "🌿 分支信息:"
    git branch -v
    echo ""
    
    echo "🏷️ 最近标签:"
    git tag -l | tail -5 || echo "  (暂无标签)"
    echo ""
    
    echo "📝 最近提交:"
    git log --oneline -5
    echo ""
    
    echo "📊 工作目录状态:"
    git status --porcelain
    if [ $? -eq 0 ] && [ -z "$(git status --porcelain)" ]; then
        log_success "工作目录干净"
    else
        log_warning "工作目录有未提交的更改"
    fi
    echo ""
    
    echo "📁 版本管理的文件统计:"
    echo "  总文件数: $(git ls-files | wc -l)"
    echo "  脚本文件: $(git ls-files | grep -E '\.(py|sh)$' | wc -l)"
    echo "  配置文件: $(git ls-files | grep -E 'configurations/' | wc -l)"
    echo "  示例文件: $(git ls-files | grep -E 'sample-files/' | wc -l)"
}

# 清理动态生成的文件
cleanup_files() {
    log_info "清理动态生成的文件..."
    
    # 使用清理脚本
    if [ -f "test-scripts/cleanup.py" ]; then
        python test-scripts/cleanup.py --all --quiet
        log_success "测试环境已清理"
    fi
    
    # 清理可能的临时文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.log" -path "./logs/*" -delete 2>/dev/null || true
    find . -name "*.json" -path "./scenarios/*" -delete 2>/dev/null || true
    
    # 检查Git状态
    if [ -z "$(git status --porcelain)" ]; then
        log_success "清理完成，工作目录干净"
    else
        log_warning "清理后仍有未跟踪的文件"
        git status --short
    fi
}

# 检查是否有需要提交的更改
check_commits() {
    log_info "检查是否有待提交的更改..."
    
    # 检查暂存区
    if ! git diff --cached --quiet; then
        log_warning "暂存区有待提交的更改:"
        git diff --cached --name-only | sed 's/^/  - /'
        echo ""
    fi
    
    # 检查工作目录
    if ! git diff --quiet; then
        log_warning "工作目录有未暂存的更改:"
        git diff --name-only | sed 's/^/  - /'
        echo ""
    fi
    
    # 检查未跟踪文件
    untracked=$(git ls-files --others --exclude-standard)
    if [ -n "$untracked" ]; then
        log_warning "有未跟踪的文件:"
        echo "$untracked" | sed 's/^/  - /'
        echo ""
        
        # 检查是否是应该被版本管理的文件
        should_track=""
        for file in $untracked; do
            case "$file" in
                *.py|*.sh|*.md|test-data/configurations/*|test-data/sample-files/*)
                    should_track="$should_track\n  - $file"
                    ;;
            esac
        done
        
        if [ -n "$should_track" ]; then
            log_warning "以下文件可能需要添加到版本管理:"
            echo -e "$should_track"
        fi
    fi
    
    if git diff --quiet && git diff --cached --quiet && [ -z "$untracked" ]; then
        log_success "没有待提交的更改，工作目录干净"
    fi
}

# 格式化代码
format_code() {
    log_info "格式化Python代码..."
    
    if ! command -v black >/dev/null 2>&1; then
        log_warning "black 未安装，跳过代码格式化"
        log_info "安装建议: pip install black"
        return
    fi
    
    # 格式化Python文件
    python_files=$(find test-scripts -name "*.py" -type f)
    if [ -n "$python_files" ]; then
        black $python_files
        log_success "Python代码格式化完成"
        
        # 检查是否有更改
        if ! git diff --quiet; then
            log_info "格式化产生了更改，建议提交:"
            git diff --name-only | sed 's/^/  - /'
        fi
    else
        log_info "未找到需要格式化的Python文件"
    fi
}

# 创建标签
create_tag() {
    local tag_name=$1
    
    if [ -z "$tag_name" ]; then
        log_error "请提供标签名称"
        echo "用法: $0 create-tag <tag_name>"
        echo "示例: $0 create-tag v1.1.0"
        return 1
    fi
    
    # 检查工作目录是否干净
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_error "工作目录不干净，请先提交更改"
        return 1
    fi
    
    log_info "创建标签: $tag_name"
    
    # 获取当前日期
    local current_date=$(date +%Y-%m-%d)
    
    # 创建带注释的标签
    git tag -a "$tag_name" -m "Git Merge Orchestrator 测试环境 $tag_name

发布日期: $current_date

$(git log --oneline $(git describe --tags --abbrev=0 2>/dev/null)..HEAD 2>/dev/null | head -10 || git log --oneline -5)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    log_success "标签 $tag_name 创建完成"
    log_info "查看标签详情: git show $tag_name"
}

# 重置测试环境
reset_test_env() {
    log_info "重置测试环境（保持Git历史）..."
    
    # 清理动态文件
    cleanup_files
    
    # 重置到最新提交
    git reset --hard HEAD
    
    # 清理未跟踪文件（保留应该被忽略的）
    git clean -fd -e logs -e scenarios -e test-repos
    
    log_success "测试环境已重置"
    log_info "如需重新设置测试场景，运行: python test-scripts/setup_scenarios.py --scenario all"
}

# 健康检查
health_check() {
    log_info "Git仓库健康检查..."
    
    local issues=0
    
    # 检查Git配置
    if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
        log_error "Git用户配置缺失"
        echo "  解决方案: git config user.name 'Your Name'"
        echo "            git config user.email 'your.email@example.com'"
        ((issues++))
    else
        log_success "Git用户配置正常"
    fi
    
    # 检查文件权限
    if [ ! -x "batch_test.sh" ]; then
        log_warning "batch_test.sh 不可执行"
        chmod +x batch_test.sh
        log_info "已修复执行权限"
    fi
    
    # 检查重要目录
    for dir in logs scenarios test-repos test-scripts test-data; do
        if [ ! -d "$dir" ]; then
            log_error "缺少重要目录: $dir"
            ((issues++))
        fi
    done
    
    # 检查核心脚本
    core_scripts=("test-scripts/setup_scenarios.py" "test-scripts/integration_tests.py" "test-scripts/cleanup.py")
    for script in "${core_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            log_error "缺少核心脚本: $script"
            ((issues++))
        elif [ ! -x "$script" ]; then
            log_warning "$script 不可执行"
            chmod +x "$script"
            log_info "已修复 $script 执行权限"
        fi
    done
    
    # 检查忽略规则
    if [ ! -f ".gitignore" ]; then
        log_error "缺少 .gitignore 文件"
        ((issues++))
    fi
    
    if [ $issues -eq 0 ]; then
        log_success "仓库健康检查通过"
    else
        log_warning "发现 $issues 个问题，请检查上述输出"
    fi
}

# 主函数
main() {
    case "${1:-help}" in
        "status")
            show_status
            ;;
        "cleanup")
            cleanup_files
            ;;
        "commit-check")
            check_commits
            ;;
        "format-code")
            format_code
            ;;
        "create-tag")
            create_tag "$2"
            ;;
        "reset-test")
            reset_test_env
            ;;
        "health-check")
            health_check
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 确保在正确的目录中
if [ ! -f ".gitignore" ] || [ ! -d "test-scripts" ]; then
    log_error "请在Git Merge Orchestrator测试目录中运行此脚本"
    exit 1
fi

main "$@"