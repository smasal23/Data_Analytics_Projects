from src.pipeline.run_stock_pipeline import run_stock
from src.pipeline.run_crypto_pipeline import run_crypto
from src.pipeline.run_oil_pipeline import run_oil

def run_pipeline():
    print("🚀 Starting Cross-Market Pipeline")

    run_crypto()
    run_oil()
    run_stock()

    print("✅ Pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
