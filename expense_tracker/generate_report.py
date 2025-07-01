#!/usr/bin/env python3

import csv
import sys
from pathlib import Path
import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def read_contributions(contrib_file):
    """
    Reads a contributions CSV file with columns: Name,Amount
    Returns a dict: {name: total_paid}
    """
    contributions = {}
    virtual_contributions = {}
    if not contrib_file.exists():
        return contributions, virtual_contributions
    with contrib_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Name"].strip()
            amount = float(row["Amount"].strip())
            virtual = row.get("Virtual Contribution", "No").strip().lower() == "yes"
            if virtual:
                virtual_contributions[name] = (
                    virtual_contributions.get(name, 0.0) + amount
                )
            else:
                contributions[name] = contributions.get(name, 0.0) + amount
    return contributions, virtual_contributions


def calculate_month_data(month, csv_file, contrib_file):
    """
    Calculate all relevant data for a given month: contributions, virtual contributions,
    paid_by, balances, etc.
    Returns a dict with all relevant fields for reporting.
    """
    contributions, virtual_contributions = read_contributions(contrib_file)
    total_shared = 0.0
    csv_rows = []
    people = set(contributions.keys())
    people.update(virtual_contributions.keys())

    with csv_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_rows.append(dict(row))
            people.add(row["Paid By"].strip())
            total_shared += float(row["Amount"].strip())
    half_share = total_shared / 2

    people.discard("Both")
    if not people:
        people = {"PersonA", "PersonB"}  # fallback

    paid_by = {}
    for row in csv_rows:
        amount = float(row["Amount"].strip())
        payer = row["Paid By"].strip()
        if payer.lower() != "both":
            paid_by[payer] = paid_by.get(payer, 0.0) + amount

    # Merge paid_by into contributions (add amounts)
    for person, amt in paid_by.items():
        contributions[person] = contributions.get(person, 0.0) + amt

    balances = {}
    for person in people:
        balances[person] = (
            contributions.get(person, 0.0)
            + virtual_contributions.get(person, 0.0)
            - half_share
        )

    account_balance = (
        sum(contributions.values())  - total_shared
    )

    return {
        "month": month,
        "account_balance": account_balance,
        "contributions": contributions,
        "virtual_contributions": virtual_contributions,
        "balances": balances,
        "total_shared": total_shared,
        "half_share": half_share,
        "csv_rows": csv_rows,
    }


