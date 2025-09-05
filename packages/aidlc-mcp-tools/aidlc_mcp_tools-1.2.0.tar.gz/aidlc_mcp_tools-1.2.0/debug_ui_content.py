#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def debug_ui_content():
    tools = AIDLCDashboardMCPTools(base_url="http://44.253.157.102:8000/api")
    
    # Test the content preparation logic
    ui_plan = {
        "components": [{"name": "TestComponent", "type": "functional"}],
        "pages": [{"name": "TestPage", "route": "/test"}]
    }
    
    # Simulate what happens in aidlc_upload_ui_code_plan
    ui_plan_content = ui_plan.copy()
    
    ui_title = "Debug Test Title"
    ui_description = "Debug Test Description"
    
    # This is the key fix - set title and description in content
    ui_plan_content['title'] = ui_title
    ui_plan_content['description'] = ui_description
    
    print("Content before upload:")
    print(f"Title: {ui_plan_content.get('title', 'NOT SET')}")
    print(f"Description: {ui_plan_content.get('description', 'NOT SET')}")
    print(f"Full content: {ui_plan_content}")

if __name__ == "__main__":
    debug_ui_content()
