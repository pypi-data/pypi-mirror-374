# Basic CLI entry point for Flowscribe
import sys
import argparse

def main():
	parser = argparse.ArgumentParser(prog="flowscribe")
	subparsers = parser.add_subparsers(dest="command")

	# 'run' command
	run_parser = subparsers.add_parser("run", help="Run the Flowscribe app")
	run_parser.add_argument("--app", required=True, help="App name to run")

	args = parser.parse_args()

	if args.command == "run":
		print("Started session")
		# Placeholder for actual app logic
		print("Ended session")
	else:
		parser.print_help()

if __name__ == "__main__":
	main()
