import papermill as pm
import subprocess

def run_crypto():
    print("Starting CRYPTO Pipeline")

    pm.execute_notebook (
        "src/extraction/crypto_markets.ipynb",
        "src/pipeline/logs/crypto_markets_out.ipynb"
    )
    pm.execute_notebook (
        "src/extraction/crypto_prices.ipynb",
        "src/pipeline/logs/crypto_prices_out.ipynb"
    )

    pm.execute_notebook (
        "src/transformation/crypto_metadata_cleaning.ipynb",
        "src/pipeline/logs/crypto_metadata_cleaning_out.ipynb"
    )
    pm.execute_notebook(
        "src/transformation/crypto_price_cleaning.ipynb",
        "src/pipeline/  logs/crypto_price_cleaning_out.ipynb"
    )

    subprocess.run(["python", "src/validation/crypto_checks.py"], check = True)

    subprocess.run(["python", "src/database/insert_crypto.py"], check = True)

    print("Crypto Pipeline Completed")

if __name__ == "__main__":
    run_crypto()