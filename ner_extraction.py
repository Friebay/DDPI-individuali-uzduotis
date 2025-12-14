import time
from typing import List
import pandas as pd
import pyarrow.parquet as pq
import spacy

nlp = spacy.load("lt_core_news_sm")


def extract_organizations(texts: List[str]) -> List[str]:
    found_orgs = []

    for doc in nlp.pipe(texts, disable=["parser", "tagger"]):
        for ent in doc.ents:
            if ent.label_ == "ORG":
                found_orgs.append(ent.text)

    return found_orgs


def process_file_stream(file_name: str, batch_size: int) -> pd.Series:
    parquet_file = pq.ParquetFile(file_name)

    all_orgs = []
    total_rows = 0

    print(f"Failas: {file_name}, rinkinio dydis: {batch_size}.")

    for batch in parquet_file.iter_batches(batch_size=batch_size, columns=["title"]):

        df_chunk = batch.to_pandas()
        titles = df_chunk["title"].dropna().tolist()

        orgs = extract_organizations(titles)

        all_orgs.extend(orgs)
        total_rows += len(titles)

        if total_rows % batch_size == 0:
            print(f"Apdorota {total_rows} eilučių.")

    org_series = pd.Series(all_orgs)
    return org_series.value_counts()


if __name__ == "__main__":
    FILE_NAME = "ccnews_LT_subset.parquet"

    start_time = time.time()

    org_counts = process_file_stream(FILE_NAME, batch_size=500)

    end_time = time.time()

    print(f"\nApdorota per {end_time - start_time:.2f} sek.")
    print()
    print("Dažniau paminėtos organizacijos:")
    for org, count in org_counts.head(10).items():
        print(f"{org}: {count}")
