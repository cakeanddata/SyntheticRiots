import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

# Define parameters
areas = [
    "BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "BT7", "BT8", "BT9", "BT10", "BT11", "BT12", "BT13",
    "BT14", "BT15", "BT17", "BT18", "BT19", "BT20", "BT23", "BT27", "BT28", "BT29", "BT37", "BT38", "BT39"
]

incident_types = {
    "Graffiti": ["public park", "residential area", "transport hub", "school", "shop or business", "city centre", "council/ governemnt office"],
    "Threat Poster": ["public park", "residential area", "transport hub", "shop or business", "city centre"],
    "School Bullying": ["school"],
    "House Attack": ["residential area"],
    "Business Attack": ["shop or business"],
    "Protest": ["city centre", "council/ governemnt office", "residential area"],
    "Armed Mugging": ["residential area", "transport hub"],
    "Riot": ["residential area", "shop front", "transport hub", "council/government office", "city centre"]
}

sources = ["PSNI", "School", "MEARS"]
severity_levels = ["Low", "Moderate", "High", "Severe"]
start_date = datetime(2025, 3, 1)
weeks = 52

# Assign numeric severity weights
incident_severity_base = {incident: i for i, incident in enumerate(incident_types.keys())}
incident_location_severity = {
    incident: {loc: i for i, loc in enumerate(locs)}
    for incident, locs in incident_types.items()
}

incident_history = {}
data = []

for week in range(weeks):
    week_date = start_date + timedelta(weeks=week)
    for _ in range(random.randint(10, 20)):
        area = random.choice(areas)
        incident = random.choice(list(incident_types.keys()))
        location_type = random.choice(incident_types[incident])
        source = random.choice(sources)

        # Validate logical combinations
        if incident == "House Attack":
            location_type = "residential area"
        elif incident == "School Bullying":
            location_type = "school"
        elif incident == "Business Attack":
            location_type = "shop or business"

# Riot escalation logic — only allow riot if lagged predictors present
if incident == "Riot":
    graffiti_lag_week = week - 4
    poster_lag_week = week - 2

    graffiti_in_area = (area, "Graffiti", graffiti_lag_week) in incident_history
    poster_in_area = (area, "Threat Poster", poster_lag_week) in incident_history

    # Check bullying with weak response in last ~6 weeks
    recent_bullying_weak = any(
        dp['Incident_Type'] == "School Bullying" and
        dp['Area_Code'] == area and
        dp.get('Response_Strength') in ["None", "Weak"]
        for dp in data[-60:]  # Covers roughly 6 weeks of entries
    )

    if not (graffiti_in_area and poster_in_area and recent_bullying_weak):
        continue  # Skip generating this Riot if predictors aren't met


        # Weighted severity score
        base_weight = incident_severity_base[incident]
        loc_weight = incident_location_severity[incident][location_type]
        severity_score = base_weight * 10 + loc_weight

        if severity_score >= 60:
            severity = np.random.choice(severity_levels, p=[0.05, 0.1, 0.35, 0.5])
        elif severity_score >= 40:
            severity = np.random.choice(severity_levels, p=[0.1, 0.2, 0.4, 0.3])
        elif severity_score >= 20:
            severity = np.random.choice(severity_levels, p=[0.2, 0.3, 0.35, 0.15])
        else:
            severity = np.random.choice(severity_levels, p=[0.3, 0.3, 0.25, 0.15])

        # Escalation Event logic
        lag_weeks = [week - 4, week - 5]
        lagged_graffiti = sum(
            1 for lag in lag_weeks if (area, "Graffiti", lag) in incident_history
        )
        escalation_event = 1 if lagged_graffiti >= 2 and incident in ["Protest", "House Attack"] else 0

        # Bullying response strength
        if incident == "School Bullying":
            if severity == "Severe":
                response_strength = np.random.choice(["None", "Weak", "Moderate", "Strong"], p=[0.4, 0.3, 0.2, 0.1])
            else:
                response_strength = np.random.choice(["None", "Weak", "Moderate", "Strong"], p=[0.1, 0.2, 0.4, 0.3])
        else:
            response_strength = None

        data.append({
            "ID": str(uuid.uuid4())[:8],
            "Date": week_date.strftime("%Y-%m-%d"),
            "Area_Code": area,
            "Incident_Type": incident,
            "Location_Type": location_type,
            "Severity": severity,
            "Severity_Score": severity_score,
            "Source": source,
            "Escalation_Event": escalation_event,
            "Response_Strength": response_strength
        })

        incident_history[(area, incident)] = incident_history.get((area, incident), 0) + 1
        incident_history[(area, incident, week)] = 1

df = pd.DataFrame(data)

import ace_tools as tools; tools.display_dataframe_to_user(name="Riot Prediction Dataset with Escalation Logic", dataframe=df)



import openai

def generate_description(row):
    prompt = (
        f"Generate a short, incident-report style summary (1–2 sentences) for the following event:\n\n"
        f"- Date: {row['Date']}\n"
        f"- Location: {row['Location_Type']} at postcode {row['Area_Code']}\n"
        f"- Incident Type: {row['Incident_Type']}\n"
        f"- Severity: {row['Severity']}\n"
        f"- Source of Report: {row['Source']}\n\n"
        f"Write clearly and concisely, in the tone of a police or community incident report."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[Description generation failed: {str(e)}]"

# Apply function to generate descriptions
df['Incident_Description'] = df.apply(generate_description, axis=1)

