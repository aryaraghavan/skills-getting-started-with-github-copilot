#!/usr/bin/env python3
"""
Simple test runner script for the Mergington High School Activities API.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run tests with coverage report
    python run_tests.py --verbose    # Run tests with verbose output
    python run_tests.py --help       # Show help
"""
import subprocess
import sys
import argparse


def run_command(cmd):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for the FastAPI application")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Run tests with verbose output")
    parser.add_argument("--file", "-f", type=str,
                       help="Run tests from specific file")
    parser.add_argument("--class", "-k", type=str, dest="test_class",
                       help="Run specific test class")
    
    args = parser.parse_args()
    
    # Build the pytest command
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    if args.file:
        cmd = ["python", "-m", "pytest", args.file]
        
    if args.test_class:
        if args.file:
            cmd.append(f"::{args.test_class}")
        else:
            cmd = ["python", "-m", "pytest", f"tests/::*::{args.test_class}"]
    
    # Run the tests
    return run_command(cmd)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)