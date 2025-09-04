import asyncio
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastmcp import FastMCP, Client
from appcan_helper_mcp.utility import AppCanDocsUtility

# 创建 MCP 服务器实例，复制服务器中的配置
mcp = FastMCP("AppCan Helper MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """向用户问候的工具"""
    return f"Hello, {name}! 欢迎使用 AppCan Helper MCP 服务器"

@mcp.tool
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool
def search_appcan_docs(query: str, category: str = "all") -> str:
    """
    搜索 AppCan 文档内容 - 改进的智能搜索
    
    Args:
        query: 搜索关键词，支持中文和英文
        category: 文档分类（可选，默认搜索所有分类）
        
    Returns:
        搜索结果和匹配的文档信息
    """
    try:
        if not query.strip():
            return "请提供搜索关键词"
        
        # 搜索文档
        search_results = AppCanDocsUtility.search_docs(query)
        
        if not search_results:
            # 获取智能建议
            suggestions = AppCanDocsUtility.get_search_suggestions(query)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f"\n4. 尝试相关关键词：{', '.join(suggestions)}"
            
            return f"🔍 未找到与 '{query}' 相关的文档。\n\n💡 **建议**：\n"\
                   f"1. 尝试使用更具体或更简单的关键词\n"\
                   f"2. 使用 `get_appcan_doc_categories` 查看所有可用的文档分类\n"\
                   f"3. 检查拼写是否正确（如：uexBaiduMap 而不是 uexBaidumap）{suggestion_text}"
        
        # 检查是否有更多结果
        total_matches = AppCanDocsUtility.get_total_search_count(query)
        
        result_text = f"🔍 **搜索关键词**: {query}\n\n"
        
        if total_matches > AppCanDocsUtility.MAX_SEARCH_RESULTS:
            result_text += f"📋 找到 **{total_matches}** 个匹配结果，显示前 {AppCanDocsUtility.MAX_SEARCH_RESULTS} 个最相关的：\n\n"
        else:
            result_text += f"📋 找到 **{len(search_results)}** 个匹配结果：\n\n"
        
        for i, (cat, doc_name, doc_path) in enumerate(search_results, 1):
            result_text += f"{i}. **{doc_name}** （分类：{cat}）\n"
            result_text += f"   🔗 文档路径：`{doc_path}`\n\n"
        
        # 添加智能建议
        if total_matches > AppCanDocsUtility.MAX_SEARCH_RESULTS:
            result_text += f"💡 **更多结果建议**：\n"
            result_text += f"- 共有 {total_matches} 个匹配项，如需查看其他结果：\n"
            result_text += f"  1. 使用更精确的关键词缩小范围\n"
            result_text += f"  2. 使用 `get_appcan_doc_categories` 查看完整目录结构\n"
            result_text += f"  3. 根据目录结构直接获取目标文档\n\n"
        
        result_text += f"🔍 **下一步**：使用 `get_appcan_doc_content` 工具查看具体文档内容"
        
        return result_text
        
    except Exception as e:
        return f"搜索过程中出错: {str(e)}"

@mcp.tool
def get_appcan_doc_categories() -> str:
    """
    获取 AppCan 文档分类列表 - 完整目录索引
    
    Returns:
        所有文档分类和子文档的详细列表
    """
    try:
        categories = AppCanDocsUtility.get_all_docs()
        
        result_text = "📚 **AppCan 文档中心完整目录**\n\n"
        result_text += "📝 *提示：可以直接使用下方的文档路径查看具体内容*\n\n"
        
        total_docs = 0
        for category, docs in categories.items():
            result_text += f"## 📁 {category}\n"
            
            for doc_name, doc_path in docs.items():
                total_docs += 1
                result_text += f"- **{doc_name}**\n"
                result_text += f"  🔗 路径：`{doc_path}`\n"
            result_text += "\n"
        
        result_text += f"📋 **总计**: {total_docs} 个文档\n\n"
        result_text += "💡 **使用方法**：\n"
        result_text += "1. 使用 `search_appcan_docs(关键词)` 搜索特定内容\n"
        result_text += "2. 使用 `get_appcan_doc_content(路径)` 直接获取文档内容\n"
        result_text += "3. 常用文档推荐：\n"
        result_text += "   - 🔥 插件API：`/plugin-API/manual`\n"
        result_text += "   - 🔥 引擎功能：`/app-engine/uexWindow`\n"
        result_text += "   - 🔥 JS SDK：`/JSSDK/summary`\n"
        result_text += "   - 🔥 IDE使用：`/IDE/summary`"
        
        return result_text
        
    except Exception as e:
        return f"获取文档分类失败: {str(e)}"

@mcp.tool
def get_appcan_doc_content(doc_path: str, page: int = 1, force_refresh: bool = False) -> str:
    """
    获取指定 AppCan 文档的内容
    
    Args:
        doc_path: 文档路径（如 '/IDE/summary'）
        page: 页码，当内容较长时分页显示（默认第1页）
        force_refresh: 是否强制刷新缓存（默认False）
        
    Returns:
        文档内容（Markdown格式）
    """
    try:
        if not doc_path.strip():
            return "请提供文档路径"
        
        # 确保路径以/开头
        if not doc_path.startswith('/'):
            doc_path = '/' + doc_path
        
        print(f"正在获取文档: {doc_path}")
        if force_refresh:
            print("强制刷新缓存")
        
        # 获取文档内容
        content = AppCanDocsUtility.fetch_doc_content(doc_path, force_refresh)
        
        if content.startswith("获取文档内容失败"):
            return content
        
        # 分页处理
        page_content, has_next, total_pages = AppCanDocsUtility.paginate_content(content, page)
        
        result_text = f"📄 **文档路径**: {doc_path}\n"
        result_text += f"📅 **缓存状态**: {'已刷新' if force_refresh else '使用缓存'}\n\n"
        
        if total_pages > 1:
            result_text += f"📖 **分页信息**: 第 {page} 页 / 共 {total_pages} 页\n\n"
        
        result_text += "---\n\n"
        result_text += page_content
        
        if has_next:
            result_text += f"\n\n---\n\n📄 **继续阅读**: 使用 `get_appcan_doc_content('{doc_path}', {page + 1})` 查看下一页"
        
        return result_text
        
    except Exception as e:
        return f"获取文档内容失败: {str(e)}"

@mcp.tool
def clear_appcan_docs_cache() -> str:
    """
    清空 AppCan 文档缓存
    
    Returns:
        清理结果信息
    """
    try:
        cache_dir = AppCanDocsUtility.CACHE_DIR
        
        if not os.path.exists(cache_dir):
            return "缓存目录不存在，无需清理"
        
        # 统计缓存文件
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        if not cache_files:
            return "缓存目录为空，无需清理"
        
        # 删除缓存文件
        deleted_count = 0
        for file in cache_files:
            try:
                os.remove(os.path.join(cache_dir, file))
                deleted_count += 1
            except Exception as e:
                print(f"删除缓存文件 {file} 失败: {e}")
        
        return f"🗑️ 已清理 {deleted_count} 个缓存文件"
        
    except Exception as e:
        return f"清理缓存失败: {str(e)}"

async def test_server():
    """测试 MCP 服务器的各种功能"""
    print("开始测试 AppCan Helper MCP 服务器...")
    
    try:
        # 通过内存中传输连接
        async with Client(mcp) as client:
            print("✅ 成功连接到服务器")
            
            # 测试问候工具
            print("\n📋 测试问候工具...")
            result1 = await client.call_tool("greet", {"name": "张三"})
            result1_text = result1.content[0].text if hasattr(result1, 'content') and result1.content else str(result1)
            print(f"问候结果: {result1_text}")
            
            # 测试时间工具
            print("\n⏰ 测试时间工具...")
            time_result = await client.call_tool("get_current_time", {})
            time_text = time_result.content[0].text if hasattr(time_result, 'content') and time_result.content else str(time_result)
            print(f"时间结果: {time_text}")
            
            # 测试 AppCan 文档功能
            print("\n📚 测试 AppCan 文档功能...")
            
            # 获取文档分类
            print("\n📊 获取文档分类...")
            categories_result = await client.call_tool("get_appcan_doc_categories", {})
            categories_text = categories_result.content[0].text if hasattr(categories_result, 'content') and categories_result.content else str(categories_result)
            print(f"文档分类: {categories_text[:500]}...")  # 只显示前500字符
            
            # 搜索文档
            print("\n🔍 测试文档搜索...")
            search_tests = [
                "uexGaodeMap",
                "插件开发",
            ]
            
            for query in search_tests:
                search_result = await client.call_tool("search_appcan_docs", {"query": query})
                search_text = search_result.content[0].text if hasattr(search_result, 'content') and search_result.content else str(search_result)
                print(f"\n搜索 '{query}': {search_text}")
            
            # 测试获取具体文档内容
            print("\n📄 测试获取文档内容...")
            try:
                doc_content = await client.call_tool("get_appcan_doc_content", {
                    "doc_path": "/IDE/summary",
                    "page": 1,
                    "force_refresh": False
                })
                doc_text = doc_content.content[0].text if hasattr(doc_content, 'content') and doc_content.content else str(doc_content)
                print(f"文档内容: {doc_text[:800]}...")  # 只显示前800字符
            except Exception as e:
                print(f"获取文档内容时出错: {e}")
            
            # 获取可用工具列表
            print("\n🛠️ 获取可用工具...")
            tools = await client.list_tools()
            print("可用工具:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n✅ 所有测试完成!")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())