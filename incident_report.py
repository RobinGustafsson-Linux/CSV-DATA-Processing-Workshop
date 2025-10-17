import csv
from datetime import datetime
from statistics import mean


# Read incident data from a CSV file
incidents = []
with open ("network_incidents.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Try to convert numbers and costs
        try:
            row["resolution_minutes"] = int(row["resolution_minutes"])
        except:
            row["resolution_minutes"] = 0
        
        try:
            row["affected_users"] =int(row["affected_users"]) if row["affected_users"] else 0
        except: 
            row["affected_users"] = 0

        try:
            # convert swedish formatted cost
            cost = row["cost_sek"].replace(" " ,"").replace(",", ".")
            row["cost_sek"] = float(cost)
        except:
            row["cost_sek"] = 0.0

        try: 
            row["impact_score"] = float(row["impact_score"])
        except:
            row["impact_score"] = 0.0

        incidents.append(row)

    # if the list is empty, exit
if not incidents:
     print("Ingen data hitades i CSV-filen.")
     exit()

# Del A: Grundanalys
sites = sorted(set(i["sites"] for i in incidents)) # Creates a list of unique sites, set removes duplicates
weeks = sorted(set(int(i["week_number"]) for i in incidents)) # Creates a list of unique week numbers
total_incidents = len(incidents) # total number of incidents
total_cost = sum(i["cost_sek"] for i in incidents) # total cost of all incidents


# Find the period covered by the weeknumbers
start_date = "2024-09-01"
end_date = "2024-09-30"

# Count incidents per severity level
severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0} # Initialize counts to zero
for i in incidents: # Iterate through each incident 
    sev = i["severity"].lower() # Get the severity level in lowercase
    if sev in severity_count: # Check if the severity level is valid 
        severity_count[sev] += 1 # Increment the count for the corresponding severity level


