import pandas as pd

def create_subset(file_name: str) -> pd.DataFrame:
    df = pd.read_parquet(
        path=file_name,
        columns=["title", "published_date", "publisher"],
        engine="pyarrow",
    )

    subset_df = df.head(5000)
    subset_df.to_parquet("ccnews_LT_subset.parquet", engine="pyarrow", index=False)
    return subset_df

if __name__ == "__main__":
    create_subset(file_name = "ccnews_LT.parquet")

