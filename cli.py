import argparse
import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

from .core.search_client import EpsteinSearchClient
from .core.linkedin_parser import LinkedInParser
from .ai.analyzer import AIAnalyzer
from .database.models import Database
from .utils.report_generator import ReportGenerator
from .monitoring.monitor import MonitoringSystem, run_manual_check

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Enhanced Epstein document search tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  epstein-cli search --connections contacts.csv --output report.html
  
  epstein-cli search --connections contacts.csv --use-ai --api-key sk-xxx
  
  epstein-cli search --connections contacts.csv --format json
  
  epstein-cli monitor --connections contacts.csv --email you@example.com --interval 24
  
  epstein-cli check --connections contacts.csv
  
  epstein-cli graph --connections contacts.csv --output network.html
