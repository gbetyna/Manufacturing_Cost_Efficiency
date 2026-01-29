Manufacturing Cost Efficiency Analysis

End-to-End Data Analysis & BI Project

🇵🇱 Opis projektu (PL)
🎯 Cel projektu

Celem projektu jest analiza efektywności kosztowej produkcji oraz identyfikacja czynników wpływających na koszt jednostkowy dobrego wyrobu (Cost per Good Unit).
Projekt łączy analizę danych, SQL Server oraz Power BI, odwzorowując realny proces analityczny stosowany w środowisku produkcyjnym.

🧩 Zakres projektu

Projekt obejmuje pełny pipeline analityczny:

Generowanie i eksploracja danych (Python)

Warstwa danych i czyszczenie (SQL Server)

Warstwa decyzyjna i wizualizacja (Power BI)

🛠️ Technologie

Python (pandas, numpy, matplotlib, seaborn)

SQL Server (Developer Edition)

Power BI Desktop

Git / GitHub

## 📁 Struktura projektu

```text
MANUFACTURING_COST_EFFICIENCY/
├── data/
│   └── cost_efficiency_data.csv
├── src/
│   ├── data_generation.py
│   └── eda.py
├── sql/
│   └── 01_load_clean_and_kpi.sql
├── power_bi/
│   └── manufacturing_cost_efficiency.pbix
├── reports/
│   ├── figures/
│   │   ├── hist_cost_per_good_unit.png
│   │   ├── box_cost_good_by_plant.png
│   │   ├── scatter_efficiency_vs_costgood.png
│   │   └── corr_heatmap.png
│   └── tables/
│       ├── avg_metrics_by_plant.csv
│       ├── avg_metrics_by_line.csv
│       └── correlation_matrix.csv
└── README.md
```



📊 Analiza danych (EDA – Python)

W folderze reports/ znajdują się:

rozkłady zmiennych (koszt, wydajność, czas cyklu),

analizy porównawcze (plant, line, shift, product family),

analizy zależności (scatter plots, korelacje),

tabele agregujące KPI (CSV).

EDA pozwoliła:

zidentyfikować czynniki wpływające na koszt,

potwierdzić zależności między wydajnością, scrapem i downtime,

przygotować dane do warstwy SQL i BI.

🗄️ Warstwa danych (SQL Server)

Dane zostały załadowane do SQL Server.

Utworzono warstwę CLEAN (dbo.cost_efficiency_clean).

SQL pełni rolę warstwy analitycznej, gotowej do BI i raportowania.

Skrypt: sql/01_load_clean_and_kpi.sql.

📈 Dashboard (Power BI)

Finalnym elementem projektu jest dashboard decyzyjny w Power BI, zawierający m.in.:

KPI:

Avg Cost per Good Unit

Cost Improvement % vs Benchmark

Analizy:

Cost per Good Unit by Plant

interaktywne filtrowanie (plant / line / shift – opcjonalnie)

Dashboard odpowiada na pytania:

Jaki jest aktualny koszt jednostkowy?

Czy koszt jest lepszy czy gorszy od benchmarku?

Gdzie powstają największe różnice kosztowe?

📌 Kluczowe wnioski biznesowe

Koszt jednostkowy dobrego wyrobu jest ~27% niższy od benchmarku.

Widoczne są różnice kosztowe pomiędzy zakładami produkcyjnymi.

Wydajność, scrap oraz downtime mają istotny wpływ na koszt końcowy.

🧠 Wartość projektu

Projekt pokazuje:

myślenie analityczne i kosztowe,

umiejętność budowy pełnego pipeline’u danych,

praktyczne wykorzystanie SQL + Power BI w analizie produkcyjnej.

🇬🇧 Project Description (EN)
🎯 Project Goal

The goal of this project is to analyze manufacturing cost efficiency and identify key drivers of Cost per Good Unit.
The project replicates a real-world analytical workflow combining Python, SQL Server, and Power BI.

🧩 Project Scope

The project covers a complete analytical pipeline:

Data generation and exploratory analysis (Python)

Data cleaning and analytical layer (SQL Server)

Decision-making and visualization layer (Power BI)

🛠️ Tech Stack

Python (pandas, numpy, matplotlib, seaborn)

SQL Server (Developer Edition)

Power BI Desktop

Git / GitHub

📊 Data Analysis (EDA)

The reports/ folder contains:

distributions, boxplots, scatter plots,

correlation analysis,

aggregated KPI tables (CSV).

EDA was used to:

identify cost drivers,

validate relationships between efficiency, scrap, and downtime,

prepare clean analytical data for BI.

🗄️ Data Layer (SQL Server)

Data stored in SQL Server.

Clean analytical table: dbo.cost_efficiency_clean.

SQL acts as a central analytical layer.

Script: 01_load_clean_and_kpi.sql.

📈 Power BI Dashboard

The final Power BI dashboard includes:

KPIs

Avg Cost per Good Unit

Cost Improvement % vs Benchmark

Analysis

Cost per Good Unit by Plant

The dashboard answers:

What is the current unit cost?

Is performance better or worse than benchmark?

Where do cost differences originate?

📌 Key Business Insights

Unit cost is ~27% better than benchmark.

Cost differences are visible across plants.

Efficiency, scrap, and downtime significantly impact total cost.

🧠 Project Value

This project demonstrates:

cost-focused analytical thinking,

end-to-end data pipeline design,

practical BI and SQL skills in a manufacturing context.
