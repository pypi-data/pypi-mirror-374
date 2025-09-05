#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_compare_plans():
    tools = AIDLCDashboardMCPTools()
    
    # Create test project
    project_result = tools.aidlc_create_project("Compare Plans Test")
    if not project_result.success:
        print(f"Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data["project_id"]
    print(f"Created project: {project_id}")
    
    # Test UI code plan upload
    ui_plan = {
        "pages": [{"name": "TestPage", "route": "/test"}],
        "components": [{"name": "TestComponent", "type": "display"}]
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(
        project_id=project_id,
        ui_code_plan=ui_plan,
        title="Test UI Plan",
        description="Test UI description"
    )
    
    # Test model code plan upload
    code_phases = [{
        "description": "Test phase description",
        "components": [{"name": "TestEntity", "type": "entity"}],
        "phase_name": "Test Phase"
    }]
    
    model_result = tools.aidlc_upload_model_code_plan(
        project_id=project_id,
        code_phases=code_phases,
        title="Test Model Plan",
        description="Test model description"
    )
    
    if ui_result.success and model_result.success:
        print("\nBoth uploads successful!")
        
        # Check project status
        status_result = tools.aidlc_get_project_status(project_id)
        if status_result.success:
            artifacts = status_result.data["data"]["project"]["artifacts"]
            for artifact_id, artifact in artifacts.items():
                print(f"\n{artifact['type']} Artifact {artifact_id}:")
                print(f"  Title: {artifact['title']}")
                print(f"  Description: {artifact['description']}")
                print(f"  Content title: {artifact['content'].get('title', 'NOT FOUND')}")
                print(f"  Content description: {artifact['content'].get('description', 'NOT FOUND')}")
    else:
        print(f"UI result: {ui_result.success}, Model result: {model_result.success}")

if __name__ == "__main__":
    test_compare_plans()
