import streamlit as st
import pandas as pd
import datetime as dt

from tab_placares import get_dates, show_placares
from tab_stats import plot_stats, artilharia
from tab_notas import best_of_month, plot_notas
from tab_optimization import bate_times

# xls = pd.ExcelFile('Streamlit/Dashboard Pelada/data.xlsx')

st.title(':soccer: Pelada de toda quarta :soccer:')

season = st.selectbox("Selecione a temporada", ['Todas', 2024, 2025], index=2)

@st.cache_data
def load_data(season):
    xls = pd.ExcelFile('data/condominio.xlsx')
    notas = pd.read_excel(xls, 'notas')
    placares = pd.read_excel(xls, 'placares')
    art = pd.read_excel(xls, 'artilharia')

    if season != 'Todas':
        dates = [d for d in notas.columns if type(d) == dt.datetime and d.year == season]
        notas = notas[['Jogador'] + dates]
        placares = placares[placares['Data'].dt.year == season]

        dates_art = [d for d in dates if d in art.columns]
        art = art[['Jogador'] + dates_art]

        notas.reset_index(drop=True, inplace=True)
        placares.reset_index(drop=True, inplace=True)
        art.reset_index(drop=True, inplace=True)

        

    return notas, placares, art

notas, placares, art = load_data(season)


bt, plac, stats, nts = st.tabs(['Bate Times', 'Placares', 'Estatísticas', 'Notas'])

with bt: 
    st.markdown('## Bate Times')
    bate_times()


with plac:
    (placares, dates) = get_dates(placares)
    date = st.selectbox('Selecione a semana', dates)

    if date == 'Todas':
        for d in dates[1:]:
            st.markdown(f'# {d}')
            show_placares(placares, d)
    else:
        show_placares(placares, date)

with stats:
    plot_stats(placares)
    artilharia(art, notas)

with nts:
    df_notas = notas.copy()

    best_of_month(df_notas)
    plot_notas(df_notas)
