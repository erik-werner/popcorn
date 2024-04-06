import pandas as pd
import numpy as np
import arviz as az

blind_a = {"a": 2, "b": 3, "c": 1, "d": 4}
blind_a = {v: k for k, v in blind_a.items()}
blind_b = {"a": "default", "b": "latmask", "c": "ugn", "d": "smör"}
decoding = {k: blind_b[v] for k, v in blind_a.items()}


def get_next_pair(user_uid):


    df = pd.read_csv('pre_test.csv')
    trace = az.from_netcdf(f'trace.nc')
    df = df[df['user_uid'] == user_uid]
    df = df[df["popcorn_id_1"] != 10]
    df["popcorn_1"] = [decoding[int(id_)] for id_ in df["popcorn_id_1"]]
    df["popcorn_2"] = [decoding[int(id_)] for id_ in df["popcorn_id_2"]]
    df = df[["popcorn_1", "popcorn_2"]]
    existing_pairs = [tuple(row) for row in df.values]
    popcorn_rating_std = trace.posterior["popcorn_rating"].sel(people=user_uid).std(dim=["draw", "chain"]).to_numpy()
    popcorn_names = trace.posterior["popcorn_rating"].indexes["popcorn"].to_numpy()
    std_array = np.add.outer(popcorn_rating_std, popcorn_rating_std)
    sorted_pairs = np.argwhere(std_array)
    sorted_pairs = sorted(sorted_pairs, key=lambda x: -std_array[x[0], x[1]])
    sorted_pairs = [pair for pair in sorted_pairs if pair[1] > pair[0]]
    corresponding_names = [(popcorn_names[pair[0]], popcorn_names[pair[1]]) for pair in sorted_pairs]
    
    for pair in corresponding_names:
        if pair not in existing_pairs and pair[::-1] not in existing_pairs:
            return pair


if __name__ == '__main__':
    print(get_next_pair("atg"))