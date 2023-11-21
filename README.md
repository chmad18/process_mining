# Process Mining Project

## To Run the Script

1. Open the project folder in cmd/terminal.
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment: 
- On Windows: `.venv\Scripts\activate`
- On macOS/Linux (untested): `source .venv/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`
5. Run the `inductive_generate_norm_model.py` to generate comparison file
5. Run the `inductive_miner.py` script.
6. If you get error like "module not found" make sure the python interpreter is set to the one of the virtual environment

## Show Data in Excel

1. Open the file `process_mining_results_expanded.csv`
2. Select the first column (Click on A1 and drag to A4).
3. On the menu line / toolbar, select `Data`.
4. Choose `text to Columns`.
5. Select `Delimited` (`afgrænset`) and click Next.
   6. Check `Comma` and click `Next` until you finish the wizard.
7. Open `comparison_analysis.csv` and apply the same logic. 
   8. You might need to set the number seperator (thousands, decimal),
      9. file -> settings
      10. advanced
      11. uncheck `system seperator` and reverse the default values in the below now editable boxes


