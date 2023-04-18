import os
import urllib.request as urlreq

tgt_markets = ['ca', 'de', 'fr', 'in', 'jp', 'mx', 'uk', 'us']
tgt_cat = 'Electronics'

##########
### Download XMarket data for papers categories and markets
#########
fix_url = 'https://ciir.cs.umass.edu/downloads/XMarket/FULL/'
orig_data_dl = 'DATA2/orig_data'
proc_data_out = 'DATA2/proc_data'
if not os.path.exists(orig_data_dl):
    os.makedirs(orig_data_dl)
if not os.path.exists(proc_data_out):
    os.makedirs(proc_data_out)

for tgt_market in tgt_markets:
    cur_url = f'{fix_url}{tgt_market}/{tgt_cat}/ratings_{tgt_market}_{tgt_cat}.txt.gz'
    urlreq.urlretrieve(cur_url, f'{orig_data_dl}/ratings_{tgt_market}_{tgt_cat}.txt.gz')
    print(f'Done: {cur_url}')


# set thr for K-core data cleaning. We use 5core, +1 valid and +1 test-> so at this point we filter 7core
user_thr = 7
item_thr = 7

# one can iterate a few times, we only perform one time filter
def get_kcore(ratings_all, user_thr, item_thr, repeat=1):
    for i in range(repeat):
        ratings_all.reset_index(drop=True, inplace=True)
        ratings_all = ratings_all.loc[ratings_all.groupby("itemId").filter(lambda x: len(x) >= item_thr).index]
        ratings_all.reset_index(drop=True, inplace=True)
        ratings_all = ratings_all.loc[ratings_all.groupby("userId").filter(lambda x: len(x) >= user_thr).index]
        ratings_all.reset_index(drop=True, inplace=True)
    return ratings_all

def rating_stats(ratings_all):
    n_rating = ratings_all.shape[0]
    n_user = len(set(ratings_all['userId'].unique()))
    n_item = len(set(ratings_all['itemId'].unique()))

    if (n_user*n_item)!=0:
        density = round((n_rating/(n_user*n_item) )*100, 5)
    else:
        density = 0

    return { '#users': n_user,
        '#items': n_item,
        '#rates': n_rating,
        'dens\%': density,
        }


##########
### load and clean us market as the M0
#########
import pandas as pd

tgt_market = 'us'
us_ratings_file = f'{orig_data_dl}/ratings_{tgt_market}_{tgt_cat}.txt.gz'

us_df = pd.read_csv(us_ratings_file, compression='gzip', header=None, sep=' ', names=["userId", "itemId", "rate", "date"] )
us_df_7core = get_kcore(us_df, user_thr=user_thr, item_thr=item_thr)

us_user_thr = 10
us_item_thr = 25
us_df_10core = get_kcore(us_df, user_thr=us_user_thr, item_thr=us_item_thr)

# write us data
us_df_7core.to_csv(f'{proc_data_out}/{tgt_market}_5core.txt', index=False, sep=' ')
us_df_10core.to_csv(f'{proc_data_out}/{tgt_market}_10core.txt', index=False, sep=' ')

print('US Market data stats:')
print(rating_stats(us_df))
print(rating_stats(us_df_7core))
print(rating_stats(us_df_10core))

##########
### load and clean target markets
#########
us_items_set = set(us_df_10core['itemId'].unique())

for tgt_market in tgt_markets:
    if tgt_market=='us':
        continue
    #read market ratings
    cur_ratings_file = f'{orig_data_dl}/ratings_{tgt_market}_{tgt_cat}.txt.gz'
    cur_df = pd.read_csv(cur_ratings_file, compression='gzip', header=None, sep=' ', names=["userId", "itemId", "rate", "date"] )

    # item exist for us
    cur_df = cur_df.loc[cur_df['itemId'].isin( us_items_set )]
    cur_df_7core = get_kcore(cur_df, user_thr=user_thr, item_thr=item_thr)
    cur_df_7core.to_csv(f'{proc_data_out}/{tgt_market}_5core.txt', index=False, sep=' ')
    print(f'\n-- {tgt_market} stats: ')
    print(rating_stats(cur_df_7core))
