import papermill as pm
import subprocess

def run_stock():
    print("Starting STOCK Pipeline")

    pm.execute_notebook (
        "src/extraction/stock_prices.ipynb",
        "src/pipeline/logs/stock_prices_out.ipynb"
    )

    pm.execute_notebook (
        "src/transformation/stock_cleaning.ipynb",
        "src/pipeline/logs/stock_cleaning_out.ipynb"
    )

    subprocess.run(["python", "src/database/insert_stocks.py"], check = True)

    print("Stock Pipeline Completed")

if __name__ == "__main__":
    run_stock()