import streamlit as st
import pandas as pd
import numpy as np

def get_dates(placares):
    placares['Data str'] = pd.to_datetime(placares['Data']).dt.strftime('%d/%m/%Y')
    dates = placares['Data str'].unique()
    dates = dates[dates != '12/06/2024'] # Dia dos Namorados, não tinham 3 times
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
