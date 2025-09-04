#!/usr/bin/env python3
"""
Complete test of AIDLC Dashboard with updated server
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_complete_workflow():
    # Initialize tools with the new server
    tools = AIDLCDashboardMCPTools(base_url="http://44.235.223.99:8000/api")
    
    print("=== Complete AIDLC Dashboard Test ===")
    print("Server: http://44.235.223.99:8000")
    
    # 1. Health check
    print("\n1. Health Check:")
    health = tools.aidlc_health_check()
    print(f"✅ Health: {health.success}")
    if health.data:
        print(f"   Version: {health.data.get('version', 'Unknown')}")
    
    # 2. Create project
    print("\n2. Creating Project:")
    project_result = tools.aidlc_create_project("Complete Test Project", "Testing all functionality with updated server")
    if not project_result.success:
        print(f"❌ Failed: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ Project created: {project_id}")
    
    # 3. Upload Epics
    print("\n3. Uploading Epics:")
    epics = [
        {
            "id": "epic-001",
            "title": "User Management Epic",
            "description": "Complete user authentication and profile management",
            "priority": "high",
            "acceptance_criteria": ["User can register", "User can login", "User can update profile"]
        },
        {
            "id": "epic-002", 
            "title": "Order Processing Epic",
            "description": "Handle order creation and fulfillment",
            "priority": "medium",
            "acceptance_criteria": ["Create orders", "Process payments", "Track shipments"]
        }
    ]
    
    epics_result = tools.aidlc_upload_epics(project_id, epics)
    print(f"✅ Epics: {epics_result.success} ({epics_result.data.get('total_count', 0)} uploaded)")
    
    # 4. Upload User Stories
    print("\n4. Uploading User Stories:")
    user_stories = [
        {
            "id": "us-001",
            "title": "User Registration",
            "description": "As a new user, I want to create an account",
            "acceptance_criteria": ["Valid email required", "Password strength validation"],
            "priority": "high",
            "story_points": 5
        },
        {
            "id": "us-002",
            "title": "User Login", 
            "description": "As a user, I want to login to my account",
            "acceptance_criteria": ["Email/password authentication", "Remember me option"],
            "priority": "high",
            "story_points": 3
        }
    ]
    
    stories_result = tools.aidlc_upload_user_stories(project_id, user_stories)
    print(f"✅ User Stories: {stories_result.success} ({stories_result.data.get('total_count', 0)} uploaded)")
    
    # 5. Upload Domain Model
    print("\n5. Uploading Domain Model:")
    domain_entities = [
        {
            "id": "entity-user",
            "name": "User",
            "attributes": ["id", "email", "password_hash", "profile", "created_at"],
            "description": "System user entity"
        },
        {
            "id": "entity-order",
            "name": "Order", 
            "attributes": ["id", "user_id", "items", "total", "status", "created_at"],
            "description": "Customer order entity"
        }
    ]
    
    domain_result = tools.aidlc_upload_domain_model(project_id, domain_entities)
    print(f"✅ Domain Model: {domain_result.success}")
    
    # 6. Upload Model Code Plan
    print("\n6. Uploading Model Code Plan:")
    code_phases = [
        {
            "id": "phase-entities",
            "name": "Entity Layer",
            "description": "Core domain entities and value objects",
            "components": ["User", "Order", "Profile"],
            "dependencies": []
        },
        {
            "id": "phase-services",
            "name": "Service Layer",
            "description": "Business logic and application services", 
            "components": ["UserService", "OrderService", "AuthService"],
            "dependencies": ["Entity Layer"]
        }
    ]
    
    code_result = tools.aidlc_upload_model_code_plan(project_id, code_phases)
    print(f"✅ Model Code Plan: {code_result.success} ({code_result.data.get('total_count', 0)} phases)")
    
    # 7. Upload UI Code Plan
    print("\n7. Uploading UI Code Plan:")
    ui_plan = {
        "plan_id": "ui-main-plan",
        "title": "Main Application UI",
        "pages": [
            {
                "name": "LoginPage",
                "route": "/login",
                "components": ["LoginForm", "ForgotPassword", "Header"]
            },
            {
                "name": "DashboardPage", 
                "route": "/dashboard",
                "components": ["UserProfile", "OrderHistory", "Navigation"]
            },
            {
                "name": "OrderPage",
                "route": "/orders",
                "components": ["OrderList", "OrderDetails", "StatusTracker"]
            }
        ],
        "navigation": {
            "type": "SPA",
            "router": "React Router",
            "authentication": "required"
        }
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(project_id, ui_plan)
    print(f"✅ UI Code Plan: {ui_result.success}")
    
    # 8. Get final project status
    print("\n8. Final Project Status:")
    status_result = tools.aidlc_get_project_status(project_id)
    if status_result.success:
        project_data = status_result.data.get("data", {}).get("project", {})
        artifacts = project_data.get("artifacts", {})
        
        print(f"✅ Project Status Retrieved")
        print(f"   Total Artifacts: {len(artifacts)}")
        
        # Check artifact titles
        print("\n📋 Artifact Titles:")
        for artifact_id, artifact in artifacts.items():
            artifact_type = artifact.get("type", "unknown")
            title = artifact.get("title", "No title")
            print(f"   {artifact_type}: '{title}'")
        
        # Summary
        counts = project_data.get("artifact_counts", {})
        print(f"\n📊 Artifact Counts:")
        for artifact_type, count in counts.items():
            print(f"   {artifact_type}: {count}")
            
    else:
        print(f"❌ Failed to get project status: {status_result.error}")

if __name__ == "__main__":
    test_complete_workflow()
