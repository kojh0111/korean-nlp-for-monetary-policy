import numpy as np
import pandas as pd


def create_call_rate_change_df(csv_file_path="data/call_rate.csv"):
    # CSV 파일 읽기 및 데이터 준비
    df = pd.read_csv(csv_file_path)
    df_prepared = prepare_data(df)

    # 변화 계산
    result_df = calculate_changes(df_prepared)

    # 빈 날짜 제거
    result_df = result_df[result_df["change"] != "N/A"]

    return result_df


def prepare_data(df):
    # 데이터 재구성 및 정렬
    df_melted = df.melt(var_name="date", value_name="call_rate")
    df_melted["date"] = pd.to_datetime(df_melted["date"])
    df_sorted = df_melted.sort_values("date").set_index("date")

    # 모든 날짜 생성 (시작일부터 종료일까지 1일 간격)
    all_dates = pd.date_range(
        start=df_sorted.index.min(), end=df_sorted.index.max(), freq="D"
    )

    # 모든 날짜를 포함하는 새로운 DataFrame 생성 및 Forward Fill
    df_filled = df_sorted.reindex(all_dates).ffill()

    return df_filled


def calculate_changes(df):
    THRESHOLD = 0.03  # 3bp threshold

    # 한 달 전 call rate 계산
    df["past_rate"] = df["call_rate"].shift(30)  # 약 한 달(30일) 전의 값

    # 변화량 계산
    df["rate_difference"] = df["call_rate"] - df["past_rate"]

    # 변화 판단
    conditions = [
        (df["rate_difference"].abs() < THRESHOLD),
        (df["rate_difference"] >= THRESHOLD),
        (df["rate_difference"] <= -THRESHOLD),
    ]
    choices = ["neutral", "hawkish", "dovish"]
    df["change"] = np.select(conditions, choices, default="N/A")

    # 불필요한 열 제거
    df = df.drop(["past_rate", "rate_difference"], axis=1)

    return df
