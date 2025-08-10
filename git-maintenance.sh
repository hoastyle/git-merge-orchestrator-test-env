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
  status          显示详细的Git状态（包含被忽略文件统计）
  cleanup         清理所有动态生成的文件
  commit-check    检查是否有需要提交的更改
  format-code     格式化Python代码
  create-tag      创建版本标签
  reset-test      重置测试环境（保持Git历史）
  health-check    检查仓库健康状态

  # 被忽略文件管理命令
  ignored-files   分析被忽略文件的详细状态
  cleanup-ignored 安全清理被忽略的临时文件
  ignored-diff    检测被忽略文件的变化

  help            显示此帮助信息

示例:
  $0 status              # 查看详细状态（含被忽略文件）
  $0 cleanup             # 清理环境
  $0 commit-check        # 检查是否有待提交内容
  $0 create-tag v1.1.0   # 创建标签

  # 被忽略文件管理示例
  $0 ignored-files                    # 显示被忽略文件统计
  $0 ignored-files --details          # 显示详细分析
  $0 ignored-files --by-type --by-dir # 按类型和目录分析
  $0 cleanup-ignored --dry-run        # 预览可清理文件
  $0 cleanup-ignored                  # 执行安全清理
  $0 cleanup-ignored --aggressive     # 积极清理模式
  $0 ignored-diff                     # 检查文件变化
  $0 ignored-diff --since=1641038400  # 检查指定时间以来的变化

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
    echo ""

    echo "🙈 被忽略文件统计:"
    # 获取被忽略的文件（简化版，避免过长时间）
    local ignored_files=$(get_ignored_files | head -100)  # 限制前100个以提高速度
    local ignored_count=$(echo "$ignored_files" | grep -c . 2>/dev/null || echo "0")

    if [[ $ignored_count -eq 0 ]]; then
        echo "  被忽略文件: 0"
    else
        echo "  被忽略文件: $ignored_count"

        # 快速分类统计
        local temp_count=$(echo "$ignored_files" | grep -E '\.(tmp|bak|backup|orig)$|temp_' 2>/dev/null | wc -l || echo "0")
        local python_count=$(echo "$ignored_files" | grep -E '\.py[co]$|__pycache__|build/|dist/' 2>/dev/null | wc -l || echo "0")
        local log_count=$(echo "$ignored_files" | grep -E '\.log$|logs/' 2>/dev/null | wc -l || echo "0")
        local test_count=$(echo "$ignored_files" | grep -E 'test-repos/|scenarios/' 2>/dev/null | wc -l || echo "0")

        [[ $temp_count -gt 0 ]] && echo "    临时文件: $temp_count"
        [[ $python_count -gt 0 ]] && echo "    Python相关: $python_count"
        [[ $log_count -gt 0 ]] && echo "    日志文件: $log_count"
        [[ $test_count -gt 0 ]] && echo "    测试产物: $test_count"

        # 检查是否有可清理的文件
        local cleanable=$(echo "$ignored_files" | grep -E '\.(tmp|bak|backup|orig|pyc|pyo|log)$|__pycache__|\.DS_Store|Thumbs\.db' 2>/dev/null | wc -l || echo "0")
        if [[ $cleanable -gt 0 ]]; then
            echo "    💡 可清理: $cleanable (运行 '$0 cleanup-ignored --dry-run' 查看)"
        fi
    fi

    echo ""
    echo "💡 详细分析: '$0 ignored-files --details'"
}

