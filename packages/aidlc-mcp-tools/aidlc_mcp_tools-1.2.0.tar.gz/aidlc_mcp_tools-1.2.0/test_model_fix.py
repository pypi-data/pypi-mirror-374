#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_model_code_plan_fix():
    tools = AIDLCDashboardMCPTools()
    
    # Create test project
    project_result = tools.aidlc_create_project("Model Fix Test")
    if not project_result.success:
        print(f"Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data["project_id"]
    print(f"Created project: {project_id}")
    
    # Test model code plan upload
    code_phases = [{
        "description": "Test phase description",
        "components": [{"name": "TestEntity", "type": "entity"}],
        "phase_name": "Test Phase"
    }]
    
    result = tools.aidlc_upload_model_code_plan(
        project_id=project_id,
        code_phases=code_phases,
        title="Test Model Plan",
        description="Test description for model plan"
    )
    
    if result.success:
        print("Upload successful!")
        print(f"Result: {result.data}")
        
        # Check project status
        status_result = tools.aidlc_get_project_status(project_id)
        if status_result.success:
            artifacts = status_result.data["data"]["project"]["artifacts"]
            for artifact_id, artifact in artifacts.items():
                print(f"\nArtifact {artifact_id}:")
                print(f"  Title: {artifact['title']}")
                print(f"  Description: {artifact['description']}")
                print(f"  Content title: {artifact['content'].get('title', 'NOT FOUND')}")
                print(f"  Content description: {artifact['content'].get('description', 'NOT FOUND')}")
    else:
        print(f"Upload failed: {result.error}")

if __name__ == "__main__":
    test_model_code_plan_fix()
