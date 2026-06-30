import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

# --- Page Config ---
st.set_page_config(page_title="CarVenu - Price Predictor", page_icon="🚗")

# --- Helpers (From your original code) ---
def format_value(value):
    if value >= 10_000_000:
        return f"₹ {value/10_000_000:.2f} Cr"
    elif value >= 100_000:
        return f"₹ {value/100_000:.2f} Lakhs"
    else:
        return f"₹ {int(value):,}"

# --- Load Model & Scaler ---
# Using the paths from your folder structure
@st.cache_resource # This keeps the model in memory so it doesn't reload every time
def load_assets():
    with open('./saved_models/RandomForestRegressor.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('./saved_scaling/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler

try:
    model, scaler = load_assets()
except FileNotFoundError:
    st.error("Model or Scaler files not found. Please check 'saved_models' and 'saved_scaling' folders.")

# --- App UI ---
st.title("🚗 CarVenu Price Predictor")
st.markdown("Enter car details to estimate the fair market price.")

# We create two columns for the input form
col1, col2 = st.columns(2)

with col1:
    vehicle_age = st.number_input("Vehicle Age (Years)", min_value=0, max_value=30, value=5)
    km_driven = st.number_input("Kilometers Driven", min_value=0, value=20000, step=1000)
    mileage = st.number_input("Mileage (kmpl)", min_value=0.0, value=18.0)
    engine = st.number_input("Engine Capacity (CC)", min_value=600, max_value=7000, value=1200)

with col2:
    max_power = st.number_input("Max Power (bhp)", min_value=30.0, value=85.0)
    seats = st.selectbox("Seats", [2, 4, 5, 7, 8, 10], index=2)
    seller_type = st.selectbox("Seller Type", ["Dealer", "Individual", "Trustmark Dealer"])
    fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG", "LPG", "Electric"])

transmission_type = st.radio("Transmission Type", ["Manual", "Automatic"], horizontal=True)

# --- Prediction Logic ---
if st.button("Predict Selling Price", type="primary", use_container_width=True):
    
    # 1. Prepare the input Dictionary (Must match the columns of your X_train)
    # The order and columns must be EXACTLY what the model saw during training
    input_dict = {
        'vehicle_age': vehicle_age,
        'km_driven': km_driven,
        'mileage': mileage,
        'engine': engine,
        'max_power': max_power,
        'seats': seats,
        'seller_type_Dealer': 1 if seller_type == "Dealer" else 0,
        'seller_type_Individual': 1 if seller_type == "Individual" else 0,
        'seller_type_Trustmark Dealer': 1 if seller_type == "Trustmark Dealer" else 0,
        'fuel_type_CNG': 1 if fuel_type == "CNG" else 0,
        'fuel_type_Diesel': 1 if fuel_type == "Diesel" else 0,
        'fuel_type_Electric': 1 if fuel_type == "Electric" else 0,
        'fuel_type_LPG': 1 if fuel_type == "LPG" else 0,
        'fuel_type_Petrol': 1 if fuel_type == "Petrol" else 0,
        'transmission_type_Automatic': 1 if transmission_type == "Automatic" else 0,
        'transmission_type_Manual': 1 if transmission_type == "Manual" else 0,
    }

    # Convert to DataFrame
    input_df = pd.DataFrame([input_dict])

    # 2. Scale the input using the loaded scaler
    input_scaled = scaler.transform(input_df)

    # 3. Predict
    prediction = model.predict(input_scaled)[0]

    # 4. Display Result
    st.divider()
    st.subheader("Estimated Price")
    st.title(format_value(prediction))
    
    # Visual feedback
    if prediction > 500000:
        st.balloons()