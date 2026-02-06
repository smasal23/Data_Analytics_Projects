import papermill as pm
import subprocess

def run_oil():
    print("Starting OIL Pipeline")

    pm.execute_notebook (
        "src/extraction/oil_prices.ipynb",
        "src/pipeline/logs/oil_prices_out.ipynb"
    )

    pm.execute_notebook (
        "src/transformation/oil_cleaning.ipynb",
        "src/pipeline/logs/oil_cleaning_out.ipynb"
    )

    subprocess.run(["python", "src/database/insert_oil.py"], check = True)

    print("Oil Pipeline Completed")

if __name__ == "__main__":
    run_oil()