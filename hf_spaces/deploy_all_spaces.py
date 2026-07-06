#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_all_spaces.py — backward-compatible entry point for deploy workflow.
The GitHub Actions workflow calls this file by name; it delegates to
deploy_spaces.py which contains all implementation.

Accepts all arguments deploy_spaces.py accepts:
  --priority INT     max priority level (1=critical, 5=all)
  --batch-size INT   spaces per batch between sleeps
  --dry-run          plan without deploying
  --node STR         deploy single node (e.g. N003)
  --group STR        deploy all nodes in group (e.g. A_COMMAND)
  --skip-live        skip already-live nodes
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from deploy_spaces import main

if __name__ == "__main__":
    main()
