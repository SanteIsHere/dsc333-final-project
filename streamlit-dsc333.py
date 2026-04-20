import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Measuring Foot Traffic at Lansing Building Products")
st.subheader("A Data Science Project by Tyler Gaudino and Asante Frye")
url_lansing = "https://lansingbp.com/wp-content/themes/lansing/images/logo-hi-res.png"

st.image(url_lansing, use_container_width=True)
