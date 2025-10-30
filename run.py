from engine import run_pipeline

if __name__ == "__main__":
    text = "The discussion was okay, but the guest kept interrupting and it was kind of annoying."
    output = run_pipeline("pipeline.json", text)
    print("\n--- FINAL OUTPUT ---")
    print(output)

from logger import compress_old_logs
compress_old_logs()
