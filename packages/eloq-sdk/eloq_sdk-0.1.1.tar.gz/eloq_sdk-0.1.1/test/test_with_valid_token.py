#!/usr/bin/env python3
"""
Eloq SDK 函数功能可用性测试 - 使用有效token
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eloq_sdk import from_token
from eloq_sdk.utils import compact_mapping, to_iso8601, from_iso8601


def test_with_example_token():
    """使用example文件中的有效token进行测试"""
    
    # 从example文件中提取的token
    example_token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIzMCwiZXhwIjoxNzU2MTMyMTMwfQ.9EsOwdhaUQUOey7o3-qIfHESCaQTjOor6orNTb51HsGznnFm_vTEEmfnvKe1_6I_Erq2bU2BaCsuq3DoXe-d-w"
    
    print("🔑 使用example文件中的token进行测试...")
    print(f"Token: {example_token[:20]}...")
    
    try:
        # 创建客户端
        client = from_token(example_token)
        print("✅ 客户端创建成功")
        
        # 测试 org_info
        print("\n🔍 测试 org_info...")
        org_info = client.org_info()
        print(f"✅ org_info 调用成功，返回类型: {type(org_info)}")
        
        # 检查返回结果的结构
        if hasattr(org_info, '__dict__'):
            print(f"   属性: {list(org_info.__dict__.keys())}")
        
        if hasattr(org_info, 'org_info'):
            org_details = org_info.org_info
            print(f"✅ 找到 org_info 子对象")
            if hasattr(org_details, 'org_id'):
                org_id = org_details.org_id
                print(f"   组织ID: {org_id}")
            if hasattr(org_details, 'projects') and org_details.projects:
                project_id = org_details.projects[0].project_id
                print(f"   项目ID: {project_id}")
                
                # 测试 clusters
                print(f"\n🔍 测试 clusters...")
                try:
                    clusters = client.clusters(org_id, project_id, page=1, per_page=5)
                    print(f"✅ clusters 调用成功，返回类型: {type(clusters)}")
                    if clusters:
                        print(f"   找到 {len(clusters)} 个集群")
                        for i, cluster in enumerate(clusters[:3]):  # 只显示前3个
                            if hasattr(cluster, 'cluster_name'):
                                print(f"   [{i+1}] {cluster.cluster_name}")
                    else:
                        print("   没有找到集群")
                except Exception as e:
                    print(f"❌ clusters 调用失败: {e}")
            else:
                print("⚠️ 没有找到项目信息")
        else:
            print("⚠️ 返回结果中没有 org_info 属性")
            
        # 测试其他函数
        print(f"\n🔍 测试其他函数...")
        
        # 测试 dashboard_info
        try:
            dashboard = client.dashboard_info()
            print(f"✅ dashboard_info 调用成功")
        except Exception as e:
            print(f"❌ dashboard_info 调用失败: {e}")
        
        # 测试 user_subscription
        try:
            subscription = client.user_subscription()
            print(f"✅ user_subscription 调用成功")
        except Exception as e:
            print(f"❌ user_subscription 调用失败: {e}")
        
        # 测试 list_pricing_plans
        try:
            plans = client.list_pricing_plans()
            print(f"✅ list_pricing_plans 调用成功")
        except Exception as e:
            print(f"❌ list_pricing_plans 调用失败: {e}")
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("🚀 Eloq SDK 有效Token测试")
    print("=" * 50)
    
    test_with_example_token()


if __name__ == "__main__":
    main()
