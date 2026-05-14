#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""股票筛选器 - 按条件筛选A股股票"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Optional

try:
    import akshare as ak
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误: 请先安装依赖: pip install akshare pandas numpy")
    sys.exit(1)


SCOPE_MAP = {
    'all': None,
    'hs300': '000300',
    'zz500': '000905',
    'cyb': 'cyb',
    'kcb': 'kcb',
}


def get_stock_list(scope: str, custom_codes: Optional[str] = None) -> List[str]:
    """获取股票列表"""
    if custom_codes:
        return [c.strip() for c in custom_codes.split(',')]

    if scope == 'all':
        df = ak.stock_zh_a_spot_em()
        return df['代码'].tolist()[:100]
    elif scope in ['hs300', 'zz500']:
        df = ak.index_stock_cons_weight_csindex(symbol=SCOPE_MAP[scope])
        return df['成分券代码'].tolist()
    elif scope == 'cyb':
        df = ak.stock_board_concept_name_em()
        return df[df['板块名称'].str.contains('创业板')]['代码'].tolist()[:50]
    elif scope == 'kcb':
        df = ak.stock_board_concept_name_em()
        return df[df['板块名称'].str.contains('科创板')]['代码'].tolist()[:50]

    return []


def get_stock_metrics(code: str) -> dict:
    """获取单只股票的关键指标"""
    try:
        df = ak.stock_a_lg_indicator(symbol=code)
        if len(df) == 0:
            return None

        latest = df.iloc[-1]
        return {
            "code": code,
            "pe": float(latest.get('pe', 0) or 0),
            "pe_ttm": float(latest.get('pe_ttm', 0) or 0),
            "pb": float(latest.get('pb', 0) or 0),
            "ps": float(latest.get('ps', 0) or 0),
            "dv_ratio": float(latest.get('dv_ratio', 0) or 0),
            "total_mv": float(latest.get('total_mv', 0) or 0),
        }
    except Exception:
        return None


def get_financial_indicator(code: str) -> dict:
    """获取财务指标"""
    try:
        df = ak.stock_financial_analysis_indicator(symbol=code)
        if len(df) == 0:
            return None

        latest = df.iloc[0]
        return {
            "code": code,
            "roe": float(latest.get('净资产收益率(%)', 0) or 0),
            "roa": float(latest.get('总资产净利润ROA(%)', 0) or 0),
            "gross_margin": float(latest.get('销售毛利率(%)', 0) or 0),
            "net_margin": float(latest.get('销售净利率(%)', 0) or 0),
            "debt_ratio": float(latest.get('资产负债率(%)', 0) or 0),
            "current_ratio": float(latest.get('流动比率', 0) or 0),
            "quick_ratio": float(latest.get('速动比率', 0) or 0),
        }
    except Exception:
        return None


def calculate_score(stock: dict, financial: dict, criteria: dict) -> int:
    """计算综合评分"""
    score = 50

    if financial:
        if financial.get('roe', 0) >= criteria.get('roe_min', 15):
            score += 10
        if financial.get('debt_ratio', 100) <= criteria.get('debt_ratio_max', 60):
            score += 10
        if financial.get('gross_margin', 0) >= 30:
            score += 5

    if stock:
        if 0 < stock.get('pe', 999) <= criteria.get('pe_max', 20):
            score += 10
        if 0 < stock.get('pb', 999) <= criteria.get('pb_max', 3):
            score += 5
        if stock.get('dv_ratio', 0) >= criteria.get('dividend_min', 2):
            score += 10

    return min(score, 100)


def screen_stocks(codes: List[str], criteria: dict) -> List[dict]:
    """筛选股票"""
    results = []

    for code in codes:
        stock = get_stock_metrics(code)
        financial = get_financial_indicator(code)

        if not stock or not financial:
            continue

        if criteria.get('pe_max') and stock['pe'] > 0 and stock['pe'] > criteria['pe_max']:
            continue
        if criteria.get('pb_max') and stock['pb'] > 0 and stock['pb'] > criteria['pb_max']:
            continue
        if criteria.get('roe_min') and financial['roe'] < criteria['roe_min']:
            continue
        if criteria.get('debt_ratio_max') and financial['debt_ratio'] > criteria['debt_ratio_max']:
            continue
        if criteria.get('dividend_min') and stock['dv_ratio'] < criteria['dividend_min']:
            continue

        score = calculate_score(stock, financial, criteria)

        results.append({
            "code": code,
            "pe": stock['pe'],
            "pb": stock['pb'],
            "roe": round(financial['roe'], 2),
            "dividend_yield": round(stock['dv_ratio'], 2),
            "debt_ratio": round(financial['debt_ratio'], 2),
            "score": score,
        })

    return sorted(results, key=lambda x: x['score'], reverse=True)


def main():
    parser = argparse.ArgumentParser(description='A股股票筛选器')
    parser.add_argument('--scope', type=str, default='hs300',
                        choices=['all', 'hs300', 'zz500', 'cyb', 'kcb', 'custom'],
                        help='筛选范围')
    parser.add_argument('--custom-codes', type=str, help='自定义股票代码列表')
    parser.add_argument('--pe-max', type=float, help='最大市盈率')
    parser.add_argument('--pe-min', type=float, help='最小市盈率')
    parser.add_argument('--pb-max', type=float, help='最大市净率')
    parser.add_argument('--pb-min', type=float, help='最小市净率')
    parser.add_argument('--roe-min', type=float, help='最小ROE(%)')
    parser.add_argument('--debt-ratio-max', type=float, help='最大资产负债率(%)')
    parser.add_argument('--dividend-min', type=float, help='最小股息率(%)')
    parser.add_argument('--output', type=str, default='screening_result.json', help='输出文件')

    args = parser.parse_args()

    criteria = {
        'pe_max': args.pe_max,
        'pe_min': args.pe_min,
        'pb_max': args.pb_max,
        'pb_min': args.pb_min,
        'roe_min': args.roe_min,
        'debt_ratio_max': args.debt_ratio_max,
        'dividend_min': args.dividend_min,
    }

    criteria = {k: v for k, v in criteria.items() if v is not None}

    print(f"正在获取股票列表...")
    codes = get_stock_list(args.scope, args.custom_codes)
    print(f"共 {len(codes)} 只股票待筛选...")

    results = screen_stocks(codes, criteria)

    output = {
        "screening_date": datetime.now().strftime('%Y-%m-%d'),
        "criteria": criteria,
        "total_screened": len(codes),
        "total_matched": len(results),
        "results": results[:50],
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"筛选完成，共 {len(results)} 只股票符合条件")
    print(f"结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
