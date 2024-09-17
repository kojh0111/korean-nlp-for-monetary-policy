def calculate_polarity_score(row):
    """
    Calculate the polarity score of the sentence.
    """
    if row["상승 카운트"] == row["하락 카운트"]:
        return 0
    elif row["상승 카운트"] > row["하락 카운트"]:
        return row["상승 카운트"] / max(row["하락 카운트"], 1)
    else:
        return -(row["하락 카운트"] / max(row["상승 카운트"], 1))


def determine_polarity(row):
    """
    Determine the polarity of the sentence based on the polarity score.
    """
    if abs(row["polarity_score"]) >= 1.3:
        if row["상승 카운트"] > row["하락 카운트"]:
            return "positive"
        elif row["하락 카운트"] > row["상승 카운트"]:
            return "negative"
    return "neutral"


if __name__ == "__main__":
    from tqdm import tqdm
    import pandas as pd

    # 데이터 로드
    ngram_count_df = pd.read_csv("data/ngram_count_df.csv")

    # polarity score 계산
    tqdm.pandas(desc="Calculating polarity score")
    ngram_count_df["polarity_score"] = ngram_count_df.progress_apply(
        calculate_polarity_score, axis=1
    )

    # 극성 판단
    tqdm.pandas(desc="Determining polarity")
    ngram_count_df["polarity"] = ngram_count_df.progress_apply(
        determine_polarity, axis=1
    )

    # 결과 확인
    print(ngram_count_df[["ngram", "polarity_score", "polarity"]].head(10))

    # 극성별 개수 확인
    print(ngram_count_df["polarity"].value_counts())
