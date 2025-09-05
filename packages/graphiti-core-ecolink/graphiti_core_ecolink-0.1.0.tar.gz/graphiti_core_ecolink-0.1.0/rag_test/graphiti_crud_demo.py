"""
Graphiti CRUD 功能演示
使用Graphiti实现完整的CRUD操作，连接Neo4j数据库
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from typing import List, Optional

# ==================== 本地Graphiti Core配置 ====================
# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（rag_test的父目录）
project_root = os.path.dirname(current_dir)

# 添加项目根目录到Python路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✓ 已添加项目根目录到Python路径: {project_root}")

# 验证graphiti_core目录存在
graphiti_core_path = os.path.join(project_root, 'graphiti_core')
if os.path.exists(graphiti_core_path):
    print(f"✓ 找到本地Graphiti Core路径: {graphiti_core_path}")
else:
    print(f"⚠ 警告: 未找到本地Graphiti Core路径: {graphiti_core_path}")

# ==================== 导入Graphiti Core模块 ====================
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    from graphiti_core.utils.maintenance.graph_data_operations import clear_data
    
    # 验证是否使用了本地版本
    import graphiti_core
    print(f"Graphiti Core模块路径: {graphiti_core.__file__}")
    
    if 'site-packages' in graphiti_core.__file__:
        print("⚠ 警告: 使用的是已安装的Graphiti Core包，不是本地版本")
    else:
        print("✓ 正在使用本地Graphiti Core代码")
        
except ImportError as e:
    print(f"❌ 导入Graphiti Core失败: {e}")
    print("尝试备用导入方式...")
    
    # 备用导入方式：直接添加graphiti_core目录
    try:
        sys.path.insert(0, graphiti_core_path)
        from graphiti_core import Graphiti
        from graphiti_core.nodes import EpisodeType
        from graphiti_core.utils.maintenance.graph_data_operations import clear_data
        print("✓ 使用备用方式成功导入本地Graphiti Core")
    except ImportError as e2:
        print(f"❌ 备用导入也失败: {e2}")
        print("请检查graphiti_core目录结构是否正确")
        sys.exit(1)

# import time
# time.sleep(10000)

# ==================== 导入其他模块 ====================
# 导入阿里云模型配置
sys.path.append(current_dir)
from llm.aliyun_models_config import get_model_config, ALIYUN_API_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

def estimate_tokens(text: str) -> int:
    """
    估算文本的token数量
    使用简单的估算方法：大约4个字符=1个token
    
    Args:
        text: 要估算的文本
        
    Returns:
        int: 估算的token数量
    """
    # 简单的token估算：大约4个字符=1个token
    return len(text) // 4

def split_text_by_tokens(text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
    """
    按token数量分割文本
    
    Args:
        text: 要分割的文本
        max_tokens: 每个分片的最大token数量
        overlap: 分片之间的重叠token数量
        
    Returns:
        List[str]: 分割后的文本片段列表
    """
    if not text.strip():
        return []
    
    # 按句子分割，保持语义完整性
    sentences = re.split(r'[。！？\n]+', text)
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_tokens = estimate_tokens(sentence)
        
        # 如果当前句子加上当前分片超过最大token数
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            
            # 计算重叠部分
            overlap_text = ""
            overlap_tokens = 0
            words = current_chunk.split()
            
            # 从后往前添加词，直到达到重叠token数
            for word in reversed(words):
                word_tokens = estimate_tokens(word)
                if overlap_tokens + word_tokens <= overlap:
                    overlap_text = word + " " + overlap_text
                    overlap_tokens += word_tokens
                else:
                    break
            
            current_chunk = overlap_text + sentence
            current_tokens = overlap_tokens + sentence_tokens
        else:
            current_chunk += sentence + "。"
            current_tokens += sentence_tokens
    
    # 添加最后一个分片
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

class GraphitiCRUD:
    """Graphiti CRUD操作类 - 使用自定义阿里云百联LLM客户端"""
    
    def __init__(self, uri: str, user: str, password: str, api_key: str, 
                 base_url: Optional[str] = None, model_config: str = "fast"):
        """
        初始化Graphiti CRUD类
        
        Args:
            uri: Neo4j数据库URI
            user: Neo4j用户名
            password: Neo4j密码
            api_key: API密钥（OpenAI或阿里云等）
            base_url: API基础URL（用于阿里云等第三方服务）
            model_config: 模型配置名称 ("fast", "balanced", "performance", "longtext")
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.api_key = api_key
        self.base_url = base_url or ALIYUN_API_CONFIG["base_url"]
        self.model_config_name = model_config
        self.model_config = get_model_config(model_config)
        self.graphiti: Optional[Graphiti] = None
        
        # 设置环境变量
        import os
        os.environ['OPENAI_API_KEY'] = api_key
        if self.base_url:
            os.environ['OPENAI_BASE_URL'] = self.base_url
    
    async def connect(self):
        """连接到Neo4j数据库并初始化Graphiti（使用自定义阿里云百联LLM客户端）"""
        try:
            logger.info("正在连接到Neo4j数据库...")
            
            # 导入必要的模块
            from graphiti_core.llm_client import LLMConfig
            from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
            
            # 导入阿里云LLM客户端
            from llm.aliyun_llm_client import AliyunLLMClient
            
            # 创建LLM配置 - 使用阿里云百联模型
            chat_model = self.model_config["chat_model"]
            logger.info(f"使用聊天模型: {chat_model} ({self.model_config['description']})")
            
            llm_config = LLMConfig(
                api_key=self.api_key,
                base_url=self.base_url,
                model=chat_model,  # 阿里云百联聊天模型
                temperature=self.model_config.get("temperature", 0.3),
                max_tokens=self.model_config.get("max_tokens", 4096)
            )
            
            # 创建自定义阿里云百联LLM客户端
            llm_client = AliyunLLMClient(config=llm_config)
            
            # 创建嵌入客户端 - 使用阿里云百联向量模型
            embedding_model = self.model_config["embedding_model"]
            logger.info(f"使用向量模型: {embedding_model}")
            
            embedder_config = OpenAIEmbedderConfig(
                api_key=self.api_key,
                base_url=self.base_url,
                embedding_model=embedding_model  # 阿里云百联向量模型
            )
            embedder = OpenAIEmbedder(config=embedder_config)
            
            # 初始化Graphiti（使用自定义阿里云百联LLM客户端）
            self.graphiti = Graphiti(
                self.uri, 
                self.user, 
                self.password,
                llm_client=llm_client,
                embedder=embedder
                # 不传入cross_encoder参数，使用默认的搜索方式
            )
            
            # 初始化数据库索引和约束
            await self.graphiti.build_indices_and_constraints()
            logger.info("成功连接到Neo4j数据库并初始化索引")
            
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    async def close(self):
        """关闭数据库连接和LLM客户端"""
        if self.graphiti:
            # 关闭Graphiti连接
            await self.graphiti.close()
            logger.info("数据库连接已关闭")
            
            # 关闭LLM客户端
            if hasattr(self.graphiti, 'llm_client'):
                try:
                    llm_client = self.graphiti.llm_client
                    # 检查是否是我们的自定义阿里云客户端
                    if hasattr(llm_client, 'close'):
                        await llm_client.close()
                        logger.info("LLM客户端已关闭")
                except Exception as e:
                    logger.warning(f"关闭LLM客户端时出错: {e}")
    
    # ==================== CREATE 操作 ====================
    
    async def add_episode(self, name: str, content: str, description: str = "用户输入") -> str:
        """
        添加一个episode（创建数据）
        
        Args:
            name: episode名称
            content: episode内容
            description: episode描述
            
        Returns:
            str: episode的UUID
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        # try:
        logger.info(f"正在添加episode: {name}")

        result = await self.graphiti.add_episode(
            name=name,
            episode_body=content,
            source_description=description,
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text,
            update_communities=True, # 临时禁用社区更新以避免bug
        )

        logger.info(f"成功添加episode: {name}")
        return result.episode.uuid
            
        # except Exception as e:
        #     logger.error(f"添加episode失败: {e}")
        #     raise
    
    async def add_json_episode(self, name: str, data: dict, description: str = "JSON数据") -> str:
        """
        添加JSON格式的episode
        
        Args:
            name: episode名称
            data: JSON数据
            description: episode描述
            
        Returns:
            str: episode的UUID
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在添加JSON episode: {name}")
            
            result = await self.graphiti.add_episode(
                name=name,
                episode_body=json.dumps(data, ensure_ascii=False),
                source_description=description,
                reference_time=datetime.now(timezone.utc),
                source=EpisodeType.json
            )
            
            logger.info(f"成功添加JSON episode: {name}")
            return result.episode.uuid
            
        except Exception as e:
            logger.error(f"添加JSON episode失败: {e}")
            raise
    
    async def process_documents_from_directory(self, doc_dir: str = "doc", max_tokens: int = 512, overlap: int = 50) -> List[str]:
        """
        读取指定目录下的所有文档，按token数量分片，然后添加到graphiti中
        
        Args:
            doc_dir: 文档目录路径（相对于当前文件）
            max_tokens: 每个分片的最大token数量
            overlap: 分片之间的重叠token数量
            
        Returns:
            List[str]: 所有添加的episode UUID列表
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
        
        # 构建完整的文档目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_doc_dir = os.path.join(current_dir, doc_dir)
        
        if not os.path.exists(full_doc_dir):
            raise FileNotFoundError(f"文档目录不存在: {full_doc_dir}")
        
        episode_uuids = []
        
        try:
            # 遍历目录下的所有文件
            for filename in os.listdir(full_doc_dir):
                file_path = os.path.join(full_doc_dir, filename)
                print(file_path,'file_pathfile_pathfile_path')
                
                # 只处理文本文件
                if os.path.isfile(file_path) and filename.lower().endswith(('.txt', '.md')):
                    logger.info(f"正在处理文档: {filename}")
                    
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 按token数量分片
                    chunks = split_text_by_tokens(content, max_tokens, overlap)
                    logger.info(f"文档 {filename} 被分割为 {len(chunks)} 个片段")
                    
                    # 为每个分片创建episode
                    for i, chunk in enumerate(chunks):
                        chunk_name = f"{os.path.splitext(filename)[0]}_片段_{i+1:03d}"
                        chunk_description = f"来自文档 {filename} 的第 {i+1} 个片段，共 {len(chunks)} 个片段"
                        
                        try:
                            episode_uuid = await self.add_episode(
                                name=chunk_name,
                                content=chunk,
                                description=chunk_description
                            )
                            episode_uuids.append(episode_uuid)
                            logger.info(f"成功添加片段 {i+1}/{len(chunks)}: {chunk_name}")
                            
                        except Exception as e:
                            logger.error(f"添加片段 {i+1} 失败: {e}")
                            continue
            
            logger.info(f"文档处理完成，共添加了 {len(episode_uuids)} 个episode")
            return episode_uuids
            
        except Exception as e:
            logger.error(f"处理文档目录失败: {e}")
            raise
    
    # ==================== READ 操作 ====================
    
    async def search_edges(self, query: str, num_results: int = 10) -> List:
        """
        搜索边（关系，不使用重排序功能）
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            List: 搜索结果列表
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在搜索边: {query}")
            
            # 使用简单的搜索配置，不使用重排序
            from graphiti_core.search.search_config import SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker
            
            # 创建不使用重排序的搜索配置
            search_config = SearchConfig(
                edge_config=EdgeSearchConfig(
                    search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
                    reranker=EdgeReranker.rrf  # 使用RRF而不是交叉编码器重排序
                ),
                limit=num_results
            )
            # 使用_search方法进行搜索
            results = await self.graphiti._search(
                query=query,
                config=search_config
            )
            
            logger.info(f"边搜索完成，找到 {len(results.edges)} 个结果")
            return results.edges
            
        except Exception as e:
            import traceback
            logger.error(f"边搜索失败: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def search_nodes(self, query: str, num_results: int = 10) -> List:
        """
        搜索节点（不使用重排序功能）
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            List: 搜索结果列表
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在搜索节点: {query}")
            
            # 使用简单的搜索配置，不使用重排序
            from graphiti_core.search.search_config import SearchConfig, NodeSearchConfig, NodeSearchMethod, NodeReranker
            
            # 创建不使用重排序的搜索配置
            search_config = SearchConfig(
                node_config=NodeSearchConfig(
                    search_methods=[NodeSearchMethod.bm25, NodeSearchMethod.cosine_similarity],
                    reranker=NodeReranker.rrf  # 使用RRF而不是交叉编码器重排序
                ),
                limit=num_results
            )
            
            # 使用_search方法进行搜索
            results = await self.graphiti._search(
                query=query,
                config=search_config
            )
            
            logger.info(f"节点搜索完成，找到 {len(results.nodes)} 个节点")
            return results.nodes
            
        except Exception as e:
            logger.error(f"节点搜索失败: {e}")
            raise
    
    async def search_with_center_node(self, query: str, center_node_uuid: str, num_results: int = 10) -> List:
        """
        基于中心节点的搜索（不使用重排序功能）
        
        Args:
            query: 搜索查询
            center_node_uuid: 中心节点UUID
            num_results: 返回结果数量
            
        Returns:
            List: 搜索结果列表
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在基于中心节点 {center_node_uuid} 搜索: {query}")
            
            # 使用简单的搜索配置，不使用重排序
            from graphiti_core.search.search_config import SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker
            
            # 创建不使用重排序的搜索配置
            search_config = SearchConfig(
                edge_config=EdgeSearchConfig(
                    search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
                    reranker=EdgeReranker.node_distance  # 使用节点距离而不是交叉编码器重排序
                ),
                limit=num_results
            )
            
            # 使用_search方法进行搜索
            results = await self.graphiti._search(
                query=query,
                config=search_config,
                center_node_uuid=center_node_uuid
            )
            
            logger.info(f"中心节点搜索完成，找到 {len(results.edges)} 个结果")
            return results.edges
            
        except Exception as e:
            logger.error(f"中心节点搜索失败: {e}")
            raise
    
    # ==================== UPDATE 操作 ====================
    
    async def add_updated_episode(self, name: str, content: str, description: str = "更新数据") -> str:
        """
        通过添加新的episode来"更新"数据
        （Graphiti中数据是不可变的，通过添加新版本实现更新）
        
        Args:
            name: episode名称
            content: 更新后的内容
            description: episode描述
            
        Returns:
            str: 新episode的UUID
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在添加更新episode: {name}")
            
            # 添加新的episode作为"更新"
            result = await self.graphiti.add_episode(
                name=f"{name}_updated",
                episode_body=content,
                source_description=description,
                reference_time=datetime.now(timezone.utc),
                source=EpisodeType.text,
                update_communities=True
            )
            
            logger.info(f"成功添加更新episode: {name}")
            return result.episode.uuid
            
        except Exception as e:
            logger.error(f"添加更新episode失败: {e}")
            raise
    
    # ==================== DELETE 操作 ====================
    
    async def delete_all_data(self):
        """删除所有数据"""
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info("正在删除所有数据...")
            
            await clear_data(self.graphiti.driver)
            
            logger.info("成功删除所有数据")
            
        except Exception as e:
            logger.error(f"删除数据失败: {e}")
            raise
    
    async def delete_group_data(self, group_ids: List[str]):
        """
        删除指定组的数据
        
        Args:
            group_ids: 要删除的组ID列表
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")
            
        try:
            logger.info(f"正在删除组数据: {group_ids}")
            
            await clear_data(self.graphiti.driver, group_ids=group_ids)
            
            logger.info(f"成功删除组数据: {group_ids}")
            
        except Exception as e:
            logger.error(f"删除组数据失败: {e}")
            raise
    
    # ==================== 辅助方法 ====================
    
    def print_search_results(self, results: List, result_type: str = "边"):
        """
        打印搜索结果
        
        Args:
            results: 搜索结果列表
            result_type: 结果类型（"边"或"节点"）
        """
        print(f"\n=== {result_type}搜索结果 ===")
        if not results:
            print("没有找到结果")
            return

        print(f"找到 {len(results)} 个{result_type}结果:")
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            if hasattr(result, 'uuid'):
                print(f"UUID: {result.uuid}")
            if hasattr(result, 'fact'):
                print(f"事实: {result.fact}")
            if hasattr(result, 'name'):
                print(f"名称: {result.name}")
            if hasattr(result, 'summary'):
                summary = result.summary[:100] + '...' if len(result.summary) > 100 else result.summary
                print(f"摘要: {summary}")
            if hasattr(result, 'valid_at') and result.valid_at:
                print(f"有效时间: {result.valid_at}")
            if hasattr(result, 'invalid_at') and result.invalid_at:
                print(f"失效时间: {result.invalid_at}")
            print("-" * 50)

async def main():
    """主函数 - 演示CRUD操作（使用自定义阿里云百联LLM客户端）"""
    
    # 配置参数
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"
    API_KEY = "sk-12924ea745d84ff59c6aea09ffe2a343"  # 请确保这是正确的阿里云API密钥
    
    # 阿里云API配置
    # 请根据您的阿里云API配置修改以下URL
    ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里云通义千问API端点
    
    # 创建CRUD实例（使用自定义阿里云百联LLM客户端和performance配置）
    crud = GraphitiCRUD(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, API_KEY, ALIYUN_BASE_URL, model_config="performance")
    
    # try:
        # 连接数据库
    await crud.connect()

    print("=" * 60)
    print("Graphiti CRUD 功能演示")
    print("=" * 60)

    # ==================== CREATE 操作演示 ====================
    # print("\n1. 创建数据 (CREATE)")
    # print("-" * 40)

    # 添加文本episode
    print('____________________________')
#     episode_uuid1 = await crud.add_episode(
#         name="人物信息2",
#         content="""张三和李四都是腾讯公司的员工，张三是一名高级软件工程师，负责前端开发，
# 李四是一名产品经理，负责用户增长产品。他们都在深圳总部工作，
# 张三擅长React、Vue、TypeScript等前端技术，李四熟悉产品设计、用户研究、数据分析。
# 他们经常一起开会讨论产品功能，张三负责技术实现，李四负责产品需求。
# 王五也是腾讯的员工，是一名数据科学家，和张三、李四在同一个项目组工作。""",
#         description="用户输入的人物信息"
#     )
#     print("+++++++++++++++++")
#     print(f"添加文本episode成功，UUID: {episode_uuid1}")

    # ==================== 文档处理演示 ====================
    # print("\n2. 文档处理 (DOCUMENT PROCESSING)")
    # print("-" * 40)
        
    # 处理doc目录下的文档，按512token分片
    print("正在处理doc目录下的文档...")
    episode_uuids = await crud.process_documents_from_directory(
        doc_dir="doc",
        max_tokens=1024,
        overlap=50
    )
    print(f"文档处理完成，共添加了 {len(episode_uuids)} 个episode",'episodeepisodeepisodeepisode')
    print(f"前5个episode UUID: {episode_uuids[:5] if len(episode_uuids) > 5 else episode_uuids}")

        # # 添加JSON episode
        # person_data = {
        #     "name": "李四",
        #     "age": 30,
        #     "profession": "数据科学家",
        #     "location": "上海",
        #     "skills": ["Python", "R", "SQL", "机器学习"]
        # }
        # episode_uuid2 = await crud.add_json_episode(
        #     name="李四信息",
        #     data=person_data,
        #     description="JSON格式的人物信息"
        # )
        # print(f"添加JSON episode成功，UUID: {episode_uuid2}")
        #
        # # 添加更多数据用于演示
        # await crud.add_episode(
        #     name="公司信息",
        #     content="腾讯是一家互联网公司，总部位于深圳，主要业务包括社交、游戏、云计算等。",
        #     description="公司信息"
        # )
        #
        # await crud.add_episode(
        #     name="技术信息",
        #     content="Python是一种编程语言，广泛应用于数据分析、人工智能、Web开发等领域。",
        #     description="技术信息"
        # )
        
        # ==================== READ 操作演示 ====================
        # print("\n3. 读取数据 (READ)")
        # print("-" * 40)
        #
        # # 搜索边（关系）
    # print("\n2.1 搜索关系:")
    # edge_results = await crud.search_edges("我和帅帅是什么关系", num_results=5)
    # crud.print_search_results(edge_results, "关系")
    #
        # # 搜索节点
        # print("\n2.2 搜索节点:")
        # node_results = await crud.search_nodes("Python", num_results=5)
        # crud.print_search_results(node_results, "节点")
        #
        # # 基于中心节点的搜索
        # if edge_results:
        #     center_uuid = edge_results[0].source_node_uuid
        #     print(f"\n2.3 基于中心节点 {center_uuid} 的搜索:")
        #     center_results = await crud.search_with_center_node(
        #         "工程师", center_uuid, num_results=3
        #     )
        #     crud.print_search_results(center_results, "中心节点关系")
        
        # ==================== UPDATE 操作演示 ====================
        # print("\n3. 更新数据 (UPDATE)")
        # print("-" * 40)
        #
        # # 通过添加新episode来"更新"数据
        # updated_uuid = await crud.add_updated_episode(
        #     name="张三信息更新",
        #     content="张三是一名高级软件工程师，在北京工作，擅长Python、机器学习和深度学习，有5年工作经验。",
        #     description="更新后的人物信息"
        # )
        # print(f"添加更新episode成功，UUID: {updated_uuid}")
        #
        # # 搜索更新后的信息
        # print("\n搜索更新后的信息:")
        # update_results = await crud.search_edges("高级软件工程师", num_results=3)
        # crud.print_search_results(update_results, "更新后关系")
        #
        # # ==================== DELETE 操作演示 ====================
        # print("\n4. 删除数据 (DELETE)")
        # print("-" * 40)
        #
        # # 注意：这里只是演示，实际使用时请谨慎
        # print("注意：删除操作会清空所有数据，这里仅作演示")
        #
        # # 如果要实际删除，取消下面的注释
        # # await crud.delete_all_data()
        # # print("所有数据已删除")
        #
        # print("删除操作演示完成（未实际执行删除）")
        #
        # # ==================== 综合演示 ====================
        # print("\n5. 综合搜索演示")
        # print("-" * 40)
        #
        # # 搜索不同类型的信息
        # search_queries = [
        #     "工程师",
        #     "Python",
        #     "公司",
        #     "机器学习"
        # ]
        
        # for query in search_queries:
        #     print(f"\n搜索: {query}")
        #     results = await crud.search_edges(query, num_results=3)
        #     if results:
        #         print(f"找到 {len(results)} 个相关关系")
        #         for result in results[:2]:  # 只显示前2个
        #             print(f"  - {result.fact}")
        #     else:
        #         print("没有找到相关结果")

        # print("\n" + "=" * 60)
        # print("CRUD演示完成！（使用自定义阿里云百联LLM客户端）")
        # print("=" * 60)
        #
    # except Exception as e:
    #     logger.error(f"演示过程中发生错误: {e}")
    #     print(f"错误: {e}")
    #
    # finally:
    #     # 关闭连接
    #     await crud.close()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
