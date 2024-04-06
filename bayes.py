import pandas as pd
import numpy as np
import arviz as az
import pymc as pm
from utils import read_table

#blind_a = {"a": 2, "b": 3, "c": 1, "d": 4}
#blind_a = {v: k for k, v in blind_a.items()}
#blind_b = {"a": "default", "b": "latmask", "c": "ugn", "d": "smör"}
#decoding = {k: blind_b[v] for k, v in blind_a.items()}

decoding = {1: "Babe", 2: "Default", 3: "Default", 4: "Dolly",
            5: "Micro", 6: "Köpe", 7: "Latmask", 8: "Rey"}


def get_next_pair(user_uid):
    df = read_table()
    trace = az.from_netcdf(f'trace.nc')
    df = df[df['user_uid'] == user_uid]
    # df = df[df["popcorn_id_1"] != 10]
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


def update_model():
    #df = pd.read_csv('pre_test.csv')
    try:
        df = read_table()
        df["rating_diff"] = df["score"]
        df = df[df["popcorn_id_1"] != 10]
        df["popcorn_1"] = [decoding[int(id_)] for id_ in df["popcorn_id_1"]]
        df["popcorn_2"] = [decoding[int(id_)] for id_ in df["popcorn_id_2"]]
        popcorn = list(df["popcorn_1"].unique())
        people = list(df["user_uid"].unique())
        person_indices = [people.index(p) for p in df["user_uid"]]
        popcorn_1_indices = [popcorn.index(p) for p in df["popcorn_1"]]
        popcorn_2_indices = [popcorn.index(p) for p in df["popcorn_2"]]
        with pm.Model(coords={"popcorn": popcorn, "people": people}) as model:
            mu_popcorn = pm.ZeroSumNormal("mu_popcorn", sigma=1, dims="popcorn")
            person_popcorn_interaction = pm.ZeroSumNormal("person_popcorn_interaction", sigma=0.3, dims=["people", "popcorn"])

            popcorn_rating = pm.Normal("popcorn_rating", mu=mu_popcorn + person_popcorn_interaction, sigma=0.2, dims=["people", "popcorn"])


            rating_diff = pm.Deterministic("rating_diff", popcorn_rating[person_indices, popcorn_2_indices] - popcorn_rating[person_indices, popcorn_1_indices])
            observed_rating_diff = pm.Normal("observed_rating_diff", mu=rating_diff, sigma=0.3, observed=df["rating_diff"])

            trace = pm.sample(1000, tune=1000)
            az.to_netcdf(trace, 'trace.nc')
            return trace
    except:
        print("No data")
        return None

if __name__ == '__main__':
    # print(get_next_pair("atg"))
    print(update_model())