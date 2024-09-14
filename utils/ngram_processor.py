from collections import Counter


def _generate_ngrams(text, n):
    words = text.split()
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def _process_ngrams_to_dict(sentences):
    ngram_counts = {
        i: Counter() for i in range(1, 6)
    }  # 1-gram부터 5-gram까지의 Counter 객체

    for sentence in sentences:
        for n in range(1, 6):
            ngrams = _generate_ngrams(sentence, n)
            ngram_counts[n].update(ngrams)

    return ngram_counts


def _update_ngram_dict(row, sentences_column, ngram_column, total_counts):
    new_ngrams = _process_ngrams_to_dict(row[sentences_column])

    # 기존 딕셔너리가 없으면 새로 생성
    if not isinstance(row[ngram_column], dict):
        row[ngram_column] = {}

    # 각 n에 대해 기존 딕셔너리 업데이트 및 total_counts 업데이트
    for n, gram_counter in new_ngrams.items():
        n_gram = f"{n}-gram"
        if n_gram not in row[ngram_column]:
            row[ngram_column][n_gram] = {}
        for gram, count in gram_counter.items():
            row[ngram_column][n_gram][gram] = (
                row[ngram_column][n_gram].get(gram, 0) + count
            )
            total_counts[n_gram][gram] += count

    return row


def process_dataframe(df, sentences_column, ngram_column):
    total_counts = {f"{i}-gram": Counter() for i in range(1, 6)}
    df = df.apply(
        lambda row: _update_ngram_dict(
            row, sentences_column, ngram_column, total_counts
        ),
        axis=1,
    )
    return df, total_counts


def analyze_low_count_ngrams(total_counts, threshold=15):
    low_count_analysis = {}
    for n, counter in total_counts.items():
        low_count_ngrams = {
            gram: count for gram, count in counter.items() if count < threshold
        }
        low_count_analysis[n] = {
            "count": len(low_count_ngrams),
            "examples": list(low_count_ngrams.items())[:10],  # 예시로 10개만 보여줍니다
        }
    return low_count_analysis


def analyze_high_count_ngrams(total_counts, threshold=15):
    high_count_analysis = {}
    high_count_dict = {}

    for n, counter in total_counts.items():
        high_count_ngrams = {
            gram: count for gram, count in counter.items() if count >= threshold
        }
        high_count_analysis[n] = {
            "count": len(high_count_ngrams),
            "examples": list(high_count_ngrams.items())[:5],  # 예시로 5개만 보여줍니다
        }
        high_count_dict[n] = high_count_ngrams

    return high_count_analysis, high_count_dict
