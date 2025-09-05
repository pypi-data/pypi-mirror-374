#!/usr/bin/env python3
"""
Final verification test with a completely new project
"""

import os
import sys
import json
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_final_verification():
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    print("=== FINAL VERIFICATION - New Project Test ===")
    
    # Create brand new project
    project_result = tools.aidlc_create_project(
        "Final Verification Project", 
        "Complete test of all fixes with proper titles and descriptions"
    )
    
    if not project_result.success:
        print(f"❌ Failed to create project: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ Created new project: {project_id}")
    
    # 1. Upload Epics
    print("\n1️⃣ Uploading Epics:")
    epics = [
        {
            "id": "epic-auth",
            "title": "Authentication System",
            "description": "Complete user authentication and authorization system",
            "priority": "high"
        },
        {
            "id": "epic-orders",
            "title": "Order Management",
            "description": "Order processing and tracking system",
            "priority": "medium"
        }
    ]
    
    epics_result = tools.aidlc_upload_epics(project_id, epics)
    print(f"   Result: {epics_result.success}")
    
    # 2. Upload User Stories
    print("\n2️⃣ Uploading User Stories:")
    user_stories = [
        {
            "id": "us-login",
            "title": "User Login",
            "description": "As a user, I want to login to access my account",
            "priority": "high",
            "story_points": 3
        },
        {
            "id": "us-register",
            "title": "User Registration",
            "description": "As a new user, I want to create an account",
            "priority": "high",
            "story_points": 5
        }
    ]
    
    stories_result = tools.aidlc_upload_user_stories(project_id, user_stories)
    print(f"   Result: {stories_result.success}")
    
    # 3. Upload Domain Model
    print("\n3️⃣ Uploading Domain Model:")
    domain_entities = [
        {
            "id": "entity-customer",
            "name": "Customer",
            "attributes": ["id", "email", "name", "phone", "address"],
            "description": "Customer entity for the system"
        },
        {
            "id": "entity-product",
            "name": "Product",
            "attributes": ["id", "name", "price", "category", "stock"],
            "description": "Product catalog entity"
        }
    ]
    
    domain_result = tools.aidlc_upload_domain_model(project_id, domain_entities)
    print(f"   Result: {domain_result.success}")
    
    # 4. Upload Model Code Plan
    print("\n4️⃣ Uploading Model Code Plan:")
    code_phases = [
        {
            "id": "phase-entities",
            "name": "Entity Layer",
            "description": "Core domain entities and value objects",
            "components": ["Customer", "Product", "Order"]
        },
        {
            "id": "phase-services",
            "name": "Service Layer",
            "description": "Business logic and application services",
            "components": ["CustomerService", "ProductService", "OrderService"]
        }
    ]
    
    code_result = tools.aidlc_upload_model_code_plan(project_id, code_phases)
    print(f"   Result: {code_result.success}")
    
    # 5. Upload UI Code Plan
    print("\n5️⃣ Uploading UI Code Plan:")
    ui_plan = {
        "plan_id": "main-ui-plan",
        "title": "E-commerce Web Application",
        "name": "Main UI Plan",
        "description": "Complete web application UI for e-commerce platform",
        "pages": [
            {
                "name": "HomePage",
                "route": "/",
                "components": ["Header", "ProductGrid", "Footer"]
            },
            {
                "name": "LoginPage",
                "route": "/login",
                "components": ["LoginForm", "SocialLogin"]
            },
            {
                "name": "ProductPage",
                "route": "/product/:id",
                "components": ["ProductDetails", "ReviewSection", "RelatedProducts"]
            },
            {
                "name": "CartPage",
                "route": "/cart",
                "components": ["CartItems", "CheckoutButton", "PriceCalculator"]
            }
        ],
        "navigation": {
            "type": "SPA",
            "router": "React Router",
            "authentication": "JWT"
        },
        "styling": {
            "framework": "Tailwind CSS",
            "theme": "modern"
        }
    }
    
    ui_result = tools.aidlc_upload_ui_code_plan(project_id, ui_plan)
    print(f"   Result: {ui_result.success}")
    
    # 6. Get final project status and analyze
    print("\n📊 FINAL PROJECT ANALYSIS:")
    status_result = tools.aidlc_get_project_status(project_id)
    
    if status_result.success:
        project_data = status_result.data.get("data", {}).get("project", {})
        artifacts = project_data.get("artifacts", {})
        
        print(f"✅ Total artifacts created: {len(artifacts)}")
        
        # Analyze each artifact type
        artifact_types = {}
        for artifact in artifacts.values():
            artifact_type = artifact.get("type")
            if artifact_type not in artifact_types:
                artifact_types[artifact_type] = []
            artifact_types[artifact_type].append(artifact)
        
        # Check each type
        for artifact_type, artifacts_list in artifact_types.items():
            print(f"\n📋 {artifact_type.upper()} ({len(artifacts_list)} artifacts):")
            
            for i, artifact in enumerate(artifacts_list, 1):
                title = artifact.get("title", "NO TITLE")
                description = artifact.get("description", "NO DESCRIPTION")
                
                print(f"   {i}. Title: '{title}'")
                print(f"      Description: '{description}'")
                
                # Show content keys for verification
                content = artifact.get("content", {})
                if content:
                    important_keys = []
                    if artifact_type == "ui-code-plan":
                        important_keys = ["plan_id", "title", "name", "description", "pages"]
                    elif artifact_type == "domain-model":
                        important_keys = ["entities"]
                    elif artifact_type == "user-stories":
                        important_keys = ["story_id", "title"]
                    elif artifact_type == "epics":
                        important_keys = ["epic_id", "title"]
                    elif artifact_type == "model-code-plan":
                        important_keys = ["phase_id", "name", "description"]
                    
                    for key in important_keys:
                        if key in content:
                            value = content[key]
                            if isinstance(value, list):
                                print(f"      Content {key}: {len(value)} items")
                            else:
                                print(f"      Content {key}: '{value}'")
                        else:
                            print(f"      Content {key}: ❌ MISSING")
                print()
        
        # Summary
        counts = project_data.get("artifact_counts", {})
        print(f"📈 SUMMARY:")
        for artifact_type, count in counts.items():
            print(f"   {artifact_type}: {count} artifacts")
            
    else:
        print(f"❌ Failed to get project status: {status_result.error}")

if __name__ == "__main__":
    test_final_verification()
