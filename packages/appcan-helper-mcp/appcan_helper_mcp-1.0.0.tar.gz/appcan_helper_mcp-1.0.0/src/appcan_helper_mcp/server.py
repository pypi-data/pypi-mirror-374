from fastmcp import FastMCP
import json
import os
from datetime import datetime
from .utility import AppCanDocsUtility

mcp = FastMCP("AppCan Helper MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """向用户问候的工具"""
    return f"Hello, {name}! 欢迎使用 AppCan Helper MCP 服务器 v1.0.0"

@mcp.tool
def get_current_time() -> str:
    """获取当前时间"""
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
                   f"2. 推荐使用 `get_appcan_doc_categories` 查看所有可用的文档目录索引\n"\
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
        result_text += "   - 🔥 引擎功能：`/app-engine/summary`\n"
        result_text += "   - 🔥 JS SDK：`/JSSDK/summary`\n"
        result_text += "   - 🔥 Android插件开发：`/dev-guide/openSource-native-capability-dev/android-native`"
        result_text += "   - 🔥 iOS插件开发：`/dev-guide/openSource-native-capability-dev/ios-native`"
        result_text += "   - 🔥 config.xml配置：`/dev-guide/config·xml`"
        
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



@mcp.prompt
def help_prompt() -> str:
    """获取AppCan Helper MCP的帮助信息和完整使用指南"""
    return """
🚀 AppCan Helper MCP 服务器使用指南

## 📝 基础工具
1. **greet(name: str)** - 向指定用户问候，用于测试服务器是否正常
   - 功能: 向指定用户发送问候
   - 参数: name - 用户姓名
   - 示例: greet("张三")

2. **get_current_time()** - 获取当前系统时间
   - 无参数

## 📚 AppCan 文档查询工具（核心功能）

### 🔍 搜索文档
**search_appcan_docs(query: str, category: str = "all")**
- 功能: 在AppCan官方文档中搜索相关内容
- 参数:
  - query: 搜索关键词（支持中文，如"插件开发"、"uexWindow"等）
  - category: 文档分类（可选，默认搜索所有分类）
- 特性: 模糊匹配、智能排序、最多返回3个最相关结果
- 示例: search_appcan_docs("插件开发")

### 📋 查看所有文档的目录，用于精准查找内容，推荐优先使用本工具
**get_appcan_doc_categories()**
- 功能: 获取AppCan文档中心的完整分类目录
- 无参数
- 返回: 所有文档分类及其子文档列表

### 📄 根据文档路径获取文档内容
**get_appcan_doc_content(doc_path: str, page: int = 1, force_refresh: bool = False)**
- 功能: 获取指定文档的详细内容
- 参数:
  - doc_path: 文档路径（如"/IDE/summary"、"/plugin-API/manual"）
  - page: 页码（长文档自动分页，每页约15KB）
  - force_refresh: 是否强制刷新缓存（默认使用1天缓存）
- 返回: Markdown格式的文档内容
- 示例: get_appcan_doc_content("/IDE/summary", 1, false)

### 🗑️ 缓存管理
**clear_appcan_docs_cache()**
- 功能: 清空所有文档缓存
- 无参数
- 用途: 释放磁盘空间或强制更新所有内容

## 💡 最佳使用流程

### 查找AppCan文档信息的推荐步骤：
1. **先搜索**: 使用 search_appcan_docs("关键词") 找到相关文档
2. **若搜索结果不理想，拉取文档目录**: 使用 get_appcan_doc_categories()
3. **根据搜索结果，查看具体文档内容**: 使用返回的文档路径调用 get_appcan_doc_content()
4. **按照需要进行分页**: 如果文档较长，使用page参数查看后续页面
5. **获取最新**: 需要最新内容时设置force_refresh=True

### 常见使用场景：
- 🔍 "我想了解AppCan插件开发" → search_appcan_docs("插件机制开发")
- 📋 "AppCan都有哪些文档？" → get_appcan_doc_categories()
- 📖 "查看IDE使用手册" → get_appcan_doc_content("/IDE/summary")
- 🔄 "获取最新的API文档" → get_appcan_doc_content("/plugin-API/manual", 1, True)

## ⚠️ 注意事项
- 文档内容自动缓存1天，提高访问速度
- 长文档(>50KB)自动分页显示，每页约15KB
- 支持中文搜索和模糊匹配
- 所有内容以Markdown格式返回，便于阅读
    """

def main():
    """
    主入口函数 - 用于命令行调用
    这个函数会在 pyproject.toml 中被指定为入口点
    """
    print("启动 AppCan Helper MCP 服务器...")
    mcp.run()

if __name__ == "__main__":
    main()