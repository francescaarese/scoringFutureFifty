import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DATA THAT NEEDS TO BE USED IS DR DATA
# TO TRIAL, USE EU INVESTMENTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Title of the app
st.title("Future 50 Scoring App")

# Instructions
st.markdown("""
### Instructions:
1. Upload your input company data Excel file.
2. Adjust the weights of scoring parameters as needed in the sidebar.
3. Click "Process Data" to calculate scores and view results.
4. Download the updated Excel file with scores and see the community metrics (median & average).
""")

# Sidebar for weight adjustments
st.sidebar.header("Adjust Weights")
weights = {
    'VC Score': st.sidebar.slider("VC Score Weight", 0.0, 1.0, 0.15, 0.01),
    'Funding Valuation Score': st.sidebar.slider("Funding Valuation Score Weight", 0.0, 1.0, 0.3, 0.01),
    'Raised Score': st.sidebar.slider("Raised Score Weight", 0.0, 1.0, 0.2, 0.01),
    'Recent Financing Score': st.sidebar.slider("Recent Financing Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Company Growth Score': st.sidebar.slider("Company Growth Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Emerging and Verticals Score': st.sidebar.slider("Emerging and Verticals Score Weight", 0.0, 1.0, 0.1, 0.01),
    'HQ City Score': st.sidebar.slider("HQ City Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Founders Genders Score': st.sidebar.slider("Founders Genders Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Founders Is Serial Score': st.sidebar.slider("Founders Is Serial Score Weight", 0.0, 1.0, 0.1, 0.01)
}

# Function to load Top VCs from a file
def load_top_vcs(file_path="VCtop_latest.txt"):
    try:
        with open(file_path, 'r') as file:
            return {line.strip() for line in file}
    except FileNotFoundError:
        st.error(f"Could not find the Top VCs file at {file_path}. Please ensure the file is available.")
        st.stop()

# Load Top VCs
TOP_VCS = load_top_vcs()



# File uploader
uploaded_file = st.file_uploader("Upload Company Data Excel File", type=["xlsx"])

# Helper function to parse employee history
def parse_employee_data(row):
    try:
        if isinstance(row, str):
            entries = row.split(', ')
            return {int(entry.split(': ')[0]): int(entry.split(': ')[1]) for entry in entries}
    except (ValueError, IndexError):
        pass  # Ignore invalid rows
    return {}  # Return an empty dictionary for invalid or missing data

# Function to calculate growth between two years
def calculate_growth(data, start_year):
    years = sorted(data.keys(), reverse=True)  # Sort descending
    recent_years = [year for year in years if year <= start_year][:5]
    if len(recent_years) < 2:
        return None  # Not enough data to calculate growth
    first_year = recent_years[-1]
    last_year = recent_years[0]
    return ((data[last_year] - data[first_year]) / data[first_year]) * 100

# Function to add 'growth to 2024' column
def add_growth_column(df, starting_year):
    if 'EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)' not in df.columns:
        st.error("The required column 'EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)' is missing.")
        st.stop()

    df['Parsed Data'] = df['EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)'].apply(parse_employee_data)
    df['growth to 2024'] = df['Parsed Data'].apply(lambda x: calculate_growth(x, starting_year))
    return df

# Define scoring functions
def score_vc(company):
    active_investors = company.get('ALL INVESTORS', '').split(',')
    count = sum(vc.strip() in TOP_VCS for vc in active_investors)
    return 10 if count > 1 else 8 if count == 1 else 0

def score_funding_valuation(company):
    valuation = company.get('CURRENT COMPANY VALUATION (EUR)', 0)
    if valuation >= 1000:
        return 10
    elif valuation >= 500:
        return 9
    elif valuation >= 400:
        return 8
    elif valuation > 300:
        return 5
    elif valuation > 200:
        return 4
    elif valuation > 100:
        return 3
    return 0

def score_raised(company):
    raised = company.get('TOTAL AMOUNT RAISED (EUR)', 0)
    if raised >= 100:
        return 10
    elif raised > 90:
        return 8
    elif raised > 80:
        return 7
    elif raised > 50:
        return 6
    elif raised > 30:
        return 5
    elif raised >= 10:
        return 4
    return 0

def recent_financing(company):
    reference_date = datetime.strptime('2024-11-18', '%Y-%m-%d')
    last_financing_date = pd.to_datetime(company.get('DATE'), errors='coerce')
    recent_raise = 0
    if pd.notna(last_financing_date) and last_financing_date > reference_date - timedelta(days=365):
        recent_raise = 5
    return recent_raise

def score_emerging_and_verticals(company):
    verticals = company.get('TAGS', '').lower().split(',')
    target_keywords = {'ai', 'robotics', 'space', 'cybersecurity'}
    return 10 if any(tag.strip() in target_keywords for tag in verticals) else 0

def calculate_overall_score(row):
    total_score = sum(row[score] * weight for score, weight in weights.items())
    return total_score

# Main processing pipeline
if st.button("Process Data"):
    if uploaded_file:
        # Read uploaded data
        df = pd.read_excel(uploaded_file)

        # Add growth column
        df = add_growth_column(df, 2024)

        # Apply scoring functions
        df['VC Score'] = df.apply(score_vc, axis=1)
        df['Funding Valuation Score'] = df.apply(score_funding_valuation, axis=1)
        df['Raised Score'] = df.apply(score_raised, axis=1)
        df['Recent Financing Score'] = df.apply(recent_financing, axis=1)
        df['Emerging and Verticals Score'] = df.apply(score_emerging_and_verticals, axis=1)
        df['Overall Score'] = df.apply(calculate_overall_score, axis=1)

        # Sort by overall score
        df = df.sort_values(by='Overall Score', ascending=False)

        # Display metrics
        median_score = df['Overall Score'].median()
        average_score = df['Overall Score'].mean()
        st.write(f"Median Score: {median_score:.2f}")
        st.write(f"Average Score: {average_score:.2f}")

        # Provide file download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button("Download Results", output, "company_scores.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Please upload the company data file.")

