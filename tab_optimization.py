from ortools.linear_solver import pywraplp
import numpy as np
import streamlit as st
import pandas as pd

def soma_ovrs(dic_jog_ovr, todos):
    ovrs = []
    soma = 0
    for t in todos:
        pos = [dic_jog_ovr[el] for el in t]
        ovrs.append(pos)
        soma += sum(pos)
    return soma, ovrs

def modelagem(todos, idxs_pos, P, n_pos, ovrs, media, junta, separa, minutos_max):
    solver = pywraplp.Solver.CreateSolver('SCIP')

    x = {}
    for i in range(len(todos)):
        for idx in idxs_pos[i]:
            for j in P:
                x[(i, idx, j)] = solver.BoolVar(f'x_{i}_{idx}_{j}')
    
    s = {j: solver.NumVar(0, solver.infinity(), f's_{j}') for j in P}
    z = {j: solver.NumVar(0, solver.infinity(), f'z_{j}') for j in P}
    alpha = solver.NumVar(0, solver.infinity(), 'alpha')

    solver.Minimize(alpha)

    for n in range(len(todos)):
        for j in P:
            solver.Add(sum(x[(n, i, j)] for i in idxs_pos[n]) == len(idxs_pos[n]) / len(P))
        for i in idxs_pos[n]:
            solver.Add(sum(x[(n, i, j)] for j in P) == 1)
    
    for j in P:
        solver.Add(s[j] == sum(sum(ovrs[k][i] * x[(k, i, j)] for i in idxs_pos[k]) for k in n_pos))
        solver.Add(media - s[j] <= z[j])
        solver.Add(s[j] - media <= z[j])
    
    for j in P:
        solver.Add(z[j] <= alpha)
    
    if junta[0]:
        for el in junta:
            juntos(el[0], el[1], todos, P, solver, x)
    if separa[0]:
        for el in separa:
            separados(el[0], el[1], todos, P, solver, x)

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        st.error('Não foi possível encontrar uma solução.')
    
    s_values = {j: s[j].solution_value() for j in P}
    x_values = {(i, idx, j): x[(i, idx, j)].solution_value() for i in range(len(todos)) for idx in idxs_pos[i] for j in P}
    return solver, s_values, x_values

