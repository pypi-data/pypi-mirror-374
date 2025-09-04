import fire
import polars as pl
from tqdm.auto import tqdm
import scipy.spatial as sp
import numpy as np
from ranx import Qrels, Run, evaluate
from transformers import AutoTokenizer, AutoModel
from safetensors.torch import save_file, load_file
import torch as th


def prepare_embs(
    dataset: str = './med_link_datasets/IfMedLink-name.csv',
    output: str = './exps/name-only/If_SapBERT.safetensors',
    model_name: str = 'cambridgeltl/SapBERT-from-PubMedBERT-fulltext',
):
    # prepare models
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.to(device)
    print(f'Using device: {device}. Model: {model_name} loaded.')
    # load dataset
    df = pl.read_csv(dataset)
    corpus = df['med_name_generic'].to_list()
    queries = df['med_name'].to_list()
    # get embs
    bs = 64
    corpus_embs = []
    model.eval()
    for i in tqdm(range(0, len(corpus), bs)):
        batch = corpus[i : i + bs]
        inputs = tokenizer(batch, padding=True, truncation=False, return_tensors="pt").to(device)
        with th.no_grad():
            outputs = model(**inputs)
        corpus_embs.append(outputs.last_hidden_state[:, 0, :].cpu().detach())
    corpus_embs = th.cat(corpus_embs, dim=0)
    queries_embs = []
    for i in tqdm(range(0, len(queries), bs)):
        batch = queries[i : i + bs]
        inputs = tokenizer(batch, padding=True, truncation=False, return_tensors="pt").to(device)
        with th.no_grad():
            outputs = model(**inputs)
        queries_embs.append(outputs.last_hidden_state[:, 0, :].cpu().detach())
    queries_embs = th.cat(queries_embs, dim=0)
    print(f'Corpus embs shape: {corpus_embs.shape}. Queries embs shape: {queries_embs.shape}')
    tensors = {
        "corpus_embs": corpus_embs,
        "queries_embs": queries_embs,
    }
    save_file(
        tensors,
        output,
    )
    print(f'Saved embs to {output}')


def run(
    dataset: str = './med_link_datasets/IfMedLink-name.csv',
    emb_path: str = './exps/name-only/If_SapBERT.safetensors',
    output: str = './exps/name-only/SapBERT_If_name_result.csv',
):
    # load data
    df = pl.read_csv(dataset)
    corpus = df['med_name_generic'].to_list()
    queries = df['med_name'].to_list()
    print('loaded data')
    # load embs
    embs = load_file(emb_path)
    corpus_embs = embs['corpus_embs'].numpy()
    queries_embs = embs['queries_embs'].numpy()
    assert corpus_embs.shape[0] == len(corpus)
    assert queries_embs.shape[0] == len(queries)
    print('loaded embs')
    # create qrels
    qrels_dict = {}
    for input, target in zip(queries, corpus):
        qrels_dict[input] = {target: 1}
    # get run
    run_dict = {}
    for i in tqdm(range(0, len(queries))):
        query = queries[i]
        q_emb = queries_embs[i:i+1, :]  # (1, emb_size)
        sim_scores = 1 - sp.distance.cdist(q_emb, corpus_embs, 'cosine')  # (1, corpus_size)
        sim_scores = np.squeeze(sim_scores, axis=0)  # (corpus_size,)
        # add to run dict
        run_dict[query] = {}
        for doc, score in zip(corpus, sim_scores):
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