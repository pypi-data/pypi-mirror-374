#!/usr/bin/env python3
"""
Test content field preservation after server update
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_content_preservation():
    tools = AIDLCDashboardMCPTools(base_url="http://44.235.223.99:8000/api")
    
    print("=== Testing Content Field Preservation ===")
    
    # Create a new project for testing
    project_result = tools.aidlc_create_project("Content Fix Test", "Testing field preservation")
    if not project_result.success:
        print(f"❌ Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ Created project: {project_id}")
    
    # Test UI Code Plan with explicit fields
    print("\n🎨 Testing UI Code Plan with explicit fields:")
    ui_plan = {
        "plan_id": "explicit-plan-001",
        "title": "Explicit Title Test",
        "name": "Test Plan Name",
        "description": "Test plan description",
        "pages": [
            {"name": "HomePage", "route": "/", "components": ["Header", "Hero"]},
            {"name": "AboutPage", "route": "/about", "components": ["AboutContent"]}
        ],
        "navigation": {"type": "SPA", "router": "React Router"}
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(project_id, ui_plan)
    if ui_result.success:
        print("✅ UI Code Plan uploaded")
    else:
        print(f"❌ Upload failed: {ui_result.error}")
        return
    
    # Get project status to check content
    print("\n🔍 Checking preserved content:")
    status_result = tools.aidlc_get_project_status(project_id)
    if status_result.success:
        artifacts = status_result.data.get("data", {}).get("project", {}).get("artifacts", {})
        ui_artifacts = [art for art in artifacts.values() if art.get("type") == "ui-code-plan"]
        
        if ui_artifacts:
            ui_artifact = ui_artifacts[0]
            print(f"📋 UI Artifact Title: '{ui_artifact.get('title', 'NO TITLE')}'")
            
            content = ui_artifact.get('content', {})
            print(f"📦 Content keys: {list(content.keys())}")
            
            # Check specific fields
            fields_to_check = ['plan_id', 'title', 'name', 'description']
            for field in fields_to_check:
                if field in content:
                    print(f"   ✅ {field}: '{content[field]}'")
                else:
                    print(f"   ❌ {field}: MISSING")
        else:
            print("❌ No UI artifacts found")
    else:
        print(f"❌ Failed to get status: {status_result.error}")

if __name__ == "__main__":
    test_content_preservation()
