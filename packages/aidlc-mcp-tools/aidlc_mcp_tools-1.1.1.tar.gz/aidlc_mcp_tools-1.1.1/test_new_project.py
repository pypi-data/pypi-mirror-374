#!/usr/bin/env python3
"""
Test creating new project with domain model (User, Order, Product entities)
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_new_project_with_domain_model():
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    print("=== 创建新项目并提交 Domain Model ===")
    
    # 1. 创建项目
    print("\n1️⃣ 创建项目:")
    project_result = tools.aidlc_create_project(
        "电商系统项目", 
        "包含用户管理、订单处理和商品管理的完整电商系统"
    )
    
    if not project_result.success:
        print(f"❌ 项目创建失败: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ 项目创建成功: {project_id}")
    
    # 2. 提交 Domain Model - 用户、订单、商品三个实体
    print("\n2️⃣ 提交 Domain Model:")
    domain_entities = [
        {
            "id": "entity-user",
            "name": "User",
            "attributes": [
                "id", 
                "username", 
                "email", 
                "password_hash", 
                "phone", 
                "address",
                "created_at",
                "updated_at"
            ],
            "description": "系统用户实体，包含用户基本信息和认证数据"
        },
        {
            "id": "entity-order",
            "name": "Order",
            "attributes": [
                "id",
                "user_id",
                "order_number",
                "total_amount",
                "status",
                "payment_method",
                "shipping_address",
                "order_date",
                "delivery_date"
            ],
            "description": "订单实体，记录用户购买行为和订单状态"
        },
        {
            "id": "entity-product",
            "name": "Product",
            "attributes": [
                "id",
                "name",
                "description",
                "price",
                "category_id",
                "stock_quantity",
                "sku",
                "brand",
                "created_at",
                "updated_at"
            ],
            "description": "商品实体，包含商品信息、价格和库存数据"
        }
    ]
    
    # 提交 Domain Model，包含整体标题和描述
    domain_result = tools.aidlc_upload_domain_model(
        project_id, 
        domain_entities,
        title="电商系统领域模型",
        description="包含用户、订单、商品三个核心实体的完整电商系统领域模型，支持用户注册登录、商品浏览购买、订单管理等核心业务流程"
    )
    
    if domain_result.success:
        print(f"✅ Domain Model 提交成功")
        print(f"   实体数量: {domain_result.data.get('entity_count', 0)}")
    else:
        print(f"❌ Domain Model 提交失败: {domain_result.error}")
        return
    
    # 3. 查看项目状态
    print("\n3️⃣ 查看项目状态:")
    status_result = tools.aidlc_get_project_status(project_id)
    
    if status_result.success:
        project_data = status_result.data.get("data", {}).get("project", {})
        artifacts = project_data.get("artifacts", {})
        
        print(f"✅ 项目状态获取成功")
        print(f"   项目名称: {project_data.get('name', 'Unknown')}")
        print(f"   总 artifacts: {len(artifacts)}")
        
        # 查看 Domain Model artifact 详情
        domain_artifacts = [art for art in artifacts.values() if art.get("type") == "domain-model"]
        if domain_artifacts:
            domain_artifact = domain_artifacts[0]
            print(f"\n📊 Domain Model Artifact 详情:")
            print(f"   标题: '{domain_artifact.get('title', 'NO TITLE')}'")
            print(f"   描述: '{domain_artifact.get('description', 'NO DESCRIPTION')}'")
            
            content = domain_artifact.get('content', {})
            entities = content.get('entities', [])
            print(f"   实体数量: {len(entities)}")
            
            for i, entity in enumerate(entities, 1):
                entity_name = entity.get('name', 'Unknown')
                entity_desc = entity.get('description', 'No description')
                attributes_count = len(entity.get('attributes', []))
                print(f"   {i}. {entity_name}: {attributes_count} 个属性")
                print(f"      描述: {entity_desc}")
        
        # 显示项目统计
        counts = project_data.get("artifact_counts", {})
        if counts:
            print(f"\n📈 项目统计:")
            for artifact_type, count in counts.items():
                print(f"   {artifact_type}: {count} 个")
    else:
        print(f"❌ 获取项目状态失败: {status_result.error}")

if __name__ == "__main__":
    test_new_project_with_domain_model()