def monta_times(todos, idxs_pos, P, n_pos, x_values):
    tam = sum(len(pos) for pos in todos)
    times = np.empty((tam // len(P), 0), dtype=object)
    for p in P:
        a = np.empty((tam // len(P), 1), dtype=object)
        loc = 0
        for n in n_pos:
            v = []
            for k in idxs_pos[n]:
                v.append(x_values[(n, k, p)])
            ps = np.array(todos[n])[np.round(v).astype(bool)]
            a[loc:loc + len(ps), 0] = ps
            loc += len(ps)
        times = np.hstack((times, a))
    return times

def modela(dic_jog_ovr, todos, n_times, separa=[[]], junta=[[]], minutos_max=1/12):
    junta = junta if junta else [[]]
    separa = separa if separa else [[]]
    soma, ovrs = soma_ovrs(dic_jog_ovr, todos)
    idxs_pos = [list(range(len(p))) for p in todos]
    P = list(range(n_times))
    media = soma / n_times
    n_pos = list(range(len(todos)))
    solver, s_values, x_values = modelagem(todos, idxs_pos, P, n_pos, ovrs, media, junta, separa, minutos_max)
    times = monta_times(todos, idxs_pos, P, n_pos, x_values)
    return times, s_values

def separados(j1, j2, todos, P, solver, x):
    x1, x2 = -1, -1
    for i in range(len(todos)):
        if j1 in todos[i]:
            x1 = i
        if j2 in todos[i]:
            x2 = i
    
    if x1 >= 0 and x2 >= 0:
        for j in P:
            solver.Add(x[(x1, todos[x1].index(j1), j)] + x[(x2, todos[x2].index(j2), j)] <= 1)

def juntos(j1, j2, todos, P, solver, x):
    x1, x2 = -1, -1
    for i in range(len(todos)):
        if j1 in todos[i]:
            x1 = i
        if j2 in todos[i]:
            x2 = i
    
    if x1 >= 0 and x2 >= 0:
        for j in P:
            solver.Add(x[(x1, todos[x1].index(j1), j)] == x[(x2, todos[x2].index(j2), j)])

def select_players(dict_ovr):
    all_names = sorted(list(dict_ovr.keys()))
    with st.expander('Selecione os jogadores'):
        selected = st.multiselect('Quem vai jogar essa semana?:', all_names)
        return selected

def positions(names, n_times):
    with st.expander('Escolha as posições de cada um (opcional)'):
        pos = []
        pos_names = []
        selected_players = []

        group_count = st.number_input("Quantas posições diferentes você quer criar?", min_value=1, value=1)
        for i in range(group_count):
            pos_name = st.text_input(f"Digite o nome da posição {i+1} (atacante, zagueiro, etc.)", key=f"Nome posição {i}", value=f"Jogador")
            default = None if group_count > 1 else names

            available_players = [player for player in names if player not in selected_players]
            group = st.multiselect(pos_name, key=f"Posição {i}", default=default, options=available_players)

            pos.append(group)
            pos_names.append(pos_name)

            selected_players.extend(group)

        pos_names_final = []
        for p in pos:
            if len(p) % n_times != 0:
                st.markdown(f'Cuidado! Tem {len(p)} {pos_names[pos.index(p)]}. É necessário que o número de jogadores em cada posição seja múltiplo de {n_times}.')
            pos_names_final.extend([pos_names[pos.index(p)]] * int(len(p) / n_times))

        return pos, pos_names_final


def pair_constraints(names):
    with st.expander('Escolha pares de jogadores que você quer juntar ou separar (opcional)'):
        junta = []
        group_count = st.number_input("Quantos pares de jogadores você quer juntar?", min_value=0, value=0)
        for i in range(group_count):
            group = st.multiselect(f"Par junto #{i+1}", options=names, key = f"Juntos {i}")
            junta.append(group)
        
        separa = []
        group_count = st.number_input("Quantos pares de jogadores você quer separar?", min_value=0, value=0)
        for i in range(group_count):
            group = st.multiselect(f"Par separado #{i+1}", options=names, key = f"Separados {i}")
            separa.append(group)
        return junta, separa
    
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def ovr_bars(names, dict_ovr):
    with st.expander('Escolha os OVRs de cada um'):
        new_dict = {}
        for name in names:
            default = dict_ovr.get(name, 0)
            ovr = st.slider(name, min_value=0., max_value=100., value=default, step=.1, format='%.1f')
            new_dict[name] = ovr

        # csv = convert_df(pd.DataFrame(new_dict, index=['OVR'])) # está invertido linha e coluna
        df = pd.DataFrame(new_dict, index=['OVR']).T
        csv = convert_df(df)

        st.download_button('Salvar seus OVRs em CSV', csv, 'ovrs.csv', 'text/csv')
        return new_dict

def bate_times():
    n_times = st.number_input('Número de times', value=3, min_value=2)
    with st.expander('Importe seu arquivo CSV com OVRs customizados (opcional)'):
        uploaded_csv = st.file_uploader("Escolha um arquivo CSV", type='csv')
    dict_ovr = pd.read_csv('data/cond ovrs.csv', index_col=0).to_dict()['OVR'] if uploaded_csv is None else pd.read_csv(uploaded_csv, index_col=0).to_dict()['OVR']
    names = select_players(dict_ovr)
    pos, pos_names = positions(names, n_times)
    junta, separa = pair_constraints(names)
    dict_ovr = ovr_bars(names, dict_ovr)
    if st.button('Bater Times', icon = ':material/shuffle:'):
        times, s_values = modela(dict_ovr, pos, n_times, separa, junta)
        cols = ['Vermelho', 'Azul', 'Branco'][:n_times] if n_times <= 3 else ['Time ' + str(i+1) for i in range(n_times)]
        times = pd.DataFrame(times, columns=cols, index=pos_names)
        st.dataframe(times)
        
        if n_times <= 3:
            st.markdown('Somatório dos OVRs (Força do time)')
            st.markdown(f' :red_circle: : {s_values[0]:.1f}')
            st.markdown(f' :large_blue_circle: : {s_values[1]:.1f}')
            st.markdown(f' :white_circle: : {s_values[2]:.1f}') if n_times >= 3 else None
