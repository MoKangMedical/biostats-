"""REST接口 — Biostats API层"""

from typing import Dict, List, Optional


class APIRouter:
    """Biostats REST API路由管理"""

    def __init__(self):
        self._routes: Dict[str, dict] = {}
        self._register_routes()

    def _register_routes(self):
        routes = [
            {"method": "POST", "path": "/api/survival", "handler": "survival_analysis", "desc": "生存分析"},
            {"method": "POST", "path": "/api/trial", "handler": "trial_design", "desc": "临床试验设计"},
            {"method": "POST", "path": "/api/bayesian", "handler": "bayesian_inference", "desc": "贝叶斯推断"},
            {"method": "POST", "path": "/api/power", "handler": "power_analysis", "desc": "功效分析"},
            {"method": "POST", "path": "/api/longitudinal", "handler": "longitudinal_analysis", "desc": "纵向分析"},
            {"method": "POST", "path": "/api/multivariate", "handler": "multivariate_analysis", "desc": "多变量分析"},
            {"method": "POST", "path": "/api/diagnostic", "handler": "diagnostic_test", "desc": "诊断试验评价"},
            {"method": "POST", "path": "/api/meta", "handler": "meta_analysis", "desc": "Meta分析"},
            {"method": "POST", "path": "/api/propensity", "handler": "propensity_score", "desc": "倾向性评分"},
            {"method": "POST", "path": "/api/mixed", "handler": "mixed_model", "desc": "混合效应模型"},
            {"method": "POST", "path": "/api/timeseries", "handler": "time_series", "desc": "时间序列"},
            {"method": "POST", "path": "/api/bootstrap", "handler": "bootstrap", "desc": "Bootstrap方法"},
            {"method": "POST", "path": "/api/nonparametric", "handler": "non_parametric", "desc": "非参数检验"},
            {"method": "POST", "path": "/api/visualization", "handler": "visualization", "desc": "数据可视化"},
            {"method": "GET", "path": "/api/health", "handler": "health_check", "desc": "健康检查"},
        ]
        for r in routes:
            self._routes[r["path"]] = r

    def get_routes(self) -> List[dict]:
        return list(self._routes.values())

    def match_route(self, method: str, path: str) -> Optional[dict]:
        route = self._routes.get(path)
        if route and route["method"] == method:
            return route
        return None

    def process_request(self, method: str, path: str, data: dict = None) -> dict:
        route = self.match_route(method, path)
        if not route:
            return {"status": 404, "error": "Route not found"}
        return {"status": 200, "handler": route["handler"], "data": data or {}}

    def add_route(self, method: str, path: str, handler: str, desc: str = ""):
        self._routes[path] = {"method": method, "path": path, "handler": handler, "desc": desc}

    def health_check(self) -> dict:
        return {"status": "ok", "routes": len(self._routes), "service": "Biostats"}

    def openapi_spec(self) -> dict:
        paths = {}
        for path, route in self._routes.items():
            paths[path] = {route["method"].lower(): {"summary": route["desc"]}}
        return {"openapi": "3.0.0", "info": {"title": "Biostats API", "version": "1.0"}, "paths": paths}

    def list_endpoints(self) -> str:
        lines = []
        for r in self._routes.values():
            lines.append(f"  {r['method']:6s} {r['path']:30s} {r['desc']}")
        return "Biostats Endpoints:\n" + "\n".join(lines)
