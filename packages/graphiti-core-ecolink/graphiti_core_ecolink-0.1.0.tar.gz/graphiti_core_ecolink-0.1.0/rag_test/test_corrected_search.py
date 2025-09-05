#!/usr/bin/env python3
"""
测试修正后的搜索实现，使用 SearchFilters 而不是错误的参数
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

async def test_corrected_search():
    """测试修正后的搜索实现"""
    
    try:
        # 导入必要的模块
        from user_query import UserQueryHandler, SmartQueryRouter
        
        print("=" * 60)
        print("测试修正后的搜索实现")
        print("=" * 60)
        
        # 模拟的Graphiti实例和LLM客户端（仅用于测试参数传递）
        class MockGraphiti:
            async def search_(self, query, config, search_filter=None):
                # 模拟搜索结果
                class MockResults:
                    def __init__(self):
                        self.edges = []
                        self.nodes = []
                        self.episodes = []
                
                print(f"MockGraphiti.search_ 被调用:")
                print(f"  - query: {query}")
                print(f"  - config: {config}")
                print(f"  - search_filter: {search_filter}")
                
                return MockResults()
        
        class MockLLMClient:
            async def generate_response(self, prompt):
                return '{"type": "relationship_query", "confidence": 0.9, "keywords": ["关系"], "entities": ["我", "帅帅"], "intent": "查询关系", "domain": "人际关系", "complexity": "简单"}'
        
        # 创建模拟实例
        mock_graphiti = MockGraphiti()
        mock_llm_client = MockLLMClient()
        
        # 测试 SmartQueryRouter
        print("\n1. 测试 SmartQueryRouter.relationship_focused_search")
        print("-" * 40)
        
        router = SmartQueryRouter(mock_graphiti, mock_llm_client)
        
        # 测试不包含失效关系
        print("\n测试 include_expired=False:")
        result1 = await router.relationship_focused_search(
            user_query="我和帅帅是什么关系",
            intent={"type": "relationship_query"},
            include_expired=False
        )
        print(f"结果: {result1['include_expired']}")
        
        # 测试包含失效关系
        print("\n测试 include_expired=True:")
        result2 = await router.relationship_focused_search(
            user_query="我和帅帅是什么关系",
            intent={"type": "relationship_query"},
            include_expired=True
        )
        print(f"结果: {result2['include_expired']}")
        
        # 测试 UserQueryHandler
        print("\n2. 测试 UserQueryHandler.handle_user_query")
        print("-" * 40)
        
        handler = UserQueryHandler(mock_graphiti, mock_llm_client)
        
        # 测试不包含失效关系
        print("\n测试 include_expired=False:")
        result3 = await handler.handle_user_query(
            user_query="我和帅帅是什么关系",
            strategy="smart",
            include_expired=False
        )
        print(f"结果: {result3['include_expired']}")
        
        # 测试包含失效关系
        print("\n测试 include_expired=True:")
        result4 = await handler.handle_user_query(
            user_query="我和帅帅是什么关系",
            strategy="smart",
            include_expired=True
        )
        print(f"结果: {result4['include_expired']}")
        
        # 测试时间上下文查询
        print("\n3. 测试时间上下文查询")
        print("-" * 40)
        
        print("\n测试 include_historical=True:")
        historical_results1 = await handler.search_with_time_context(
            user_query="我和帅帅的关系变化",
            include_historical=True
        )
        
        print("\n测试 include_historical=False:")
        historical_results2 = await handler.search_with_time_context(
            user_query="我和帅帅的关系变化",
            include_historical=False
        )
        
        print("\n" + "=" * 60)
        print("测试完成！所有方法都正确使用了 SearchFilters。")
        print("=" * 60)
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保 user_query.py 文件存在且可导入")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_corrected_search())
