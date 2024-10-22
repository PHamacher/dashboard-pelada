import streamlit as st
import pandas as pd

from tab_placares import get_dates, show_placares
from tab_stats import plot_stats, artilharia
from tab_notas import best_of_month, plot_notas
from tab_optimization import bate_times

# xls = pd.ExcelFile('Streamlit/Dashboard Pelada/data.xlsx')
xls = pd.ExcelFile('data/data.xlsx')

notas = pd.read_excel(xls, 'notas')
placares = pd.read_excel(xls, 'placares')
art = pd.read_excel(xls, 'artilharia')

st.title(':soccer: Pelada de toda quarta :soccer:')

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
    artilharia(art)

with nts:
    df_notas = notas.copy()

    best_of_month(df_notas)
    plot_notas(df_notas)
