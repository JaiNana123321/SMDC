import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# Set page title and favicon
st.set_page_config(page_title="Delusion Calculator", page_icon=":money_with_wings:")

# App title and description
st.title("Delusion Calculator")
st.write("Analyze stocks and get insights on whether to short them or not.")


# Function to load data from JSON file
@st.cache(allow_output_mutation=True)
def load_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data)


# Load data from JSON file
df = load_data()

# Sort option
sort_option = st.selectbox("Sort companies by:",
                           ["Alphabetical (A-Z)", "Alphabetical (Z-A)", "Hype Score (High to Low)",
                            "Hype Score (Low to High)"])

if sort_option == "Alphabetical (A-Z)":
    df = df.sort_values("company", ascending=True)
elif sort_option == "Alphabetical (Z-A)":
    df = df.sort_values("company", ascending=False)
elif sort_option == "Hype Score (High to Low)":
    df = df.sort_values("hype_score", ascending=False)
else:
    df = df.sort_values("hype_score", ascending=True)

# Search bar
search_query = st.text_input("Search for a company")

# Initialize selected companies
selected_companies = []

# Display companies in a list format
company_list = st.empty()
with company_list.container():
    for _, row in df.iterrows():
        if search_query.lower() in row['company'].lower() or not search_query:
            panel_style = """
            <style>
            .panel {
                background-color: #f0f0f0; 
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            </style>
            """
            st.markdown(panel_style, unsafe_allow_html=True)

            cols = st.columns([4, 1, 1])
            cols[0].markdown(f"<div class='panel'>{row['company']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='panel'>Hype Score: {row['hype_score']}</div>", unsafe_allow_html=True)
            if cols[2].checkbox(" ", key=row['company']):
                selected_companies.append(row["company"])

# Analyze button
if st.button("Analyze"):
    if selected_companies:
        # Display selected companies
        st.subheader("Selected Companies")
        for company in selected_companies:
            st.write(f"- {company}")

        # Generate analysis based on the number of selected companies
        if len(selected_companies) == 1:
            company = selected_companies[0]
            comment = df.loc[df["company"] == company, "comment"].values[0]
            st.subheader(f"{company} Analysis")
            st.write(f"Description: {comment}")
            st.write(f"Recommendation: {'Short' if np.random.rand() < 0.5 else 'Do not short'}")
        elif len(selected_companies) >= 2:
            st.subheader("Comparison Analysis")
            for company in selected_companies:
                comment = df.loc[df["company"] == company, "comment"].values[0]
                st.write(f"{company}: {comment}")
            st.write(f"Historical Competitors: {'Yes' if np.random.rand() < 0.5 else 'No'}")
            st.write(f"Better option to short: {np.random.choice(selected_companies)}")

        # Create a square plot with selected companies
        fig, ax = plt.subplots(figsize=(6, 6))
        for company in selected_companies:
            hype = df.loc[df["company"] == company, "hype_score"].values[0]
            valuation = df.loc[df["company"] == company, "valuation"].values[0]
            ax.scatter(valuation, hype, label=company)
        ax.axvline(5, color='gray', linestyle='--', linewidth=0.5)
        ax.axhline(5, color='gray', linestyle='--', linewidth=0.5)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xlabel("Valuation")
        ax.set_ylabel("Hype Score")
        ax.set_title("Stock Analysis")
        ax.legend()

        # Display the scatter plot
        st.pyplot(fig)
    else:
        st.write("No companies selected.")