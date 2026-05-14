#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""估值计算器 - DCF/DDM/相对估值"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Optional

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误: 请先安装依赖: pip install pandas numpy")
    sys.exit(1)


def dcf_valuation(
    free_cash_flow: float,
    growth_rate: float = 0.08,
    discount_rate: float = 0.10,
    terminal_growth: float = 0.03,
    forecast_years: int = 5,
) -> Dict:
    """DCF估值模型"""
    if free_cash_flow <= 0:
        return {"error": "自由现金流为负，DCF模型不适用"}

    pv_fcf = 0
    for year in range(1, forecast_years + 1):
        fcf = free_cash_flow * ((1 + growth_rate) ** year)
        pv = fcf / ((1 + discount_rate) ** year)
        pv_fcf += pv

    terminal_fcf = free_cash_flow * ((1 + growth_rate) ** forecast_years) * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_years)

    intrinsic_value = pv_fcf + pv_terminal

    return {
        "method": "DCF",
        "intrinsic_value": round(intrinsic_value, 2),
        "assumptions": {
            "growth_rate": f"{growth_rate * 100:.1f}%",
            "discount_rate": f"{discount_rate * 100:.1f}%",
            "terminal_growth": f"{terminal_growth * 100:.1f}%",
            "forecast_years": forecast_years,
        },
    }


def ddm_valuation(
    dividend_per_share: float,
    required_return: float = 0.10,
    dividend_growth: float = 0.05,
) -> Dict:
    """DDM股息贴现模型"""
    if dividend_per_share <= 0:
        return {"error": "无股息或股息为0，DDM模型不适用"}

    if required_return <= dividend_growth:
        return {"error": "要求回报率必须大于股息增长率"}

    intrinsic_value = dividend_per_share * (1 + dividend_growth) / (required_return - dividend_growth)

    return {
        "method": "DDM",
        "intrinsic_value": round(intrinsic_value, 2),
        "assumptions": {
            "dividend_per_share": dividend_per_share,
            "required_return": f"{required_return * 100:.1f}%",
            "dividend_growth": f"{dividend_growth * 100:.1f}%",
        },
    }


def relative_valuation(
    pe: float,
    pb: float,
    industry_pe: float,
    industry_pb: float,
    eps: float = 1.0,
    book_value: float = 1.0,
) -> Dict:
    """相对估值法"""
    results = {}

    if pe > 0 and industry_pe > 0:
        pe_value = eps * industry_pe
        results["pe_based"] = {
            "value": round(pe_value, 2),
            "current_pe": pe,
            "industry_pe": industry_pe,
            "undervalued": pe < industry_pe,
        }

    if pb > 0 and industry_pb > 0:
        pb_value = book_value * industry_pb
        results["pb_based"] = {
            "value": round(pb_value, 2),
            "current_pb": pb,
            "industry_pb": industry_pb,
            "undervalued": pb < industry_pb,
        }

    return {
        "method": "相对估值",
        "results": results,
    }


def calculate_margin_of_safety(intrinsic_value: float, current_price: float, margin: float = 0.30) -> Dict:
    """计算安全边际"""
    safe_price = intrinsic_value * (1 - margin)
    upside = (intrinsic_value - current_price) / current_price * 100

    return {
        "intrinsic_value": intrinsic_value,
        "current_price": current_price,
        "safe_price": round(safe_price, 2),
        "margin_of_safety": f"{margin * 100:.0f}%",
        "upside": f"{upside:.1f}%",
        "conclusion": "低估" if current_price < safe_price else "合理" if current_price < intrinsic_value else "高估",
    }


def main():
    parser = argparse.ArgumentParser(description='A股估值计算器')
    parser.add_argument('--input', type=str, help='输入数据文件')
    parser.add_argument('--code', type=str, help='股票代码')
    parser.add_argument('--methods', type=str, default='all',
                        help='估值方法: dcf,ddm,relative,all')
    parser.add_argument('--discount-rate', type=float, default=0.10, help='折现率')
    parser.add_argument('--growth-rate', type=float, default=0.08, help='增长率')
    parser.add_argument('--terminal-growth', type=float, default=0.03, help='永续增长率')
    parser.add_argument('--forecast-years', type=int, default=5, help='预测年数')
    parser.add_argument('--margin-of-safety', type=float, default=0.30, help='安全边际')
    parser.add_argument('--output', type=str, default='valuation_result.json', help='输出文件')

    args = parser.parse_args()

    data = {}
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)

    methods = args.methods.split(',') if args.methods != 'all' else ['dcf', 'ddm', 'relative']

    results = {
        "valuation_date": datetime.now().strftime('%Y-%m-%d'),
        "code": args.code or data.get('basic', {}).get('code', ''),
        "valuations": [],
    }

    fcf = data.get('financial', {}).get('data', [{}])[0].get('自由现金流量', 1000000000)
    dividend = data.get('valuation', {}).get('dv_ratio', 0) * 100
    pe = data.get('valuation', {}).get('pe', 15)
    pb = data.get('valuation', {}).get('pb', 2)

    if 'dcf' in methods:
        dcf_result = dcf_valuation(
            free_cash_flow=fcf / 100000000,
            growth_rate=args.growth_rate,
            discount_rate=args.discount_rate,
            terminal_growth=args.terminal_growth,
            forecast_years=args.forecast_years,
        )
        results['valuations'].append(dcf_result)

    if 'ddm' in methods:
        ddm_result = ddm_valuation(
            dividend_per_share=dividend,
            required_return=args.discount_rate,
            dividend_growth=args.terminal_growth,
        )
        results['valuations'].append(ddm_result)

    if 'relative' in methods:
        relative_result = relative_valuation(
            pe=pe,
            pb=pb,
            industry_pe=pe * 1.1,
            industry_pb=pb * 1.1,
        )
        results['valuations'].append(relative_result)

    valid_values = [v['intrinsic_value'] for v in results['valuations'] if 'intrinsic_value' in v]
    if valid_values:
        results['average_value'] = round(sum(valid_values) / len(valid_values), 2)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("估值结果:")
    for v in results['valuations']:
        if 'intrinsic_value' in v:
            print(f"  {v['method']}: {v['intrinsic_value']}")
    print(f"\n详细结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
