import streamlit as st
import pandas as pd
from __init__ import ROOT
import plotly.express as px

st.set_page_config(layout='wide',page_title='Модная морда')




left_bar,main = st.columns((2,8))



@st.cache_data()
def get_data() -> pd.DataFrame:
    dd = pd.read_parquet(f'{ROOT}/AwesomeDAG/dags/data/imdb_data.parquet')
    # dd['actor'] = dd.apply(lambda row: set(row.fillna('')['actor']) | set(row.fillna('')['actress']) ,axis=1).apply(list)
    dd['startYear'] = dd['startYear'].astype('float16')
    return dd.drop('actress',axis=1)



data = get_data()

with left_bar:
    years = st.slider('Year',1950,2023,1970)
    votes = st.slider('Votes',100,int(data['numVotes'].quantile(.95)),int(data['numVotes'].median()))
    director_name = st.text_input('director_name')
    actor_name = st.text_input('actor_name')
    genres = st.multiselect('genre',data['genres'].explode().unique().tolist())
    if genres is None:
        genres = data['genres'].explode().unique().tolist()

genres = '|'.join(genres)

query_filter = '''
                startYear > @years
                & numVotes > @votes
                & genres.explode().str.contains(@genres).groupby(level=0).sum()>0
                & actor.explode().str.contains(@actor_name).groupby(level=0).sum()>0
                & directors.explode().str.contains(@director_name).groupby(level=0).sum()>0
                '''.replace('\n','')

df = data.query(query_filter) 

with main:
    st.write(df.sort_values(by='averageRating',ascending=False).head())
    st.plotly_chart(
        px.line(df.groupby(['startYear','titleType'])['averageRating'].mean().reset_index(),x='startYear',y='averageRating',color='titleType')
                ,use_container_width=True
    )