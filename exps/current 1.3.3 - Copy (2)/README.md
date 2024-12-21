# Expense Tracker

A web-based expense tracking application that helps you monitor and manage your personal expenses.

## Features

- Add new expenses with details like date, item, place, and amount
- Categorize expenses (food, entertainment, tithe, repairs, maintenance, clothing, etc.)
- View and sort expense history
- Track monthly expenses
- Special tracking for bank transactions and gas expenses

## Project Structure

```
.
├── bank/           # Bank transaction related files
├── gas/            # Gas expense tracking
├── monthly/        # Monthly expense summaries
├── db_connect.php  # Database connection and core functions
├── expenses.db     # SQLite database file
├── index.php       # Main application entry point
└── style.css       # Application styling
```

## Requirements

- PHP server (with SQLite support)
- Web browser
- SQLite database

## Installation

1. Clone this repository to your web server directory
2. Ensure PHP has write permissions for the `expenses.db` file
3. Access the application through your web browser

## Usage

1. Open the application in your web browser
2. Use the form to add new expenses:
   - Enter the date (defaults to current date)
   - Input item description
   - Specify the place of purchase
   - Enter the amount
   - Select expense category
3. View your expense history in the table below
4. Use the navigation links to access specific expense categories or views

## License

This project is for personal use.

## Contributing

This is a personal expense tracking tool, but feel free to fork and modify for your own use.
