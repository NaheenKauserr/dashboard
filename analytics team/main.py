from analysis import RetailDataAnalyzer
from insights import generate_ai_insights
from my_recommendations import generate_smart_recommendations
from predictive_engine import SalesPredictiveEngine

# Initialize analyzer
analyzer = RetailDataAnalyzer("../data/SALES_DATA_SETT.csv")

# Run base analysis
results = analyzer.run_complete_analysis()

# Generate insights & recommendations
insights = generate_ai_insights(results['kpis'])
recommendations = generate_smart_recommendations(results['kpis'])

# Print results
print("\n===== AI INSIGHTS =====")
for i, insight in enumerate(insights, 1):
    print(f"{i}. {insight}")

print("\n===== RECOMMENDATIONS =====")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")

# ─── PREDICTIVE ENGINE ───────────────────────────────────────────────────────
engine = SalesPredictiveEngine(df=analyzer.df)
engine.run_full_forecast(forecast_periods=6, target_growth_pct=10.0)
