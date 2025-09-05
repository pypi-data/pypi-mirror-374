#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_ui_code_plan_fix():
    # Use local server
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    # Create a test project
    print("Creating test project...")
    result = tools.aidlc_create_project("UI Fix Test Project")
    if not result.success:
        print(f"Failed to create project: {result.error}")
        return
    
    project_id = result.data["project_id"]
    print(f"Created project: {project_id}")
    
    # Test UI code plan upload with explicit title and description
    ui_plan = {
        "components": [
            {"name": "TestComponent", "type": "functional", "props": ["testProp"]}
        ],
        "pages": [
            {"name": "TestPage", "components": ["TestComponent"], "route": "/test"}
        ]
    }
    
    print("Uploading UI code plan...")
    result = tools.aidlc_upload_ui_code_plan(
        project_id=project_id,
        ui_code_plan=ui_plan,
        title="Custom UI Plan Title",
        description="Custom UI Plan Description"
    )
    
    if not result.success:
        print(f"Failed to upload UI code plan: {result.error}")
        return
    
    print(f"Uploaded UI code plan: {result.data}")
    
    # Get project status to check the content
    print("Checking project status...")
    result = tools.aidlc_get_project_status(project_id)
    if not result.success:
        print(f"Failed to get project status: {result.error}")
        return
    
    # Find the UI code plan artifact
    artifacts = result.data["data"]["project"]["artifacts"]
    ui_artifacts = [a for a in artifacts.values() if a["type"] == "ui-code-plan"]
    
    if ui_artifacts:
        ui_artifact = ui_artifacts[0]
        content = ui_artifact["content"]
        print(f"UI Artifact Title: {ui_artifact['title']}")
        print(f"UI Artifact Description: {ui_artifact['description']}")
        print(f"Content Title: {content.get('title', 'NOT SET')}")
        print(f"Content Description: {content.get('description', 'NOT SET')}")
        
        # Check if the fix worked
        if content.get('title') and content.get('description'):
            print("✅ FIX SUCCESSFUL: Title and description are set in content!")
        else:
            print("❌ FIX FAILED: Title and description are still empty in content")
    else:
        print("No UI code plan artifacts found")

if __name__ == "__main__":
    test_ui_code_plan_fix()
