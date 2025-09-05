#!/usr/bin/env python3
"""
Test script for AIDLC Dashboard MCP Tools
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_dashboard():
    # Initialize tools with the test server
    tools = AIDLCDashboardMCPTools(base_url="http://44.253.157.102:8000/api")
    
    print("=== Testing AIDLC Dashboard ===")
    
    # 1. Health check
    print("\n1. Health Check:")
    health = tools.aidlc_health_check()
    print(f"Health: {health.success}, Data: {health.data}")
    
    # 2. Create a new project
    print("\n2. Creating new project:")
    project_result = tools.aidlc_create_project("Test Project - Field Mapping", "Testing field name mapping fixes")
    print(f"Project creation: {project_result.success}")
    if project_result.success:
        project_id = project_result.data.get("project_id")
        print(f"Project ID: {project_id}")
    else:
        print(f"Error: {project_result.error}")
        return
    
    # 3. Test domain model upload
    print("\n3. Testing domain model upload:")
    domain_entities = [
        {
            "id": "user-entity-001",
            "name": "User",
            "attributes": ["id", "username", "email", "created_at"],
            "description": "System user entity"
        },
        {
            "id": "order-entity-002", 
            "name": "Order",
            "attributes": ["id", "user_id", "total", "status", "created_at"],
            "description": "Order entity"
        }
    ]
    
    domain_result = tools.aidlc_upload_domain_model(project_id, domain_entities)
    print(f"Domain model upload: {domain_result.success}")
    if domain_result.success:
        print(f"Uploaded entities: {domain_result.data.get('total_count')}")
    else:
        print(f"Error: {domain_result.error}")
    
    # 4. Test model code plan upload
    print("\n4. Testing model code plan upload:")
    code_phases = [
        {
            "id": "phase-001",
            "name": "Entity Layer",
            "component_name": "UserService",
            "type": "service",
            "dependencies": ["UserRepository"],
            "description": "User management service"
        },
        {
            "id": "phase-002",
            "name": "Repository Layer", 
            "component_name": "OrderRepository",
            "type": "repository",
            "dependencies": ["Database"],
            "description": "Order data access layer"
        }
    ]
    
    code_result = tools.aidlc_upload_model_code_plan(project_id, code_phases)
    print(f"Model code plan upload: {code_result.success}")
    if code_result.success:
        print(f"Uploaded phases: {code_result.data.get('total_count')}")
    else:
        print(f"Error: {code_result.error}")
    
    # 5. Test UI code plan upload
    print("\n5. Testing UI code plan upload:")
    ui_plan = {
        "id": "ui-plan-001",
        "pages": [
            {
                "name": "LoginPage",
                "route": "/login",
                "components": ["LoginForm", "Header"]
            },
            {
                "name": "DashboardPage",
                "route": "/dashboard", 
                "components": ["UserProfile", "OrderList"]
            }
        ],
        "navigation": {
            "type": "SPA",
            "router": "React Router"
        }
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(project_id, ui_plan)
    print(f"UI code plan upload: {ui_result.success}")
    if ui_result.success:
        print(f"UI plan uploaded successfully")
    else:
        print(f"Error: {ui_result.error}")
    
    # 6. Get project status to see all artifacts
    print("\n6. Getting project status:")
    status_result = tools.aidlc_get_project_status(project_id)
    print(f"Project status: {status_result.success}")
    if status_result.success:
        print("Project data:")
        import json
        print(json.dumps(status_result.data, indent=2))
    else:
        print(f"Error: {status_result.error}")

if __name__ == "__main__":
    test_dashboard()
