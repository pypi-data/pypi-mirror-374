#!/usr/bin/env python3
"""
Test script to verify domain model content includes title and description
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aidlc_mcp_tools.server import AIDLCMCPServer

def test_and_verify_domain_model():
    """Test domain model upload and verify content"""
    
    server = AIDLCMCPServer()
    project_id = "project-2173fcf5"
    
    # Test data
    test_title = "测试电商领域模型"
    test_description = "这是一个测试用的电商系统领域模型，包含核心业务实体"
    test_entities = [
        {
            "name": "TestEntity",
            "description": "测试实体",
            "attributes": ["id", "name", "created_at"]
        }
    ]
    
    print("=== 测试MCP域模型上传（带title和description）===")
    
    # 1. Upload domain model with title and description
    print("1. 上传域模型...")
    upload_result = server.tools.aidlc_upload_domain_model(
        project_id,
        test_entities,
        test_title,
        test_description
    )
    
    if not upload_result.success:
        print(f"❌ 上传失败: {upload_result.error}")
        return False
    
    artifact_id = upload_result.data.get('artifact_id')
    print(f"✅ 上传成功，artifact_id: {artifact_id}")
    
    # 2. Get project status to verify content
    print("2. 获取项目状态验证内容...")
    import time
    time.sleep(1)  # Wait for server to process
    status_result = server.tools.aidlc_get_project_status(project_id)
    
    if not status_result.success:
        print(f"❌ 获取项目状态失败: {status_result.error}")
        return False
    
    # 3. Check if the uploaded artifact contains title and description
    project_data = status_result.data.get('project', {})
    artifacts = project_data.get('artifacts', {})
    
    print(f"Available artifacts: {list(artifacts.keys())}")
    print(f"Looking for artifact: {artifact_id}")
    
    if artifact_id not in artifacts:
        print(f"❌ 找不到artifact {artifact_id}")
        # Try to find the most recent artifact
        if artifacts:
            latest_artifact_id = max(artifacts.keys())
            print(f"使用最新的artifact: {latest_artifact_id}")
            artifact_id = latest_artifact_id
        else:
            print("❌ 没有找到任何artifacts")
            return False
    
    artifact = artifacts[artifact_id]
    content = artifact.get('content', {})
    
    print("3. 验证内容...")
    print(f"Artifact content: {json.dumps(content, indent=2, ensure_ascii=False)}")
    
    # Check title and description in content
    content_title = content.get('title', '')
    content_description = content.get('description', '')
    
    print(f"Content title: '{content_title}'")
    print(f"Content description: '{content_description}'")
    print(f"Expected title: '{test_title}'")
    print(f"Expected description: '{test_description}'")
    
    # Verify results
    title_correct = content_title == test_title
    description_correct = content_description == test_description
    
    if title_correct and description_correct:
        print("✅ 验证成功！title和description都正确保存在content中")
        return True
    else:
        print("❌ 验证失败！")
        if not title_correct:
            print(f"  - Title不匹配: 期望'{test_title}', 实际'{content_title}'")
        if not description_correct:
            print(f"  - Description不匹配: 期望'{test_description}', 实际'{content_description}'")
        return False

if __name__ == "__main__":
    success = test_and_verify_domain_model()
    sys.exit(0 if success else 1)
