#!/usr/bin/env python3
"""
DevLog 工作量统计脚本

功能:
1. 从Git历史提取代码提交统计
2. 计算工作时长和任务完成率
3. 生成统计数据JSON文件
4. 支持日报、周报、月报统计

使用方法:
    python stats.py --date 2026-04-30
    python stats.py --week
    python stats.py --month 2026-04
"""

import os
import sys
import re
import json
import calendar
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


def run_git_command(args):
    """执行Git命令并返回输出(跨平台安全)"""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        print(f"Git命令执行失败: git {' '.join(args)}\n错误: {e}", file=sys.stderr)
        return ""


def is_git_repo():
    """检查是否在Git仓库中"""
    output = run_git_command(['rev-parse', '--is-inside-work-tree'])
    return output.strip().lower() == 'true'


def get_git_stats(date_str=None):
    """获取Git提交统计信息"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    if not is_git_repo():
        return None

    log_output = run_git_command([
        'log', '--oneline',
        '--since', f'{date_str} 00:00',
        '--until', f'{date_str} 23:59'
    ])

    commit_count = 0
    if log_output:
        commit_count = len([l for l in log_output.split('\n') if l.strip()])

    log_stat_output = run_git_command([
        'log', '--pretty=format:', '--stat',
        '--since', f'{date_str} 00:00',
        '--until', f'{date_str} 23:59'
    ])

    insertions = 0
    deletions = 0
    files_changed = 0

    for line in log_stat_output.split('\n'):
        line = line.strip()
        if 'file' in line and 'changed' in line:
            ins_match = re.search(r'(\d+) insertion', line)
            del_match = re.search(r'(\d+) deletion', line)
            fc_match = re.search(r'(\d+) file', line)
            if ins_match:
                insertions += int(ins_match.group(1))
            if del_match:
                deletions += int(del_match.group(1))
            if fc_match:
                files_changed += int(fc_match.group(1))

    return {
        'commit_count': commit_count,
        'insertions': insertions,
        'deletions': deletions,
        'files_changed': files_changed
    }


def calculate_work_hours(time_ranges):
    """计算工作时长

    Args:
        time_ranges: 时间段列表,如 ["09:00-12:00", "13:30-18:00"]

    Returns:
        总时长(小时)
    """
    total_minutes = 0

    for time_range in time_ranges:
        if '-' not in time_range:
            continue

        start_str, end_str = time_range.split('-', 1)

        try:
            start = datetime.strptime(start_str.strip(), '%H:%M')
            end = datetime.strptime(end_str.strip(), '%H:%M')

            diff = (end - start).total_seconds() / 60
            if diff < 0:
                diff += 24 * 60
            total_minutes += diff
        except ValueError:
            continue

    return round(total_minutes / 60, 2)


def parse_log_file(log_path):
    """解析日志文件,提取关键信息"""
    if not os.path.exists(log_path):
        return None

    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()

    info = {
        'tasks_completed': 0,
        'tasks_in_progress': 0,
        'issues_count': 0,
        'issues_resolved': 0,
        'time_ranges': [],
        'work_hours': 0
    }

    info['tasks_completed'] = content.count('- [x]')
    info['tasks_in_progress'] = content.count('- [ ]')

    if '## 🐛 遇到的问题' in content:
        issues_section = content.split('## 🐛 遇到的问题')[1].split('##')[0]
        info['issues_count'] = issues_section.count('### 问题')
        info['issues_resolved'] = issues_section.count('✅ 已解决')

    time_patterns = re.findall(r'(\d{2}:\d{2})-(\d{2}:\d{2}):', content)
    info['time_ranges'] = [f"{start}-{end}" for start, end in time_patterns]

    if info['time_ranges']:
        info['work_hours'] = calculate_work_hours(info['time_ranges'])

    return info


def generate_daily_stats(date_str=None, devlog_dir='.devlog'):
    """生成单日统计"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    stats = {
        'date': date_str,
        'generated_at': datetime.now().isoformat()
    }

    log_path = os.path.join(devlog_dir, date_str, 'log.md')
    log_info = parse_log_file(log_path)

    if log_info:
        stats.update(log_info)

    git_stats = get_git_stats(date_str)
    if git_stats:
        stats['git'] = git_stats

    if stats.get('work_hours', 0) == 0:
        if git_stats and git_stats['commit_count'] > 0:
            stats['work_hours'] = git_stats['commit_count'] * 1.0

    return stats


def _accumulate_summary(stats, daily_stats):
    """累加汇总数据"""
    if daily_stats.get('work_hours', 0) > 0:
        stats['summary']['total_work_hours'] += daily_stats['work_hours']
        stats['summary']['working_days'] += 1

    stats['summary']['total_tasks'] += daily_stats.get('tasks_completed', 0)

    if 'git' in daily_stats:
        stats['summary']['total_commits'] += daily_stats['git'].get('commit_count', 0)
        stats['summary']['total_insertions'] += daily_stats['git'].get('insertions', 0)
        stats['summary']['total_deletions'] += daily_stats['git'].get('deletions', 0)


