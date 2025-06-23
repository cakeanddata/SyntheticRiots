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

severity_levels = ["Low", "Moderate", "High", "Severe"]
start_date = datetime(2025, 3, 1)
weeks = 52

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

        if incident == "House Attack":
            location_type = "residential area"
        elif incident == "School Bullying":
            location_type = "school"
        elif incident == "Business Attack":
            location_type = "shop or business"

        # Riot escalation logic
        if incident == "Riot":
            graffiti_lag_week = week - 4
            poster_lag_week = week - 2

            graffiti_in_area = (area, "Graffiti", graffiti_lag_week) in incident_history
            poster_in_area = (area, "Threat Poster", poster_lag_week) in incident_history

            recent_bullying_weak = any(
                dp['Incident_Type'] == "School Bullying" and
                dp['Area_Code'] == area and
                dp.get('Response_Strength') in ["None", "Weak"]
                for dp in data[-60:]
            )

            if not (graffiti_in_area and poster_in_area and recent_bullying_weak):
                continue

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

        # Assign source
        if incident == "School Bullying" or (incident in ["Protest", "Graffiti", "Threat Poster"] and location_type == "school"):
            source = "School"
        elif incident == "House Attack":
            source = "MEARS"
        elif severity == "Severe":
            source = "PSNI"
        else:
            source = random.choice(["PSNI", "MEARS"])

        # Escalation Event
        lag_weeks = [week - 4, week - 5]
        lagged_graffiti = sum(
            1 for lag in lag_weeks if (area, "Graffiti", lag) in incident_history
        )
        escalation_event = 1 if lagged_graffiti >= 2 and incident in ["Protest", "House Attack"] else 0

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
import ace_tools as tools; tools.display_dataframe_to_user(name="Cleaned Simulated Incident Data", dataframe=df)