# 清理动态生成的文件
cleanup_files() {
    log_info "清理动态生成的文件..."

    # 使用清理脚本
    if [ -f "test-scripts/cleanup.py" ]; then
        python test-scripts/cleanup.py --all --force
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

# 获取被忽略的文件列表
get_ignored_files() {
    # 获取所有文件（排除 .git 目录）
    local all_files=$(find . -type f -not -path './.git/*' 2>/dev/null | sort)

    # 获取被Git跟踪的文件
    local tracked_files=$(git ls-files | sort)

    # 获取未跟踪但不被忽略的文件
    local untracked_files=$(git ls-files --others --exclude-standard | sort)

    # 通过差集计算被忽略的文件
    # 所有文件 - 跟踪文件 - 未跟踪但不被忽略的文件 = 被忽略的文件
    echo "$all_files" | while read -r file; do
        if [[ -n "$file" ]]; then
            # 检查文件是否被跟踪
            if ! echo "$tracked_files" | grep -Fxq "$file" 2>/dev/null; then
                # 检查文件是否是未跟踪但不被忽略的
                if ! echo "$untracked_files" | grep -Fxq "$file" 2>/dev/null; then
                    echo "$file"
                fi
            fi
        fi
    done
}

# 按类型分类被忽略的文件
classify_ignored_files() {
    local ignored_files="$1"

    # 使用简单变量代替关联数组
    local temp_count=0
    local python_count=0
    local logs_count=0
    local build_count=0
    local ide_count=0
    local system_count=0
    local test_count=0
    local other_count=0

    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            case "$file" in
                # 临时文件
                *.tmp|*.bak|*.backup|*.orig|temp_*)
                    ((temp_count++))
                    ;;
                # Python 相关
                *__pycache__*|*.pyc|*.pyo|*.egg-info*|build/|dist/)
                    ((python_count++))
                    ;;
                # 日志文件
                *.log|logs/*|debug.*|trace.*)
                    ((logs_count++))
                    ;;
                # 构建产物
                *.so|*.dll|*.dylib)
                    ((build_count++))
                    ;;
                # IDE 文件
                .vscode/*|.idea/*|*.swp|*.swo)
                    ((ide_count++))
                    ;;
                # 系统文件
                .DS_Store|Thumbs.db|*.lnk)
                    ((system_count++))
                    ;;
                # 测试相关
                test-repos/*|scenarios/*|benchmark_*)
                    ((test_count++))
                    ;;
                *)
                    ((other_count++))
                    ;;
            esac
        fi
    done <<< "$ignored_files"

    # 输出分类统计
    echo "📁 按类型分类:"
    printf "   临时文件: %d\n" "$temp_count"
    printf "   Python相关: %d\n" "$python_count"
    printf "   日志文件: %d\n" "$logs_count"
    printf "   构建产物: %d\n" "$build_count"
    printf "   IDE文件: %d\n" "$ide_count"
    printf "   系统文件: %d\n" "$system_count"
    printf "   测试产物: %d\n" "$test_count"
    printf "   其他: %d\n" "$other_count"
}

# 显示被忽略文件的详细信息
show_ignored_files() {
    local show_details=false
    local by_type=false
    local by_dir=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --details)
                show_details=true
                shift
                ;;
            --by-type)
                by_type=true
                shift
                ;;
            --by-dir)
                by_dir=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    log_info "分析被忽略文件状态..."
    echo "========================="

    # 获取被忽略的文件
    local ignored_files=$(get_ignored_files)
    local count=$(echo "$ignored_files" | grep -c . 2>/dev/null || echo "0")

    echo "🔍 被忽略文件总数: $count"
    echo ""

    if [[ $count -eq 0 ]]; then
        log_success "没有被忽略的文件"
        return
    fi

    # 按类型分类显示
    if [[ "$by_type" == true ]] || [[ "$show_details" == true ]]; then
        classify_ignored_files "$ignored_files"
        echo ""
    fi

    # 按目录分布显示
    if [[ "$by_dir" == true ]] || [[ "$show_details" == true ]]; then
        echo "📂 按目录分布:"
        echo "$ignored_files" | sed 's|/[^/]*$||' | sort | uniq -c | sort -nr | head -10 | while read count dir; do
            if [[ "$dir" == "." ]]; then
                dir="根目录"
            fi
            printf "   %-20s: %d\n" "$dir" "$count"
        done
        echo ""
    fi

    # 显示详细文件列表
    if [[ "$show_details" == true ]]; then
        echo "📋 详细文件列表（前20个）:"
        echo "$ignored_files" | head -20 | sed 's/^/   - /'

        if [[ $count -gt 20 ]]; then
            echo "   ... 还有 $((count - 20)) 个文件"
        fi
        echo ""
    fi

    # 检测可清理的文件
    local cleanable=$(echo "$ignored_files" | grep -E '\.(tmp|bak|backup|orig|pyc|pyo|log)$|__pycache__|\.DS_Store|Thumbs\.db' | wc -l)
    if [[ $cleanable -gt 0 ]]; then
        log_warning "发现 $cleanable 个可安全清理的文件"
        log_info "使用 '$0 cleanup-ignored --dry-run' 查看可清理文件列表"
    fi
}

# 清理被忽略的文件
cleanup_ignored_files() {
    local dry_run=false
    local aggressive=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --aggressive)
                aggressive=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ "$dry_run" == true ]]; then
        log_info "预览模式：显示将要清理的文件..."
    else
        log_info "清理被忽略的临时文件..."
    fi
    echo "====================================="

    # 获取被忽略的文件
    local ignored_files=$(get_ignored_files)
    local count=$(echo "$ignored_files" | grep -c . 2>/dev/null || echo "0")

    if [[ $count -eq 0 ]]; then
        log_success "没有被忽略的文件需要清理"
        return
    fi

    # 定义安全清理的文件类型
    local safe_patterns
    if [[ "$aggressive" == true ]]; then
        safe_patterns='\.(tmp|bak|backup|orig|pyc|pyo|log|swp|swo)$|__pycache__|\.DS_Store|Thumbs\.db|test-repos/.*|logs/.*\.log|logs/.*\.json'
    else
        safe_patterns='\.(tmp|bak|backup|orig|pyc|pyo|log)$|__pycache__|\.DS_Store|Thumbs\.db'
    fi

    # 筛选可安全清理的文件
    local cleanable_files=$(echo "$ignored_files" | grep -E "$safe_patterns")
    local cleanable_count=$(echo "$cleanable_files" | grep -c . 2>/dev/null || echo "0")

    if [[ $cleanable_count -eq 0 ]]; then
        log_info "没有找到可安全清理的文件"
        log_warning "总共有 $count 个被忽略的文件，但都不在安全清理范围内"
        return
    fi

    echo "🧹 可清理文件 ($cleanable_count/$count):"
    echo ""

    # 按类型显示将要清理的文件
    local temp_files=$(echo "$cleanable_files" | grep -E '\.(tmp|bak|backup|orig)$' | wc -l)
    local python_files=$(echo "$cleanable_files" | grep -E '\.py[co]$|__pycache__' | wc -l)
    local log_files=$(echo "$cleanable_files" | grep -E '\.log$' | wc -l)
    local system_files=$(echo "$cleanable_files" | grep -E '\.DS_Store|Thumbs\.db' | wc -l)
    local test_files=$(echo "$cleanable_files" | grep -E 'test-repos/.*|logs/.*' | wc -l)

    [[ $temp_files -gt 0 ]] && echo "   临时文件: $temp_files"
    [[ $python_files -gt 0 ]] && echo "   Python字节码: $python_files"
    [[ $log_files -gt 0 ]] && echo "   日志文件: $log_files"
    [[ $system_files -gt 0 ]] && echo "   系统文件: $system_files"
    [[ $test_files -gt 0 ]] && echo "   测试产物: $test_files"
    echo ""

    if [[ "$dry_run" == true ]]; then
        echo "📋 将要清理的文件列表（前15个）:"
        echo "$cleanable_files" | head -15 | sed 's/^/   - /'

        if [[ $cleanable_count -gt 15 ]]; then
            echo "   ... 还有 $((cleanable_count - 15)) 个文件"
        fi
        echo ""
        log_info "使用 '$0 cleanup-ignored' 执行实际清理"
        return
    fi

    # 执行清理
    local cleaned=0
    local errors=0

    echo "🚀 开始清理..."
    while IFS= read -r file; do
        if [[ -n "$file" && -f "$file" ]]; then
            if rm -f "$file" 2>/dev/null; then
                ((cleaned++))
            else
                ((errors++))
                log_error "清理失败: $file"
            fi
        elif [[ -n "$file" && -d "$file" ]]; then
            # 清理目录（如 __pycache__）
            if rm -rf "$file" 2>/dev/null; then
                ((cleaned++))
            else
                ((errors++))
                log_error "清理失败: $file"
            fi
        fi
    done <<< "$cleanable_files"

    echo ""
    log_success "清理完成: $cleaned 个文件/目录"

    if [[ $errors -gt 0 ]]; then
        log_warning "$errors 个文件/目录清理失败"
    fi

    # 显示清理后的统计
    local remaining_ignored=$(get_ignored_files | wc -l)
    log_info "清理后还有 $remaining_ignored 个被忽略的文件"
}

# 比较被忽略文件的变化
compare_ignored_files() {
    local since_timestamp=""
    local timestamp_file=".ignored_files_timestamp"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --since=*)
                since_timestamp="${1#*=}"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    log_info "检测被忽略文件的变化..."
    echo "==========================="

    # 获取当前被忽略的文件
    local current_ignored=$(get_ignored_files)
    local current_count=$(echo "$current_ignored" | grep -c . 2>/dev/null || echo "0")
    local current_timestamp=$(date +%s)

    echo "🕒 当前时间: $(date)"
    echo "🔍 当前被忽略文件总数: $current_count"
    echo ""

    # 如果指定了时间戳
    if [[ -n "$since_timestamp" ]]; then
        log_info "检查自 $since_timestamp 以来的变化..."

        # 查找自指定时间以来修改的被忽略文件
        local recent_files=$(echo "$current_ignored" | while read -r file; do
            if [[ -n "$file" && -f "$file" ]]; then
                local file_mtime=$(stat -c %Y "$file" 2>/dev/null || echo "0")
                if [[ $file_mtime -gt $since_timestamp ]]; then
                    echo "$file"
                fi
            fi
        done)

        local recent_count=$(echo "$recent_files" | grep -c . 2>/dev/null || echo "0")

        if [[ $recent_count -gt 0 ]]; then
            log_warning "发现 $recent_count 个新的或更新的被忽略文件:"
            echo "$recent_files" | head -10 | sed 's/^/   - /'

            if [[ $recent_count -gt 10 ]]; then
                echo "   ... 还有 $((recent_count - 10)) 个文件"
            fi
        else
            log_success "自指定时间以来没有新的被忽略文件"
        fi

        return
    fi

    # 检查是否有历史记录
    if [[ ! -f "$timestamp_file" ]]; then
        log_info "首次运行，记录当前状态..."
        echo "$current_timestamp:$current_count" > "$timestamp_file"
        echo "$current_ignored" > "${timestamp_file}.files"
        log_success "状态已记录，下次运行时将显示变化"
        return
    fi

    # 读取历史记录
    local last_record=$(head -1 "$timestamp_file")
    local last_timestamp=$(echo "$last_record" | cut -d: -f1)
    local last_count=$(echo "$last_record" | cut -d: -f2)
    local last_ignored=""

    if [[ -f "${timestamp_file}.files" ]]; then
        last_ignored=$(cat "${timestamp_file}.files")
    fi

    echo "📊 变化统计:"
    echo "   上次检查: $(date -d @$last_timestamp)"
    echo "   上次文件数: $last_count"
    echo "   当前文件数: $current_count"
    echo "   变化: $((current_count - last_count))"
    echo ""

    # 查找新增的文件
    local new_files=""
    if [[ -n "$current_ignored" ]]; then
        new_files=$(comm -23 <(echo "$current_ignored" | sort) <(echo "$last_ignored" | sort) 2>/dev/null)
    fi
    local new_count=$(echo "$new_files" | grep -c . 2>/dev/null || echo "0")

    # 查找删除的文件
    local removed_files=""
    if [[ -n "$last_ignored" ]]; then
        removed_files=$(comm -13 <(echo "$current_ignored" | sort) <(echo "$last_ignored" | sort) 2>/dev/null)
    fi
    local removed_count=$(echo "$removed_files" | grep -c . 2>/dev/null || echo "0")

    if [[ $new_count -gt 0 ]]; then
        log_warning "新增 $new_count 个被忽略文件:"
        echo "$new_files" | head -10 | sed 's/^/   + /'

        if [[ $new_count -gt 10 ]]; then
            echo "   ... 还有 $((new_count - 10)) 个文件"
        fi
        echo ""
    fi

    if [[ $removed_count -gt 0 ]]; then
        log_success "清理了 $removed_count 个被忽略文件:"
        echo "$removed_files" | head -10 | sed 's/^/   - /'

        if [[ $removed_count -gt 10 ]]; then
            echo "   ... 还有 $((removed_count - 10)) 个文件"
        fi
        echo ""
    fi

    if [[ $new_count -eq 0 && $removed_count -eq 0 ]]; then
        log_success "被忽略文件没有变化"
    fi

    # 更新记录
    echo "$current_timestamp:$current_count" > "$timestamp_file"
    echo "$current_ignored" > "${timestamp_file}.files"
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
        "ignored-files")
            shift
            show_ignored_files "$@"
            ;;
        "cleanup-ignored")
            shift
            cleanup_ignored_files "$@"
            ;;
        "ignored-diff")
            shift
            compare_ignored_files "$@"
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