def _finalize_summary(stats):
    """计算汇总平均值"""
    if stats['summary']['working_days'] > 0:
        stats['summary']['avg_work_hours'] = round(
            stats['summary']['total_work_hours'] / stats['summary']['working_days'],
            2
        )


def generate_weekly_stats(week_start=None, devlog_dir='.devlog'):
    """生成周统计"""
    if not week_start:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

    stats = {
        'period': f"Week of {week_start.strftime('%Y-%m-%d')}",
        'generated_at': datetime.now().isoformat(),
        'daily_stats': [],
        'summary': {
            'total_work_hours': 0,
            'total_tasks': 0,
            'total_commits': 0,
            'total_insertions': 0,
            'total_deletions': 0,
            'working_days': 0
        }
    }

    for i in range(7):
        date = week_start + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        daily_stats = generate_daily_stats(date_str, devlog_dir)
        stats['daily_stats'].append(daily_stats)
        _accumulate_summary(stats, daily_stats)

    _finalize_summary(stats)
    return stats


def generate_monthly_stats(year_month=None, devlog_dir='.devlog'):
    """生成月统计"""
    if not year_month:
        year_month = datetime.now().strftime('%Y-%m')

    stats = {
        'period': year_month,
        'generated_at': datetime.now().isoformat(),
        'daily_stats': [],
        'summary': {
            'total_work_hours': 0,
            'total_tasks': 0,
            'total_commits': 0,
            'total_insertions': 0,
            'total_deletions': 0,
            'working_days': 0
        }
    }

    year, month = map(int, year_month.split('-'))
    _, num_days = calendar.monthrange(year, month)

    for day in range(1, num_days + 1):
        date_str = f"{year_month}-{day:02d}"
        log_dir = os.path.join(devlog_dir, date_str)

        if os.path.exists(log_dir):
            daily_stats = generate_daily_stats(date_str, devlog_dir)
            stats['daily_stats'].append(daily_stats)
            _accumulate_summary(stats, daily_stats)

    _finalize_summary(stats)
    return stats


def save_stats(stats, output_path):
    """保存统计数据到JSON文件"""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"统计数据已保存到: {output_path}")


def format_stats_report(stats):
    """格式化统计报告"""
    lines = []

    if 'date' in stats:
        lines.append(f"# 工作统计 - {stats['date']}")
        lines.append("")
        lines.append(f"- 工作时长: {stats.get('work_hours', 0)}小时")
        lines.append(f"- 完成任务: {stats.get('tasks_completed', 0)}个")
        lines.append(f"- 进行中任务: {stats.get('tasks_in_progress', 0)}个")
        lines.append(f"- 遇到问题: {stats.get('issues_count', 0)}个")
        lines.append(f"- 已解决问题: {stats.get('issues_resolved', 0)}个")

        if 'git' in stats:
            git = stats['git']
            lines.append(f"- 代码提交: {git.get('commit_count', 0)}次")
            lines.append(f"- 代码行数: +{git.get('insertions', 0)}/-{git.get('deletions', 0)}")

    elif 'period' in stats:
        if 'Week' in stats['period']:
            lines.append(f"# 周工作统计 - {stats['period']}")
        else:
            lines.append(f"# 月工作统计 - {stats['period']}")
        lines.append("")
        summary = stats['summary']
        lines.append(f"- 总工作时长: {summary['total_work_hours']}小时")
        lines.append(f"- 工作天数: {summary['working_days']}天")
        lines.append(f"- 平均每日: {summary.get('avg_work_hours', 0)}小时")
        lines.append(f"- 完成任务: {summary['total_tasks']}个")
        lines.append(f"- 代码提交: {summary['total_commits']}次")
        lines.append(f"- 代码行数: +{summary['total_insertions']}/-{summary['total_deletions']}")

    return '\n'.join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='DevLog 工作量统计工具')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--week', action='store_true', help='生成本周统计')
    parser.add_argument('--month', type=str, help='指定月份 (YYYY-MM)')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--devlog-dir', type=str, default='.devlog', help='日志目录')
    parser.add_argument('--report', action='store_true', help='输出文本报告')

    args = parser.parse_args()

    if args.date:
        stats = generate_daily_stats(args.date, args.devlog_dir)
        default_output = os.path.join(args.devlog_dir, args.date, 'stats.json')
    elif args.week:
        stats = generate_weekly_stats(devlog_dir=args.devlog_dir)
        today = datetime.now().strftime('%Y-%m-%d')
        default_output = os.path.join(args.devlog_dir, f'weekly-{today}.json')
    elif args.month:
        stats = generate_monthly_stats(args.month, args.devlog_dir)
        default_output = os.path.join(args.devlog_dir, f'monthly-{args.month}.json')
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        stats = generate_daily_stats(today, args.devlog_dir)
        default_output = os.path.join(args.devlog_dir, today, 'stats.json')

    output_path = args.output or default_output

    save_stats(stats, output_path)

    if args.report:
        report = format_stats_report(stats)
        print("\n" + report)


if __name__ == '__main__':
    main()
