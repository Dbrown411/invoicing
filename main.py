from pathlib import Path
from datetime import datetime
from invoices import build_invoice
from jobs import Job, date_by_adding_business_days

output_dir = Path("./invoices")
today = datetime.now()
due_date = date_by_adding_business_days(today, 30)


def main():
    job_directory = Path(__file__).parent / "jobs"
    for test_job in job_directory.glob("*.json"):
        job = Job.from_json(test_job)
        build_invoice(job, days_due=45)


if __name__ == "__main__":
    main()