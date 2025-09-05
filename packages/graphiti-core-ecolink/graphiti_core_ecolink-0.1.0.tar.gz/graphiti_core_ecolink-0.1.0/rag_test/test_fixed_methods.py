#!/usr/bin/env python3
"""
测试修正后的方法定义，确保所有方法都正确定义和可访问
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

async def test_method_definitions():
    """测试所有方法的定义和可访问性"""
    
    try:
        # 导入必要的模块
        from user_query import UserQueryHandler, SmartQueryRouter
        
        print("=" * 60)
        print("测试方法定义和可访问性")
        print("=" * 60)
        
        # 模拟的Graphiti实例和LLM客户端
        class MockGraphiti:
            async def search(self, query, num_results=20):
                class MockResults:
                    def __init__(self):
                        self.edges = []
                        self.nodes = []
                        self.episodes = []
                return MockResults()
            
            async def search_(self, query, config, search_filter=None):
                class MockResults:
                    def __init__(self):
                        self.edges = []
                        self.nodes = []
                        self.episodes = []
                return MockResults()
        
        class MockLLMClient:
            async def generate_response(self, prompt):
                return '{"type": "relationship_query", "confidence": 0.9, "keywords": ["关系"], "entities": ["我", "帅帅"], "intent": "查询关系", "domain": "人际关系", "complexity": "简单"}'
        
        # 创建模拟实例
        mock_graphiti = MockGraphiti()
        mock_llm_client = MockLLMClient()
        
        # 测试 SmartQueryRouter
        print("\n1. 测试 SmartQueryRouter 类")
        print("-" * 40)
        
        router = SmartQueryRouter(mock_graphiti, mock_llm_client)
        print("✓ SmartQueryRouter 实例创建成功")
        
        # 检查方法是否存在
        methods_to_check = [
            'smart_query_router',
            'analyze_user_intent',
            'relationship_focused_search',
            'entity_focused_search',
            'content_focused_search',
            'knowledge_focused_search',
            'comprehensive_search',
            'fallback_search'
        ]
        
        for method_name in methods_to_check:
            if hasattr(router, method_name):
                print(f"✓ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法缺失")
        
        # 测试 fallback_search 方法
        print("\n测试 fallback_search 方法:")
        try:
            result = await router.fallback_search("测试查询")
            print(f"✓ fallback_search 执行成功，返回结果: {result['search_strategy']}")
        except Exception as e:
            print(f"❌ fallback_search 执行失败: {e}")
        
        # 测试 UserQueryHandler
        print("\n2. 测试 UserQueryHandler 类")
        print("-" * 40)
        
        handler = UserQueryHandler(mock_graphiti, mock_llm_client)
        print("✓ UserQueryHandler 实例创建成功")
        
        # 检查方法是否存在
        handler_methods_to_check = [
            'handle_user_query',
            'post_process_results',
            'extract_similarity_score',
            'generate_answer',
            'fallback_search',
            'search_with_time_context'
        ]
        
        for method_name in handler_methods_to_check:
            if hasattr(handler, method_name):
                print(f"✓ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法缺失")
        
        # 测试 extract_similarity_score 方法
        print("\n测试 extract_similarity_score 方法:")
        try:
            # 创建一个模拟的item对象
            class MockItem:
                def __init__(self, score_value):
                    self.score = score_value
            
            mock_item = MockItem(0.8)
            score = handler.extract_similarity_score(mock_item)
            print(f"✓ extract_similarity_score 执行成功，返回评分: {score}")
        except Exception as e:
            print(f"❌ extract_similarity_score 执行失败: {e}")
        
        # 测试 handle_user_query 方法
        print("\n测试 handle_user_query 方法:")
        try:
            result = await handler.handle_user_query(
                user_query="测试查询",
                strategy="smart",
                include_expired=False
            )
            print(f"✓ handle_user_query 执行成功，返回结果: {result['search_strategy']}")
        except Exception as e:
            print(f"❌ handle_user_query 执行失败: {e}")
        
        print("\n" + "=" * 60)
        print("方法定义测试完成！")
        print("=" * 60)
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保 user_query.py 文件存在且可导入")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_method_definitions())
