import fire
import polars as pl
from rank_bm25 import BM25Okapi
from tqdm.auto import tqdm
from ranx import Qrels, Run, evaluate


def run(
    dataset: str = './med_link_datasets/IfMedLink-name.csv',
    output: str = './exps/name-only/BM25_If_name_result.csv',
):
    df = pl.read_csv(dataset)
    corpus = df['med_name_generic'].to_list()
    corpus = [i.lower() for i in corpus]
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    queries = df['med_name'].to_list()
    queries = [i.lower() for i in queries]

    # create qrels
    qrels_dict = {}
    for input, target in zip(queries, corpus):
        qrels_dict[input] = {target: 1}
    # get run
    bm25 = BM25Okapi(tokenized_corpus)
    run_dict = {}
    for query in tqdm(queries):
        tokenizer_query = query.split(" ")
        doc_scores = bm25.get_scores(tokenizer_query)
        # add to run dict
        run_dict[query] = {}
        for doc, score in zip(corpus, doc_scores):
            run_dict[query][doc] = score
    # create qrels and run
    qrels = Qrels(qrels_dict)
    run = Run(run_dict)
    # evaluate
    metrics = evaluate(qrels, run, ['hit_rate@1', 'hit_rate@5', 'mrr@10', 'mrr@50'])
    print(metrics)
    # save metrics
    metrics['dataset'] = dataset
    metrics_df = pl.from_dicts([metrics])
    metrics_df.write_csv(output)


if __name__ == "__main__":
    fire.Fire()