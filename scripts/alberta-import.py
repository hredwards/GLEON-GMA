#!/usr/bin/python3

import pandas as pd

# Script to import Florida data into pandas DataFrame, format headers,
# and save as a pickle file

alberta = '../data/Alberta_microcystin_lakes2005to2009.csv'
df = pd.read_csv(alberta)

df["STN_NO_NM_LOC"] = df["STN_NO_NM_LOC"].\
    str.replace(r"[-]?.COMPOSITE(.*)", "", regex=True).\
    str.strip()

df['DATETIME'] = pd.to_datetime(df['SAMPLE_DATETIME.1']).\
    dt.strftime('%Y/%m/%d')

df.rename(columns={"M_LATITUDE": "LAT",
                   "M_LONGITUDE": "LONG",
                   "secchi.m": "Secchi Depth (m)",
                   "MC": "Microcysticn (ug/L)",
                   "TP.mg.L": "Total Phosphorous (ug/L)",
                   "TN.mg.L": "Total Nitrogen (ug/L)",
                   "chla.ug.L": "Total Chlorophyll (ug/L)",
                   "Station Type": "Body of Water",
                   "1.0 m Water Temp DegC": "Temperature (degrees celsius)",
                   "STN_NO_NM_LOC": "Body of Water Name"},
          inplace=True)

df = df[["LAT", "LONG", "Secchi Depth (m)", "Microcysticn (ug/L)", "Total Phosphorous (ug/L)", "Total Nitrogen (ug/L)", "Total Chlorophyll (ug/L)", "Body of Water", "Temperature (degrees celsius)", "Body of Water Name", "DATETIME"]]

df.to_pickle('../data/alberta.pkl')