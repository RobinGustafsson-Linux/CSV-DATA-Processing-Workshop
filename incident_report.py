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
sites = sorted(set(i["site"] for i in incidents)) # Creates a list of unique sites, set removes duplicates
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


# filter incidents with 100 or more affected users
high_impact = [i for i in incidents if i["affected_users"] > 100]
               
# 5 most costly incidents
top_cost = sorted(incidents, key=lambda x: x["cost_sek"], reverse=True)[:5] # lambda function sorts by cost in descending order


# DEL B: Numerisk analys

# Calculate average resolution time per severity
avg_resolution = {}
for sev in severity_count.keys():
    times = [i["resolution_minutes"] for i in incidents if i ["severity"].lower() == sev and i ["resolution_minutes"] > 0]
    avg_resolution[sev] = round(mean(times), 1) if times else 0

# Creates summary per site
site_summary = {}
for site in sites:
    site_data = [i for i in incidents if i["site"] == site]
    site_summary[site] = {
        "total_incidents": len(site_data),
        "critical_incidents": sum(1 for i in site_data if i["severity"] == "critical"),
        "high_incidents": sum(1 for i in site_data if i["severity"] == "high"),
        "medium_incidents": sum(1 for i in site_data if i["severity"] == "medium"),
        "low_incidents": sum(1 for i in site_data if i["severity"] == "low"),
        "avg_resolution_minutes": round(mean(i["resolution_minutes"] for i in site_data if i ["resolution_minutes"] > 0), 1),
        "total_cost_sek": round(sum(i["cost_sek"] for i  in site_data), 2)
    }


# Report generation

with open("incident_analysis.txt", "w", encoding="utf-8") as report:
    report.write("=" * 80 + "\n")
    report.write("INCIDENT ANALYSIS - SEPTEMBER 2024\n")
    report.write("=" * 80 + "\n\n")
    report.write(f"Analyserad period: {start_date} till {end_date}\n")
    report.write(f"Totalt antal incidents: {total_incidents} st\n")
    report.write(f"Total kostnad: {total_cost:,.2f} SEK\n\n")

    report.write("EXECUTIVE SUMMARY\n")
    report.write("-----------------\n")
    report.write(f"⚠ KRITISKT: {severity_count['critical']} st kritiska incidenter totalt\n")
    report.write(f"⚠ DYRASTE INCIDENT: {top_cost[0]['cost_sek']:,.2f} SEK ({top_cost[0]['device_hostname']} - {top_cost[0]['category']})\n")
    report.write(f"⚠ {len(high_impact)} incidenter påverkade fler än 100 användare\n\n")
    
    report.write("INCIDENTS PER SEVERITY\n")
    report.write("-----------------------\n")
    for sev, count in severity_count.items():
        pct = (count / total_incidents * 100)
        report.write(f"{sev.capitalize():10}: {count:2d} st ({pct:.0f}%) - Genomsnitt: {avg_resolution[sev]} min resolution\n")
    report.write("\n")


    report.write("5 DYRASTE INCIDENTER\n")
    report.write("--------------------\n")
    for inc in top_cost:
        report.write(f"{inc['ticket_id']:12} {inc['device_hostname']:15} {inc['cost_sek']:>10,.2f} SEK - {inc['site']}\n")
    report.write("\n")

    report.write("INCIDENTS MED >100 PÅVERKADE ANVÄNDARE\n")
    report.write("---------------------------------------\n")
    for inc in high_impact:
        report.write(f"{inc['ticket_id']:12} {inc['device_hostname']:15} {inc['affected_users']:4} användare - {inc['site']}\n")
    report.write("\n")

    report.write("=" * 80 + "\n")
    report.write("RAPPORT SLUT\n")
    report.write("=" * 80 + "\n")


    # Write CSV file, incidents_by_site.csv

with open("incidents_by_site.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "site",
        "total_incidents",
        "critical_incidents",
        "high_incidents",
        "medium_incidents",
        "low_incidents",
        "avg_resolution_minutes",
        "total_cost_sek"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for site, data in site_summary.items():
        row = {"site": site}
        row.update(data)
        writer.writerow(row)

print("Analys klar! Filer skapade:")
print(" - incident_analysis.txt")
print(" - incidents_by_site.csv")
