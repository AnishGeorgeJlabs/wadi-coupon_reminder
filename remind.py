"""
Main Module for the coupon reminder system
"""

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('data', 'templates'))
