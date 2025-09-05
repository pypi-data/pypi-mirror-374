import pandas as pd
import requests
import json
from datetime import datetime

def get_a_info_em(symbol: str) -> tuple:
    """
    从东方财富网获取指定股票的财务数据，并拆分为基本数据和对比数据两个表格
    
    参数:
    symbol -- 股票代码，格式如"600028.SH"
    
    返回:
    tuple -- (基本数据DataFrame, 对比数据DataFrame)
    """
    # 构建请求URL
    base_url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    params = {
        "reportName": "RPT_PCF10_FINANCEMAINFINADATA",
        "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,REPORT_DATE,REPORT_TYPE,EPSJB,EPSKCJB,EPSXS,BPS,MGZBGJ,MGWFPLR,MGJYXJJE,TOTAL_OPERATEINCOME,TOTAL_OPERATEINCOME_LAST,PARENT_NETPROFIT,PARENT_NETPROFIT_LAST,KCFJCXSYJLR,KCFJCXSYJLR_LAST,ROEJQ,ROEJQ_LAST,XSMLL,XSMLL_LAST,ZCFZL,ZCFZL_LAST,YYZSRGDHBZC_LAST,YYZSRGDHBZC,NETPROFITRPHBZC,NETPROFITRPHBZC_LAST,KFJLRGDHBZC,KFJLRGDHBZC_LAST,TOTALOPERATEREVETZ,TOTALOPERATEREVETZ_LAST,PARENTNETPROFITTZ,PARENTNETPROFITTZ_LAST,KCFJCXSYJLRTZ,KCFJCXSYJLRTZ_LAST,TOTAL_SHARE,FREE_SHARE,EPSJB_PL,BPS_PL",
        "quoteColumns": "",
        "filter": f"(SECUCODE=\"{symbol}\")",
        "sortTypes": "-1",
        "sortColumns": "REPORT_DATE",
        "pageNumber": "1",
        "pageSize": "1",
        "source": "HSF10",
        "client": "PC",
        "v": str(int(datetime.now().timestamp() * 1000))  # 使用当前时间戳作为随机参数
    }
    
    # 设置请求头
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
        "Connection": "keep-alive",
        "Origin": "https://emweb.securities.eastmoney.com",
        "Referer": "https://emweb.securities.eastmoney.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    try:
        # 发送GET请求
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析JSON数据
        data = response.json()
        
        # 检查API返回是否成功
        if not data.get("success", False):
            print(f"API请求失败: {data.get('message', '未知错误')}")
            return pd.DataFrame(), pd.DataFrame()
        
        # 检查是否有数据
        if not data["result"].get("data"):
            print(f"未找到股票 {symbol} 的财务数据")
            return pd.DataFrame(), pd.DataFrame()
        
        # 提取数据记录
        record = data["result"]["data"][0]
        
        # 创建基本数据表格
        base_data = {
            '股票代码': record['SECUCODE'],
            '证券代码': record['SECURITY_CODE'],
            '证券简称': record['SECURITY_NAME_ABBR'],
            '报告日期': record['REPORT_DATE'].split()[0],
            '报告类型': record['REPORT_TYPE'],
            '基本每股收益(元)': f"{record['EPSJB']:.3f}",
            '扣非每股收益(元)': f"{record['EPSKCJB']:.3f}",
            '稀释每股收益(元)': f"{record['EPSXS']:.3f}",
            '每股净资产(元)': f"{record['BPS']:.3f}",
            '每股资本公积金(元)': f"{record['MGZBGJ']:.3f}",
            '每股未分配利润(元)': f"{record['MGWFPLR']:.3f}",
            '每股经营现金流(元)': f"{record['MGJYXJJE']:.3f}",
            '营业总收入(元)': f"{record['TOTAL_OPERATEINCOME']:,}",
            '净利润(元)': f"{record['PARENT_NETPROFIT']:,}",
            '扣非净利润(元)': f"{record['KCFJCXSYJLR']:,}",
            '净资产收益率(%)': f"{record['ROEJQ']:.2f}%",
            '销售毛利率(%)': f"{record['XSMLL']:.2f}%",
            '资产负债率(%)': f"{record['ZCFZL']:.2f}%",
            '总股本(股)': f"{record['TOTAL_SHARE']:,}",
            '流通股本(股)': f"{record['FREE_SHARE']:,}"
        }
        
        # 创建对比数据表格
        comparison_data = {
            '指标': [
                '营业总收入', '净利润', '扣非净利润', 
                '净资产收益率', '销售毛利率', '资产负债率',
                '营业收入同比增长率', '净利润同比增长率', '扣非净利润同比增长率',
                '营业总收入环比增长率', '净利润环比增长率', '扣非净利润环比增长率'
            ],
            '本期值': [
                f"{record['TOTAL_OPERATEINCOME']:,}",
                f"{record['PARENT_NETPROFIT']:,}",
                f"{record['KCFJCXSYJLR']:,}",
                f"{record['ROEJQ']:.2f}%",
                f"{record['XSMLL']:.2f}%",
                f"{record['ZCFZL']:.2f}%",
                f"{record['YYZSRGDHBZC']:.2f}%",
                f"{record['NETPROFITRPHBZC']:.2f}%",
                f"{record['KFJLRGDHBZC']:.2f}%",
                f"{record['TOTALOPERATEREVETZ']:.2f}%",
                f"{record['PARENTNETPROFITTZ']:.2f}%",
                f"{record['KCFJCXSYJLRTZ']:.2f}%"
            ],
            '上期值': [
                f"{record['TOTAL_OPERATEINCOME_LAST']:,}",
                f"{record['PARENT_NETPROFIT_LAST']:,}",
                f"{record['KCFJCXSYJLR_LAST']:,}",
                f"{record['ROEJQ_LAST']:.2f}%",
                f"{record['XSMLL_LAST']:.2f}%",
                f"{record['ZCFZL_LAST']:.2f}%",
                f"{record['YYZSRGDHBZC_LAST']:.2f}%",
                f"{record['NETPROFITRPHBZC_LAST']:.2f}%",
                f"{record['KFJLRGDHBZC_LAST']:.2f}%",
                f"{record['TOTALOPERATEREVETZ_LAST']:.2f}%",
                f"{record['PARENTNETPROFITTZ_LAST']:.2f}%",
                f"{record['KCFJCXSYJLRTZ_LAST']:.2f}%"
            ],
            '变化率': [
                f"{(record['TOTAL_OPERATEINCOME'] - record['TOTAL_OPERATEINCOME_LAST']) / record['TOTAL_OPERATEINCOME_LAST'] * 100 if record['TOTAL_OPERATEINCOME_LAST'] != 0 else 0:.2f}%",
                f"{(record['PARENT_NETPROFIT'] - record['PARENT_NETPROFIT_LAST']) / record['PARENT_NETPROFIT_LAST'] * 100 if record['PARENT_NETPROFIT_LAST'] != 0 else 0:.2f}%",
                f"{(record['KCFJCXSYJLR'] - record['KCFJCXSYJLR_LAST']) / record['KCFJCXSYJLR_LAST'] * 100 if record['KCFJCXSYJLR_LAST'] != 0 else 0:.2f}%",
                f"{(record['ROEJQ'] - record['ROEJQ_LAST']):.2f}%",
                f"{(record['XSMLL'] - record['XSMLL_LAST']):.2f}%",
                f"{(record['ZCFZL'] - record['ZCFZL_LAST']):.2f}%",
                f"{(record['YYZSRGDHBZC'] - record['YYZSRGDHBZC_LAST']):.2f}%",
                f"{(record['NETPROFITRPHBZC'] - record['NETPROFITRPHBZC_LAST']):.2f}%",
                f"{(record['KFJLRGDHBZC'] - record['KFJLRGDHBZC_LAST']):.2f}%",
                f"{(record['TOTALOPERATEREVETZ'] - record['TOTALOPERATEREVETZ_LAST']):.2f}%",
                f"{(record['PARENTNETPROFITTZ'] - record['PARENTNETPROFITTZ_LAST']):.2f}%",
                f"{(record['KCFJCXSYJLRTZ'] - record['KCFJCXSYJLRTZ_LAST']):.2f}%"
            ]
        }
        
        # 创建DataFrame
        df_base = pd.DataFrame([base_data]).T
        df_comparison = pd.DataFrame(comparison_data)
        df_base.index.name = "指标"
        df_base.rename(columns={0: "数值"}, inplace=True)
        
        return df_base, df_comparison
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return pd.DataFrame(), pd.DataFrame()
    except json.JSONDecodeError:
        print("响应解析失败")
        return pd.DataFrame(), pd.DataFrame()
    except KeyError as e:
        print(f"数据解析错误: {e}")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        print(f"发生未知错误: {e}")
        return pd.DataFrame(), pd.DataFrame()

# 使用示例
if __name__ == "__main__":
    # 获取中国石化的财务数据
    df_base, df_comparison = get_a_info_em("600028.SH")
    
    if not df_base.empty:
        # 打印基本数据
        print("基本财务数据:")
        print(df_base)
        
        # 打印对比数据
        print("\n财务数据对比:")
        print(df_comparison)
        
        # 保存到Excel文件
        with pd.ExcelWriter(f"{df_base['证券简称'][0]}.xlsx") as writer:
            df_base.to_excel(writer, sheet_name="基本数据", index=False)
            df_comparison.to_excel(writer, sheet_name="对比数据", index=False)
        print(f"数据已保存到 {df_base['证券简称'][0]}.xlsx")
    else:
        print("未能获取数据")