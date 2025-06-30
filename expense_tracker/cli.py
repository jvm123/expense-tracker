import datetime
import click
from pathlib import Path
import csv
from expense_tracker.generate_report import generate_report, get_current_month

DATA_DIR = Path("data")

# Get the current date in YYYY-MM-DD format
current_date = datetime.datetime.now().strftime("%Y-%m-%d")


def get_month_from_date(date_str):
    # Accepts YYYY-MM-DD, returns YYYY-MM
    return date_str[:7]


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def append_row_to_csv(file_path, fieldnames, row):
    file_exists = file_path.exists()
    with file_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


@click.group()
def cli():
    """Expense Tracker CLI"""
    pass


@cli.command()
@click.option("--date", help="Date of the expense (YYYY-MM-DD)")
@click.option("--category", help="Expense category (e.g. Rent, Groceries)")
@click.option("--paid-by", required=True, help="Who paid (Alice, Bob, or Both)")
@click.option("--amount", required=True, type=float, help="Amount of the expense")
@click.option("--notes", required=True, help="Notes")
def add_expense(date, category, paid_by, amount, notes):
    """Add a shared expense to the monthly CSV file."""
    ensure_data_dir()
    if date is None:
        date_val = current_date
    else:
        date_val = date
    if category is None:
        category_val = ""
    else:
        category_val = category
    month = get_month_from_date(date_val)
    file_path = DATA_DIR / f"{month}.csv"
    row = {
        "Date": date_val,
        "Category": category_val,
        "Paid By": paid_by,
        "Amount": amount,
        "Notes": notes,
    }
    fieldnames = ["Date", "Category", "Paid By", "Amount", "Notes"]
    append_row_to_csv(file_path, fieldnames, row)
    click.echo(f"✅ Expense added to {file_path}")
    click.echo(f"Rows: {row}")


@cli.command()
@click.option("--date", help="Date of the contribution (YYYY-MM-DD)")
@click.option("--name", required=True, help="Contributor's name (Alice or Bob)")
@click.option("--amount", required=True, type=float, help="Amount contributed")
@click.option("--virtual", is_flag=True, help="Is this a virtual contribution?")
@click.option("--notes", help="Optional notes")
def add_contribution(date, name, amount, virtual, notes):
    """Add a contribution (real or virtual) to the monthly contributions CSV file."""
    ensure_data_dir()
    # If called with only --name and --amount, fill in defaults and do not prompt
    if date is None:
        date_val = current_date
    else:
        date_val = date
    if notes is None:
        notes_val = ""
    else:
        notes_val = notes
    virtual_val = "Yes" if virtual else "No"
    month = get_month_from_date(date_val)
    file_path = DATA_DIR / f"{month}-contributions.csv"
    row = {
        "Date": date_val,
        "Name": name,
        "Amount": amount,
        "Virtual Contribution": virtual_val,
        "Notes": notes_val,
    }
    fieldnames = ["Date", "Name", "Amount", "Virtual Contribution", "Notes"]
    append_row_to_csv(file_path, fieldnames, row)
    click.echo(f"✅ Contribution added to {file_path}")
    click.echo(f"Rows: {row}")


@cli.command()
@click.argument("month", required=False)
def report(month):
    """Generate the report for a given MONTH (format: YYYY-MM). Defaults to current month."""
    if not month:
        month = get_current_month()
    generate_report(month)


if __name__ == "__main__":
    cli()
