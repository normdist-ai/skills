#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行业对比器 - 同行业横向对比分析"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误: 请先安装依赖: pip install pandas numpy")
    sys.exit(1)


def calculate_industry_average(stocks: List[dict]) -> dict:
    """计算行业平均值"""
    if not stocks:
        return {}

    metrics = ['pe', 'pb', 'roe', 'gross_margin', 'net_margin', 'debt_ratio', 'dividend_yield']
    avg = {}

    for metric in metrics:
        values = [s.get(metric, 0) for s in stocks if s.get(metric, 0) > 0]
        if values:
            avg[metric] = round(sum(values) / len(values), 2)

    return avg


def compare_stocks(stocks: List[dict], industry_avg: dict) -> List[dict]:
    """对比股票与行业均值"""
    results = []

    for stock in stocks:
        comparison = {
            "code": stock.get('code', ''),
            "name": stock.get('name', ''),
            "metrics": {},
        }

        for metric in ['pe', 'pb', 'roe', 'gross_margin', 'dividend_yield']:
            stock_val = stock.get(metric, 0)
            avg_val = industry_avg.get(metric, 0)

            if stock_val > 0 and avg_val > 0:
                if metric in ['pe', 'pb', 'debt_ratio']:
                    status = "低于均值" if stock_val < avg_val else "高于均值"
                else:
                    status = "高于均值" if stock_val > avg_val else "低于均值"

                comparison["metrics"][metric] = {
                    "value": stock_val,
                    "industry_avg": avg_val,
                    "status": status,
                }

        score = calculate_comparison_score(stock, industry_avg)
        comparison["score"] = score
        results.append(comparison)

    return sorted(results, key=lambda x: x['score'], reverse=True)


def calculate_comparison_score(stock: dict, industry_avg: dict) -> int:
    """计算对比评分"""
    score = 50

    pe = stock.get('pe', 0)
    avg_pe = industry_avg.get('pe', 0)
    if pe > 0 and avg_pe > 0:
        if pe < avg_pe * 0.8:
            score += 10
        elif pe < avg_pe:
            score += 5

    roe = stock.get('roe', 0)
    avg_roe = industry_avg.get('roe', 0)
    if roe > 0 and avg_roe > 0:
        if roe > avg_roe * 1.2:
            score += 15
        elif roe > avg_roe:
            score += 10

    debt = stock.get('debt_ratio', 100)
    avg_debt = industry_avg.get('debt_ratio', 0)
    if debt > 0 and avg_debt > 0:
        if debt < avg_debt * 0.8:
            score += 10
        elif debt < avg_debt:
            score += 5

    return min(score, 100)


def generate_comparison_table(stocks: List[dict], industry_avg: dict) -> str:
    """生成对比表格"""
    lines = []
    lines.append("| 指标 | " + " | ".join([s.get('name', s.get('code', '')) for s in stocks]) + " | 行业均值 |")
    lines.append("|" + "|".join(["---"] * (len(stocks) + 2)) + "|")

    metrics = [
        ('pe', 'PE'),
        ('pb', 'PB'),
        ('roe', 'ROE(%)'),
        ('gross_margin', '毛利率(%)'),
        ('dividend_yield', '股息率(%)'),
    ]

    for metric_key, metric_name in metrics:
        row = [metric_name]
        for stock in stocks:
            val = stock.get(metric_key, '-')
            row.append(f"{val:.2f}" if isinstance(val, (int, float)) else str(val))
        row.append(f"{industry_avg.get(metric_key, '-'):.2f}" if industry_avg.get(metric_key) else '-')
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='A股行业对比器')
    parser.add_argument('--input', type=str, required=True, help='输入数据文件')
    parser.add_argument('--output', type=str, default='comparison_result.json', help='输出文件')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stocks = data.get('stocks', [])

    stock_list = []
    for s in stocks:
        basic = s.get('basic', {})
        valuation = s.get('valuation', {})
        stock_list.append({
            "code": basic.get('code', ''),
            "name": basic.get('name', ''),
            "pe": valuation.get('pe', 0),
            "pb": valuation.get('pb', 0),
            "roe": valuation.get('roe', 0),
            "gross_margin": valuation.get('gross_margin', 0),
            "dividend_yield": valuation.get('dv_ratio', 0),
            "debt_ratio": valuation.get('debt_ratio', 0),
        })

    industry_avg = calculate_industry_average(stock_list)
    comparison = compare_stocks(stock_list, industry_avg)
    table = generate_comparison_table(stock_list, industry_avg)

    result = {
        "comparison_date": datetime.now().strftime('%Y-%m-%d'),
        "industry_average": industry_avg,
        "comparison": comparison,
        "table": table,
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("行业对比结果:")
    print(table)
    print(f"\n详细结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
