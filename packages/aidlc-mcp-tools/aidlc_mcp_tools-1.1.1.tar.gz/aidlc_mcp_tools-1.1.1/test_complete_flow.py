#!/usr/bin/env python3
"""
Complete end-to-end test: Create project -> Upload domain model with title -> Verify
"""

import json
import sys
import os
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aidlc_mcp_tools.server import AIDLCMCPServer

def test_complete_flow():
    """Test complete flow from project creation to domain model verification"""
    
    server = AIDLCMCPServer()
    
    print("=== 完整MCP流程测试 ===")
    
    # 1. Create new project
    print("1. 创建新项目...")
    project_name = "MCP修复验证项目"
    create_result = server.tools.aidlc_create_project(project_name)
    
    if not create_result.success:
        print(f"❌ 项目创建失败: {create_result.error}")
        return False
    
    project_id = create_result.data.get('project_id')
    print(f"✅ 项目创建成功: {project_name}")
    print(f"   项目ID: {project_id}")
    
    # 2. Upload domain model with title and description
    print("\n2. 上传带title的domain model...")
    
    test_title = "电商系统完整领域模型"
    test_description = "包含用户管理、商品管理、订单处理、支付处理等核心业务领域的完整模型"
    test_entities = [
        {
            "name": "User",
            "description": "系统用户实体，管理用户基本信息和认证",
            "attributes": ["id", "username", "email", "password_hash", "phone", "created_at", "updated_at"]
        },
        {
            "name": "Product", 
            "description": "商品实体，存储商品基本信息和库存",
            "attributes": ["id", "name", "description", "price", "stock_quantity", "category_id", "created_at", "updated_at"]
        },
        {
            "name": "Order",
            "description": "订单实体，记录用户购买信息和订单状态", 
            "attributes": ["id", "user_id", "order_number", "total_amount", "status", "shipping_address", "created_at", "updated_at"]
        }
    ]
    
    # Simulate MCP call with all parameters
    upload_result = server.tools.aidlc_upload_domain_model(
        project_id,
        test_entities,
        test_title,
        test_description
    )
    
    if not upload_result.success:
        print(f"❌ Domain model上传失败: {upload_result.error}")
        return False
    
    artifact_id = upload_result.data.get('artifact_id')
    entity_count = upload_result.data.get('entity_count')
    print(f"✅ Domain model上传成功")
    print(f"   Artifact ID: {artifact_id}")
    print(f"   实体数量: {entity_count}")
    
    # 3. Wait and verify content
    print("\n3. 验证上传内容...")
    time.sleep(1)  # Wait for server processing
    
    status_result = server.tools.aidlc_get_project_status(project_id)
    
    if not status_result.success:
        print(f"❌ 获取项目状态失败: {status_result.error}")
        return False
    
    # Extract artifact content
    project_data = status_result.data.get('data', {}).get('project', {})
    artifacts = project_data.get('artifacts', {})
    
    if artifact_id not in artifacts:
        print(f"❌ 找不到artifact {artifact_id}")
        print(f"   可用artifacts: {list(artifacts.keys())}")
        return False
    
    artifact = artifacts[artifact_id]
    content = artifact.get('content', {})
    
    # Verify title and description
    content_title = content.get('title', '')
    content_description = content.get('description', '')
    entities = content.get('entities', [])
    
    print(f"✅ 找到artifact内容")
    print(f"   Content title: '{content_title}'")
    print(f"   Content description: '{content_description}'")
    print(f"   实体数量: {len(entities)}")
    print(f"   实体名称: {[e.get('name') for e in entities]}")
    
    # Validation
    title_correct = content_title == test_title
    description_correct = content_description == test_description
    entity_count_correct = len(entities) == len(test_entities)
    
    print(f"\n4. 验证结果:")
    print(f"   Title匹配: {'✅' if title_correct else '❌'}")
    print(f"   Description匹配: {'✅' if description_correct else '❌'}")
    print(f"   实体数量匹配: {'✅' if entity_count_correct else '❌'}")
    
    if title_correct and description_correct and entity_count_correct:
        print(f"\n🎉 完整流程测试成功！")
        print(f"   项目: {project_name} ({project_id})")
        print(f"   Domain model包含正确的title和description")
        return True
    else:
        print(f"\n❌ 验证失败")
        if not title_correct:
            print(f"     期望title: '{test_title}'")
            print(f"     实际title: '{content_title}'")
        if not description_correct:
            print(f"     期望description: '{test_description}'")
            print(f"     实际description: '{content_description}'")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
