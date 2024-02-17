import requests
import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

def genius(search_term, access_token, per_page=15):
    '''
    Collect data from the Genius API by searching for `search_term`.
    
    **Assumes ACCESS_TOKEN is loaded in the environment.**
    '''
    genius_search_url = f"http://api.genius.com/search?q={search_term}&" + \
                        f"access_token={access_token}&per_page={per_page}"
    
    try:
        response = requests.get(genius_search_url)
        json_data = response.json()
        return json_data['response']['hits']
    except requests.exceptions.RequestException as e:
        print(f"Error for search term '{search_term}': {e}")
        return []

def genius_to_df(json_data):
    if not json_data:
        return pd.DataFrame()  
    
    hits = [hit['result'] for hit in json_data]
    df = pd.DataFrame(hits)

    # expand dictionary elements
    df_stats = df['stats'].apply(pd.Series)
    df_stats.rename(columns={c:'stat_' + c for c in df_stats.columns},
                    inplace=True)
    
    df_primary = df['primary_artist'].apply(pd.Series)
    df_primary.rename(columns={c:'primary_artist_' + c for c in df_primary.columns},
                      inplace=True)
    
    df = pd.concat((df, df_stats, df_primary), axis=1)
    
    return df

def process_search_term(search_term, access_token, n_results_per_term=10):
    json_data = genius(search_term, access_token, per_page=n_results_per_term)
    df = genius_to_df(json_data)
    return df

def process_search_terms(search_terms, access_token, n_results_per_term=10):
    dfs = []
    for search_term in tqdm(search_terms):
        df = process_search_term(search_term, access_token, n_results_per_term)
        dfs.append(df)
    df_genius = pd.concat(dfs)
    df_genius.to_csv("genius_data.csv", index=False)

def main():
    search_terms = ['BTS', 'New Jeans', 'Armaan Malik', 'Taylor Swift', 'Coldplay']
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    process_search_terms(search_terms, access_token, n_results_per_term=10)

if __name__ == "__main__":
    main()
