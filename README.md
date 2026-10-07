# BMI Calculator

A desktop BMI calculator built with **Python**, **Tkinter**, **SQLite**, and **Matplotlib** to calculate, save, and visualize Body Mass Index (BMI).

## Requirements

- Python 3
- Tkinter (usually included with Python)
- The Python packages listed in `requirements.txt`

## Installation

Open a terminal in the project folder and install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

```powershell
python bmi_t1.py
```

## Features

- Calculate BMI and display its category: Underweight, Normal, Overweight, or Obese.
- Save measurements for multiple users in a local SQLite database.
- Browse and search BMI history by user.
- View a graph of BMI trends over time, with reference lines for BMI thresholds.
- Export measurement history to CSV.
- Clear saved data after confirming the action.
- Validate input and show errors in the application.

## How It Works

1. Enter a name, weight in kilograms, and height in metres.
2. The application calculates BMI using the formula:

   **BMI = weight (kg) ÷ height (m)²**

3. The calculated BMI and its category are displayed in the app.
4. Each successful calculation is saved with the user's name and timestamp in the local SQLite database.
5. Use **View History** to browse records or search by name.
6. Enter a user's name and select **BMI Graph** to view their saved BMI measurements over time.
7. Select **Export CSV** to save the records as a CSV file, or **Clear Data** to delete all saved records after confirmation.

## Data Storage

The application stores its data alongside the application:

- `bmi_data.db` — SQLite database containing BMI records.
- `bmi_export.csv` — CSV file created when records are exported.

These files are local application data and are excluded from version control.

## Clone the Repository

```bash
git clone https://github.com/SayanTheCoder/OIBSIP_Python_Task2.git
cd OIBSIP_Python_Task2
```

## Developed By

**Sayan Pramanik © 2026**
