import argparse
import asyncio
import json
from src.core.scraper import run_scraper
from src.utils.const import FILTERS

def main():
    """Parses command-line arguments and runs the LinkedIn API scraper."""

    epilog_example = """
    Example Usage:
      ljobx "Senior Python Developer" "Noida, India" --job-type "Full-time" "Contract" --date-posted "Past week" --max-jobs 50 --concurrency 10 --delay 2
    """

    # ... (the rest of your code is the same)
    parser = argparse.ArgumentParser(
        description="Scrape LinkedIn job postings using its internal API.",
        epilog=epilog_example,
        formatter_class=argparse.RawTextHelpFormatter
    )

    required_group = parser.add_argument_group("Required Arguments")
    filter_group = parser.add_argument_group("Filtering Options")
    scraper_group = parser.add_argument_group("Scraper Settings")

    required_group.add_argument("keywords", type=str, help="Job title or keywords to search for.")
    required_group.add_argument("location", type=str, help="Geographical location to search in.")

    for key, config in FILTERS.items():
        flag_name = f'--{key.replace("_", "-")}'
        help_text = f"Filter by {key.replace('_', ' ')}.\\nChoices: {', '.join(config['options'].keys())}"
        if config['allowMultiple']:
            filter_group.add_argument(
                flag_name, type=str, choices=config['options'].keys(),
                nargs='+', metavar='OPTION', help=help_text
            )
        else:
            filter_group.add_argument(
                flag_name, type=str, choices=config['options'].keys(), help=help_text
            )

    scraper_group.add_argument("--max-jobs", type=int, default=25, help="Maximum number of jobs to scrape (default: 25).")
    scraper_group.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests for job details (default: 5).")
    scraper_group.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between concurrent requests (default: 1.0).")
    args = parser.parse_args()
    scraper_settings = {
        'max_jobs': args.max_jobs,
        'concurrency_limit': args.concurrency,
        'delay': args.delay
    }
    search_criteria = {
        key: value for key, value in vars(args).items()
        if value is not None and key not in scraper_settings
    }
    print("--- Scraper Configuration ---")
    print(f"Search Criteria: {search_criteria}")
    print(f"Scraper Settings: {scraper_settings}")
    print("-----------------------------\\n")

    results = asyncio.run(
        run_scraper(
            search_criteria=search_criteria,
            **scraper_settings
        )
    )
    if results:
        filename = f"{search_criteria['keywords'].lower().replace(' ', '_')}_jobs.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\\nSuccessfully extracted {len(results)} jobs -> saved to {filename}")

if __name__ == "__main__":
    main()