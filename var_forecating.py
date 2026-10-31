# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from datetime import date

# Load your data
df = pd.read_csv(r"C:\Users\kguke\Documents\WGu\ETF Forecasting\etf_price.csv", parse_dates=['Date'], index_col='Date')

# Optional: sort index
df.sort_index(inplace=True)

# Check data
print(df.head())

#convert to return

returns = df.pct_change().dropna()

print (returns.head())

# Initialize the VAR model
model = VAR(returns)

# Select the optimal lag order
lag_order_results = model.select_order(maxlags=15)
print(lag_order_results.summary())

# Fit the model with optimal lag (you can pick e.g. AIC or BIC)
model_fitted = model.fit(lag_order_results.aic)

print(model_fitted.summary())


# Number of steps ahead
n_forecast =5

# Get the forecast input
forecast_input = returns.values[-model_fitted.k_ar:]

# Forecast returns
forecast = model_fitted.forecast(y=forecast_input, steps=n_forecast)

# Create a DataFrame for the forecast
forecast_df = pd.DataFrame(forecast, index=pd.date_range(returns.index[-1], periods=n_forecast+1, freq='B')[1:], 
                           columns=returns.columns)

print(forecast_df)

forecast_df.plot(figsize=(12, 6))
plt.title('Forecasted Returns (Next 10 Days)')
plt.xlabel('Date')
plt.ylabel('Predicted Return')
plt.grid(True)
plt.show()

forecast_df.to_csv('forecast_returns.csv')

# Ranking sectors

# Step 1: Select the first 5 forecasted days
five_day_forecast = forecast_df.iloc[:5]

# Step 2: Calculate cumulative return for each stock
# Using geometric return: cumulative_return = (1 + r1) * (1 + r2) * ... - 1
cumulative_returns = (1 + five_day_forecast).prod() - 1

# Step 3: Sort stocks by cumulative return
ranked_returns = cumulative_returns.sort_values(ascending=True)

ranked_returns_df = ranked_returns.reset_index()
ranked_returns_df.columns=["Sector","PredictedReturn"]
ranked_returns_df.to_csv ('ranked_returns.csv')

# Step 4: Display results
print("5-Day Forecasted Cumulative Returns:")
print(cumulative_returns)

print("\nRanked Stocks by 5-Day Forecasted Return:")
print(ranked_returns)



########Draw publishing



# Sort sectors by predicted return
df = ranked_returns_df

# === Step 2: Plot ===
fig, ax = plt.subplots(figsize=(7,9))
bars = ax.barh(
    df["Sector"], 
    df["PredictedReturn"]*100,  ##To make it to percentage point 
    #color=["green" if x > 0 else "red" for x in df["PredictedReturn"]]
    color = ["blue" if sector == "spy" else "green" if ret > 0 else "red"
    for sector, ret in zip(df["Sector"], df["PredictedReturn"])])


# Title & labels
today = date.today().strftime("%b %d, %Y")
ax.set_title(f"\nSector ETF 5-Day Predictions \n({today})\n", fontsize=14, weight='bold')
ax.set_xlabel("Predicted Return (%)", fontsize=12)
ax.set_xlim(min(df["PredictedReturn"]*100)-0.2, max(df["PredictedReturn"]*100)+0.2)

# Annotate bars
for bar in bars:
    width = bar.get_width()
    ax.text(width + (0.01 if width > 0 else -0.05),
            bar.get_y() + bar.get_height()/2,
            f"{width:.2f}%", va='center', fontsize=10, weight='bold')

plt.tight_layout()


# Add text box at bottom-left
plt.gca().text(
    0.00, -0.2, "Note: \n1. Provided for informational purposes only; not intended as financial advice. \n"
    "2. Forecasts based on statistical modeling of daily returns and sector interactions.\n\n"
    "For daily updates, subscribe here: https://www.patreon.com/sectoredge",
    ha="left", va="bottom",
    transform=plt.gca().transAxes,
    fontsize=10,
    #weight ='bold',
    style="italic",
    
    #bbox=dict(facecolor="white", alpha=0.7, edgecolor="grey")
)

plt.tight_layout()  #automatically adjusts the spacing of your plot elements

# === Step 3: Save Chart ===
output_file = f"sector_predictions_{date.today()}.png"
plt.savefig(output_file, dpi=300)

plt.show()
plt.close()

print(f"✅ Chart saved as {output_file}")


#Plot HTML Interactive plot
# pip install plotly pandas
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import plotly.io as pio

# ===== Input =====
# expects a DataFrame like your ranked_returns_df with columns:
#   "Sector" (str) and "PredictedReturn" (float, e.g., 0.0123 for 1.23%)
df = ranked_returns_df.copy()

# sort (optional, same as your original intent)
df = df.sort_values("PredictedReturn", ascending=True)

# colors: blue for SPY, green for positive, red for negative
def pick_color(sector, ret):
    if str(sector).lower() == "spy":
        return "blue"
    return "green" if ret > 0 else "red"

colors = [pick_color(s, r) for s, r in zip(df["Sector"], df["PredictedReturn"])]

# values in percentage points
x_vals = (df["PredictedReturn"] * 100).round(2)
y_vals = df["Sector"]

# ===== Figure =====
today = date.today().strftime("%b %d, %Y")
title = f"<b>Sector ETF 5-Day Predictions</b><br>({today})"

fig = go.Figure()

fig.add_trace(go.Bar(
    x=x_vals,
    y=y_vals,
    orientation="h",
    marker=dict(color=colors),
    hovertemplate="<b>%{y}</b><br>Predicted Return: %{x:.2f}%<extra></extra>",
))

# end-of-bar value labels
fig.update_traces(
    text=[f"{v:.2f}%" for v in x_vals],
    textposition="outside",
    cliponaxis=False
)

# x-axis range with padding similar to your matplotlib code
pad = 0.2
xmin = float(x_vals.min()) - pad
xmax = float(x_vals.max()) + pad
fig.update_xaxes(title_text="Predicted Return (%)", range=[xmin, xmax], zeroline=True)

fig.update_layout(
    title=title,
    margin=dict(l=90, r=40, t=90, b=130),  # extra bottom for the note
    yaxis=dict(autorange=True, categoryorder="array", categoryarray=y_vals),  # preserve sort
)

# Note / disclaimer block (HTML, multi-line)
note = (
    "<b>Note:</b><br>"
    "1) Provided for informational purposes only; not intended as financial advice.<br>"
    "2) Forecasts based on statistical modeling of daily returns and sector interactions.<br><br>"
    
)

fig.add_annotation(
    xref="paper", yref="paper",
    x=0.0, y=-0.16,
    showarrow=False,
    align="left",
    text=note,
    font=dict(size=14),
    font_style="italic"
)

# Subscription "button" (top-right corner)
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.95, y=1.02,   # above the plot, right side
    xanchor="right", yanchor="bottom",
    showarrow=False,
    text=(
        '<a href="https://www.patreon.com/sectoredge" target="_blank" '
        'style="color:white; text-decoration:none;">'
        '<b>🔔 Subscribe for Daily Updates</b></a>'
    ),
    font=dict(size=16),
    align="center",
    bordercolor="black",
    borderwidth=1,
    borderpad=6,
    bgcolor="blue",
    opacity=0.9
)
# nicer spacing
fig.update_layout(bargap=0.25)

# ===== Save as standalone HTML =====
output_file = f"sector_predictions_{date.today()}.html"
pio.write_html(fig, file=output_file, full_html=True, include_plotlyjs="cdn")
print(f"✅ Interactive chart saved to {output_file}")



