# data_analyst_agent.py
import datetime

def respond(user_input: str) -> str:
    today = datetime.date.today().isoformat()
    response = ["📊 Data Analyst Activated"]
    if any(term in user_input.lower() for term in ["chart", "trend", "plot"]):
        response.append(f"\n📈 Chart Suggestion:\n- I can generate line or bar charts for time-series data.\n- Sample data range: Last 7 days up to {today}")
    if any(term in user_input.lower() for term in ["forecast", "predict", "estimate"]):
        response.append("\n🔮 Forecasting Support:\n- I use historical patterns to project future trends.\n- Let me know what metric you want to forecast.")
    if any(term in user_input.lower() for term in ["spreadsheet", "csv", "table"]):
        response.append("\n📁 Spreadsheet Tools:\n- I can parse and summarize data tables.\n- Upload your .csv for analysis.")
    if len(response) == 1:
        response.append("\n🤖 Please clarify: charts, forecasts, or spreadsheet analysis?")
    return "\n".join(response)
