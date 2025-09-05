#!/usr/bin/env python3
"""
Test content field preservation with local fixed server
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_local_fix():
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    print("=== Testing Local Fixed Server ===")
    
    # Health check
    health = tools.aidlc_health_check()
    print(f"✅ Health: {health.success}")
    
    # Create project
    project_result = tools.aidlc_create_project("Local Fix Test", "Testing field preservation locally")
    if not project_result.success:
        print(f"❌ Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ Created project: {project_id}")
    
    # Test UI Code Plan with all fields
    print("\n🎨 Testing UI Code Plan with explicit fields:")
    ui_plan = {
        "plan_id": "local-test-001",
        "title": "Local Test UI Plan",
        "name": "Test Plan Name",
        "description": "Testing field preservation",
        "pages": [
            {"name": "HomePage", "route": "/", "components": ["Header", "Hero"]},
            {"name": "AboutPage", "route": "/about", "components": ["AboutContent"]},
            {"name": "ContactPage", "route": "/contact", "components": ["ContactForm"]}
        ],
        "navigation": {"type": "SPA", "router": "React Router"},
        "styling": {"framework": "Tailwind CSS"}
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(project_id, ui_plan)
    print(f"UI Upload: {ui_result.success}")
    
    # Test Domain Model
    print("\n📊 Testing Domain Model:")
    domain_entities = [
        {
            "id": "local-user",
            "name": "LocalUser",
            "attributes": ["id", "name", "email"],
            "description": "Local test user entity"
        }
    ]
    
    domain_result = tools.aidlc_upload_domain_model(project_id, domain_entities)
    print(f"Domain Upload: {domain_result.success}")
    
    # Check results
    print("\n🔍 Checking preserved content:")
    status_result = tools.aidlc_get_project_status(project_id)
    if status_result.success:
        artifacts = status_result.data.get("data", {}).get("project", {}).get("artifacts", {})
        
        # Check UI Code Plan
        ui_artifacts = [art for art in artifacts.values() if art.get("type") == "ui-code-plan"]
        if ui_artifacts:
            ui_artifact = ui_artifacts[0]
            print(f"\n📋 UI Code Plan:")
            print(f"   Title: '{ui_artifact.get('title', 'NO TITLE')}'")
            print(f"   Description: '{ui_artifact.get('description', 'NO DESCRIPTION')}'")
            
            content = ui_artifact.get('content', {})
            print(f"   Content keys: {list(content.keys())}")
            
            # Check preserved fields
            preserved_fields = ['plan_id', 'title', 'name', 'description']
            for field in preserved_fields:
                if field in content:
                    print(f"   ✅ {field}: '{content[field]}'")
                else:
                    print(f"   ❌ {field}: MISSING")
        
        # Check Domain Model
        domain_artifacts = [art for art in artifacts.values() if art.get("type") == "domain-model"]
        if domain_artifacts:
            domain_artifact = domain_artifacts[0]
            print(f"\n📊 Domain Model:")
            print(f"   Title: '{domain_artifact.get('title', 'NO TITLE')}'")
            print(f"   Description: '{domain_artifact.get('description', 'NO DESCRIPTION')}'")
            
            content = domain_artifact.get('content', {})
            entities = content.get('entities', [])
            print(f"   Entities: {len(entities)}")
            if entities:
                print(f"   First entity: {entities[0]}")
    
    else:
        print(f"❌ Failed to get status: {status_result.error}")

if __name__ == "__main__":
    test_local_fix()
