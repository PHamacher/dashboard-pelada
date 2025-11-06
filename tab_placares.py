import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

def get_dates(placares):
    placares['Data str'] = pd.to_datetime(placares['Data']).dt.strftime('%d/%m/%Y')
    dates = placares['Data str'].unique()
    invalid_dates = ['12/06/2024', '30/10/2025'] # Dias sem 3 times
    dates = dates[~np.isin(dates, invalid_dates)]
    dates = np.append(dates, 'Todas')
    dates = dates[::-1]
    return (placares, dates)

def show_placares(placares, date):
    plac_date = placares[placares['Data str'] == date]

    red_team = np.sort(plac_date.iloc[0, 2:8].dropna().values)
    blue_team = np.sort(plac_date.iloc[1, 2:8].dropna().values)
    white_team = np.sort(plac_date.iloc[2, 2:8].dropna().values)

    text_red = '#### :red_circle: ' + ', '.join(red_team)
    text_blue = '#### :large_blue_circle: ' + ', '.join(blue_team)
    text_white = '#### :white_circle: ' + ', '.join(white_team)

    st.markdown(text_red)
    st.markdown(text_blue)
    st.markdown(text_white)


    match1_text = f"#### :red_circle:  {plac_date.iloc[0,:]['A']} x {plac_date.iloc[0,:]['B']} :large_blue_circle:" + f" ({plac_date.iloc[0,:]['Jogos']} jogos)"
    match2_text = f"#### :large_blue_circle:  {plac_date.iloc[1,:]['A']} x {plac_date.iloc[1,:]['B']} :white_circle:" + f" ({plac_date.iloc[1,:]['Jogos']} jogos)"
    match3_text = f"#### :white_circle:  {plac_date.iloc[2,:]['A']} x {plac_date.iloc[2,:]['B']} :red_circle:" + f" ({plac_date.iloc[2,:]['Jogos']} jogos)"


    st.markdown(match1_text)
    st.markdown(match2_text)
    st.markdown(match3_text)

def calc_aggregates(placares):
    placares_color = placares[placares['Data'] > dt.datetime(2024, 6, 12)].copy()

    n = placares_color.shape[0]
    Va = placares_color.iloc[range(0,n,3),:].A.sum()
    Av = placares_color.iloc[range(0,n,3),:].B.sum()
    Ab = placares_color.iloc[range(1,n,3),:].A.sum()
    Ba = placares_color.iloc[range(1,n,3),:].B.sum()
    Bv = placares_color.iloc[range(2,n,3),:].A.sum()
    Vb = placares_color.iloc[range(2,n,3),:].B.sum()

    st.markdown('# Agregado')

    st.markdown(f"#### :red_circle:  {Va} x {Av} :large_blue_circle:")
    st.markdown(f"#### :large_blue_circle:  {Ab} x {Ba} :white_circle:")
    st.markdown(f"#### :white_circle:  {Bv} x {Vb} :red_circle:")
   
    st.markdown('### Saldo')

    st.markdown(f"#### :red_circle:  {Va + Vb - (Av + Bv)}")
    st.markdown(f"#### :large_blue_circle:  {Av + Ab - (Va + Ba)}")
    st.markdown(f"#### :white_circle:  {Ba + Bv - (Ab + Vb)}")

    return
