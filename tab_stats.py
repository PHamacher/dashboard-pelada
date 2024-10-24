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

    min_partidas = st.slider('Mínimo de partidas', min_value=0, max_value=df_stats['P'].max(), value=10)
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
    art['Jogos oficiais'] = notas.iloc[:, 20:-5].count(axis=1) # fazer usando o índice das colunas
    art['Gols/j'] = round(art['Gols oficiais'] / art['Jogos oficiais'], 2)
    df = art.loc[:,['Jogador','Gols oficiais', 'Jogos oficiais', 'Gols/j', 'Gols (total)']]
    
    df = df.sort_values(by=['Gols oficiais', 'Gols/j', 'Gols (total)'], ascending=False)
    df = df.reset_index(drop=True)
    df.index += 1

    st.markdown('## Artilharia')
    st.text('Nota: Gols até 9/10 são considerados não-oficiais (apenas 20% foram contabilizados)')
    st.dataframe(df)
