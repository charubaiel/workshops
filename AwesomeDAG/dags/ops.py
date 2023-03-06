import pandas as pd
from dagster import asset,AssetIn,file_relative_path
import warnings
from dagstermill import define_dagstermill_asset
warnings.simplefilter('ignore')
import pathlib
ROOT = pathlib.Path(__file__).parent

@asset(name='ratings',group_name='download')
def download_imdb_ratings(context) -> pd.DataFrame:

    min_votes = context.op_config['min_votes']
    ratings = pd.read_csv("https://datasets.imdbws.com/title.ratings.tsv.gz",
                        sep='\t',compression='gzip')
    ratings = ratings[ratings['numVotes']>min_votes].set_index('tconst')

    return ratings



@asset(name='names',group_name='download')
def download_imdb_names() -> pd.DataFrame:

    names = pd.read_csv('https://datasets.imdbws.com/name.basics.tsv.gz',
                        sep='\t',compression='gzip')

    return names





@asset(name='cast',group_name='download')
def download_imdb_principals(ratings:pd.DataFrame) -> pd.DataFrame:

    datasets_urls = 'https://datasets.imdbws.com/title.principals.tsv.gz'
    
    data_iterator = pd.read_csv(datasets_urls,
                                compression='gzip',
                                sep='\t',
                                chunksize=100000)
    result_list = []

    category_list = ['cinematographer','actor','actress']
    filter = 'tconst in @ratings.index & category in @category_list'
    for sample in data_iterator:

        result_list.append(sample.query(filter))
    
    return pd.concat(result_list)


@asset(name='crew',group_name='download')
def download_imdb_crew(ratings:pd.DataFrame) -> pd.DataFrame:

    datasets_urls = 'https://datasets.imdbws.com/title.crew.tsv.gz'
    
    data_iterator = pd.read_csv(datasets_urls,
                                compression='gzip',
                                sep='\t',
                                chunksize=100000)
    result_list = []

    for sample in data_iterator:
        result_list.append(sample[sample['tconst'].isin(ratings.index)])
    
    return pd.concat(result_list)


@asset(name='titles',group_name='download')
def download_imdb_titles(ratings:pd.DataFrame) -> pd.DataFrame:

    datasets_urls = 'https://datasets.imdbws.com/title.basics.tsv.gz'

    data_iterator = pd.read_csv(datasets_urls,
                                compression='gzip',
                                sep='\t',
                                chunksize=100000)
    result_list = []
    category_types = ['movie','tvMovie','tvMiniSeries']
    filter = 'tconst in @ratings.index & titleType in @category_types'
    for sample in data_iterator:
        result_list.append(sample.query(filter))
    result = pd.concat(result_list)

    return result


# dicts

@asset(name='titles_dict',group_name='dicts')
def create_title_dict(titles:pd.DataFrame) -> dict:
    return titles.set_index('tconst')['primaryTitle'].to_dict()

@asset(name='names_dict',group_name='dicts')
def create_names_dict(names:pd.DataFrame) -> dict:
    return names.set_index('nconst')['primaryName'].to_dict()



# Clean data


@asset(name='clean_names',group_name='clean',)
def clean_names(names:pd.DataFrame,titles_dict:dict) -> pd.DataFrame:
    df = names.astype({
                'nconst':'category',
                'primaryName':'category'
            })
    df = df.set_index('nconst').apply(lambda x: x.replace('\\N',None))
    df['birthYear'] = pd.to_numeric(df['birthYear'],errors='coerce',downcast='unsigned')
    df['deathYear'] = pd.to_numeric(df['deathYear'],errors='coerce',downcast='unsigned')
    
    df['primaryProfession'] = df['primaryProfession'].str.split(',')
    exploded = df.explode(column=['primaryProfession'])
    exploded = pd.get_dummies(exploded,columns=['primaryProfession'])
    exploded = exploded.groupby(level=0).max()
    exploded['knownForTitles'] = exploded['knownForTitles'].str.split(',')\
                                                                .explode().map(titles_dict)\
                                                                .groupby(level=0).unique()
    return exploded



@asset(name='clean_titles',group_name='clean')
def clean_titles(titles:pd.DataFrame) -> pd.DataFrame:

    titles['genres'] = titles['genres'].str.split(',')

    titles['startYear'] = titles['startYear'].replace('\\N',None).astype(float)
    titles['runtimeMinutes'] = titles['runtimeMinutes'].replace('\\N',None).astype(float)

    # titles = pd.get_dummies(titles.explode('genres'),columns=['genres'])
                            
    # titles = titles.drop(['endYear','originalTitle'],axis=1)
    
    return titles.groupby('tconst').max()


@asset(name='clean_cast',group_name='clean')
def clean_cast(cast:pd.DataFrame,names_dict:dict) -> pd.DataFrame:
    cast['nconst'] = cast['nconst'].map(names_dict)
    return cast.pivot_table('nconst','tconst','category',aggfunc=list)




@asset(name='clean_crew',group_name='clean')
def clean_crew(crew:pd.DataFrame,names_dict:dict) -> pd.DataFrame:
    
    crew['directors'] = crew['directors'].map(names_dict)
    crew['writers'] = crew['writers'].str.split(',')\
                                    .explode().map(names_dict)\
                                    .groupby(level=0).unique()
    return crew.set_index('tconst')



# fin

@asset(name = 'final_df',group_name='result')
def result_dataset(clean_titles:pd.DataFrame,
                    clean_crew:pd.DataFrame,
                    clean_cast:pd.DataFrame,
                    ratings:pd.DataFrame
                    )-> pd.DataFrame:
    result = clean_titles.join(ratings).join(clean_cast).join(clean_crew)
    result = result.apply(pd.to_numeric, errors='ignore',downcast='unsigned')
    return result
        

@asset(name = 'save_data',group_name='save')
def save_data(final_df:pd.DataFrame,
                    ) -> None:
    final_df.to_parquet(f'{ROOT}/data/imdb_data.parquet')
    return None
    


@asset(name='save_big_data',group_name='save')
def save_big_data(clean_names:pd.DataFrame) -> None:
    clean_names.to_parquet(f'{ROOT}/data/names.parquet')
    return None





asset_notebook = define_dagstermill_asset(
    name="interactive_result_notebook",
    notebook_path=file_relative_path(__file__, "notebook_asset.ipynb"),
    group_name="result",
    ins= {"final_df": AssetIn("final_df")},
    
)