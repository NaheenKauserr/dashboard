def generate_ai_insights(kpis):
    insights = []

    # Profit
    if kpis['total_profit'] < 0:
        insights.append("⚠ The business is running at a loss.")
    else:
        insights.append("✅ The business is profitable overall.")

    # Discount
    if kpis['avg_discount'] > 0.2:
        insights.append("⚠ High discounting is impacting profit margins.")
    elif kpis['avg_discount'] > 0.1:
        insights.append("Moderate discount strategy is being used.")

    # Shipping
    if kpis['avg_shipping_delay'] > 5:
        insights.append("🚚 Shipping delays are higher than optimal levels.")

    # Customers
    if kpis['unique_customers'] > 500:
        insights.append("📈 Strong customer base contributing to sales.")

    # Order value
    if kpis['avg_order_value'] > 400:
        insights.append("💰 High average order value indicates strong sales performance.")

    return insights