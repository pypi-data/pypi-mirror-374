#!/usr/bin/env python3
"""
Test script to verify MCP domain model fix through direct MCP server simulation
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aidlc_mcp_tools.server import AIDLCMCPServer

def test_domain_model_with_title():
    """Test domain model upload with title and description through MCP interface"""
    
    # Create MCP server instance
    server = AIDLCMCPServer()
    
    # Simulate MCP tool call with title and description
    tool_name = "aidlc_upload_domain_model"
    arguments = {
        "project_id": "project-2173fcf5",
        "domain_entities": [
            {
                "name": "OrderItem",
                "description": "订单项实体，记录订单中的具体商品信息",
                "attributes": ["id", "order_id", "product_id", "quantity", "unit_price", "total_price", "created_at"]
            }
        ],
        "title": "完整电商系统领域模型",
        "description": "包含用户管理、订单处理、商品管理和库存管理的完整电商系统领域模型"
    }
    
    print("Testing MCP domain model upload with title and description...")
    print(f"Tool: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
    
    try:
        # This simulates the MCP call path
        result = server.tools.aidlc_upload_domain_model(
            arguments["project_id"],
            arguments["domain_entities"],
            arguments.get("title", ""),
            arguments.get("description", "")
        )
        
        print(f"\nResult: {result}")
        
        if result.success:
            print("✅ MCP domain model upload with title/description works!")
            return True
        else:
            print(f"❌ Upload failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_domain_model_with_title()
    sys.exit(0 if success else 1)
