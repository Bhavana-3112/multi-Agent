import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from app.mesh import run_mesh


def main() -> None:
    load_dotenv(override=True)

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Multi-agent coding mesh")
    parser.add_argument("task", nargs="?", help="Coding task description")
    args = parser.parse_args()

    task = args.task
    if not task:
        task = input("Enter your coding task: ").strip()
        if not task:
            print("Error: no task provided.")
            sys.exit(1)

    result = asyncio.run(run_mesh(task))

    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    print(f"\nTask: {result.task}")
    print(f"Rounds completed: {result.rounds}")
    if result.review:
        print(f"Review verdict: {result.review.splitlines()[0]}")
    print(f"Status: {'PASSED' if result.passed else 'COMPLETED (no PASS)'}")
    print("\nCheck the output/ folder for generated files.")


if __name__ == "__main__":
    main()
