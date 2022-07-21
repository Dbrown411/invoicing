from pathlib import Path
from datetime import datetime
from invoice.jobs import Job
import invoice
import argparse

output_dir = Path("./invoices")
today = datetime.now()
job_directory = Path(__file__).parent / "invoice/data/jobs"


def main():
    for job_info in job_directory.glob("*.json"):
        job = Job.from_json(job_info)
        invoice.build_pdf(job, days_due=45)


def test():
    test_job = Job.from_json(job_directory / "test.json")
    invoice.build_pdf(test_job, days_due=45)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--test',
                        help='generate test invoice',
                        default=False,
                        action='store_true')
    kwargs = vars(parser.parse_args())
    if kwargs['test']:
        test()
    else:
        main()