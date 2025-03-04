import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def plot_stats(placares):
    df = placares.copy()

    players = set(df.iloc[:, np.r_[2:8, 10:16]].values.flatten())

    dict_players = {player: np.zeros(df.shape[0], dtype=int) for player in players}
    difs = []

    for i, row in df.iterrows():
        for player in row[2:8]:
            if pd.notna(player):
                dict_players[player][i] = 1
        for player in row[10:16]:
            if pd.notna(player):
                dict_players[player][i] = -1
        difs.append(row.A / row.Jogos - row.B / row.Jogos)

    dict_wdl = {player: (0, 0, 0) for player in players}
    dict_goals = {player: (0, 0) for player in players}
    dict_jogos_8mins = {player: 0 for player in players}

    for i, row in df.iterrows():
        for player in row[2:8]:
            if pd.notna(player):
                dict_goals[player] = (dict_goals[player][0] + row.A, dict_goals[player][1] + row.B)
                dict_jogos_8mins[player] += row.Jogos
                if row.A > row.B:
                    dict_wdl[player] = (dict_wdl[player][0] + 1, dict_wdl[player][1], dict_wdl[player][2])
                elif row.A == row.B:
                    dict_wdl[player] = (dict_wdl[player][0], dict_wdl[player][1] + 1, dict_wdl[player][2])
                else:
                    dict_wdl[player] = (dict_wdl[player][0], dict_wdl[player][1], dict_wdl[player][2] + 1)
        for player in row[10:16]:
            if pd.notna(player):
                dict_goals[player] = (dict_goals[player][0] + row.B, dict_goals[player][1] + row.A)
                dict_jogos_8mins[player] += row.Jogos
                if row.B > row.A:
                    dict_wdl[player] = (dict_wdl[player][0] + 1, dict_wdl[player][1], dict_wdl[player][2])
                elif row.A == row.B:
                    dict_wdl[player] = (dict_wdl[player][0], dict_wdl[player][1] + 1, dict_wdl[player][2])
                else:
                    dict_wdl[player] = (dict_wdl[player][0], dict_wdl[player][1], dict_wdl[player][2] + 1)

    df_stats = pd.DataFrame({
        'Nome': list(players),
        'V': [dict_wdl[p][0] for p in players],
        'E': [dict_wdl[p][1] for p in players],
        'D': [dict_wdl[p][2] for p in players],
        'GP': [dict_goals[p][0] for p in players],
        'GC': [dict_goals[p][1] for p in players],
        'J (8 min)': [dict_jogos_8mins[p] for p in players]
    })

    df_stats['%'] = np.round((df_stats.V * 3 + df_stats.E) / (df_stats.V + df_stats.E + df_stats.D) / 3, 2)
    df_stats['P'] = df_stats.V + df_stats.E + df_stats.D
    df_stats['SG'] = df_stats.GP - df_stats.GC
    df_stats['GP/jogo'] = np.round(df_stats.GP / df_stats['J (8 min)'], 2)
    df_stats['GC/jogo'] = np.round(df_stats.GC / df_stats['J (8 min)'], 2)

    df_stats = df_stats.sort_values(by=['SG', '%', 'P'], ascending=False)

    max_val = df_stats['P'].max()
    min_partidas = st.slider('Mínimo de partidas', min_value=0, max_value=max_val, value=min(max_val, 10))
    df_stats = df_stats[df_stats.P >= min_partidas]
    df_stats = df_stats.loc[:,['Nome', 'J (8 min)', 'P', 'V', 'E', 'D', '%', 'GP', 'GC', 'SG', 'GP/jogo', 'GC/jogo']] # reordenar colunas

    st.markdown('## Tabela')
    st.dataframe(df_stats, hide_index=True)

    fig = px.scatter(df_stats, x='GP/jogo', y='GC/jogo', size='J (8 min)', color='SG', color_continuous_scale='RdYlGn', hover_name='Nome', text='Nome')
    fig.update_traces(textposition='top center')
    fig.update_layout(title='Gols feitos e sofridos por jogo', xaxis_title='Gols feitos pelo time por jogo', yaxis_title='Gols sofridos pelo time por jogo')

    st.markdown('## Gráfico')
    st.plotly_chart(fig)

def artilharia(art, notas):
    art.sort_values(by='Jogador', ascending=True, inplace=True)
    art.reset_index(drop=True, inplace=True)
    cols = art.columns
    notas = notas[cols]
    notas.sort_values(by=cols[0], ascending=True, inplace=True) # ordem alfabética dos jogadores
    notas.reset_index(drop=True, inplace=True)
    art['Gols'] = art.iloc[:, 1:].sum(axis=1)
    art['Peladas'] = notas.count(axis=1) - 1
    art['Gols/j'] = round(art['Gols'] / art['Peladas'], 2)
    df = art.loc[:,['Jogador','Gols', 'Peladas', 'Gols/j']]
    
    df = df.sort_values(by=['Gols', 'Gols/j'], ascending=False)
    df = df.reset_index(drop=True)
    df.index += 1

    st.markdown('## Artilharia')
    st.dataframe(df)
