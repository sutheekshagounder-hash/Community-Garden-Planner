
import csv
import json
import os
from datetime import datetime, date
from collections import Counter

DATA_FILE = "garden_data.json"


# ----------- DATA STORAGE -----------

def load_records():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print("Warning: Data file is damaged. Starting fresh.")
        return []


def save_records(records):
    with open(DATA_FILE, "w") as file:
        json.dump(records, file, indent=4)


# ----------- INPUT VALIDATION -----------

def get_text(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty!")


def get_number(message):
    while True:
        try:
            value = int(input(message))
            if value > 0:
                return value
            print("Enter a positive number!")
        except ValueError:
            print("Please enter a valid number!")


def get_date(message):
    while True:
        value = input(message).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Enter date in YYYY-MM-DD format!")


# ----------- ADD GARDEN RECORD -----------

def add_record(records):
    print("\n--- ADD GARDEN RECORD ---")

    bed = get_text("Enter garden bed: ")
    plant = get_text("Enter plant name: ")
    category = get_text("Enter category: ")
    sowing_date = get_date("Enter sowing date (YYYY-MM-DD): ")
    harvest_date = get_date("Enter expected harvest date (YYYY-MM-DD): ")

    if harvest_date < sowing_date:
        print("Harvest date cannot be before sowing date!")
        return

    quantity = get_number("Enter number of plants: ")
    notes = input("Enter harvest notes: ").strip()

    status = get_text("Enter status (Growing/Harvested/Planned/Failed): ").title()

    if status not in ["Growing", "Harvested", "Planned", "Failed"]:
        print("Invalid status!")
        return

    record = {
        "id": max([r["id"] for r in records], default=0) + 1,
        "bed": bed,
        "plant": plant,
        "category": category,
        "sowing_date": sowing_date,
        "harvest_date": harvest_date,
        "quantity": quantity,
        "notes": notes,
        "status": status
    }

    records.append(record)
    save_records(records)

    print("Garden record added successfully!")


# ----------- VIEW RECORDS -----------

def view_records(records):
    print("\n--- ALL GARDEN RECORDS ---")

    if not records:
        print("No records available!")
        return

    for r in records:
        print("-" * 40)
        print("ID:", r["id"])
        print("Bed:", r["bed"])
        print("Plant:", r["plant"])
        print("Category:", r["category"])
        print("Sowing Date:", r["sowing_date"])
        print("Harvest Date:", r["harvest_date"])
        print("Quantity:", r["quantity"])
        print("Notes:", r["notes"])
        print("Status:", r["status"])


# ----------- SEARCH RECORDS -----------

def search_records(records):
    keyword = get_text("Enter plant name or category to search: ").lower()

    found = [
        r for r in records
        if keyword in r["plant"].lower()
        or keyword in r["category"].lower()
        or keyword in r["bed"].lower()
        or keyword in r["status"].lower()
    ]

    if found:
        view_records(found)
    else:
        print("No matching records found!")


# ----------- UPDATE RECORD -----------

def update_record(records):
    record_id = get_number("Enter record ID to update: ")

    for r in records:
        if r["id"] == record_id:

            print("1. Update Plant Name")
            print("2. Update Quantity")
            print("3. Update Status")
            print("4. Update Notes")

            choice = input("Enter choice: ")

            if choice == "1":
                r["plant"] = get_text("Enter new plant name: ")

            elif choice == "2":
                r["quantity"] = get_number("Enter new quantity: ")

            elif choice == "3":
                status = get_text("Enter new status: ").title()
                if status in ["Growing", "Harvested", "Planned", "Failed"]:
                    r["status"] = status
                else:
                    print("Invalid status!")
                    return

            elif choice == "4":
                r["notes"] = input("Enter new notes: ")

            else:
                print("Invalid choice!")
                return

            save_records(records)
            print("Record updated successfully!")
            return

    print("Record not found!")


# ----------- DELETE RECORD -----------

def delete_record(records):
    record_id = get_number("Enter record ID to delete: ")

    for r in records:
        if r["id"] == record_id:
            records.remove(r)
            save_records(records)
            print("Record deleted successfully!")
            return

    print("Record not found!")


# ----------- EXECUTIVE SUMMARY -----------

def summary(records):
    print("\n--- GARDEN EXECUTIVE SUMMARY ---")

    if not records:
        print("No records available!")
        return

    total_plants = sum(r["quantity"] for r in records)
    total_beds = len(set(r["bed"] for r in records))

    print("Total Records:", len(records))
    print("Total Plants:", total_plants)
    print("Total Garden Beds:", total_beds)
    print("Average Plants per Record:", round(total_plants / len(records), 2))

    print("\nPlant Status Summary:")

    statuses = Counter(r["status"] for r in records)

    for status, count in statuses.items():
        print(status, ":", count)

    print("\nCategory Summary:")

    categories = Counter(r["category"] for r in records)

    for category, count in categories.items():
        print(category, ":", count)

    print("\nHarvest Alerts:")

    today = date.today()

    for r in records:
        harvest = datetime.strptime(
            r["harvest_date"], "%Y-%m-%d"
        ).date()

        if harvest < today and r["status"] not in ["Harvested", "Failed"]:
            print("OVERDUE:", r["plant"])

        elif (harvest - today).days <= 7 and r["status"] not in ["Harvested", "Failed"]:
            print("UPCOMING:", r["plant"])


# ----------- CSV EXPORT -----------

def export_csv(records):
    if not records:
        print("No records to export!")
        return

    with open("garden_report.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print("CSV report exported successfully!")


# ----------- MARKDOWN EXPORT -----------

def export_markdown(records):
    with open("garden_report.md", "w") as file:

        file.write("# Community Garden Planner Report\n\n")

        file.write("| Plant | Bed | Category | Quantity | Status |\n")
        file.write("|---|---|---|---|---|\n")

        for r in records:
            file.write(
                f"| {r['plant']} | {r['bed']} | "
                f"{r['category']} | {r['quantity']} | "
                f"{r['status']} |\n"
            )

    print("Markdown report exported successfully!")


# ----------- DATA VISUALIZATION -----------

def generate_chart(records):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install matplotlib using: pip install matplotlib")
        return

    if not records:
        print("No data available!")
        return

    categories = Counter(r["category"] for r in records)

    plt.bar(categories.keys(), categories.values())

    plt.title("Garden Plant Categories")
    plt.xlabel("Plant Category")
    plt.ylabel("Number of Records")

    plt.tight_layout()
    plt.savefig("garden_chart.png")
    plt.show()


# ----------- SAMPLE DATA -----------

def sample_data(records):
    if records:
        print("Sample data can only be loaded into an empty database.")
        return

    plants = [
        ("Bed A", "Tomato", "Vegetable", "2026-02-01", "2026-05-15", 8, "Healthy", "Growing"),
        ("Bed A", "Chilli", "Vegetable", "2026-02-10", "2026-06-01", 12, "Growing well", "Growing"),
        ("Bed B", "Spinach", "Vegetable", "2026-03-01", "2026-04-01", 20, "Ready to harvest", "Harvested"),
        ("Bed B", "Mint", "Herb", "2026-03-05", "2026-04-20", 5, "Fresh leaves", "Growing"),
        ("Bed C", "Marigold", "Flower", "2026-02-15", "2026-05-01", 10, "Yellow flowers", "Growing"),
        ("Bed C", "Carrot", "Vegetable", "2026-01-15", "2026-04-15", 15, "Good growth", "Harvested"),
        ("Bed D", "Strawberry", "Fruit", "2026-02-20", "2026-06-10", 6, "Healthy plants", "Growing"),
        ("Bed D", "Basil", "Herb", "2026-03-12", "2026-05-12", 7, "Regular watering", "Growing"),
        ("Bed E", "Sunflower", "Flower", "2026-03-01", "2026-06-15", 4, "Needs sunlight", "Planned"),
        ("Bed E", "Cucumber", "Vegetable", "2026-03-10", "2026-05-25", 9, "Needs support", "Growing")
    ]

    for p in plants:
        record = {
            "id": len(records) + 1,
            "bed": p[0],
            "plant": p[1],
            "category": p[2],
            "sowing_date": p[3],
            "harvest_date": p[4],
            "quantity": p[5],
            "notes": p[6],
            "status": p[7]
        }
        records.append(record)

    save_records(records)
    print("Sample data loaded successfully!")


# ----------- MAIN MENU -----------

def main():

    records = load_records()

    while True:

        print("\n")
        print("=" * 50)
        print("          COMMUNITY GARDEN PLANNER")
        print("=" * 50)

        print("1. Add Garden Record")
        print("2. View All Records")
        print("3. Search Records")
        print("4. Update Record")
        print("5. Delete Record")
        print("6. Executive Summary")
        print("7. Export CSV Report")
        print("8. Export Markdown Report")
        print("9. Generate Garden Chart")
        print("10. Load Sample Data")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            add_record(records)

        elif choice == "2":
            view_records(records)

        elif choice == "3":
            search_records(records)

        elif choice == "4":
            update_record(records)

        elif choice == "5":
            delete_record(records)

        elif choice == "6":
            summary(records)

        elif choice == "7":
            export_csv(records)

        elif choice == "8":
            export_markdown(records)

        elif choice == "9":
            generate_chart(records)

        elif choice == "10":
            sample_data(records)

        elif choice == "0":
            save_records(records)
            print("Thank you for using Community Garden Planner!")
            break

        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
