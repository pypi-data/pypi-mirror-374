import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mock_optimize_testing_only", action=argparse.BooleanOptionalAction, default=False)
args = parser.parse_args()

print(args.mock_optimize_testing_only)