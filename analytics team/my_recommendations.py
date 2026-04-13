def generate_smart_recommendations(kpis):
    recommendations = []

    if kpis['avg_discount'] > 0.2:
        recommendations.append("Reduce discount levels to improve profitability.")

    if kpis['avg_shipping_delay'] > 5:
        recommendations.append("Optimize logistics to reduce shipping delays.")

    if kpis['total_profit'] > 0:
        recommendations.append("Focus on scaling high-performing categories like Technology.")

    if kpis['avg_order_value'] > 400:
        recommendations.append("Introduce premium product bundles to increase revenue further.")

    if kpis['unique_customers'] > 500:
        recommendations.append("Leverage customer loyalty programs to retain users.")

    return recommendations