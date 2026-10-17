import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Generate an illustrated five-page children's book PDF.")
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Create a five-page children's book story about a young, brave character discovering a hidden, magical garden.",
    )
    parser.add_argument("--demo", action="store_true", help="Use built-in story data instead of calling the AI model.")
    args = parser.parse_args()

    if args.demo:
        os.environ["DEMO_MODE"] = "true"

    from app import jobs

    job_id = jobs.create_job(args.prompt)
    jobs.run_job(job_id, args.prompt)
    record = jobs.read_job(job_id)
    if record["status"] != "completed":
        print(f"Failed: {record['error']}", file=sys.stderr)
        sys.exit(1)
    print(f"Title: {record['title']}")
    print(f"PDF:   {jobs.job_directory(job_id) / 'storybook.pdf'}")


if __name__ == "__main__":
    main()
