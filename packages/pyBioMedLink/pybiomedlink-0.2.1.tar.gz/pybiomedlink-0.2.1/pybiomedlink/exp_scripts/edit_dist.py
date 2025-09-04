import fire
import polars as pl
from ranx import Qrels, Run, evaluate
import editdistance
from heapq import heappush, nsmallest
from tqdm.auto import tqdm


def run(
    dataset: str = './med_link_datasets/IfMedLink-name.csv',
    output: str = './exps/name-only/edit_dist_If_name_result.csv',
):
    df = pl.read_csv(dataset)
    targets = df['med_name_generic'].to_list()
    inputs = df['med_name'].to_list()
    inputs = [i.lower() for i in inputs]
    targets = [t.lower() for t in targets]
    # create qrels
    qrels_dict = {}
    for input, target in zip(inputs, targets):
        qrels_dict[input] = {target: 1}
    # get run
    run_dict = {}
    for input in tqdm(inputs):
        h = []
        for target in targets:
            dist = editdistance.eval(input, target)
            heappush(h, (dist, target))
        # get top 50
        topk = nsmallest(50, h)
        # min-max inverted norm
        topk_dists = [_[0] for _ in topk]
        min_dist = min(topk_dists)
        max_dist = max(topk_dists)
        # add to run dict
        run_dict[input] = {}
        for dist, target in topk:
            norm_score = (max_dist - dist) / (max_dist - min_dist)
            run_dict[input][target] = norm_score
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