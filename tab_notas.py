import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def best_of_month(notas):
    # st.table(notas)

    st.markdown("## Melhor do mês - Hall da Fama")
    st.text('Nota: Para ser elegível, o jogador não pode ter faltado mais do que 1 pelada no mês')
    df_notas = notas.copy()

    bools = df_notas.iloc[0].notnull()
    idxs = bools[bools].index[1:-4]
    dates = pd.to_datetime(idxs, format='%b/%y')

    months = dates.month

    dict_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    dict_mvp = {}
    for m in pd.unique(months):
        idx = np.where(months == m)[0]
        df_month = df_notas.iloc[1:, np.concatenate(([0], idx + 1))]
        df_month = df_month.dropna(thresh=len(df_month.columns) - 1)
        avg = df_month.iloc[:, 1:].mean(skipna=True, axis=1)
        df_month['Avg'] = avg
        df_month['Len'] = df_month.iloc[:, 1:].count(axis=1)
        df_month = df_month.sort_values(by=['Avg', 'Len'], ascending=False)
        nome_mes = dict_meses[m]
        dict_mvp[nome_mes] = df_month.iloc[0:3, :].loc[:, ['Jogador', 'Avg']]
        text = f'#### {nome_mes} :first_place_medal: {df_month.iloc[0,0]} (em andamento)' if m == pd.unique(months)[-1] else f'#### {nome_mes} :trophy: {df_month.iloc[0,0]}'
        st.markdown(text)

    st.markdown('## Pódio do mês')
    mes = st.selectbox('Mês', [dict_meses[m] for m in pd.unique(months)], index = len(pd.unique(months)[:-1]) - 1)
    text1 = f'#### :first_place_medal: {dict_mvp[mes].iloc[0,0]} (Média {np.round(dict_mvp[mes].iloc[0,1], 2)})'
    text2 = f'#### :second_place_medal: {dict_mvp[mes].iloc[1,0]} (Média {np.round(dict_mvp[mes].iloc[1,1], 2)})'
    text3 = f'#### :third_place_medal: {dict_mvp[mes].iloc[2,0]} (Média {np.round(dict_mvp[mes].iloc[2,1], 2)})'

    st.markdown(text1)
    st.markdown(text2)
    st.markdown(text3)


def plot_notas(df_notas):
    st.markdown('## Gráfico')
    df_notas['Média'] = np.round(df_notas['Média'], 2)
    fig = px.scatter(df_notas, x='Total', y='Média', hover_name='Jogador', text='Jogador')
    fig.update_traces(textposition='top center')
    fig.update_layout(title='Notas dos jogadores', xaxis_title='Jogos', yaxis_title='Nota média')

    st.plotly_chart(fig)

