#!/usr/bin/env python3
"""
Test script to verify UI code plan title generation
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_ui_title():
    # Initialize tools with the test server
    tools = AIDLCDashboardMCPTools(base_url="http://44.253.157.102:8000/api")
    
    print("=== Testing UI Code Plan Title Generation ===")
    
    # Create a new project
    print("\n1. Creating new project:")
    project_result = tools.aidlc_create_project("UI Title Test", "Testing UI code plan title generation")
    if not project_result.success:
        print(f"Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"Project ID: {project_id}")
    
    # Test UI code plan with different structures
    test_cases = [
        {
            "name": "Single Page Plan",
            "plan": {
                "plan_id": "ui-plan-single",
                "pages": [
                    {
                        "name": "LoginPage",
                        "route": "/login",
                        "components": ["LoginForm", "Header"]
                    }
                ],
                "navigation": {"type": "SPA", "router": "React Router"}
            }
        },
        {
            "name": "Multi Page Plan",
            "plan": {
                "plan_id": "ui-plan-multi",
                "pages": [
                    {"name": "HomePage", "route": "/", "components": ["Hero", "Navigation"]},
                    {"name": "AboutPage", "route": "/about", "components": ["AboutContent"]},
                    {"name": "ContactPage", "route": "/contact", "components": ["ContactForm"]}
                ],
                "navigation": {"type": "SPA", "router": "React Router"}
            }
        },
        {
            "name": "Plan with Title",
            "plan": {
                "plan_id": "ui-plan-titled",
                "title": "Custom Dashboard UI",
                "pages": [
                    {"name": "DashboardPage", "route": "/dashboard", "components": ["Charts", "Tables"]}
                ],
                "navigation": {"type": "SPA", "router": "React Router"}
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i+1}. Testing {test_case['name']}:")
        
        result = tools.aidlc_upload_ui_code_plan(project_id, test_case['plan'])
        if result.success:
            print(f"✅ Upload successful")
        else:
            print(f"❌ Upload failed: {result.error}")
    
    # Get project status to see all UI plans
    print(f"\n{len(test_cases)+2}. Getting project status to check titles:")
    status_result = tools.aidlc_get_project_status(project_id)
    if status_result.success:
        artifacts = status_result.data.get("data", {}).get("project", {}).get("artifacts", {})
        ui_artifacts = [art for art in artifacts.values() if art.get("type") == "ui-code-plan"]
        
        print(f"Found {len(ui_artifacts)} UI code plan artifacts:")
        for i, artifact in enumerate(ui_artifacts, 1):
            title = artifact.get("title", "No title")
            content = artifact.get("content", {})
            pages = content.get("pages", [])
            plan_id = content.get("plan_id", "No plan_id")
            
            print(f"  {i}. Title: '{title}'")
            print(f"     Plan ID: {plan_id}")
            print(f"     Pages: {len(pages)} pages")
            if "title" in content:
                print(f"     Content Title: '{content['title']}'")
            print()
    else:
        print(f"Failed to get project status: {status_result.error}")

if __name__ == "__main__":
    test_ui_title()
