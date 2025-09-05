#!/usr/bin/env python3
"""
Test creating 3 separate domain models: User, Order, Product
"""

import os
import sys
sys.path.insert(0, '.')

from aidlc_mcp_tools.tools import AIDLCDashboardMCPTools

def test_separate_domain_models():
    tools = AIDLCDashboardMCPTools(base_url="http://localhost:8000/api")
    
    print("=== 创建新项目并分别提交3个 Domain Model ===")
    
    # 1. 创建项目
    print("\n1️⃣ 创建项目:")
    project_result = tools.aidlc_create_project(
        "分离式电商系统", 
        "采用分离式领域模型设计的电商系统，用户、订单、商品各自独立管理"
    )
    
    if not project_result.success:
        print(f"❌ 项目创建失败: {project_result.error}")
        return
    
    project_id = project_result.data.get("project_id")
    print(f"✅ 项目创建成功: {project_id}")
    
    # 2. 提交用户 Domain Model
    print("\n2️⃣ 提交用户 Domain Model:")
    user_entities = [
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
            "description": "系统用户实体，负责用户认证、个人信息管理和权限控制"
        }
    ]
    
    user_result = tools.aidlc_upload_domain_model(
        project_id, 
        user_entities,
        title="用户管理领域模型",
        description="用户管理子系统的领域模型，包含用户注册、登录、个人信息管理等核心功能"
    )
    
    print(f"用户模型: {'✅ 成功' if user_result.success else '❌ 失败: ' + user_result.error}")
    
    # 3. 提交订单 Domain Model
    print("\n3️⃣ 提交订单 Domain Model:")
    order_entities = [
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
            "description": "订单实体，管理用户购买流程、支付状态和物流跟踪"
        }
    ]
    
    order_result = tools.aidlc_upload_domain_model(
        project_id, 
        order_entities,
        title="订单管理领域模型",
        description="订单管理子系统的领域模型，处理订单创建、支付、发货、配送等完整业务流程"
    )
    
    print(f"订单模型: {'✅ 成功' if order_result.success else '❌ 失败: ' + order_result.error}")
    
    # 4. 提交商品 Domain Model
    print("\n4️⃣ 提交商品 Domain Model:")
    product_entities = [
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
            "description": "商品实体，管理商品信息、价格策略、库存控制和分类体系"
        }
    ]
    
    product_result = tools.aidlc_upload_domain_model(
        project_id, 
        product_entities,
        title="商品管理领域模型",
        description="商品管理子系统的领域模型，包含商品信息维护、价格管理、库存控制、分类管理等功能"
    )
    
    print(f"商品模型: {'✅ 成功' if product_result.success else '❌ 失败: ' + product_result.error}")
    
    # 5. 查看最终项目状态
    print("\n5️⃣ 查看项目状态:")
    status_result = tools.aidlc_get_project_status(project_id)
    
    if status_result.success:
        project_data = status_result.data.get("data", {}).get("project", {})
        artifacts = project_data.get("artifacts", {})
        
        print(f"✅ 项目状态获取成功")
        print(f"   项目名称: {project_data.get('name', 'Unknown')}")
        print(f"   总 artifacts: {len(artifacts)}")
        
        # 查看所有 Domain Model artifacts
        domain_artifacts = [art for art in artifacts.values() if art.get("type") == "domain-model"]
        print(f"\n📊 Domain Model Artifacts ({len(domain_artifacts)} 个):")
        
        for i, domain_artifact in enumerate(domain_artifacts, 1):
            title = domain_artifact.get('title', 'NO TITLE')
            description = domain_artifact.get('description', 'NO DESCRIPTION')
            
            content = domain_artifact.get('content', {})
            entities = content.get('entities', [])
            
            print(f"\n   {i}. 标题: '{title}'")
            print(f"      描述: '{description}'")
            print(f"      实体数量: {len(entities)}")
            
            if entities:
                entity = entities[0]  # 每个模型只有一个实体
                entity_name = entity.get('name', 'Unknown')
                attributes_count = len(entity.get('attributes', []))
                print(f"      实体: {entity_name} ({attributes_count} 个属性)")
        
        # 显示项目统计
        counts = project_data.get("artifact_counts", {})
        if counts:
            print(f"\n📈 项目统计:")
            for artifact_type, count in counts.items():
                print(f"   {artifact_type}: {count} 个")
    else:
        print(f"❌ 获取项目状态失败: {status_result.error}")

if __name__ == "__main__":
    test_separate_domain_models()
