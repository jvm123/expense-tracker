# 🧾 Shared Expenses Tracker

![License](https://img.shields.io/github/license/jvm123/expense-tracker?cache-control=no-cache)
![Unit Tests](https://github.com/jvm123/expense-tracker/actions/workflows/python-test.yml/badge.svg)
![Linting](https://github.com/jvm123/expense-tracker/actions/workflows/python-lint.yml/badge.svg)

This repository helps couples fairly manage shared expenses using CSV files and GitHub Actions.

Features:
- Contributions to the shared bank account can be entered in a csv file
- Virtual contributions: To offset an agreed upon contributions gap, partner A can enter -123 and person B 123 as a virtual payment to the shared bank account. This would ensure that the calculated balance does not consider this agreed payment gap of $123 of partner B.
- Paid sums can be entered into another csv file
- The report script generates a report and shows how much each partner overpaid/underpaid. This is based on the assumptions that all payments were made from the shared bank account and that each partner is paying into it.

## 📂 Structure

- [`data/`](data/) — Monthly raw CSV data files
- [`reports/`](reports/) — Auto-generated reports
- [`expense_tracker/`](scripts/) — Report-generation logic and cli tool
- [`.github/workflows/`](.github/workflows/) — GitHub Actions

---

## 📤 How It Works

With Github Actions (runs fully on Github, you can edit your csvs there; no local Python setup needed):
1. Fork this repo
2. Add your monthly expenses to `data/YYYY-MM.csv`
3. Add your monthly contributions to `data/YYYY-MM-contributions.csv`
4. Commit
5. GitHub Actions runs `./expense_tracker.sh report`, just wait a minute for it to complete
6. The report appears in `reports/YYYY-MM-report.md`

Locally:
1. Clone this repo
2. $ poetry install
3. Add your monthly expenses to `data/YYYY-MM.csv` or run `./expense_tracker.sh add-expense --paid-by Bob --amount 42 --notes "Weekly shopping"`
4. Add your monthly contributions to `data/YYYY-MM-contributions.csv` or run `./expense_tracker.sh add-contribution --name Alice --amount 100 --notes "Monthly deposit"`
5. Run `./expense_tracker.sh report`
6. The report appears in `reports/YYYY-MM-report.md`

---

## 🚀 Command Line Usage

You can record expenses and contributions easily from the command line:

```sh
./expense_tracker.sh add-expense --date 2025-07-01 --category Groceries --paid-by Alice --amount 42.50 --notes "Weekly shopping"

./expense_tracker.sh add-contribution --date 2025-07-01 --name Bob --amount 1000 --notes "Monthly deposit"
```

This will append to the appropriate CSV files in the `data/` directory.

To trigger report generation on the command line, run
```sh
./expense_tracker.sh report
```

---

## CSV file format

### 1. Main Expenses CSV (`YYYY-MM.csv`)

| Column    | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Date      | The date of the expense (format: YYYY-MM-DD).                               |
| Category  | The category of the expense (e.g., Rent, Groceries, Utilities, etc.).       |
| Paid By   | The person who paid for the expense ("Alice", "Bob", or "Both").            |
| Amount    | The amount of the expense (numeric, in dollars).                            |
| Notes     | Optional notes or description for the expense.                              |

Example file `1970-01.csv`:
```csv
Date,Category,Paid By,Amount,Notes
2025-06-01,Rent,Both,1200,Split evenly
2025-06-03,Groceries,Alice,350,Weekly groceries
2025-06-05,Dining Out,Bob,220,Dinners
```

### 2. Contributions CSV (`YYYY-MM-contributions.csv`)

| Column               | Description                                                                                 |
|----------------------|---------------------------------------------------------------------------------------------|
| Date                 | The date of the contribution (format: YYYY-MM-DD).                                          |
| Name                 | The name of the person making the contribution ("Alice" or "Bob").                          |
| Amount               | The amount contributed (numeric, in dollars).                                               |
| Virtual Contribution | Indicates if this is a virtual contribution to offset an agreed payment gap ("Yes" or "No").|
| Notes                | Optional notes or description for the contribution.                                         |

Example file `1970-01-contributions.csv`:
```csv
Date,Name,Amount,Notes
2025-06-01,Alice,1000,Virtual Contribution,Monthly contribution
2025-06-01,Bob,1000,No,Monthly contribution
2025-06-15,Bob,75,No,Extra payment to cover shortfall
```

---

## What to do when..

- you used money from the shared account for a personal purpose: Add a negative contribution
```csv
Date,Name,Amount,Virtual Contribution,Notes
2025-06-01,Alice,-100,No,Accidental withdrawal for ..
```
- you paid something for your partner from your private account that served only them: This is not considered as relevant for the shared account -- ask to be repaid directly. Alternatively, add a negative contribution for your partner
```csv
Date,Name,Amount,Virtual Contribution,Notes
2025-06-01,Bob,-100,No,Alice bought you ..
```
- something you bought together served your partner more than you: In addition to the expense, also add a negative contribution for your partner if you must, with the fraction of the expense you would like back

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork this repository on GitHub.
2. Create a new branch for your feature or bugfix.
3. Make your changes and add tests if appropriate.
4. Run the test suite to ensure everything passes: $ make test
5. Run the linter: $ make lint
5. Open a pull request describing your changes.

For major changes, please open an issue first to discuss what you would like to change.

---
