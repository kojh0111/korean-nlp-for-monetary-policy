import pandas as pd
from tqdm import tqdm


def analyze_ngrams_and_create_dataframe(df, call_rate_df, high_count_dict):

    all_ngrams = set()
    for n_grams in high_count_dict.values():
        all_ngrams.update(n_grams.keys())

    ngram_count_dict = {
        ngram: {"상승 카운트": 0, "하락 카운트": 0, "중립 카운트": 0}
        for ngram in all_ngrams
    }

    call_rate_dict = call_rate_df["change"].to_dict()

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        date = pd.to_datetime(row["date"])
        change = call_rate_dict.get(date, "중립")
        row_sentences = (
            row["sentences"] if isinstance(row["sentences"], dict) else dict()
        )

        for n_gram, ngrams in row_sentences.items():
            for ngram in ngrams:
                if ngram in all_ngrams:
                    if change == "상승":
                        ngram_count_dict[ngram]["상승 카운트"] += 1
                    elif change == "하락":
                        ngram_count_dict[ngram]["하락 카운트"] += 1
                    else:
                        ngram_count_dict[ngram]["중립 카운트"] += 1

    ngram_count_df = pd.DataFrame.from_dict(ngram_count_dict, orient="index")
    ngram_count_df.reset_index(inplace=True)
    ngram_count_df.columns = ["ngram", "상승 카운트", "하락 카운트", "중립 카운트"]

    return ngram_count_df
