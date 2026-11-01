# Agriculture Data Visualization Dashboard with Storytelling

An interactive Streamlit dashboard for exploring Indian crop production data.

## Dashboard pages
1. **Overview** – KPI cards, annual production, season contribution and leading crops.
2. **Production Trends** – yearly production trend and year-wise summary.
3. **Crop Insights** – top crops, production contribution and crop summary.
4. **State Analysis** – state-wise production, cultivated area and area-versus-production scatter plot.

## Global filters
The sidebar filters State, District, Crop Year range, Season and Crop. The same filtered dataset is used by every KPI and chart, so selections update the dashboard together.

## Required CSV columns
`State_Name`, `District_Name`, `Crop_Year`, `Season`, `Crop`, `Area`, `Production`

Place `crop_production.csv` in the same folder as `app.py`. Alternatively, upload a CSV from the sidebar.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, and `crop_production.csv` to a GitHub repository.
2. Open https://share.streamlit.io/
3. Select **New app**.
4. Choose the repository, branch and `app.py`.
5. Select **Deploy**.

## Notes
- The app describes patterns visible in the dataset; it does not prove the causes behind changes.
- Units for Area and Production depend on the source dataset.
- Check missing values and source definitions before presenting conclusions.
