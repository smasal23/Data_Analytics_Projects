# 📊 Global Literacy & Education Trends: An Analytical Study

---

## 📝 Problem Statement

Literacy is a fundamental indicator of human development, economic growth, and social progress. This project analyzes global literacy trends from 1990–2023 by examining adult literacy, youth literacy (male & female), illiterate population, GDP per capita, and average years of schooling.

The objective is to uncover global patterns, gender disparities, regional inequalities, and economic correlations in education data to support policy and development insights.

---

## 🎯 Objectives

- Analyze global adult literacy trends over time  
- Measure youth literacy improvements and gender gaps  
- Calculate illiteracy percentage across countries  
- Examine correlation between literacy and GDP per capita  
- Analyze schooling years vs literacy outcomes  
- Perform SQL-based analytical queries  
- Build an interactive Power BI dashboard  

---

## 📂 Data Sources

Data was collected from **Our World in Data (OWID)**  

### Indicators Used:

- Adult Literacy Rate  
- Youth Literacy Rate (Male & Female)  
- Illiterate Population (Total, Male, Female)  
- GDP per Capita  
- Average Years of Schooling  

All datasets were merged using a composite key:
(country, year)

Data was filtered between 1990–2023 for consistent trend analysis.


## 🔄 Project Workflow

1️⃣ Data Collection (Google Colab – CSV download from OWID)  
2️⃣ Data Cleaning & Preprocessing  
3️⃣ Feature Engineering  
4️⃣ Exploratory Data Analysis (EDA)  
5️⃣ SQL Database Design  
6️⃣ SQL Query Implementation  
7️⃣ Power BI Dashboard Development  

---

## 🧹 Data Cleaning & Preparation

- Removed duplicate records  
- Handled missing values (drop/imputation based on context)  
- Standardized country names  
- Renamed columns for clarity  
- Verified data types  
- Filtered relevant years  
- Validated data integrity  

---

## ⚙️ Feature Engineering

The following derived features were created to enhance analysis:

- **Illiteracy %**  
- **Literacy Gender Gap**  
- **Youth Literacy Average**  
- **GDP per Schooling Year**  
- **Education Index**  
- **Literacy Growth Rate (YoY)**  

These engineered features enabled deeper socio-economic insights.

---

## 📊 Exploratory Data Analysis (EDA)

EDA was conducted following structured investigation principles :  

### 🔍 Univariate Analysis

- Distribution of literacy rates  
- GDP per capita spread  
- Schooling years variation  
- Identification of outliers  

### 🔎 Bivariate Analysis

- GDP vs Literacy correlation  
- Schooling years vs Literacy relationship  
- Male vs Female youth literacy comparison  
- Regional disparity analysis  

### 📈 Key Insights

- Strong positive correlation between GDP per capita and literacy rates  
- Youth literacy improving faster than adult literacy globally  
- Gender literacy gap narrowing in many developing regions  
- Some countries show high schooling years but inefficient literacy outcomes  
- Regional disparities remain significant in parts of Sub-Saharan Africa  

---

## 🗄️ SQL Database Implementation

### Tables Created

- `literacy_rates`  
- `illiteracy_population`  
- `gdp_schooling`  

Each table uses: PRIMARY KEY (country, year)

### Analytical SQL Queries Performed

- Top 5 countries with highest adult literacy (2020)  
- Countries where female youth literacy < 80%  
- Countries with illiteracy % > 20%  
- Ranking by GDP per schooling year  
- Join analysis of literacy vs GDP  
- Gender gap analysis for high GDP countries  

SQL scripts are available inside the `/sql` directory.

---

## 📊 Power BI Dashboard

The Power BI dashboard includes:

### 🌍 Global Trends Page
- Literacy & illiteracy trend comparison  
- Country ranking  

### ⚖ Gender Disparity Page
- Male vs Female youth literacy  
- Gender gap heatmap  

### 💰 Economic Correlation Page
- GDP vs Literacy scatter plot  
- GDP per schooling ranking  

### 🗺 Regional Analysis Page
- Continental comparison  
- Top & Bottom performers  

Interactive filters:
- Country slicer  
- Year slicer  
- Region slicer  

Dashboard file:  
`powerbi_dashboard/literacy_dashboard.pbix`

---

## 📦 Project Deliverables

- 3 Cleaned DataFrames  
- Jupyter Notebook (EDA + Feature Engineering)  
- SQL Table Creation Script  
- SQL Query Script  
- Power BI Dashboard (.pbix)  
- Insight Summary  

---

## 🛠️ Tech Stack

- Python  
- Pandas  
- NumPy  
- Matplotlib  
- Seaborn  
- MySQL  
- Power BI  

---

## 💡 Business Impact

This analysis supports:

- Government education policy planning  
- Budget allocation decisions  
- SDG 4 progress evaluation  
- CSR literacy initiatives  
- Workforce and economic forecasting  

---

## ▶️ How to Run the Project

1. Clone the repository  - git clone <your-repo-link> /n cd global-literacy-project
2. Install dependencies - pip install -r requirements.txt
3. Run Jupyter Notebook for data processing  
4. Execute SQL scripts in MySQL  
5. Open Power BI dashboard and connect to database  

---

## 🏁 Conclusion

The study reveals that literacy improvement strongly aligns with economic growth, yet regional and gender disparities still persist. Targeted educational investment in low-literacy regions can significantly improve socio-economic development.

---

## 📌 Author

Shubham Masal  
Data Analytics Capstone Project  

---