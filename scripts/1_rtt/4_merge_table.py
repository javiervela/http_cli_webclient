import pandas as pd
import os

data_dir = "data/1_rtt"
files = [
    "universities.csv",
    "universities_with_coordinates.csv",
    "universities_with_geoip.csv",
    "universities_with_rtt.csv",
]
dfs = [pd.read_csv(os.path.join(data_dir, fname)) for fname in files]
merged = dfs[0]
for df in dfs[1:]:
    common_cols = list(set(merged.columns) & set(df.columns))
    merged = pd.merge(merged, df, how="outer", on=common_cols)
merged = merged.loc[:, ~merged.columns.duplicated()]

merged = merged[
    ~merged["University"].isin(
        [
            "King's College London",
            "University of Oxford",
            "University of Berlin",
        ]
    )
]

merged.to_csv(os.path.join(data_dir, "universities_merged.csv"), index=False)
merged["Country"] = merged["Country"].replace(
    {
        "Schweiz/Suisse/Svizzera/Svizra": "Switzerland",
        "New Zealand / Aotearoa": "New Zealand",
    }
)


latex_columns = [
    "University",
    "Domain",
    "Latitude",
    "Longitude",
    "Country",
]

latex_df = merged[latex_columns].fillna("---")

column_format = "p{3cm}" + "p{3cm}" + "lll"

latex_table = latex_df.to_latex(
    index=False,
    escape=True,
    column_format=column_format,
    longtable=False,
    caption=None,
)

rowcolors = "\\rowcolors{2}{gray!15}{white}\n"
latex_table = latex_table.replace("\\begin{tabular}", rowcolors + "\\begin{tabular}")

with open(os.path.join(data_dir, "universities_table.tex"), "w") as f:
    f.write(latex_table)

rtt_columns = [
    "Domain",
    "Country",
    "RTT_min",
    "RTT_max",
    "RTT_median",
    "RTT_mean",
]
rtt_df = merged[rtt_columns].fillna("---")

for col in ["RTT_min", "RTT_max", "RTT_median"]:
    rtt_df[col] = rtt_df[col].apply(
        lambda x: f"{int(x)}" if pd.notnull(x) and x != "---" else "---"
    )
rtt_df["RTT_mean"] = rtt_df["RTT_mean"].apply(
    lambda x: f"{float(x):.2f}" if pd.notnull(x) and x != "---" else "---"
)

rtt_column_format = "p{3cm}" + "lllrrrr"
rtt_latex_table = rtt_df.to_latex(
    index=False,
    escape=True,
    column_format=rtt_column_format,
    longtable=False,
    caption=None,
)
rtt_latex_table = rtt_latex_table.replace(
    "\\begin{tabular}", rowcolors + "\\begin{tabular}"
)

figure_caption = "\\caption{University RTT statistics.}"
rtt_latex_table = (
    "\\begin{figure}[htbp]\n" + rtt_latex_table + figure_caption + "\n\\end{figure}\n"
)

with open(os.path.join(data_dir, "universities_rtt_table.tex"), "w") as f:
    f.write(rtt_latex_table)
