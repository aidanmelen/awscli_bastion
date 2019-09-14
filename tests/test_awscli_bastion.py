#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `awscli_bastion` package."""


import unittest
from click.testing import CliRunner

from awscli_bastion import awscli_bastion
from awscli_bastion import cli


class TestAwscli_bastion(unittest.TestCase):
    """Tests for `awscli_bastion` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        # assert 'awscli_bastion.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
