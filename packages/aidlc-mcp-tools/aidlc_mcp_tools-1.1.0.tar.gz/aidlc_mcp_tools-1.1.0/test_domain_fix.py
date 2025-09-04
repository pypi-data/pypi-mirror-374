#!/usr/bin/env python3
"""
Test Domain Model title and description fix
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_domain_fix():
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    print("=== Testing Domain Model Title & Description Fix ===")
    
    # Create project
    project_result = tools.aidlc_create_project("Domain Model Fix Test", "Testing domain model title and description")
    if not project_result.success:
        print(f"❌ Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ Created project: {project_id}")
    
    # Test Domain Model with explicit title and description
    print("\n📊 Testing Domain Model with explicit title and description:")
    domain_entities = [
        {
            "id": "entity-user",
            "name": "User",
            "attributes": ["id", "username", "email", "password_hash", "created_at"],
            "description": "User account entity"
        },
        {
            "id": "entity-profile",
            "name": "Profile",
            "attributes": ["id", "user_id", "first_name", "last_name", "avatar"],
            "description": "User profile information entity"
        }
    ]
    
    # Upload with explicit title and description
    domain_result = tools.aidlc_upload_domain_model(
        project_id, 
        domain_entities,
        title="User Management Domain Model",
        description="Complete domain model for user management system including authentication and profiles"
    )
    
    print(f"Upload result: {domain_result.success}")
    
    # Check the result
    print("\n🔍 Checking Domain Model artifact:")
    status_result = tools.aidlc_get_project_status(project_id)
    
    if status_result.success:
        artifacts = status_result.data.get("data", {}).get("project", {}).get("artifacts", {})
        domain_artifacts = [art for art in artifacts.values() if art.get("type") == "domain-model"]
        
        if domain_artifacts:
            domain_artifact = domain_artifacts[0]
            print(f"📋 Domain Model Artifact:")
            print(f"   Title: '{domain_artifact.get('title', 'NO TITLE')}'")
            print(f"   Description: '{domain_artifact.get('description', 'NO DESCRIPTION')}'")
            
            content = domain_artifact.get('content', {})
            print(f"   Content keys: {list(content.keys())}")
            
            # Check content fields
            if 'title' in content:
                print(f"   ✅ Content title: '{content['title']}'")
            else:
                print(f"   ❌ Content title: MISSING")
                
            if 'description' in content:
                print(f"   ✅ Content description: '{content['description']}'")
            else:
                print(f"   ❌ Content description: MISSING")
                
            entities = content.get('entities', [])
            print(f"   ✅ Entities: {len(entities)} entities")
            if entities:
                print(f"   First entity: {entities[0].get('name', 'No name')}")
        else:
            print("❌ No domain model artifacts found")
    else:
        print(f"❌ Failed to get project status: {status_result.error}")

if __name__ == "__main__":
    test_domain_fix()
