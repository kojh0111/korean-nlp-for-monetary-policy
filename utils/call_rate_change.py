import pandas as pd


def create_call_rate_change_df(csv_file_path="data/call_rate.csv"):
    # CSV 파일 읽기 및 데이터 준비
    df = pd.read_csv(csv_file_path)
    df_melted = prepare_data(df)

    # 결과 DataFrame 초기화
    result_df = df_melted.copy()
    result_df["change"] = ""

    # 변화 계산
    calculate_monthly_changes(result_df)

    return result_df


def prepare_data(df):
    # 데이터 재구성 및 정렬
    df_melted = df.melt(var_name="date", value_name="call_rate")
    df_melted["date"] = pd.to_datetime(df_melted["date"])
    return df_melted.sort_values("date").set_index("date")


def calculate_monthly_changes(df):
    for date in df.index:
        one_month_ago = date - pd.DateOffset(months=1)

        if one_month_ago in df.index:
            past_rate = df.loc[one_month_ago, "call_rate"]
        else:
            # 한 달 전 데이터가 없으면 가장 가까운 이전 데이터 사용
            past_date = df.index[df.index < date].max()
            if pd.isnull(past_date):
                df.loc[date, "change"] = "N/A"
                continue
            past_rate = df.loc[past_date, "call_rate"]

        current_rate = df.loc[date, "call_rate"]

        if current_rate > past_rate:
            df.loc[date, "change"] = "상승"
        elif current_rate < past_rate:
            df.loc[date, "change"] = "하락"
        else:
            df.loc[date, "change"] = "중립"
