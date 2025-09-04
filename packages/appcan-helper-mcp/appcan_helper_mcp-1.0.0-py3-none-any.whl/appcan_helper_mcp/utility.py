"""
AppCan 文档查询工具类
提供文档索引、搜索、内容抓取和缓存功能
"""
import os
import json
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse


class AppCanDocsUtility:
    """AppCan 文档查询工具类"""
    
    BASE_URL = "https://newdocx.appcan.cn"
    CACHE_DIR = "cache"
    CACHE_EXPIRY = 24 * 60 * 60  # 1天缓存
    MAX_CONTENT_LENGTH = 50000  # 50KB最大内容长度
    PAGE_SIZE = 15000  # 每页15KB
    MAX_SEARCH_RESULTS = 3  # 最大搜索结果数
    
    # 文档分类索引（已通过Playwright浏览器实际验证）
    DOC_CATEGORIES = {
        "入门篇": {
            "平台概述": "/AppCan",
            "创建APP": "/quickstart/create-app",
            "平台技术术语": "/quickstart/glossary",
            "帮助": "/quickstart/help"
        },
        "指导篇": {
            "平台服务": "/dev-guide/platform-services/app-dev",
            "原生能力开发": "/dev-guide/openSource-native-capability-dev/custom-engine",
            "iOS证书申请流程": "/dev-guide/ios-certi-process",
            "发布AppStore流程": "/dev-guide/ios-dev-appStore",
            "获取签名信息工具使用": "/dev-guide/get-sign-tool",
            "config.xml配置说明": "/dev-guide/config·xml",
            "iOS10配置指南": "/dev-guide/apple_ref-develop/ios10",
            "ATS说明文档": "/dev-guide/ATS",
            "推送技术": "/dev-guide/push-tec-topics",
            "使用Chrome调试应用": "/dev-guide/use-chrome-debug-app"
        },
        "基础篇-引擎": {
            "概述": "/app-engine/summary",
            "uexWindow": "/app-engine/uexWindow",
            "uexWidget": "/app-engine/uexWidget",
            "uexWidgetOne": "/app-engine/uexWidgetOne",
            "腾讯X5内核引擎": "/app-engine/appcan-tencent-x5-core-engine",
            "更新日志": "/app-engine/update"
        },
        "基础篇-插件API": {
            "使用手册": "/plugin-API/manual",
            "ErrorCode": "/plugin-API/·ErrorCode",
            "Constant": "/plugin-API/·Constant",
            # 系统功能插件 (27个) - 经过实际验证
            "uexApplePay": "/plugin-API/system/uexApplePay",
            "uexBackground": "/plugin-API/system/uexBackground",
            "uexBluetoothLE": "/plugin-API/system/uexBluetoothLE",
            "uexCall": "/plugin-API/system/uexCall",
            "uexCamera": "/plugin-API/system/uexCamera",
            "uexClipboard": "/plugin-API/system/uexClipboard",
            "uexContact": "/plugin-API/system/uexContact",
            "uexControl": "/plugin-API/system/uexControl",
            "uexDataBaseMgr": "/plugin-API/system/uexDataBaseMgr",
            "uexDevice": "/plugin-API/system/uexDevice",
            "uexDocumentReader": "/plugin-API/system/uexDocumentReader",
            "uexEmail": "/plugin-API/system/uexEmail",
            "uexFileMgr": "/plugin-API/system/uexFileMgr",
            "uexFingerPrint": "/plugin-API/system/uexFingerPrint",
            "uexJsonXmlTrans": "/plugin-API/system/uexJsonXmlTrans",
            "uexKeyChain": "/plugin-API/system/uexKeyChain",
            "uexLocalNotification": "/plugin-API/system/uexLocalNotification",
            "uexLocation": "/plugin-API/system/uexLocation",
            "uexLog": "/plugin-API/system/uexLog",
            "uexMMS": "/plugin-API/system/uexMMS",
            "uexSensor": "/plugin-API/system/uexSensor",
            "uexSMS": "/plugin-API/system/uexSMS",
            "uexTouchID": "/plugin-API/system/uexTouchID",
            "uexZip": "/plugin-API/system/uexZip",
            "uex3DTouch": "/plugin-API/system/uex3DTouch",
            "uexNFC": "/plugin-API/system/uexNFC",
            "uexInAppPurchase": "/plugin-API/system/uexInAppPurchase",
            # 功能扩展插件 (10个) - 经过实际验证
            "uexAudio": "/plugin-API/extend/uexAudio",
            "uexCreditCardRec": "/plugin-API/extend/uexCreditCardRec",
            "uexGestureUnlock": "/plugin-API/extend/uexGestureUnlock",
            "uexImage": "/plugin-API/extend/uexImage",
            "uexImageBrowser": "/plugin-API/extend/uexImageBrowser",
            "uexPDFReader": "/plugin-API/extend/uexPDFReader",
            "uexScrawl": "/plugin-API/extend/uexScrawl",
            "uexVideo": "/plugin-API/extend/uexVideo",
            "uexWebBrowser": "/plugin-API/extend/uexWebBrowser",
            "uexImageFilter": "/plugin-API/extend/uexImageFilter",
            # 界面布局插件 (30个) - 经过实际验证
            "uexActionSheet": "/plugin-API/UI/uexActionSheet",
            "uexAreaPickerView": "/plugin-API/UI/uexAreaPickerView",
            "uexBrokenLine": "/plugin-API/UI/uexBrokenLine",
            "uexButton": "/plugin-API/UI/uexButton",
            "uexCalendarView": "/plugin-API/UI/uexCalendarView",
            "uexChart": "/plugin-API/UI/uexChart",
            "uexChatKeyboard": "/plugin-API/UI/uexChatKeyboard",
            "uexCoverFlow2": "/plugin-API/UI/uexCoverFlow2",
            "uexEditDialog": "/plugin-API/UI/uexEditDialog",
            "uexHexagonal": "/plugin-API/UI/uexHexagonal",
            "uexIndexBar": "/plugin-API/UI/uexIndexBar",
            "uexInputTextFieldView": "/plugin-API/UI/uexInputTextFieldView",
            "uexListView": "/plugin-API/UI/uexListView",
            "uexLoadingView": "/plugin-API/UI/uexLoadingView",
            "uexNBListView": "/plugin-API/UI/uexNBListView",
            "uexPie": "/plugin-API/UI/uexPie",
            "uexPieChart": "/plugin-API/UI/uexPieChart",
            "uexPopoverMenu": "/plugin-API/UI/uexPopoverMenu",
            "uexScanner": "/plugin-API/UI/uexScanner",
            "uexScrollPicture": "/plugin-API/UI/uexScrollPicture",
            "uexSearchBarView": "/plugin-API/UI/uexSearchBarView",
            "uexSecurityKeyboard": "/plugin-API/UI/uexSecurityKeyboard",
            "uexSegmentControl": "/plugin-API/UI/uexSegmentControl",
            "uexSlidePager": "/plugin-API/UI/uexSlidePager",
            "uexTabBarWithPopMenu": "/plugin-API/UI/uexTabBarWithPopMenu",
            "uexTimeMachine": "/plugin-API/UI/uexTimeMachine",
            "uexWheel": "/plugin-API/UI/uexWheel",
            "uexWheelPickView": "/plugin-API/UI/uexWheelPickView",
            "uexTabIndicatorView": "/plugin-API/UI/uexTabIndicatorView",
            "uexWebView": "/plugin-API/UI/uexWebView",
            # 网络通讯插件 (7个) - 经过实际验证
            "uexDataAnalysis": "/plugin-API/network/uexDataAnalysis",
            "uexDownloaderMgr": "/plugin-API/network/uexDownloaderMgr",
            "uexMQTT": "/plugin-API/network/uexMQTT",
            "uexWebSocket": "/plugin-API/network/uexWebSocket",
            "uexSocketMgr": "/plugin-API/network/uexSocketMgr",
            "uexUploaderMgr": "/plugin-API/network/uexUploaderMgr",
            "uexXmlHttpMgr": "/plugin-API/network/uexXmlHttpMgr",
            # 第三方SDK插件 (25个) - 经过实际验证
            "uexALiBaiChuan": "/plugin-API/SDK/uexALiBaiChuan",
            "uexAliPay": "/plugin-API/SDK/uexAliPay",
            "uexBaiduMap": "/plugin-API/SDK/uexBaiduMap",
            "uexBaiduNavi": "/plugin-API/SDK/uexBaiduNavi",
            "uexCamera360": "/plugin-API/SDK/uexCamera360",
            "uexEasemob": "/plugin-API/SDK/uexEasemob",
            "uexESurfingRtc": "/plugin-API/SDK/uexESurfingRtc",
            "uexGaodeMap": "/plugin-API/SDK/uexGaodeMap",
            "uexGaodeNavi": "/plugin-API/SDK/uexGaodeNavi",
            "uexGetui": "/plugin-API/SDK/uexGetui",
            "uexJPush": "/plugin-API/SDK/uexJPush",
            "uexMobSMS": "/plugin-API/SDK/uexMobSMS",
            "uexNIM": "/plugin-API/SDK/uexNIM",
            "uexQcloudAV": "/plugin-API/SDK/uexQcloudAV",
            "uexTencentLVB": "/plugin-API/SDK/uexTencentLVB",
            "uexQQ": "/plugin-API/SDK/uexQQ",
            "uexQupai": "/plugin-API/SDK/uexQupai",
            "uexRongCloud": "/plugin-API/SDK/uexRongCloud",
            "uexSina": "/plugin-API/SDK/uexSina",
            "uexTent": "/plugin-API/SDK/uexTent",
            "uexUmeng": "/plugin-API/SDK/uexUmeng",
            "uexUnionPay": "/plugin-API/SDK/uexUnionPay",
            "uexUnisound": "/plugin-API/SDK/uexUnisound",
            "uexWeiXin": "/plugin-API/SDK/uexWeiXin",
            "uexXunfei": "/plugin-API/SDK/uexXunfei",
            "uexESurfingRtcLive": "/plugin-API/SDK/uexESurfingRtcLive"
        },
        "工具篇": {
            "IDE概述": "/IDE/summary",
            "安装下载": "/IDE/download",
            "启动": "/IDE/start-up",
            "新建项目": "/IDE/new",
            "同步项目": "/IDE/sync",
            "UI设计器": "/IDE/UI-designer",
            "实时预览": "/IDE/live-preview",
            "插入控件": "/IDE/controls",
            "本地打包": "/IDE/local-compiled",
            "本地模拟调试": "/IDE/emulator",
            "真机同步调试": "/IDE/device-debug",
            "自定义插件管理": "/IDE/custom-plugin-mgr",
            "插件同步": "/IDE/plugin-sync",
            "代码加密": "/IDE/encrypt",
            "多入口开发": "/IDE/multiple-entry-dev",
            "动态库升级": "/IDE/dynamic",
            "Git托管": "/IDE/GIT"
        },
        "基础篇-JS SDK": {
            "概述": "/JSSDK/summary",
            "基础类库": "/JSSDK/Base",
            "本地存储": "/JSSDK/LocStorage",
            "离线缓存": "/JSSDK/icache",
            "窗口模块": "/JSSDK/Window",
            "浮动窗口模块": "/JSSDK/Frame",
            "数据库模块": "/JSSDK/Database",
            "事件模块": "/JSSDK/EventEmitter",
            "网络请求": "/JSSDK/Request",
            "文件模块": "/JSSDK/File",
            "设备模块": "/JSSDK/Device",
            "Button": "/JSSDK/Button",
            "CheckBox": "/JSSDK/CheckBox",
            "Dialog": "/JSSDK/Dialog",
            "Header": "/JSSDK/Header",
            "Input/Textarea": "/JSSDK/InputTextarea",
            "ListView": "/JSSDK/Listview",
            "optionList": "/JSSDK/optionList",
            "Radio": "/JSSDK/Radio",
            "Select": "/JSSDK/Select",
            "Slider": "/JSSDK/Slider",
            "Switch": "/JSSDK/Switch",
            "Tab": "/JSSDK/Tab",
            "TreeView": "/JSSDK/Treeview",
            "widget": "/JSSDK/widget",
            "widgetOne": "/JSSDK/widgetOne"
        },
        "基础篇-UI框架": {
            "弹性盒子模型": "/UI/source",
            "base": "/UI/base",
            "box": "/UI/box",
            "color": "/UI/color"
        },
        "高级篇": {
            "移动用户交互界面开发": "/interface-dev",
            "移动应用数据对接与交互(MVVM)": "/data-docking-interaction",
            "移动应用与WEB": "/mobile-app-WEB",
            "组件化开发": "/modular-develop"
        },
        "案例篇": {
            "海外购": "/cases/shoppingApp/guide",
            "支付插件": "/cases/payApp/UI"
        },
        "常见问题篇": {
            "更多索引": "/FAQs/",
            "IDE常见问题": "/FAQs/IDE-faq",
            "MVVM常见问题": "/FAQs/MVVM-faq",
            "如何查看app上架被拒": "/FAQs/Apps-distribution-faq",
            "企业版常见问题": "/FAQs/SDK_FAQ"
        }
    }
    
    @staticmethod
    def _ensure_cache_dir():
        """确保缓存目录存在"""
        if not os.path.exists(AppCanDocsUtility.CACHE_DIR):
            os.makedirs(AppCanDocsUtility.CACHE_DIR)
    
    @staticmethod
    def _get_cache_key(url: str) -> str:
        """生成缓存键值"""
        return hashlib.md5(url.encode()).hexdigest()
    
    @staticmethod
    def _get_cache_path(cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(AppCanDocsUtility.CACHE_DIR, f"{cache_key}.json")
    
    @staticmethod
    def _is_cache_valid(cache_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return time.time() - cache_data.get('timestamp', 0) < AppCanDocsUtility.CACHE_EXPIRY
        except Exception:
            return False
    
    @staticmethod
    def _save_cache(cache_path: str, content: str, url: str):
        """保存内容到缓存"""
        try:
            cache_data = {
                'url': url,
                'content': content,
                'timestamp': time.time()
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存保存失败: {e}")
    
    @staticmethod
    def _load_cache(cache_path: str) -> Optional[str]:
        """从缓存加载内容"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return cache_data.get('content')
        except Exception:
            return None
    
    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        """提取页面主要内容并转换为Markdown格式"""
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # 查找主要内容区域
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
        
        if not main_content:
            return "未找到主要内容"
        
        # 转换为Markdown格式
        markdown_content = []
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'ul', 'ol', 'li', 'a', 'img']):
            if element.name.startswith('h'):
                level = int(element.name[1])
                markdown_content.append(f"{'#' * level} {element.get_text().strip()}")
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    markdown_content.append(text)
            elif element.name == 'pre':
                code = element.get_text().strip()
                markdown_content.append(f"```\n{code}\n```")
            elif element.name == 'code' and element.parent.name != 'pre':
                markdown_content.append(f"`{element.get_text().strip()}`")
            elif element.name == 'ul':
                for li in element.find_all('li', recursive=False):
                    markdown_content.append(f"- {li.get_text().strip()}")
            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    markdown_content.append(f"{i}. {li.get_text().strip()}")
            elif element.name == 'a' and element.get('href'):
                text = element.get_text().strip()
                href = element.get('href')
                if href.startswith('/'):
                    href = urljoin(AppCanDocsUtility.BASE_URL, href)
                markdown_content.append(f"[{text}]({href})")
            elif element.name == 'img' and element.get('src'):
                alt = element.get('alt', '图片')
                src = element.get('src')
                if src.startswith('/'):
                    src = urljoin(AppCanDocsUtility.BASE_URL, src)
                markdown_content.append(f"![{alt}]({src})")
        
        return '\n\n'.join(markdown_content)
    
    @staticmethod
    def fetch_doc_content(doc_path: str, force_refresh: bool = False) -> str:
        """
        获取文档内容
        
        Args:
            doc_path: 文档路径
            force_refresh: 是否强制刷新缓存
            
        Returns:
            文档内容（Markdown格式）
        """
        try:
            url = urljoin(AppCanDocsUtility.BASE_URL, doc_path)
            AppCanDocsUtility._ensure_cache_dir()
            
            cache_key = AppCanDocsUtility._get_cache_key(url)
            cache_path = AppCanDocsUtility._get_cache_path(cache_key)
            
            # 检查缓存
            if not force_refresh and AppCanDocsUtility._is_cache_valid(cache_path):
                cached_content = AppCanDocsUtility._load_cache(cache_path)
                if cached_content:
                    return cached_content
            
            # 抓取页面内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 忽略SSL证书验证
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content = AppCanDocsUtility._extract_content(soup)
            
            # 保存到缓存
            AppCanDocsUtility._save_cache(cache_path, content, url)
            
            return content
            
        except Exception as e:
            return f"获取文档内容失败: {str(e)}"
    
    @staticmethod
    def get_all_docs() -> Dict[str, Dict[str, str]]:
        """获取所有文档分类和路径"""
        return AppCanDocsUtility.DOC_CATEGORIES.copy()
    
    @staticmethod
    def search_docs(query: str) -> List[Tuple[str, str, str]]:
        """
        搜索文档 - 改进的搜索逻辑
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Tuple[分类, 文档名, 文档路径]]
        """
        results = []
        
        # 遍历所有文档进行智能匹配
        for category, docs in AppCanDocsUtility.DOC_CATEGORIES.items():
            for doc_name, doc_path in docs.items():
                score = AppCanDocsUtility._calculate_match_score(query, doc_name, category, doc_path)
                
                if score > 0:  # 只保留有匹配度的结果
                    results.append((category, doc_name, doc_path, score))
        
        # 按匹配度排序
        results.sort(key=lambda x: x[3], reverse=True)
        
        # 返回前N个结果，不包含分数
        return [(r[0], r[1], r[2]) for r in results[:AppCanDocsUtility.MAX_SEARCH_RESULTS]]
    
    @staticmethod
    def get_total_search_count(query: str) -> int:
        """
        获取搜索结果的总数
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的文档总数
        """
        count = 0
        for category, docs in AppCanDocsUtility.DOC_CATEGORIES.items():
            for doc_name, doc_path in docs.items():
                score = AppCanDocsUtility._calculate_match_score(query, doc_name, category, doc_path)
                if score > 0:
                    count += 1
        return count
    
    @staticmethod
    def _calculate_match_score(query: str, doc_name: str, category: str, doc_path: str) -> int:
        """
        计算匹配分数 - 智能匹配算法
        
        Args:
            query: 搜索关键词
            doc_name: 文档名称
            category: 分类名称
            doc_path: 文档路径
            
        Returns:
            匹配分数（0-1000，分数越高越匹配）
        """
        query_lower = query.lower().strip()
        doc_name_lower = doc_name.lower()
        category_lower = category.lower()
        doc_path_lower = doc_path.lower()
        
        score = 0
        
        # 1. 精确匹配（最高优先级）
        if query_lower == doc_name_lower:
            score += 1000
        elif query_lower in doc_name_lower:
            # 完整包含匹配
            if doc_name_lower.startswith(query_lower):
                score += 800  # 前缀匹配
            elif doc_name_lower.endswith(query_lower):
                score += 700  # 后缀匹配
            else:
                score += 600  # 中间匹配
        
        # 2. 路径匹配（针对插件名等）
        if query_lower in doc_path_lower:
            path_parts = doc_path_lower.split('/')
            for part in path_parts:
                if query_lower == part:
                    score += 900  # 路径段精确匹配
                elif query_lower in part:
                    if part.startswith(query_lower):
                        score += 500
                    else:
                        score += 300
        
        # 3. 分类匹配
        if query_lower in category_lower:
            score += 200
        
        # 4. 模糊匹配（用于容错）
        if score < 300:  # 只有在精确匹配分数较低时才使用模糊匹配
            name_fuzzy = fuzz.partial_ratio(query_lower, doc_name_lower)
            path_fuzzy = fuzz.partial_ratio(query_lower, doc_path_lower)
            
            # 模糊匹配阈值提高，避免过多无关结果
            if name_fuzzy > 70:
                score += name_fuzzy
            if path_fuzzy > 70:
                score += path_fuzzy // 2
        
        # 5. 特殊关键词处理
        if query_lower.startswith('uex') and len(query_lower) > 3:
            # 对于uex开头的插件名，优先匹配精确的插件
            if doc_path_lower.find(query_lower) != -1:
                score += 400
        
        return score
    
    @staticmethod
    def get_search_suggestions(query: str) -> List[str]:
        """
        根据搜索关键词提供智能建议
        
        Args:
            query: 搜索关键词
            
        Returns:
            建议的搜索关键词列表
        """
        suggestions = []
        query_lower = query.lower().strip()
        
        # 常见的搜索模式和建议
        if 'map' in query_lower or '地图' in query_lower:
            suggestions.extend(['uexBaiduMap', 'uexGaodeMap', 'uexLocation'])
        
        if 'camera' in query_lower or '相机' in query_lower or '拍照' in query_lower:
            suggestions.extend(['uexCamera', 'uexImage', 'uexVideo'])
        
        if 'pay' in query_lower or '支付' in query_lower:
            suggestions.extend(['uexApplePay', 'uexALiBaiChuan'])
        
        if 'push' in query_lower or '推送' in query_lower:
            suggestions.extend(['uexJPush', '推送技术'])
        
        if 'wechat' in query_lower or 'weixin' in query_lower or '微信' in query_lower:
            suggestions.extend(['uexWeiXin'])
        
        if 'qr' in query_lower or '二维码' in query_lower or '扫码' in query_lower:
            suggestions.extend(['uexQR', 'uexScanner'])
        
        if 'audio' in query_lower or '音频' in query_lower:
            suggestions.extend(['uexAudio'])
        
        # 移除与原查询相同的建议
        suggestions = [s for s in suggestions if s.lower() != query_lower]
        
        return suggestions[:3]  # 最多返回3个建议
    
    @staticmethod
    def paginate_content(content: str, page: int = 1) -> Tuple[str, bool, int]:
        """
        分页返回内容
        
        Args:
            content: 完整内容
            page: 页码（从1开始）
            
        Returns:
            Tuple[页面内容, 是否有下一页, 总页数]
        """
        if len(content) <= AppCanDocsUtility.MAX_CONTENT_LENGTH:
            return content, False, 1
        
        total_pages = (len(content) + AppCanDocsUtility.PAGE_SIZE - 1) // AppCanDocsUtility.PAGE_SIZE
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        start_idx = (page - 1) * AppCanDocsUtility.PAGE_SIZE
        end_idx = start_idx + AppCanDocsUtility.PAGE_SIZE
        
        page_content = content[start_idx:end_idx]
        has_next = page < total_pages
        
        return page_content, has_next, total_pages
