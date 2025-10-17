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
            