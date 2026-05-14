#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据获取器 - 获取A股股票财务数据"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("错误: 请先安装依赖: pip install akshare pandas")
    sys.exit(1)


def get_basic_info(code: str) -> dict:
    """获取股票基本信息"""
    try:
        df = ak.stock_individual_info_em(symbol=code)
        info = dict(zip(df['item'], df['value']))
        return {
            "code": code,
            "name": info.get('股票简称', ''),
            "industry": info.get('行业', ''),
            "list_date": info.get('上市时间', ''),
            "total_share": info.get('总市值', ''),
            "circulating_share": info.get('流通市值', ''),
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def get_financial_data(code: str, years: int = 5) -> dict:
    """获取财务数据"""
    try:
        df = ak.stock_financial_analysis_indicator(symbol=code)
        df = df.head(years * 4)
        return {
            "code": code,
            "data": df.to_dict(orient='records'),
            "columns": list(df.columns),
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def get_valuation_data(code: str) -> dict:
    """获取估值数据"""
    try:
        df = ak.stock_a_lg_indicator(symbol=code)
        latest = df.iloc[-1].to_dict() if len(df) > 0 else {}
        return {
            "code": code,
            "pe": latest.get('pe', None),
            "pe_ttm": latest.get('pe_ttm', None),
            "pb": latest.get('pb', None),
            "ps": latest.get('ps', None),
            "dv_ratio": latest.get('dv_ratio', None),
            "total_mv": latest.get('total_mv', None),
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def get_holder_data(code: str) -> dict:
    """获取股东数据"""
    try:
        df = ak.stock_gdfx_holding_analyze(symbol=code)
        return {
            "code": code,
            "holders": df.to_dict(orient='records')[:10],
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description='A股股票数据获取器')
    parser.add_argument('--code', type=str, help='股票代码')
    parser.add_argument('--codes', type=str, help='多个股票代码,逗号分隔')
    parser.add_argument('--data-type', type=str, default='all',
                        choices=['basic', 'financial', 'valuation', 'holder', 'all', 'comparison'],
                        help='数据类型')
    parser.add_argument('--years', type=int, default=5, help='获取历史数据年数')
    parser.add_argument('--industry', type=str, help='行业名称')
    parser.add_argument('--top', type=int, default=10, help='行业前N只股票')
    parser.add_argument('--output', type=str, default='stock_data.json', help='输出文件')

    args = parser.parse_args()

    result = {
        "fetch_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data_type": args.data_type,
    }

    codes = []
    if args.code:
        codes = [args.code]
    elif args.codes:
        codes = [c.strip() for c in args.codes.split(',')]

    if args.data_type == 'all' and codes:
        code = codes[0]
        result['basic'] = get_basic_info(code)
        result['financial'] = get_financial_data(code, args.years)
        result['valuation'] = get_valuation_data(code)
        result['holder'] = get_holder_data(code)

    elif args.data_type == 'basic':
        result['stocks'] = [get_basic_info(c) for c in codes]

    elif args.data_type == 'financial':
        result['stocks'] = [get_financial_data(c, args.years) for c in codes]

    elif args.data_type == 'valuation':
        result['stocks'] = [get_valuation_data(c) for c in codes]

    elif args.data_type == 'comparison':
        result['stocks'] = []
        for code in codes:
            stock_data = {
                "basic": get_basic_info(code),
                "valuation": get_valuation_data(code),
            }
            result['stocks'].append(stock_data)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到 {args.output}")
    return result


if __name__ == '__main__':
    main()
