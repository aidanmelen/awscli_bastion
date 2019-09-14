#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `awscli_bastion` package."""


import unittest
from click.testing import CliRunner

from awscli_bastion import cli
# from awscli_bastion import credentials
# from awscli_bastion import cache


class TestAwscli_bastion(unittest.TestCase):
    """Tests for `awscli_bastion` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help     Show this message and exit.' in help_result.output

    def test_cli_get_session_token(self):
        """Test get_session_token."""

    def test_cli_set_default(self):
        """Test set_default."""

    def test_cli_reset_cache(self):
        """Test reset_cache."""

    def test_cli_get_expiration_delta(self):
        """Test get_expiration_delta."""
