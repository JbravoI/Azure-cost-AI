import re
import subprocess
import json
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date

MONTHS = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}

def run_az_cost_command(start_date, end_date):
    cmd = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        "az", "costmanagement", "query",
        "--type", "ActualCost",
        "--timeframe", "Custom",
        "--time-period", f"{start_date}/{end_date}",
        "--dataset", '{"granularity": "None", "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}}}',
        "--output", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else {"error": result.stderr}

def get_date_range(period):
    today = datetime.today()
    if period == "this week":
        start = today - timedelta(days=today.weekday())
    elif period == "last week":
        start = today - timedelta(days=today.weekday() + 7)
        today = start + timedelta(days=6)
    elif period == "2 weeks":
        start = today - timedelta(weeks=2)
    elif period == "1 month":
        start = today.replace(day=1) - timedelta(days=1)
        start = start.replace(day=1)
    elif period == "2 months":
        first = today.replace(day=1)
        start = (first - timedelta(days=1)).replace(day=1) - timedelta(days=1)
        start = start.replace(day=1)
    else:
        return None, None
    return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def parse_custom_dates(prompt):
    month_pattern = r"compare (\w+ \d{4}) with (\w+ \d{4})"
    range_pattern = r"from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})"

    if match := re.search(month_pattern, prompt, re.IGNORECASE):
        month1, month2 = match.groups()
        d1 = datetime.strptime(month1, "%B %Y")
        d2 = datetime.strptime(month2, "%B %Y")
        start1 = d1.replace(day=1)
        end1 = (d1.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        start2 = d2.replace(day=1)
        end2 = (d2.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return (start1.strftime('%Y-%m-%d'), end1.strftime('%Y-%m-%d'),
                start2.strftime('%Y-%m-%d'), end2.strftime('%Y-%m-%d'))

    if match := re.findall(range_pattern, prompt):
        if len(match) == 2:
            return (*match[0], *match[1])
        elif len(match) == 1:
            return (*match[0], None, None)
    return None

def compare_custom_periods(s1, e1, s2, e2):
    c1 = run_az_cost_command(s1, e1)
    c2 = run_az_cost_command(s2, e2)
    return {
        "period1": {"start": s1, "end": e1, "cost": c1.get("properties", {}).get("rows", [])},
        "period2": {"start": s2, "end": e2, "cost": c2.get("properties", {}).get("rows", [])},
        "comparison": f"{s1} to {e1} vs {s2} to {e2}"
    }

def process_prompt(prompt):
    prompt = prompt.lower().strip()

    # Handle greeting
    if prompt in ["hi", "hello", "hey", "hi there", "hello azure"]:
        return {"response": "Hi, I'm Azure Cost AI 👋, How can i be of help?"}

    # Login to Azure
    if prompt in ["login to azure", "start process"]:
        return {"require_login": True}
    
    if prompt in ["list subscriptions", "subscriptions"] in prompt:
        return {"subscriptions": list_azure_subscriptions()}

    if "compare" in prompt:
        custom = parse_custom_dates(prompt)
        if custom:
            return compare_custom_periods(*custom)
        if "this week" in prompt and "last week" in prompt:
            return compare_periods("this week", "last week")

    for key in ["this week", "last week", "2 weeks", "1 month", "2 months"]:
        if key in prompt:
            start, end = get_date_range(key)
            return run_az_cost_command(start, end)

    if "from" in prompt and "to" in prompt:
        custom = parse_custom_dates(prompt)
        if custom and custom[2] is None:
            return run_az_cost_command(custom[0], custom[1])

    return {"error": "Unable to understand prompt"}

def compare_periods(period1, period2):
    s1, e1 = get_date_range(period1)
    s2, e2 = get_date_range(period2)
    c1 = run_az_cost_command(s1, e1)
    c2 = run_az_cost_command(s2, e2)
    return {
        period1: c1.get("properties", {}).get("rows", []),
        period2: c2.get("properties", {}).get("rows", []),
        "comparison": f"{period1} vs {period2}"
    }

def list_azure_subscriptions():
    cmd = ["az", "account", "list", "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": "Failed to parse subscription list."}
    else:
        return {"error": result.stderr.strip()}

def login_with_credentials(username, password, tenant):
    cmd = [
        "az", "login",
        "--service-principal",
        "-u", username,
        "-p", password,
        "--tenant", tenant
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return {"message": "Login successful"}
    else:
        return {"error": result.stderr.strip()}