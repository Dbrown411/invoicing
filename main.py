from pathlib import Path
from datetime import datetime
from invoice.jobs import Job
import invoice

output_dir = Path("./invoices")
today = datetime.now()
job_directory = Path(__file__).parent / "invoice/data/jobs"


def main():
    for test_job in job_directory.glob("*.json"):
        job = Job.from_json(test_job)
        invoice.build(job, days_due=45)


if __name__ == "__main__":
    main()