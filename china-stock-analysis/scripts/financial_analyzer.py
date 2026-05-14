#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""财务分析器 - 个股深度财务分析"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误: 请先安装依赖: pip install pandas numpy")
    sys.exit(1)


def analyze_profitability(financial_data: List[dict]) -> dict:
    """分析盈利能力"""
    if not financial_data:
        return {"error": "无财务数据"}

    df = pd.DataFrame(financial_data)
    result = {
        "roe_trend": [],
        "gross_margin_trend": [],
        "net_margin_trend": [],
        "conclusion": "",
    }

    roe_col = None
    for col in df.columns:
        if '净资产收益率' in col or 'ROE' in col.upper():
            roe_col = col
            break

    if roe_col:
        result['roe_trend'] = df[roe_col].head(8).tolist()
        avg_roe = df[roe_col].head(8).mean()
        result['avg_roe'] = round(avg_roe, 2)
        result['conclusion'] = "优秀" if avg_roe > 15 else "良好" if avg_roe > 10 else "一般"

    return result


def analyze_growth(financial_data: List[dict]) -> dict:
    """分析成长性"""
    if not financial_data:
        return {"error": "无财务数据"}

    df = pd.DataFrame(financial_data)
    result = {
        "revenue_growth": [],
        "profit_growth": [],
        "conclusion": "",
    }

    revenue_col = None
    profit_col = None

    for col in df.columns:
        if '营业收入' in col and '增长' in col:
            revenue_col = col
        if '净利润' in col and '增长' in col:
            profit_col = col

    if revenue_col:
        result['revenue_growth'] = df[revenue_col].head(8).tolist()
    if profit_col:
        result['profit_growth'] = df[profit_col].head(8).tolist()

    if result['revenue_growth'] and result['profit_growth']:
        avg_rev = pd.Series(result['revenue_growth']).mean()
        avg_prof = pd.Series(result['profit_growth']).mean()
        if avg_rev > 15 and avg_prof > 15:
            result['conclusion'] = "高成长"
        elif avg_rev > 10 or avg_prof > 10:
            result['conclusion'] = "稳健增长"
        else:
            result['conclusion'] = "增长放缓"

    return result


def analyze_safety(financial_data: List[dict]) -> dict:
    """分析财务安全"""
    if not financial_data:
        return {"error": "无财务数据"}

    df = pd.DataFrame(financial_data)
    result = {
        "debt_ratio": [],
        "current_ratio": [],
        "conclusion": "",
    }

    debt_col = None
    current_col = None

    for col in df.columns:
        if '资产负债率' in col:
            debt_col = col
        if '流动比率' in col:
            current_col = col

    if debt_col:
        result['debt_ratio'] = df[debt_col].head(8).tolist()
        avg_debt = df[debt_col].head(8).mean()
        result['avg_debt_ratio'] = round(avg_debt, 2)

    if current_col:
        result['current_ratio'] = df[current_col].head(8).tolist()
        avg_current = df[current_col].head(8).mean()
        result['avg_current_ratio'] = round(avg_current, 2)

    if 'avg_debt_ratio' in result:
        if result['avg_debt_ratio'] < 40:
            result['conclusion'] = "财务稳健"
        elif result['avg_debt_ratio'] < 60:
            result['conclusion'] = "财务安全"
        else:
            result['conclusion'] = "负债较高，需关注"

    return result


def detect_anomalies(financial_data: List[dict], stock_data: dict) -> List[dict]:
    """检测财务异常"""
    anomalies = []

    if not financial_data or len(financial_data) < 4:
        return anomalies

    df = pd.DataFrame(financial_data)

    revenue_col = None
    receivable_col = None
    inventory_col = None

    for col in df.columns:
        if '营业收入' in col and '增长' in col:
            revenue_col = col
        if '应收账款' in col and '增长' in col:
            receivable_col = col
        if '存货' in col and '增长' in col:
            inventory_col = col

    if revenue_col and receivable_col:
        rev_growth = df[revenue_col].head(4).mean()
        rec_growth = df[receivable_col].head(4).mean()
        if rec_growth > rev_growth * 1.5 and rec_growth > 20:
            anomalies.append({
                "type": "应收账款异常",
                "severity": "中",
                "detail": f"应收账款增速({rec_growth:.1f}%)远超营收增速({rev_growth:.1f}%)",
            })

    if revenue_col and inventory_col:
        rev_growth = df[revenue_col].head(4).mean()
        inv_growth = df[inventory_col].head(4).mean()
        if inv_growth > rev_growth * 2 and inv_growth > 30:
            anomalies.append({
                "type": "存货异常",
                "severity": "中",
                "detail": f"存货增速({inv_growth:.1f}%)远超营收增速({rev_growth:.1f}%)",
            })

    return anomalies


def calculate_overall_score(profitability: dict, growth: dict, safety: dict) -> int:
    """计算综合评分"""
    score = 50

    if profitability.get('avg_roe', 0) > 20:
        score += 15
    elif profitability.get('avg_roe', 0) > 15:
        score += 10
    elif profitability.get('avg_roe', 0) > 10:
        score += 5

    if growth.get('conclusion') == "高成长":
        score += 15
    elif growth.get('conclusion') == "稳健增长":
        score += 10

    if safety.get('avg_debt_ratio', 100) < 40:
        score += 10
    elif safety.get('avg_debt_ratio', 100) < 60:
        score += 5

    return min(score, 100)


def main():
    parser = argparse.ArgumentParser(description='A股财务分析器')
    parser.add_argument('--input', type=str, required=True, help='输入数据文件')
    parser.add_argument('--level', type=str, default='standard',
                        choices=['summary', 'standard', 'deep'],
                        help='分析深度')
    parser.add_argument('--output', type=str, default='analysis_result.json', help='输出文件')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    financial_data = data.get('financial', {}).get('data', [])
    stock_data = data.get('valuation', {})

    profitability = analyze_profitability(financial_data)
    growth = analyze_growth(financial_data)
    safety = analyze_safety(financial_data)
    anomalies = detect_anomalies(financial_data, stock_data)

    score = calculate_overall_score(profitability, growth, safety)

    result = {
        "analysis_date": datetime.now().strftime('%Y-%m-%d'),
        "level": args.level,
        "profitability": profitability,
        "growth": growth,
        "safety": safety,
        "anomalies": anomalies,
        "summary": {
            "score": score,
            "conclusion": "优秀" if score >= 80 else "良好" if score >= 60 else "一般",
        },
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"分析完成，综合评分: {score}")
    print(f"结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
