import streamlit as st
from streamlit_facade import StreamlitFacade
import logging

logging.basicConfig(level=logging.INFO)
st.set_page_config(layout="wide")

obj = StreamlitFacade()

st.title("Coin")
st.write(obj.get_coin_price("BTC"))
