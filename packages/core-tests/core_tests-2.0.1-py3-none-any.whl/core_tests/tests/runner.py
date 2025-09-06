# -*- coding: utf-8 -*-

"""
This module provides a group of commands related to tests, this way we
avoid defining them in each project that requires them. The following
commands will be available:
  * python manager.py run-tests --test-type unit
  * python manager.py run-tests --test-type integration
  * python manager.py run-tests --test-type "another folder that contains test cases under ./tests"
  * python manager.py run-tests --test-type functional --pattern "*.py"
  * python manager.py run-coverage
"""

import logging
import os
from unittest import TestLoader, TextTestRunner
import sys

import pytest
from click import echo, option
from click.decorators import group
from coverage import coverage, CoverageException


@group()
def cli_tests():
    """
    Group of commands related to tests.
    """


@cli_tests.command("run-tests")
@option("-t", "--test-type", "test_type", default="unit")
@option("-p", "--pattern", "pattern", default="tests*.py")
@option("-e", "--engine", "engine", default="unittest")
def run_tests(test_type: str, pattern: str, engine: str) -> None:
    """
    Runs the tests using the specific engine.
    """

    validate_engines(engine)
    if not os.path.exists(f"./tests/{test_type}"):
        echo(f"The directory: {test_type} does not exist under ./tests!", err=True)
        sys.exit(1)

    if test_type == "unit":
        # Just removing verbosity from unit tests...
        level = os.getenv("LOGGER_LEVEL_FOR_TEST", str(logging.ERROR))
        os.environ["LOGGER_LEVEL"] = level

    if engine == "pytest":
        test_path = f"./tests/{test_type}"
        args = [test_path, "-v", "-k", pattern.replace("s*.py", "")]

        exit_code = pytest.main(args)
        if exit_code != 0:
            sys.exit(exit_code)

    else:
        tests = TestLoader().discover(f"./tests/{test_type}", pattern=pattern)
        result = TextTestRunner(verbosity=2).run(tests)
        if not result.wasSuccessful():
            sys.exit(1)


@cli_tests.command("run-coverage")
@option("-s", "--save-report", "save_report", default=True)
@option("-e", "--engine", "engine", default="unittest")
def run_coverage(save_report: bool, engine: str) -> None:
    """
    Runs the unit tests and generates a coverage
    report on success.
    """

    validate_engines(engine)
    os.environ["LOGGER_LEVEL"] = os.getenv("LOGGER_LEVEL_FOR_TEST", str(logging.ERROR))
    coverage_ = coverage(branch=True, source=["."])
    coverage_.start()

    if engine == "pytest":
        exit_code = pytest.main(["./tests", "-v"])
        if exit_code != 0:
            sys.exit(exit_code)

    else:
        tests = TestLoader().discover("./tests", pattern="tests*.py")
        result = TextTestRunner(verbosity=2).run(tests)

        if not result.wasSuccessful():
            sys.exit(1)

    coverage_.stop()

    try:
        echo("Coverage Summary:")
        coverage_.report()

        if save_report:
            coverage_.save()
            coverage_.html_report()

        coverage_.erase()

    except CoverageException as error:
        echo(error)
        sys.exit(1)


def validate_engines(engine: str) -> None:
    """
    It validates the engines passed by parameter.
    """

    _engines = ["unittest", "pytest"]
    if engine not in _engines:
        echo(f"Valid engines: {_engines}", err=True)
        sys.exit(1)
