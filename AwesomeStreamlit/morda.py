import streamlit as st
import pandas as pd
from __init__ import ROOT
import plotly.express as px

st.set_page_config(layout='wide',page_title='Модная морда')




left_bar,main = st.columns((1,8))



@st.cache(allow_output_mutation=True)
def get_data() -> pd.DataFrame:
    dd = pd.read_parquet(f'{ROOT}/AwesomeDAG/data/imdb_data.parquet')
    dd['actor'] = dd.apply(lambda row: set(row.fillna('')['actor']) | set(row.fillna('')['actress']) ,axis=1).apply(list)
    dd['startYear'] = dd['startYear'].astype('category')
    return dd.drop('actress',axis=1)



data = get_data()

with left_bar:
    years = st.slider('Year',1950,2023,1970)
    votes = st.slider('Votes',100,int(data['numVotes'].quantile(.95)),int(data['numVotes'].median()))
    genres = st.multiselect('genre',data['genres'].explode().unique().tolist(),data['genres'].explode().unique().tolist())

df = data.query('startYear > @years & numVotes > @votes & genres.explode().isin(@genres).groupby(level=0).mean() >= .75 ') 

with main:
    st.write(df.head().sort_values(by='averageRating'))
    st.write( df.groupby('directors').agg({'averageRating':'mean','primaryTitle':'nunique'}).query('primaryTitle > 2').sort_values(by='averageRating',ascending=False).head(10))
    st.plotly_chart(
        px.line(df.explode('genres').query('genres in @genres').groupby(['startYear','titleType','genres'])['averageRating'].mean().reset_index(),x='startYear',y='averageRating',color='titleType',facet_row = 'genres')
                ,use_container_width=True
    )