def plot_pie_chart(data, labels, title, out_path):
    plt.figure(figsize=(6, 6))
    colors = sns.color_palette("pastel")[0 : len(data)]
    plt.pie(data, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_bar_chart(categories, values, title, ylabel, out_path):
    plt.figure(figsize=(8, 5))
    sns.barplot(x=categories, y=values, palette="pastel")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def generate_overview_report():
    """
    Generates an overview report as a markdown table summarizing each month's
    account balance, per-person contributions, virtual contributions, and balances.
    Includes a total row at the end.
    """
    overview_file = Path("reports/overview.md")
    overview_file.parent.mkdir(parents=True, exist_ok=True)

    months_data = []
    data_dir = Path("data")
    for csv_file in data_dir.glob("2[0-9][0-9][0-9]-[0-9][0-9].csv"):
        month = csv_file.stem
        contrib_file = data_dir / f"{month}-contributions.csv"
        month_data = calculate_month_data(month, csv_file, contrib_file)
        months_data.append(month_data)

    # Calculate totals
    total_account_balance = 0.0
    total_contributions = {}
    total_virtual_contributions = {}
    total_balances = {}
    for data in months_data:
        total_account_balance += data["account_balance"]
        for k, v in data["contributions"].items():
            total_contributions[k] = total_contributions.get(k, 0.0) + v
        for k, v in data["virtual_contributions"].items():
            total_virtual_contributions[k] = total_virtual_contributions.get(k, 0.0) + v
        for k, v in data["balances"].items():
            total_balances[k] = total_balances.get(k, 0.0) + v

    # Calculate expenses by category across all months
    all_categories = {}
    for csv_file in data_dir.glob("2[0-9][0-9][0-9]-[0-9][0-9].csv"):
        with csv_file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row.get("Category", "UncategorizedYes").strip()
                amount = float(row["Amount"].strip())
                if category not in all_categories:
                    all_categories[category] = 0.0
                all_categories[category] += amount

    with overview_file.open("w") as f:
        f.write("# Overview Report\n\n")
        f.write(
            "| Month | Account Balance | Contributions | Virtual Contributions | Balances |\n"
        )
        f.write(
            "|-------|-----------------|---------------|-----------------------|----------|\n"
        )
        for data in months_data:
            contributions_str = ", ".join(
                f"{k}: ${v:.2f}" for k, v in data["contributions"].items()
            )
            virtual_contributions_str = ", ".join(
                f"{k}: ${v:.2f}" for k, v in data["virtual_contributions"].items()
            )
            balances_str = ", ".join(
                f"{k}: ${v:.2f}" for k, v in data["balances"].items()
            )
            f.write(
                f"| {data['month']} | ${data['account_balance']:.2f} | "
                f"{contributions_str} | {virtual_contributions_str} | {balances_str} |\n"
            )
        # Total row
        total_contributions_str = ", ".join(
            f"{k}: ${v:.2f}" for k, v in total_contributions.items()
        )
        total_virtual_contributions_str = ", ".join(
            f"{k}: ${v:.2f}" for k, v in total_virtual_contributions.items()
        )
        total_balances_str = ", ".join(
            f"{k}: ${v:.2f}" for k, v in total_balances.items()
        )
        f.write(
            f"| **Total** | ${total_account_balance:.2f} | "
            f"{total_contributions_str} | "
            f"{total_virtual_contributions_str} | "
            f"{total_balances_str} |\n\n"
        )

        f.write("\n## Expenses by Category (All Time)\n\n")
        for category, total in all_categories.items():
            f.write(f"- {category}: ${total:.2f}\n")
        # Pie chart for all time expenses by category
        overview_pie_path = "overview-categories-pie.png"
        if all_categories:
            plot_pie_chart(
                list(all_categories.values()),
                list(all_categories.keys()),
                "Expenses by Category (All Time)",
                f"reports/{overview_pie_path}",
            )
            f.write(f"\n![Expenses by Category (All Time)]({overview_pie_path})\n")

    print(f"✅ Report generated at: {overview_file}")


def update_reports_readme():
    """
    Updates reports/README.md with a list of all report files and overview.md.
    """
    reports_dir = Path("reports")
    readme_file = reports_dir / "README.md"
    report_files = sorted(
        [f for f in reports_dir.glob("*-report.md")], key=lambda p: p.name
    )
    with readme_file.open("w") as f:
        f.write("# \U0001f4c1 reports\n\n")
        f.write("This folder contains:\n\n")
        f.write("- [`overview.md`](overview.md)\n")
        for report in report_files:
            f.write(f"- [`{report.name}`]({report.name})\n")


def generate_report(month):
    csv_file = Path(f"data/{month}.csv")
    contrib_file = Path(f"data/{month}-contributions.csv")
    report_file = Path(f"reports/{month}-report.md")

    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)

    month_data = calculate_month_data(month, csv_file, contrib_file)

    report_file.parent.mkdir(parents=True, exist_ok=True)

    # Summarize totals per category
    categories = {}
    for row in month_data["csv_rows"]:
        category = row.get("Category", "UncategorizedYes").strip()
        amount = float(row["Amount"].strip())
        if category not in categories:
            categories[category] = 0.0
        categories[category] += amount

    # Graphs
    pie_path = f"reports/{month}-categories-pie.png"
    if categories:
        plot_pie_chart(
            list(categories.values()),
            list(categories.keys()),
            f"Expenses by Category ({month})",
            pie_path,
        )
    bar_path = f"reports/{month}-bar.png"
    people = list(
        set(
            list(month_data["contributions"].keys())
            + list(month_data["virtual_contributions"].keys())
            + list(month_data["balances"].keys())
        )
    )
    bar_data = {
        "Contributions": [month_data["contributions"].get(p, 0) for p in people],
        "Virtual Contributions": [
            month_data["virtual_contributions"].get(p, 0) for p in people
        ],
        "Balances": [month_data["balances"].get(p, 0) for p in people],
    }
    plt.figure(figsize=(8, 5))
    x = range(len(people))
    width = 0.25
    plt.bar(
        [i - width for i in x],
        bar_data["Contributions"],
        width=width,
        label="Contributions",
        color=sns.color_palette("pastel")[0],
    )
    plt.bar(
        x,
        bar_data["Virtual Contributions"],
        width=width,
        label="Virtual Contributions",
        color=sns.color_palette("pastel")[1],
    )
    plt.bar(
        [i + width for i in x],
        bar_data["Balances"],
        width=width,
        label="Balances",
        color=sns.color_palette("pastel")[2],
    )
    plt.xticks(x, people)
    plt.title(f"Contributions, Virtual Contributions, and Balances ({month})")
    plt.ylabel("Amount ($)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    # Use only the basename for embedding in markdown
    pie_img = Path(pie_path).name
    bar_img = Path(bar_path).name

    # Generate report
    with report_file.open("w") as f:
        f.write(f"💰 Shared Expenses Report – {month}\n")
        f.write("======================================\n\n")

        # Markdown table for summary
        f.write("| Item                       | Amount ($) |\n")
        f.write("|----------------------------|------------|\n")
        f.write(f"| Total Shared Expenses      | {month_data['total_shared']:.2f} |\n")
        f.write(f"| Each Person Owes           | {month_data['half_share']:.2f} |\n")
        f.write(
            f"| Account Balance change     | {month_data['account_balance']:.2f} |\n"
        )
        f.write("\n")

        # Paid Toward Shared table
        f.write("#### Paid Toward Shared\n")
        if month_data["contributions"]:
            f.write("| Name   | Amount ($) |\n")
            f.write("|--------|------------|\n")
            for person, paid_amt in month_data["contributions"].items():
                f.write(f"| {person} | {paid_amt:.0f} |\n")
        else:
            f.write("No contributions recorded.\n")
        f.write("\n")

        # Virtual Contributions table
        f.write("#### Virtual Contributions Toward Shared\n")
        if month_data["virtual_contributions"]:
            f.write("| Name   | Amount ($) |\n")
            f.write("|--------|------------|\n")
            for person, paid_amt in month_data["virtual_contributions"].items():
                f.write(f"| {person} | {paid_amt:.0f} |\n")
        else:
            f.write("No virtual contributions recorded.\n")
        f.write("\n")

        # Balances table
        f.write("#### Balances\n")
        if month_data["balances"]:
            f.write("| Name   | Balance ($) | Status    |\n")
            f.write("|--------|-------------|-----------|\n")
            for person, bal in month_data["balances"].items():
                amt = abs(bal)
                status = "overpaid" if bal >= 0 else "owes"
                f.write(f"| {person} | {amt:.2f} | {status} |\n")
        else:
            f.write("No balances recorded.\n")
        f.write("\n")

        f.write(
            f"![Contributions, Virtual Contributions, and Balances]({bar_img})\n\n---\n"
        )

        # Expenses by Category table
        f.write("#### Expenses by Category\n")
        f.write("| Category           | Amount ($) |\n")
        f.write("|--------------------|------------|\n")
        for category, total in categories.items():
            f.write(f"| {category} | {total:.2f} |\n")
        f.write(f"\n![Expenses by Category]({pie_img})\n")

        f.write("\n---\nFull list of contributions:\n")
        contrib_file_path = Path(f"data/{month}-contributions.csv")
        if month_data["contributions"] or month_data["virtual_contributions"]:
            if contrib_file_path.exists():
                with contrib_file_path.open() as cf:
                    reader = csv.DictReader(cf)
                    for row in reader:
                        f.write("  - ")
                        f.write(", ".join(f"{key}: {row[key]}" for key in row))
                        f.write("\n")
            else:
                f.write("  No contributions file found.\n")
        else:
            f.write("  No contributions recorded.\n")
        f.write("\nFull list of payments:\n")
        for row in month_data["csv_rows"]:
            f.write("  - ")
            f.write(", ".join(f"{key}: {row[key]}" for key in row))
            f.write("\n")

    print(f"✅ Report generated at: {report_file}")
    generate_overview_report()
    update_reports_readme()


def get_current_month():
    return datetime.datetime.now().strftime("%Y-%m")


if __name__ == "__main__":
    month = sys.argv[1] if len(sys.argv) > 1 else get_current_month()
    generate_report(month)
