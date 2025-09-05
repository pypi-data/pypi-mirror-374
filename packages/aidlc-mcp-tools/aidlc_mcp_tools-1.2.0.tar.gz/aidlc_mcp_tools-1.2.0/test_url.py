#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_url():
    tools = AIDLCDashboardMCPTools()
    print(f"Base URL: {tools.base_url}")
    
    # Test health check
    result = tools.aidlc_health_check()
    print(f"Health check: {result.success}")
    if result.data:
        print(f"Response: {result.data}")

if __name__ == "__main__":
    test_url()
