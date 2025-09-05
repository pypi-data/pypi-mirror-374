#!/usr/bin/env python3
"""
Debug script to understand server response structure
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aidlc_mcp_tools.server import AIDLCMCPServer

def debug_server_response():
    """Debug server response structure"""
    
    server = AIDLCMCPServer()
    project_id = "project-2173fcf5"
    
    print("=== 调试服务器响应结构 ===")
    
    # Get project status
    print("获取项目状态...")
    status_result = server.tools.aidlc_get_project_status(project_id)
    
    print(f"Status result success: {status_result.success}")
    print(f"Status result error: {status_result.error}")
    print(f"Status result data keys: {list(status_result.data.keys()) if status_result.data else 'None'}")
    
    if status_result.success and status_result.data:
        print("\n=== 完整响应数据 ===")
        print(json.dumps(status_result.data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    debug_server_response()
