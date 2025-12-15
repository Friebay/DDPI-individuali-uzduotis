import cProfile
import pandas as pd
import pyarrow.parquet as pq
import spacy
from mpi4py import MPI

FILE_NAME = "ccnews_LT_subset_1.parquet"
BATCH_SIZE = 500
NLP_MODEL = "lt_core_news_sm"


def get_next_batch(parquet_iter):
    try:
        batch = next(parquet_iter)
        return batch.to_pandas()["title"].dropna().tolist()
    except StopIteration:
        return None


def worker_logic(comm):
    nlp = spacy.load(NLP_MODEL)

    while True:
        titles = comm.recv(source=0)

        if titles is None:
            break

        orgs = []
        for doc in nlp.pipe(titles, disable=["parser", "tagger"]):
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    orgs.append(ent.text)

        comm.send(orgs, dest=0)


def manager_logic(comm, size):
    parquet_file = pq.ParquetFile(FILE_NAME)
    batch_iter = parquet_file.iter_batches(batch_size=BATCH_SIZE, columns=["title"])

    results_list = []
    active_workers = 0
    status = MPI.Status()

    for i in range(1, size):
        batch = get_next_batch(batch_iter)
        if batch:
            comm.send(batch, dest=i)
            active_workers += 1
        else:
            comm.send(None, dest=i)

    while active_workers > 0:
        new_results = comm.recv(source=MPI.ANY_SOURCE, status=status)
        sender_rank = status.Get_source()

        results_list.extend(new_results)

        next_batch = get_next_batch(batch_iter)

        if next_batch:
            comm.send(next_batch, dest=sender_rank)
        else:
            comm.send(None, dest=sender_rank)
            active_workers -= 1

    return pd.Series(results_list).value_counts()


def process_file_stream(file_name, batch_size):
    nlp = spacy.load("lt_core_news_sm")

    parquet_file = pq.ParquetFile(file_name)

    all_orgs = []
    total_rows = 0

    print(f"Failas: {file_name}, vieno rinkinio dydis: {batch_size}.")

    for batch in parquet_file.iter_batches(batch_size=batch_size, columns=["title"]):

        df_chunk = batch.to_pandas()
        titles = df_chunk["title"].dropna().tolist()

        orgs = []

        for doc in nlp.pipe(titles, disable=["parser", "tagger"]):
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    orgs.append(ent.text)

        all_orgs.extend(orgs)
        total_rows += len(titles)

        if total_rows % batch_size == 0:
            print(f"Apdorota {total_rows} eilučių.")

    org_series = pd.Series(all_orgs)
    return org_series.value_counts()


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if size < 2:
        start_time = MPI.Wtime()

        final_counts = process_file_stream(FILE_NAME, BATCH_SIZE)

        end_time = MPI.Wtime()

        print(f"Apdorota per {end_time - start_time:.2f} sek.")
        print("Dažniausiai paminėtos organizacijos:")
        print(final_counts.head(10))

        return

    start_time = MPI.Wtime()

    profiler = cProfile.Profile()
    profiler.enable()

    if rank == 0:
        final_counts = manager_logic(comm, size)

        end_time = MPI.Wtime()
        print(f"Apdorota per {end_time - start_time:.2f} sek.")
        print("Dažniausiai paminėtos organizacijos:")
        print(final_counts.head(10))
    else:
        worker_logic(comm)

    profiler.disable()
    profiler.dump_stats(f"profile_rank_{rank}.stats")


if __name__ == "__main__":
    main()
