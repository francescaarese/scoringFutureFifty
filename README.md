# FUTURE 50 Scoring App - README

This application, built with Streamlit, calculates scores for companies based on various attributes provided in an Excel file. The scores are computed using specific rules and weighting factors defined in the code. The app generates an updated Excel file with scores for each company, sorted by an overall score, and displays summary statistics like median and average scores.

---

## Features:
1. **Upload and Process Company Data**: Accepts an Excel file with company data, computes scores, and outputs results.
2. **Dynamic Weight Adjustments**: Allows users to modify weights for scoring criteria via the sidebar.
3. **Scoring Metrics**: Includes metrics like VC Score, Funding Valuation Score, Growth Score, and more.
4. **Download Updated Data**: Generates a downloadable Excel file with calculated scores.

---

## How to Prepare Input Data:
To use this app, you need to download company data from Dealroom and format it as an Excel file with the following columns (the best way is to export all columns from dealroom in an excel):

### Required Columns:
1. `EMPLOYEES (2016,2017,2018,2019,2020,2021,2022,2023,2024,2025)`:
   - Semicolon-separated employee data for each year.
2. `ALL INVESTORS`:
   - A semicolon-separated list of investors.
3. `FOUNDERS`:
   - A semicolon-separated list of company founders.
4. `FOUNDERS GENDERS`:
   - A semicolon-separated list of founder genders.
5. `TAGS`:
   - A semicolon-separated list of company tags or verticals.
6. `CURRENT COMPANY VALUATION (EUR)`:
   - Numeric values or ranges in EUR for company valuation.
7. `LAUNCH YEAR`:
   - Year the company was founded.
8. `HQ CITY`:
   - City where the company is headquartered.
9. `DATE`:
   - Date of the most recent financing round.
10. `AMOUNT RAISED THIS ROUND (EUR M)`:
    - Amount raised in the most recent financing round, in millions.

---

## How to Download Data from Dealroom:
### Step-by-Step Guide:
1. **Login to Dealroom**:
   - Visit [Dealroom](https://app.dealroom.co/) and log in to your account.
2. **Navigate to Search**:
   - Use the search functionality to find a list of companies you want to analyze.
3. **Customize Columns**:
   - Click on the "Columns" dropdown menu.
   - Select the following columns:
       - Employees
       - Investors
       - Founders
       - Founders Genders
       - Tags
       - Current Company Valuation (EUR)
       - Launch Year
       - HQ City
       - Date (of last financing round)
       - Amount Raised This Round (EUR M)
4. **Export Data**:
   - Click the export button to download the data as an Excel file.
   - Ensure the file is saved as `.xlsx` for compatibility with the app.

---

## How to Use the App:
### Step-by-Step Guide:
1. **Place Top VCs File**:
    - Save a text file named `VCtop_latest.txt` in the same directory as the app. It is already in the github rep.
    - This file should contain a list of top venture capital firms, one per line.

2. **Launch the App**:
    - Run the app using the command: `streamlit run scoring_Streamlit_FFifty.py`.
    - Open the provided URL in your browser.

3. **Upload Data**:
    - Click the **Upload Company Data Excel File** button and select your Excel file.

4. **Adjust Weights**:
    - Use the sidebar sliders to adjust weights for each scoring parameter. Default weights are pre-set.

5. **Process Data**:
    - Click the **Process Data** button.
    - The app will compute scores and display median and average overall scores.

6. **Download Results**:
    - Click the **Download Updated Data** button to download the processed Excel file.

---

## Troubleshooting:
1. **Empty Columns**:
    - Ensure the input Excel file contains complete data in all required columns.
2. **Application Crashes**:
    - Review error messages in Streamlit logs for debugging.
3. **Scores Not Calculated**:
    - Verify the format of input data, especially for semicolon-separated fields.

---

Contact: francesca.areselucini@gmail.com
