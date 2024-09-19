from collections import Counter

from ekonlpy.tag import Mecab
from nltk import ngrams
from tqdm import tqdm


def _extract_nouns_from_sentences(sentences):
    mecab = Mecab()
    processed_sentences = []
    target_pos = ["NNG", "NNP", "VA", "VAX", "VV", "VCN"]
    stopwords = [
        "층",
        "늘",
        "년",
        "후",
        "장",
        "축",
        "더",
        "반",
        "면",
        "리라",
        "n",
        "우",
        "마산",
        "가",
        "를",
        "을",
        "점",
        "관",
        "월",
        "일",
        "텔",
        "남",
        "좌",
        "리",
        "중",
        "정",
        "미",
        "종",
    ]

    for sentence in sentences:
        tokens = mecab.pos(sentence)
        tokens = mecab.replace_synonyms(tokens)
        tokens = mecab.lemmatize(tokens)

        filtered_tokens = [
            word
            for word, pos, *_ in tokens
            if (pos in target_pos) and (word not in stopwords)
        ]
        processed_sentences.append(filtered_tokens)

    return processed_sentences


def _generate_ngrams(tokens, n):
    return list(ngrams(tokens, n))


def _process_ngrams_to_dict(sentences):
    ngram_counts = {i: Counter() for i in range(1, 6)}
    processed_sentences = _extract_nouns_from_sentences(sentences)

    for tokens in processed_sentences:
        for n in range(1, 6):
            ngrams_list = _generate_ngrams(tokens, n)
            ngram_counts[n].update(" ".join(gram) for gram in ngrams_list)

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

    tqdm.pandas(desc="Processing rows")
    df = df.progress_apply(
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
