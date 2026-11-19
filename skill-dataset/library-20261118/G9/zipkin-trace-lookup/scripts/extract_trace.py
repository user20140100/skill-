#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zipkin Trace 关键信息提取脚本
从 Zipkin API 获取 trace 数据，过滤并提取用于错误分析的关键信息
参考逻辑：查找叶子错误节点，构建错误调用链，提取关键字段
"""

import json
import os
import sys
import urllib.request
import urllib.error
import ssl
from typing import Dict, List, Optional, Any
from datetime import datetime

class TraceExtractor:
    def __init__(self, zipkin_base_url: str = None, page_url: str = None):
        """
        初始化 Trace 提取器
        
        URL 解析优先级：
        1. 命令行参数 --zipkin-url
        2. 环境变量 ZIPKIN_PRO_URL / ZIPKIN_TEST_URL（按环境选取）
        
        环境变量必须配置，否则脚本将报错退出。
        
        Args:
            zipkin_base_url: Zipkin 服务的基础 URL（可选，如果提供则优先使用）
            page_url: 页面 URL，用于判断环境
        """
        if zipkin_base_url is None:
            env = self._determine_environment(page_url)
            if env == "pro":
                zipkin_base_url = os.environ.get("ZIPKIN_PRO_URL")
                if not zipkin_base_url:
                    print("错误: 未设置环境变量 ZIPKIN_PRO_URL，请在 ~/.zshrc 中配置", file=sys.stderr)
                    sys.exit(1)
            else:
                zipkin_base_url = os.environ.get("ZIPKIN_TEST_URL")
                if not zipkin_base_url:
                    print("错误: 未设置环境变量 ZIPKIN_TEST_URL，请在 ~/.zshrc 中配置", file=sys.stderr)
                    sys.exit(1)
        
        self.zipkin_base_url = zipkin_base_url.rstrip('/')
        self.trace_api_path = "/api/v2/trace"
    
    def _determine_environment(self, page_url: str) -> str:
        """根据 pageUrl 判断环境"""
        if not page_url:
            return "pro"
        
        test_keywords = ['dev', 'test', 'sit', 'uat']
        page_url_lower = page_url.lower()
        
        for keyword in test_keywords:
            if keyword in page_url_lower:
                return "test"
        
        return "pro"
    
    def fetch_trace(self, trace_id: str) -> Optional[List[Dict]]:
        """从 Zipkin API 获取 trace 数据"""
        url = f"{self.zipkin_base_url}{self.trace_api_path}/{trace_id}"
        
        try:
            print(f"正在获取 trace 数据: {url}", file=sys.stderr)
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                data = response.read().decode('utf-8')
                trace_data = json.loads(data)
            
            if not isinstance(trace_data, list):
                print(f"警告: 返回的数据格式不是数组: {type(trace_data)}", file=sys.stderr)
                return None
            
            print(f"成功获取 {len(trace_data)} 个 span 节点", file=sys.stderr)
            return trace_data
        except urllib.error.HTTPError as e:
            print(f"HTTP 请求失败: {e.code} - {e.reason}", file=sys.stderr)
            return None
        except urllib.error.URLError as e:
            print(f"URL 请求失败: {e.reason}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"获取 trace 数据时发生错误: {e}", file=sys.stderr)
            return None
    
    def filter_statemachinetaskexecutor(self, nodes: List[Dict]) -> List[Dict]:
        """过滤列表中 name 为 statemachinetaskexecutor 的节点"""
        filtered_nodes = [
            node for node in nodes
            if isinstance(node, dict) and node.get("name") != "statemachinetaskexecutor"
        ]
        return filtered_nodes
    
    def find_error_node_without_children(self, nodes: List[Dict]) -> Optional[Dict]:
        """
        从所有节点中找出一个 tags.error 不为空的节点，优先选择没有子级的节点（叶子节点）
        如果找不到叶子错误节点，则选择子节点中没有错误的最深错误节点
        """
        if not nodes:
            return None
        
        parent_to_children = {}
        for node in nodes:
            if isinstance(node, dict) and "parentId" in node:
                parent_id = node.get("parentId")
                if parent_id:
                    if parent_id not in parent_to_children:
                        parent_to_children[parent_id] = []
                    parent_to_children[parent_id].append(node)
        
        id_to_node = {}
        for node in nodes:
            if isinstance(node, dict) and "id" in node:
                id_to_node[node["id"]] = node
        
        error_nodes = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            
            tags = node.get("tags", {})
            error = tags.get("error") if isinstance(tags, dict) else None
            
            if error is None or (isinstance(error, str) and error.strip() == ""):
                continue
            
            error_nodes.append(node)
        
        if not error_nodes:
            return None
        
        for node in error_nodes:
            node_id = node.get("id")
            if node_id and node_id not in parent_to_children:
                return node
        
        def has_error_in_children(node_id: str) -> bool:
            children = parent_to_children.get(node_id, [])
            for child in children:
                child_tags = child.get("tags", {})
                child_error = child_tags.get("error") if isinstance(child_tags, dict) else None
                if child_error and (not isinstance(child_error, str) or child_error.strip() != ""):
                    return True
                child_id = child.get("id")
                if child_id and has_error_in_children(child_id):
                    return True
            return False
        
        for node in error_nodes:
            node_id = node.get("id")
            if node_id and not has_error_in_children(node_id):
                return node
        
        return error_nodes[0] if error_nodes else None
    
    def get_parent_chain(self, nodes: List[Dict], target_node: Dict) -> List[Dict]:
        """获取目标节点的所有上层节点（通过 parent_id），组成一个数组，最下层放到第一个节点"""
        if not target_node or not isinstance(target_node, dict):
            return []
        
        id_to_node = {}
        for node in nodes:
            if isinstance(node, dict) and "id" in node:
                id_to_node[node["id"]] = node
        
        chain = []
        current_node = target_node
        
        while current_node:
            chain.append(current_node)
            parent_id = current_node.get("parentId")
            if parent_id and parent_id in id_to_node:
                current_node = id_to_node[parent_id]
            else:
                break
        
        return chain
    
    def filter_error_node_chain(self, nodes: List[Dict]) -> List[Dict]:
        """
        过滤节点列表：
        1. 找出 tags.error 不为空且没有子级的节点A
        2. 拿到A所有的上层(parent_id)节点，组成一个数组，最下层放到第一个节点
        """
        node_a = self.find_error_node_without_children(nodes)
        
        if not node_a:
            return []
        
        chain = self.get_parent_chain(nodes, node_a)
        
        return chain
    
    def filter_error_chain_fields(self, error_chain: List[Dict]) -> List[Dict]:
        """
        过滤 error_chain 数组中的每个节点，只保留指定字段：
        parentId, id, name, duration, localEndpoint.serviceName, tags.error, tags.http.method, tags.http.path
        """
        filtered_chain = []
        for node in error_chain:
            if not isinstance(node, dict):
                continue
            
            filtered_node = {}
            
            if "parentId" in node:
                filtered_node["parentId"] = node["parentId"]
            
            if "id" in node:
                filtered_node["id"] = node["id"]
            
            if "name" in node:
                filtered_node["name"] = node["name"]
            
            if "duration" in node:
                filtered_node["duration"] = node["duration"]
            
            if "localEndpoint" in node and isinstance(node["localEndpoint"], dict):
                service_name = node["localEndpoint"].get("serviceName")
                if service_name is not None:
                    filtered_node["localEndpoint"] = {"serviceName": service_name}
            
            if "tags" in node and isinstance(node["tags"], dict):
                filtered_tags = {}
                tags = node["tags"]
                
                if "error" in tags:
                    filtered_tags["error"] = tags["error"]
                
                if "http.method" in tags:
                    filtered_tags["http.method"] = tags["http.method"]
                
                if "http.path" in tags:
                    filtered_tags["http.path"] = tags["http.path"]
                
                if filtered_tags:
                    filtered_node["tags"] = filtered_tags
            
            filtered_chain.append(filtered_node)
        
        return filtered_chain
    
    def _extract_span_summary(self, node: Dict) -> Dict[str, Any]:
        """从单个 span 节点中提取摘要信息"""
        summary = {}
        
        if "id" in node:
            summary["id"] = node["id"]
        
        if "parentId" in node:
            summary["parentId"] = node["parentId"]
        
        if "name" in node:
            summary["name"] = node["name"]
        
        if "duration" in node:
            duration_us = node["duration"]
            summary["durationUs"] = duration_us
            summary["durationMs"] = round(duration_us / 1000, 2)
        
        if "localEndpoint" in node and isinstance(node["localEndpoint"], dict):
            service_name = node["localEndpoint"].get("serviceName")
            if service_name:
                summary["serviceName"] = service_name
        
        tags = node.get("tags", {}) if isinstance(node.get("tags"), dict) else {}
        
        http_method = tags.get("http.method", "")
        http_path = tags.get("http.path", "")
        if http_method or http_path:
            summary["httpMethod"] = http_method
            summary["httpPath"] = http_path
        
        http_status = tags.get("http.status_code", "")
        if http_status:
            summary["httpStatus"] = http_status
        
        error = tags.get("error", "")
        if error and error.strip():
            summary["hasError"] = True
            summary["error"] = error[:200] + "..." if len(error) > 200 else error
        
        return summary
    
    def _deduplicate_spans(self, nodes: List[Dict]) -> List[Dict]:
        """
        对同 ID 的 span 去重（Zipkin 中 client/server 各上报一个同 ID span）。
        优先保留 kind=SERVER 的 span，若无 kind 则保留第一个。
        合并 tags：将所有同 ID span 的 tags 合并到保留的 span 上。
        """
        id_groups = {}
        for node in nodes:
            if not isinstance(node, dict) or "id" not in node:
                continue
            nid = node["id"]
            if nid not in id_groups:
                id_groups[nid] = []
            id_groups[nid].append(node)
        
        deduped = []
        for nid, group in id_groups.items():
            if len(group) == 1:
                deduped.append(group[0])
                continue
            
            chosen = group[0]
            for g in group:
                if g.get("kind") == "SERVER":
                    chosen = g
                    break
            
            merged_tags = {}
            for g in group:
                if isinstance(g.get("tags"), dict):
                    merged_tags.update(g["tags"])
            if merged_tags:
                if not isinstance(chosen.get("tags"), dict):
                    chosen["tags"] = {}
                chosen["tags"].update(merged_tags)
            
            deduped.append(chosen)
        
        return deduped
    
    def build_call_tree(self, nodes: List[Dict]) -> List[Dict]:
        """
        构建完整的调用树（从根节点开始，按层级展示），每个节点包含 children。
        返回根节点列表（通常只有一个根节点）。
        """
        if not nodes:
            return []
        
        deduped_nodes = self._deduplicate_spans(nodes)
        
        id_to_summary = {}
        for node in deduped_nodes:
            if not isinstance(node, dict) or "id" not in node:
                continue
            summary = self._extract_span_summary(node)
            summary["children"] = []
            id_to_summary[node["id"]] = summary
        
        roots = []
        for node in deduped_nodes:
            if not isinstance(node, dict) or "id" not in node:
                continue
            node_id = node["id"]
            parent_id = node.get("parentId")
            if parent_id and parent_id in id_to_summary:
                id_to_summary[parent_id]["children"].append(id_to_summary[node_id])
            else:
                roots.append(id_to_summary[node_id])
        
        def sort_by_duration_desc(items: List[Dict]):
            items.sort(key=lambda x: x.get("durationUs", 0), reverse=True)
            for item in items:
                if item.get("children"):
                    sort_by_duration_desc(item["children"])
        
        sort_by_duration_desc(roots)
        
        return roots
    
    def flatten_call_tree(self, tree_roots: List[Dict], depth: int = 0) -> List[Dict]:
        """
        将调用树扁平化为列表，带 depth 字段表示层级深度，方便输出阅读。
        """
        result = []
        for node in tree_roots:
            flat_node = {k: v for k, v in node.items() if k != "children"}
            flat_node["depth"] = depth
            result.append(flat_node)
            if node.get("children"):
                result.extend(self.flatten_call_tree(node["children"], depth + 1))
        return result
    
    def extract(self, trace_id: str) -> Dict[str, Any]:
        """提取 trace 关键信息"""
        all_spans = self.fetch_trace(trace_id)
        if not all_spans:
            return {
                'traceId': trace_id,
                'error': '无法获取 trace 数据',
                'errorChain': [],
                'summary': {
                    'totalSpans': 0,
                    'hasErrors': False
                }
            }
        
        filtered_spans = self.filter_statemachinetaskexecutor(all_spans)
        
        trace_time = ""
        if all_spans:
            root_span = None
            for span in all_spans:
                if isinstance(span, dict) and "parentId" not in span:
                    root_span = span
                    break
            
            if root_span is None and all_spans:
                root_span = all_spans[0]
            
            if root_span and "timestamp" in root_span:
                timestamp_us = root_span["timestamp"]
                timestamp_s = timestamp_us / 1000000
                dt = datetime.fromtimestamp(timestamp_s)
                trace_time = dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        error_chain = self.filter_error_node_chain(filtered_spans)
        
        leaf_error_service_name = ""
        leaf_error_http_path = ""
        leaf_error_body = ""
        leaf_error_response = ""
        leaf_error_stack_trace = ""
        
        root_error_service_name = ""
        root_error_body = ""
        root_error_response = ""
        root_error_http_path = ""
        
        if error_chain:
            first_node = error_chain[0]
            first_node_local_endpoint = first_node.get("localEndpoint", {}) if isinstance(first_node.get("localEndpoint"), dict) else {}
            first_node_tags = first_node.get("tags", {}) if isinstance(first_node.get("tags"), dict) else {}
            
            leaf_error_service_name = first_node_local_endpoint.get("serviceName", "")
            leaf_error_http_path = first_node_tags.get("http.path", "")
            leaf_error_body = first_node_tags.get("body", "")
            leaf_error_response = first_node_tags.get("response", "")
            leaf_error_stack_trace = first_node_tags.get("stackTrace", "")
            
            last_node = error_chain[-1]
            last_node_local_endpoint = last_node.get("localEndpoint", {}) if isinstance(last_node.get("localEndpoint"), dict) else {}
            last_node_tags = last_node.get("tags", {}) if isinstance(last_node.get("tags"), dict) else {}
            
            root_error_service_name = last_node_local_endpoint.get("serviceName", "")
            root_error_body = last_node_tags.get("body", "")
            root_error_response = last_node_tags.get("response", "")
            root_error_http_path = last_node_tags.get("http.path", "")
        
        filtered_error_chain = self.filter_error_chain_fields(error_chain)
        
        call_tree = self.build_call_tree(filtered_spans)
        call_tree_flat = self.flatten_call_tree(call_tree)
        
        result = {
            'traceId': trace_id,
            'traceTime': trace_time,
            'extractedAt': datetime.now().isoformat(),
            'summary': {
                'totalSpans': len(all_spans),
                'filteredSpans': len(filtered_spans),
                'errorChainLength': len(error_chain),
                'hasErrors': len(error_chain) > 0
            },
            'callTree': call_tree_flat,
            'errorChain': filtered_error_chain,
            'leafErrorServiceName': leaf_error_service_name,
            'leafErrorHttpPath': leaf_error_http_path,
            'leafErrorBody': leaf_error_body,
            'leafErrorResponse': leaf_error_response,
            'leafErrorStackTrace': leaf_error_stack_trace,
            'rootErrorServiceName': root_error_service_name,
            'rootErrorBody': root_error_body,
            'rootErrorResponse': root_error_response,
            'rootErrorHttpPath': root_error_http_path
        }
        
        return result
    
    def format_output(self, result: Dict[str, Any], output_format: str = 'json') -> str:
        """格式化输出结果"""
        if output_format == 'json':
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif output_format == 'text':
            lines = []
            lines.append("=" * 80)
            lines.append(f"Trace ID: {result.get('traceId')}")
            lines.append(f"请求时间: {result.get('traceTime')}")
            lines.append(f"提取时间: {result.get('extractedAt')}")
            lines.append("=" * 80)
            
            summary = result.get('summary', {})
            lines.append(f"\n摘要信息:")
            lines.append(f"  总 Span 数: {summary.get('totalSpans', 0)}")
            lines.append(f"  过滤后 Span 数: {summary.get('filteredSpans', 0)}")
            lines.append(f"  错误链长度: {summary.get('errorChainLength', 0)}")
            lines.append(f"  是否有错误: {'是' if summary.get('hasErrors', False) else '否'}")
            
            error_chain = result.get('errorChain', [])
            if error_chain:
                lines.append(f"\n错误调用链 ({len(error_chain)} 个节点，从叶子到根):")
                lines.append("-" * 80)
                
                for i, node in enumerate(error_chain, 1):
                    lines.append(f"\n[{i}] 节点:")
                    lines.append(f"  ID: {node.get('id', 'N/A')}")
                    lines.append(f"  父节点ID: {node.get('parentId', 'N/A')}")
                    lines.append(f"  操作名称: {node.get('name', 'N/A')}")
                    
                    if node.get('localEndpoint', {}).get('serviceName'):
                        lines.append(f"  服务名: {node.get('localEndpoint', {}).get('serviceName')}")
                    
                    if node.get('duration'):
                        lines.append(f"  耗时: {node.get('duration')} 微秒")
                    
                    tags = node.get('tags', {})
                    if tags.get('error'):
                        error_msg = tags.get('error')
                        error_preview = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg
                        lines.append(f"  错误信息: {error_preview}")
                    
                    if tags.get('http.method') or tags.get('http.path'):
                        lines.append(f"  HTTP: {tags.get('http.method', '')} {tags.get('http.path', '')}")
                    
                    lines.append("-" * 80)
                
                lines.append(f"\n叶子节点（最下层错误节点）信息:")
                lines.append(f"  服务名: {result.get('leafErrorServiceName', 'N/A')}")
                lines.append(f"  HTTP路径: {result.get('leafErrorHttpPath', 'N/A')}")
                if result.get('leafErrorBody'):
                    body_preview = result.get('leafErrorBody', '')[:200] + "..." if len(result.get('leafErrorBody', '')) > 200 else result.get('leafErrorBody', '')
                    lines.append(f"  请求体: {body_preview}")
                if result.get('leafErrorResponse'):
                    response_preview = result.get('leafErrorResponse', '')[:200] + "..." if len(result.get('leafErrorResponse', '')) > 200 else result.get('leafErrorResponse', '')
                    lines.append(f"  响应体: {response_preview}")
                if result.get('leafErrorStackTrace'):
                    stack_preview = result.get('leafErrorStackTrace', '')[:500] + "..." if len(result.get('leafErrorStackTrace', '')) > 500 else result.get('leafErrorStackTrace', '')
                    lines.append(f"  堆栈信息:")
                    for line in stack_preview.split('\n')[:10]:
                        lines.append(f"    {line}")
                
                lines.append(f"\n根节点（最上层节点）信息:")
                lines.append(f"  服务名: {result.get('rootErrorServiceName', 'N/A')}")
                lines.append(f"  HTTP路径: {result.get('rootErrorHttpPath', 'N/A')}")
                if result.get('rootErrorBody'):
                    body_preview = result.get('rootErrorBody', '')[:200] + "..." if len(result.get('rootErrorBody', '')) > 200 else result.get('rootErrorBody', '')
                    lines.append(f"  请求体: {body_preview}")
                if result.get('rootErrorResponse'):
                    response_preview = result.get('rootErrorResponse', '')[:200] + "..." if len(result.get('rootErrorResponse', '')) > 200 else result.get('rootErrorResponse', '')
                    lines.append(f"  响应体: {response_preview}")
            else:
                lines.append("\n未发现错误节点链")
            
            return '\n'.join(lines)
        
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python extract_trace.py <traceId> [--page-url <url>] [--format json|text] [--zipkin-url <url>]")
        print("\n环境变量（必须配置）:")
        print("  ZIPKIN_PRO_URL   生产环境 Zipkin 地址")
        print("  ZIPKIN_TEST_URL  测试环境 Zipkin 地址")
        print("\n示例:")
        print("  python extract_trace.py 712a9c84d6f62e97")
        print("  python extract_trace.py 712a9c84d6f62e97 --page-url <页面URL>")
        print("  python extract_trace.py 712a9c84d6f62e97 --format text")
        print("  python extract_trace.py 712a9c84d6f62e97 --zipkin-url <Zipkin地址>")
        sys.exit(1)
    
    trace_id = sys.argv[1]
    output_format = 'json'
    zipkin_url = None
    page_url = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--format' and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--zipkin-url' and i + 1 < len(sys.argv):
            zipkin_url = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--page-url' and i + 1 < len(sys.argv):
            page_url = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    extractor = TraceExtractor(zipkin_base_url=zipkin_url, page_url=page_url)
    
    try:
        result = extractor.extract(trace_id)
        
        output = extractor.format_output(result, output_format)
        print(output)
        
        sys.exit(0)
            
    except Exception as e:
        print(f"\n提取过程中发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
