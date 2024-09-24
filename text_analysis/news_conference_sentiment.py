import json
from time import sleep

import anthropic
import pandas as pd


statements = pd.read_csv("data/news_conference.csv")
statements = statements["sentence"].tolist()


client = anthropic.Anthropic(
    api_key=""
)


def analyze_statements_batch(statements, batch_size=10):
    system_message = (
        system_message
    ) = """You are an AI assistant trained to analyze monetary policy statements based on the methodology described in the paper "Deciphering Monetary Policy Board Minutes through Text Mining Approach: The Case of Korea". Classify each statement as 'hawkish', 'dovish', or 'neutral'. 

- Hawkish statements often indicate economic growth, inflationary pressures, or the need for tighter monetary policy.
- Dovish statements often indicate economic slowdown, deflationary pressures, or the need for looser monetary policy.
- Neutral statements do not clearly lean towards hawkish or dovish interpretations.

Respond in JSON format with statement numbers as keys and classifications as values, without explanations."""

    all_results = {}

    for i in range(0, len(statements), batch_size):
        batch = statements[i : i + batch_size]
        user_message = "Classify the following statements as 'hawkish', 'dovish', or 'neutral':\n\n"
        for j, statement in enumerate(batch, 1):
            user_message += f"{i + j}. {statement}\n"

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=500,
                temperature=0,
                system=system_message,
                messages=[{"role": "user", "content": user_message}],
            )
            print(response.content)
            batch_results = json.loads(response.content[0].text)

            # Adjusting keys to maintain overall numbering
            adjusted_results = {str(int(k)): v for k, v in batch_results.items()}
            print(f"{adjusted_results=}")
            all_results.update(adjusted_results)

        except Exception as e:
            print(f"An error occurred with batch starting at index {i}: {str(e)}")

        # Adding a small delay to avoid rate limiting
        sleep(1)

    return all_results


# 예시 문장들 (실제로는 1300개의 문장이 있어야 합니다)
statements = statements

results = analyze_statements_batch(statements)


df = pd.read_csv("data/news_conference.csv")

# 'sentence' 컬럼의 인덱스를 기반으로 sentiment 값 매핑
df["sentiment"] = df.index.map(lambda x: results.get(str(x + 1), ""))

# 결과를 새 CSV 파일로 저장
df.to_csv("data/news_conference_sentiment.csv", index=False)
