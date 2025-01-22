import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Title of the app
st.title("FUTURE 50 Scoring App")

# Instructions
st.markdown("""
### Instructions:
1. Upload your input company data Excel file (with the required columns).
2. Ensure the VCtop.txt file containing the Top VCs list is stored in the same directory as this app.
3. Adjust the weights of scoring parameters as needed.
4. Click "Process Data" to calculate scores and view results.
5. Download the updated Excel file with scores and see the community metrics (median & average).
""")

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

# File Upload
uploaded_file = st.file_uploader("Upload Company Data Excel File", type=["xlsx"])

# Sidebar for weight adjustments
st.sidebar.header("Adjust Weights")
weights = {
    'VC Score': st.sidebar.slider("VC Score Weight", 0.0, 1.0, 0.15, 0.01),
    'Funding Valuation Score': st.sidebar.slider("Funding Valuation Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Raised Score': st.sidebar.slider("Raised Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Recent Financing Score': st.sidebar.slider("Recent Financing Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Company Growth Score': st.sidebar.slider("Company Growth Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Emerging and Verticals Score': st.sidebar.slider("Emerging and Verticals Score Weight", 0.0, 1.0, 0.1, 0.01),
    'HQ City Score': st.sidebar.slider("HQ City Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Founders Genders Score': st.sidebar.slider("Founders Genders Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Founders Is Serial Score': st.sidebar.slider("Founders Is Serial Score Weight", 0.0, 1.0, 0.1, 0.01),
    'Founders Count Score': st.sidebar.slider("Founders Count Score Weight", 0.0, 1.0, 0.1, 0.01),
}

# Function to validate required columns
def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"The following columns are missing in the input file: {', '.join(missing_columns)}")
        st.stop()

# Helper function to parse employee history
def parse_employee_data(row):
    if isinstance(row, str):
        entries = row.split(';')
        return {int(entry.split(':')[0]): int(entry.split(':')[1]) for entry in entries if ': ' in entry}
    return {}

# Function to add 'growth to 2024' column
def add_growth_column(df, starting_year):
    def calculate_growth(parsed_data, start_year):
        years = sorted(parsed_data.keys(), reverse=True)
        recent_years = [year for year in years if year <= start_year][:5]
        if len(recent_years) < 2:
            return None
        first_year = recent_years[-1]
        last_year = recent_years[0]
        return ((parsed_data[last_year] - parsed_data[first_year]) / parsed_data[first_year]) * 100

    df['Parsed Data'] = df['EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)'].apply(parse_employee_data)
    df['growth to 2024'] = df['Parsed Data'].apply(lambda x: calculate_growth(x, starting_year))
    return df

# Scoring functions
def score_vc(company):
    all_investors = set(str(company.get('ALL INVESTORS', '')).split(','))
    count = sum(vc.strip() in TOP_VCS for vc in all_investors if vc.strip())
    return 10 if count > 1 else 8 if count == 1 else 0

def score_funding_valuation(company):
    valuation = pd.to_numeric(company.get('CURRENT COMPANY VALUATION (EUR)', 0), errors='coerce')
    if pd.isna(valuation): return 0
    if valuation >= 1000000: return 10
    elif valuation >= 500000: return 9
    elif valuation >= 400000: return 8
    elif valuation > 300000: return 5
    elif valuation > 200000: return 4
    elif valuation > 100000: return 3
    return 0

def score_raised(company):
    raised = company.get('TOTAL AMOUNT RAISED (EUR)', 0)
    if raised >= 100000000: return 10
    elif raised > 90000000: return 8
    elif raised > 80000000: return 7
    elif raised > 50000000: return 6
    elif raised > 30000000: return 5
    elif raised >= 10000000: return 4
    return 0

def recent_financing(company):
    reference_date = datetime.strptime('Nov-24', '%b-%y')
    last_financing_date = pd.to_datetime(company.get('DATE'), format='%b-%y', errors='coerce')
    recent_raise = 0
    if pd.notna(last_financing_date) and last_financing_date > reference_date - timedelta(days=365):
        recent_raise = 5
    large_financing = company.get('AMOUNT RAISED THIS ROUND (EUR M)', 0) > 20
    return recent_raise + (5 if large_financing else 0)

def score_emerging_and_verticals(company):
    tags = str(company.get('TAGS', '')).strip().lower()
    target_keywords = {'ai', 'robotics', 'energy', 'biotechnology', 'space'}
    verticals = [v.strip() for v in tags.split(',')]
    return 10 if any(keyword in verticals for keyword in target_keywords) else 0

def score_hq_city(company):
    hq_city = company.get('HQ CITY', '').strip().lower()
    if hq_city in ['oxford', 'cambridge']: return 5
    elif hq_city != 'london': return 10
    return 0

def score_founders_genders(company):
    genders = str(company.get('FOUNDERS GENDERS', '')).strip().lower()
    return 10 if 'female' in genders.split(';') else 0

def score_founders_is_serial(company):
    is_serial = company.get('FOUNDERS IS SERIAL', '')
    if isinstance(is_serial, str):
        serial_list = [entry.strip().lower() for entry in is_serial.split(',')]
        return 10 if 'yes' in serial_list else 0
    return 0

def count_founders_score(company):
    founders = str(company.get('FOUNDERS', '')).strip()
    num_founders = len([f.strip() for f in founders.split(',') if f.strip()])
    return 10 if num_founders > 1 else 0

def calculate_overall_score(row, weights):
    return sum(row[key] * weights[key] for key in weights if key in row)

# Processing logic
if st.button("Process Data"):
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Validate required columns
        required_columns = [
            'ALL INVESTORS', 'CURRENT COMPANY VALUATION (EUR)', 'TOTAL AMOUNT RAISED (EUR)',
            'DATE', 'TAGS', 'LAUNCH YEAR', 'HQ CITY', 'FOUNDERS GENDERS', 
            'FOUNDERS IS SERIAL', 'FOUNDERS'
        ]
        validate_columns(df, required_columns)

        # Add growth column
        if 'EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)' in df.columns:
            df = add_growth_column(df, 2024)
        else:
            st.error("The input file must contain an 'Employee History' column.")
            st.stop()

        # Apply scoring functions
        df['VC Score'] = df.apply(score_vc, axis=1)
        df['Funding Valuation Score'] = df.apply(score_funding_valuation, axis=1)
        df['Raised Score'] = df.apply(score_raised, axis=1)
        df['Recent Financing Score'] = df.apply(recent_financing, axis=1)
        df['Company Growth Score'] = df.apply(evaluate_company_growth, axis=1)
        df['HQ City Score'] = df.apply(score_hq_city, axis=1)
        df['Emerging and Verticals Score'] = df.apply(score_emerging_and_verticals, axis=1)
        df['Founders Genders Score'] = df.apply(score_founders_genders, axis=1)
        df['Founders Is Serial Score'] = df.apply(score_founders_is_serial, axis=1)
        df['Founders Count Score'] = df.apply(count_founders_score, axis=1)

        # Calculate overall score
        df['Overall Score'] = df.apply(lambda x: calculate_overall_score(x, weights), axis=1)

        # Sort the DataFrame
        df = df.sort_values(by='Overall Score', ascending=False)

        # Display metrics
        st.write(f"Median Overall Score: {df['Overall Score'].median():.2f}")
        st.write(f"Average Overall Score: {df['Overall Score'].mean():.2f}")

        # Export and download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Download Updated Data",
            data=output,
            file_name="company_scores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Please upload the company data file.")








