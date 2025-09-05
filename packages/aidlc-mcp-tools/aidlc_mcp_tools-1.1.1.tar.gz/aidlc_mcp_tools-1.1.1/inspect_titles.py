#!/usr/bin/env python3
"""
Detailed inspection of Domain Model and UI Code Plan titles
"""

import os
import sys
import json
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def inspect_titles():
    tools = AIDLCDashboardMCPTools(base_url="http://44.235.223.99:8000/api")
    
    print("=== Inspecting Domain Model and UI Code Plan Titles ===")
    
    # Get the project we just created
    project_id = "project-33b5f2f2"  # From previous test
    
    status_result = tools.aidlc_get_project_status(project_id)
    if not status_result.success:
        print(f"❌ Failed to get project: {status_result.error}")
        return
    
    artifacts = status_result.data.get("data", {}).get("project", {}).get("artifacts", {})
    
    # Find Domain Model and UI Code Plan artifacts
    domain_models = [art for art in artifacts.values() if art.get("type") == "domain-model"]
    ui_plans = [art for art in artifacts.values() if art.get("type") == "ui-code-plan"]
    
    print(f"\n🔍 Found {len(domain_models)} Domain Model(s) and {len(ui_plans)} UI Code Plan(s)")
    
    # Inspect Domain Models
    print("\n📊 DOMAIN MODEL DETAILS:")
    for i, dm in enumerate(domain_models, 1):
        print(f"\n  Domain Model {i}:")
        print(f"    ID: {dm.get('id')}")
        print(f"    Title: '{dm.get('title', 'NO TITLE')}'")
        print(f"    Description: '{dm.get('description', 'NO DESCRIPTION')}'")
        
        content = dm.get('content', {})
        print(f"    Content keys: {list(content.keys())}")
        
        entities = content.get('entities', [])
        print(f"    Entities count: {len(entities)}")
        if entities:
            print(f"    First entity: {entities[0]}")
            
        # Check if title exists in content
        if 'title' in content:
            print(f"    Content title: '{content['title']}'")
        else:
            print(f"    ❌ No 'title' field in content")
    
    # Inspect UI Code Plans  
    print("\n🎨 UI CODE PLAN DETAILS:")
    for i, ui in enumerate(ui_plans, 1):
        print(f"\n  UI Code Plan {i}:")
        print(f"    ID: {ui.get('id')}")
        print(f"    Title: '{ui.get('title', 'NO TITLE')}'")
        print(f"    Description: '{ui.get('description', 'NO DESCRIPTION')}'")
        
        content = ui.get('content', {})
        print(f"    Content keys: {list(content.keys())}")
        
        pages = content.get('pages', [])
        print(f"    Pages count: {len(pages)}")
        if pages:
            print(f"    First page: {pages[0]}")
            
        # Check various title fields
        title_fields = ['title', 'plan_id', 'name']
        for field in title_fields:
            if field in content:
                print(f"    Content {field}: '{content[field]}'")
            else:
                print(f"    ❌ No '{field}' field in content")
    
    # Test with a new artifact to see the raw response
    print("\n🧪 TESTING NEW UI CODE PLAN:")
    test_ui_plan = {
        "plan_id": "test-plan-001",
        "title": "Test UI Plan Title",
        "name": "Test Plan Name",
        "pages": [
            {"name": "TestPage", "route": "/test", "components": ["TestComponent"]}
        ]
    }
    
    test_result = tools.aidlc_upload_ui_code_plan(project_id, test_ui_plan)
    if test_result.success:
        print("✅ Test UI plan uploaded")
        
        # Get updated status
        updated_status = tools.aidlc_get_project_status(project_id)
        if updated_status.success:
            updated_artifacts = updated_status.data.get("data", {}).get("project", {}).get("artifacts", {})
            new_ui_plans = [art for art in updated_artifacts.values() if art.get("type") == "ui-code-plan"]
            
            print(f"\n📋 UPDATED UI PLANS ({len(new_ui_plans)} total):")
            for i, ui in enumerate(new_ui_plans, 1):
                print(f"  {i}. Title: '{ui.get('title', 'NO TITLE')}'")
                content = ui.get('content', {})
                if 'title' in content:
                    print(f"     Content title: '{content['title']}'")
                if 'plan_id' in content:
                    print(f"     Plan ID: '{content['plan_id']}'")
    else:
        print(f"❌ Test upload failed: {test_result.error}")

if __name__ == "__main__":
    inspect_titles()
