import argparse
import contextlib
import json
import logging
import math
import os
import re
import sys
from pathlib import Path

from pmcc import __version__, execution as exec_mod, monitor as mon_mod, risk as risk_mod
from pmcc.utils import is_number

logger = logging.getLogger("pmcc.main")
REQUIRED_CONFIGS = [
    "data_sources.json",
    "universe_etf_20.json",
    "risk_policy.json",
    "event_filters.json",
    "rolling_modes.json",
    "technical_analysis.json",
    "system.json",
    "portfolio_allocation.json",
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs(system_cfg: dict):
    logs_file = system_cfg.get("logging", {}).get("file")
    cache_path = system_cfg.get("cache", {}).get("path")
    if logs_file:
        Path(logs_file).parent.mkdir(parents=True, exist_ok=True)
    if cache_path:
        Path(cache_path).mkdir(parents=True, exist_ok=True)


def configure_file_logging(system_cfg: dict, level: int) -> None:
    """If system.json specifies logging.file, attach a FileHandler to root.

    Keeps stdout handler from basicConfig; only adds an extra file handler.
    """
    try:
        file_path = system_cfg.get("logging", {}).get("file")
        if not file_path:
            return
        # Ensure parent dir exists (defensive; main() also calls ensure_dirs)
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        root = logging.getLogger()
        # Avoid duplicate handlers for the same file in rare re-init cases
        for h in root.handlers:
            if isinstance(h, logging.FileHandler):
                try:
                    if getattr(h, "baseFilename", None) == str(Path(file_path).resolve()):
                        return
                except Exception:  # nosec B110
                    pass
        fh = logging.FileHandler(file_path, mode="a", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(fh)
    except Exception:  # nosec B110
        # File logging is best-effort; do not crash main if file handler fails.
        pass


def summarize(cfgs: dict):
    universe = cfgs["universe_etf_20.json"]
    risk = cfgs["risk_policy.json"]
    events = cfgs["event_filters.json"]
    modes = cfgs["rolling_modes.json"]
    ta = cfgs["technical_analysis.json"]
    ds = cfgs["data_sources.json"]
    system = cfgs["system.json"]

    print("=== PMCC 配置加载完成 ===")
    print(f"标的池数量: {len(universe.get('tickers', []))}")
    c = risk.get("cushion", {})
    print(f"Cushion 硬下限: {c.get('hard_floor')}, 目标区间: {c.get('target_range')}")
    print(
        f"事件-宏观默认动作: {events.get('macro', {}).get('default_action')}，"
        f"窗口±{events.get('macro', {}).get('window_days')}天"
    )
    print(f"短腿当前模式: {modes.get('active_mode')} → 配置: {modes.get(modes.get('active_mode', ''), {})}")
    print(f"技术分析-背离周期: {ta.get('divergence', {}).get('timeframes')}")
    print(
        f"数据源（主）: market={ds.get('primary', {}).get('market_data')}, "
        f"options={ds.get('primary', {}).get('options_data')}, "
        f"greeks={ds.get('primary', {}).get('greeks_source')}"
    )
    print(f"系统: 语言={system.get('language')}, CPU上限={system.get('cpu_cap')}, 并发={system.get('concurrency')}")


def validate(cfgs: dict):
    # 极简校验（后续可扩展为详细 schema）
    assert cfgs["universe_etf_20.json"].get("tickers"), "标的池为空"  # nosec B101
    assert cfgs["risk_policy.json"].get("cushion", {}).get("hard_floor") is not None, "缺少 Cushion 硬下限"  # nosec B101
    assert cfgs["rolling_modes.json"].get("active_mode"), "缺少滚动模式设置"  # nosec B101


class SchemaError(Exception):
    pass


def validate_schema(cfgs: dict, schemas_dir: str | None = None):
    """内置最小 Schema 校验（无第三方依赖）。
    聚焦关键字段与类型，用于快速发现配置错误。
    若未来引入 jsonschema，可替换为标准校验。
    """
    # 若提供了 schemas 目录，优先尝试使用 jsonschema 进行严格校验
    if schemas_dir:
        try:
            import jsonschema
        except Exception as _e:  # nosec B110
            # jsonschema 不可用时，退回到内置最小校验
            pass
        else:
            schema_path = Path(schemas_dir)
            if not schema_path.exists() or not schema_path.is_dir():
                raise SchemaError(f"schema: 提供的 schemas 目录不存在或不可用: {schemas_dir}")

            # 针对目录中的每个 *.json schema，匹配同名配置文件进行校验
            for sfile in schema_path.glob("*.json"):
                name = sfile.name  # 例如 system.json
                if name not in cfgs:
                    # 若配置集中没有该文件，跳过（允许部分 schema 覆盖）
                    continue
                try:
                    schema_obj = json.loads(sfile.read_text(encoding="utf-8"))
                except Exception as e:
                    raise SchemaError(f"schema: 读入 {sfile} 失败: {e}") from e
                try:
                    jsonschema.validate(instance=cfgs[name], schema=schema_obj)
                except jsonschema.ValidationError as e:
                    raise SchemaError(f"schema: {name} 校验失败: {e.message}") from e
                except jsonschema.SchemaError as e:
                    raise SchemaError(f"schema: {sfile} 非法 Schema: {e.message}") from e
            # schema 校验通过后，继续执行额外的语义级校验（跨字段/跨文件关系）

    # data_sources.json
    ds = cfgs.get("data_sources.json", {})
    primary = ds.get("primary", {})
    for k in ["market_data", "options_data", "greeks_source"]:
        v = primary.get(k)
        if not isinstance(v, str):
            raise SchemaError(f"schema: data_sources.primary.{k} 应为字符串，实际={type(v).__name__}")

    # universe_etf_20.json
    uni = cfgs.get("universe_etf_20.json", {})
    tickers = uni.get("tickers")
    if not isinstance(tickers, list) or not all(isinstance(t, str) for t in tickers):
        raise SchemaError("schema: universe.tickers 应为字符串列表")
    # 进一步约束：Ticker 需匹配大写与限定字符
    _ticker_pat = re.compile(r"^[A-Z0-9._-]+$")
    for t in tickers:
        if not _ticker_pat.match(t):
            raise SchemaError(f"schema: universe.tickers 出现非法代码: {t}")

    # risk_policy.json
    risk = cfgs.get("risk_policy.json", {})
    cushion = risk.get("cushion", {})
    hf = cushion.get("hard_floor")
    tr = cushion.get("target_range")
    if not is_number(hf):
        raise SchemaError("schema: risk.cushion.hard_floor 应为数值")
    if not (isinstance(tr, list) and len(tr) == 2 and all(is_number(x) for x in tr)):
        raise SchemaError("schema: risk.cushion.target_range 应为长度为2的数值列表")
    # 关系约束：hard_floor <= target_range[0] <= target_range[1]
    if not (hf <= tr[0] <= tr[1]):
        raise SchemaError("schema: risk.cushion 关系约束失败，要求 hard_floor <= target_range[0] <= target_range[1]")

    # event_filters.json
    ev = cfgs.get("event_filters.json", {})
    macro = ev.get("macro", {})
    if not isinstance(macro.get("default_action"), str):
        raise SchemaError("schema: event_filters.macro.default_action 应为字符串")
    # 限定动作集合
    _allowed_actions = {"throttle", "freeze", "allow", "block", "warn"}
    if macro.get("default_action") not in _allowed_actions:
        raise SchemaError("schema: event_filters.macro.default_action 不在允许集合")
    # 窗口天数需为非负整数
    _wd = macro.get("window_days")
    if not isinstance(_wd, int) or _wd < 0:
        raise SchemaError("schema: event_filters.macro.window_days 应为非负整数")

    # rolling_modes.json
    modes = cfgs.get("rolling_modes.json", {})
    if not isinstance(modes.get("active_mode"), str):
        raise SchemaError("schema: rolling_modes.active_mode 应为字符串")

    # system.json
    system = cfgs.get("system.json", {})
    if not is_number(system.get("cpu_cap")):
        raise SchemaError("schema: system.cpu_cap 应为数值")

    # technical_analysis.json
    ta = cfgs.get("technical_analysis.json", {})
    div = ta.get("divergence", {})
    # timeframes 校验
    tfs = div.get("timeframes")
    if not isinstance(tfs, list) or not all(isinstance(x, str) for x in tfs):
        raise SchemaError("schema: technical_analysis.divergence.timeframes 应为字符串数组")
    _allowed_tfs = {"1D", "4H", "1H"}
    for tf in tfs:
        if tf not in _allowed_tfs:
            raise SchemaError(f"schema: technical_analysis.divergence.timeframes 存在非法周期: {tf}")
    if len(set(tfs)) != len(tfs):
        raise SchemaError("schema: technical_analysis.divergence.timeframes 不应包含重复")

    # weights 键集合需与 timeframes 一致，且求和≈1
    weights = div.get("weights", {})
    if not isinstance(weights, dict) or not all(isinstance(k, str) for k in weights):
        raise SchemaError("schema: technical_analysis.divergence.weights 应为以周期为键的对象")
    if set(weights) != set(tfs):
        raise SchemaError("schema: technical_analysis.divergence.weights 的键应与 timeframes 完全一致")
    if not all(is_number(v) and 0 <= v <= 1 for v in weights.values()):
        raise SchemaError("schema: technical_analysis.divergence.weights 的值应在[0,1]")
    s = sum(float(v) for v in weights.values())
    if not math.isclose(s, 1.0, rel_tol=1e-9, abs_tol=1e-6):
        raise SchemaError("schema: technical_analysis.divergence.weights 的权重之和应为1.0")

    # event_window_weight_scale 范围
    ew = div.get("event_window_weight_scale")
    if not is_number(ew) or not (0 <= ew <= 1):
        raise SchemaError("schema: technical_analysis.divergence.event_window_weight_scale 应在[0,1]")

    # MACD 关系 fast < slow
    macd = div.get("macd", {})
    fast = macd.get("fast")
    slow = macd.get("slow")
    if not (isinstance(fast, int) and isinstance(slow, int)):
        raise SchemaError("schema: technical_analysis.divergence.macd.fast/slow 应为整数")
    if not (fast < slow):
        raise SchemaError("schema: technical_analysis.divergence.macd 要求 fast < slow")

    # filters.min_price 非负
    filters = ta.get("filters", {})
    mp = filters.get("min_price")
    if not is_number(mp) or mp < 0:
        raise SchemaError("schema: technical_analysis.filters.min_price 应为非负数")


def _env_bool(var_name: str, default: bool = False) -> bool:
    v = os.environ.get(var_name)
    if v is None:
        return bool(default)
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(var_name: str, default: int) -> int:
    v = os.environ.get(var_name)
    if v is None:
        return int(default)
    try:
        return int(str(v).strip())
    except Exception:
        return int(default)


def _resolve_ibkr_summary(cfg_dir: Path, live_flag: bool) -> dict:
    """Resolve IBKR connection summary from ENV > keys.json (optional) > defaults.

    Returns a dict: {mode, host, port, client_id, use_gateway}
    """
    # defaults
    default_host = "127.0.0.1"
    default_client_id = 1001
    # default port by mode/backend
    DEFAULTS = {
        "tws": {"paper": 7497, "live": 7496},
        "gateway": {"paper": 4002, "live": 4001},
    }

    # Optional keys.json (best-effort)
    keys_host = None
    keys_client_id = None
    keys_use_gateway = None
    keys_ports = {}
    try:
        kpath = cfg_dir / "keys.json"
        if kpath.exists():
            kdata = json.loads(kpath.read_text(encoding="utf-8"))
            ib = kdata.get("ibkr", {}) if isinstance(kdata, dict) else {}
            if isinstance(ib.get("host"), str):
                keys_host = ib.get("host")
            if isinstance(ib.get("client_id"), int):
                keys_client_id = int(ib.get("client_id"))
            if isinstance(ib.get("use_gateway"), bool):
                keys_use_gateway = bool(ib.get("use_gateway"))
            # Optional nested ports
            if isinstance(ib.get("ports"), dict):
                keys_ports = ib["ports"]
    except Exception:  # nosec B110
        pass

    # Resolve live/paper mode
    mode = "live" if live_flag else "paper"

    # use_gateway default: live->True, paper->False; allow keys.json then ENV override
    use_gateway_default = bool(live_flag)
    use_gateway = keys_use_gateway if keys_use_gateway is not None else use_gateway_default
    use_gateway = _env_bool("PMCC_IBKR_USE_GATEWAY", use_gateway)

    host = os.environ.get("PMCC_IBKR_HOST", keys_host or default_host)

    # Client ID: ENV > keys > default
    default_client_from_keys = keys_client_id if isinstance(keys_client_id, int) else default_client_id
    client_id = _env_int("PMCC_IBKR_CLIENT_ID", default_client_from_keys)

    # Ports: choose family by backend, then live/paper
    if use_gateway:
        # Start from defaults by mode
        port = DEFAULTS["gateway"]["live"] if live_flag else DEFAULTS["gateway"]["paper"]
        # keys.json override
        try:
            if isinstance(keys_ports.get("gateway"), dict):
                kp = keys_ports["gateway"].get(mode)
                if isinstance(kp, int):
                    port = int(kp)
        except Exception:  # nosec B110
            pass
        # ENV override last (highest precedence)
        port = (
            _env_int("PMCC_IBKR_GATEWAY_PORT_LIVE", port)
            if live_flag
            else _env_int("PMCC_IBKR_GATEWAY_PORT_PAPER", port)
        )
    else:
        # Start from defaults by mode
        port = DEFAULTS["tws"]["live"] if live_flag else DEFAULTS["tws"]["paper"]
        # keys.json override
        try:
            if isinstance(keys_ports.get("tws"), dict):
                kp = keys_ports["tws"].get(mode)
                if isinstance(kp, int):
                    port = int(kp)
        except Exception:  # nosec B110
            pass
        # ENV override last (highest precedence)
        port = _env_int("PMCC_IBKR_TWS_PORT_LIVE", port) if live_flag else _env_int("PMCC_IBKR_TWS_PORT_PAPER", port)

    return {
        "mode": mode,
        "host": str(host),
        "port": int(port),
        "client_id": int(client_id),
        "use_gateway": bool(use_gateway),
    }


def main():
    parser = argparse.ArgumentParser(description="PMCC 最小可运行入口（仅加载配置并校验）")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="显示版本并退出",
    )
    parser.add_argument("--config-dir", default="./config", help="配置目录路径")
    parser.add_argument("--dry-risk", action="store_true", help="干跑风险检查（不下单）")
    parser.add_argument("--dry-exec", action="store_true", help="干跑执行规划（不下单）")
    parser.add_argument("--dry-monitor", action="store_true", help="干跑监控循环（不下单）")
    parser.add_argument("--dry-run", action="store_true", help="一次性干跑风险/执行/监控（不下单）")
    parser.add_argument("--summary-json", action="store_true", help="输出结构化配置摘要（JSON）")
    parser.add_argument("--redistribute-leftover", action="store_true", help="启用剩余资金重分配")
    parser.add_argument(
        "--min-total-weight",
        type=float,
        default=None,
        help="最小总权重阈值（如未提供则使用配置文件中的值）",
    )
    parser.add_argument("--summary-json-out", type=str, default=None, help="将结构化配置摘要写入文件路径")
    parser.add_argument(
        "--validate-schema",
        action="store_true",
        help="使用内置最小 Schema 或提供 schemas 目录进行校验",
    )
    parser.add_argument(
        "--schemas-dir",
        type=str,
        default=None,
        help="JSON Schema 目录（可选，提供时启用 jsonschema 校验）",
    )
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="在摘要中附带预检与审批结果（干跑，非交易）",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="日志级别",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="启用实盘模式（仍为dry-run，仅影响配置与摘要）",
    )
    args = parser.parse_args()

    # 聚合干跑选项：若指定 --dry-run，则等价开启三项干跑
    if getattr(args, "dry_run", False):
        args.dry_risk = True
        args.dry_exec = True
        args.dry_monitor = True

    # 解析配置目录优先级：CLI > ENV > 默认
    cli_explicit = any(a == "--config-dir" or a.startswith("--config-dir=") for a in sys.argv[1:])
    env_cfg = os.environ.get("PMCC_CONFIG_DIR")
    cfg_dir_str = args.config_dir if cli_explicit else (env_cfg or args.config_dir)
    # args.config_dir 在未显式传入时等于默认值
    # 若未显式传入且存在环境变量，则采用环境变量
    # 否则采用 CLI/默认值
    cfg_dir = Path(cfg_dir_str).resolve()
    if not cfg_dir.exists():
        print(f"配置目录不存在: {cfg_dir}")
        sys.exit(2)

    # 配置日志
    try:
        level = getattr(logging, args.log_level.upper(), logging.INFO)
    except Exception:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stdout)

    cfgs = {}
    try:
        for name in REQUIRED_CONFIGS:
            p = cfg_dir / name
            if not p.exists():
                print(f"缺少配置文件: {p}")
                sys.exit(2)
            cfgs[name] = load_json(p)

        # CLI 参数对 portfolio_allocation.json 的覆盖（仅在显式提供时生效）
        pa = cfgs.get("portfolio_allocation.json", {})
        if args.redistribute_leftover:
            pa["redistribute_leftover"] = True
        if args.min_total_weight is not None:
            pa["min_total_weight"] = float(args.min_total_weight)
        cfgs["portfolio_allocation.json"] = pa

        ensure_dirs(cfgs["system.json"])
        # Attach file logger if configured in system.json
        configure_file_logging(cfgs["system.json"], level)
        validate(cfgs)
        if args.validate_schema:
            _schemas_dir = args.schemas_dir
            if not _schemas_dir:
                _default = Path("schemas")
                if _default.is_dir():
                    _schemas_dir = str(_default)
            validate_schema(cfgs, _schemas_dir)
        summarize(cfgs)
        # 可选：干跑流程（仅打印，不触发交易）
        if args.dry_risk:
            risk_mod.dry_run(cfgs)
        if args.dry_exec:
            exec_mod.dry_run(cfgs)
        if args.dry_monitor:
            mon_mod.dry_run(cfgs)
        # 可选：输出结构化 JSON 摘要（最后输出，便于测试/对接）
        if args.summary_json or args.summary_json_out:
            # ENV/CLI gating for live mode
            live_flag = bool(args.live) or _env_bool("PMCC_LIVE", False)
            ibkr_summary = _resolve_ibkr_summary(cfg_dir, live_flag)
            universe = cfgs["universe_etf_20.json"]
            risk = cfgs["risk_policy.json"]
            events = cfgs["event_filters.json"]
            modes = cfgs["rolling_modes.json"]
            ds = cfgs["data_sources.json"]
            system = cfgs["system.json"]
            portfolio = cfgs["portfolio_allocation.json"]

            c = risk.get("cushion", {})
            # Build IBKR extended summary (config-derived + runtime metrics)
            ibkr_full = dict(ibkr_summary)
            from pmcc import metrics as __metrics

            counters = __metrics.get_counters()
            # derive default ext from config + metrics
            ext_obj = {"throttle": ds.get("throttle", {}), "health": "ok", "counters": counters}
            # env injection (optional, non-breaking)
            # PMCC_IBKR_COUNTERS='{"success":1,"error":0}', PMCC_IBKR_HEALTH='blocked', PMCC_KILL_SWITCH=1
            with contextlib.suppress(Exception):
                import json as _json

                counters_env = os.environ.get("PMCC_IBKR_COUNTERS")
                if counters_env:
                    cdict = _json.loads(counters_env)
                    if isinstance(cdict, dict):
                        ext_obj["counters"] = cdict
                health_env = os.environ.get("PMCC_IBKR_HEALTH")
                if health_env:
                    ext_obj["health"] = str(health_env)
                if _env_bool("PMCC_KILL_SWITCH", False):
                    ext_obj["health"] = "blocked"
            ibkr_full["ext"] = ext_obj
            summary = {
                "universe": {"count": len(universe.get("tickers", []))},
                "risk": {
                    "cushion": {
                        "hard_floor": c.get("hard_floor"),
                        "target_range": c.get("target_range"),
                    }
                },
                "events": {
                    "macro": {
                        "default_action": events.get("macro", {}).get("default_action"),
                        "window_days": events.get("macro", {}).get("window_days"),
                    }
                },
                "modes": {"active_mode": modes.get("active_mode")},
                "data_sources": {"primary": ds.get("primary", {})},
                "system": {"cpu_cap": system.get("cpu_cap")},
            }
            # IBKR connection summary (dry-run only, informative)
            summary["ibkr"] = ibkr_full
            # 同步输出与文件写入中包含组合关键信息，便于测试与对接
            summary["portfolio"] = {
                "redistribute_leftover": portfolio.get("redistribute_leftover"),
                "min_total_weight": portfolio.get("min_total_weight"),
            }
            # 附加模块摘要（dry-run 语境，结构化字段，附加且非破坏）
            with contextlib.suppress(Exception):
                summary["exec_plan"] = exec_mod.summarize(cfgs)
            with contextlib.suppress(Exception):
                summary["monitor"] = mon_mod.summarize(cfgs)
            # 预检与审批（干跑）
            if getattr(args, "require_approval", False):
                try:
                    from pmcc import approval as appr_mod, pretrade as pt_mod
                    from pmcc.contracts import ApprovalRequest

                    pre = pt_mod.run_pretrade_checks(cfgs)
                    _pd = getattr(pre, "data", None)
                    pre_ok = bool(_pd and getattr(_pd, "ok", False))
                    ep_val = summary.get("exec_plan")
                    if isinstance(ep_val, dict):
                        ep_copy: dict[str, object] = dict(ep_val)
                        ep_copy["pretrade_ok"] = pre_ok
                        summary["exec_plan"] = ep_copy
                    report_path = os.environ.get("PMCC_APPROVAL_LOG")
                    http_url = os.environ.get("PMCC_APPROVAL_HTTP_URL")
                    from typing import Any, cast

                    # Precedence: file service (if report_path), else HTTP (if url), else in-memory
                    if report_path:
                        svc: Any = cast(Any, appr_mod.ApprovalFileService(report_path))
                    elif http_url:
                        try:
                            retries = int(os.environ.get("PMCC_APPROVAL_HTTP_RETRIES", "0").strip())
                        except Exception:
                            retries = 0
                        try:
                            base_delay = float(os.environ.get("PMCC_APPROVAL_HTTP_BASE_DELAY", "0.1").strip())
                        except Exception:
                            base_delay = 0.1
                        svc = cast(Any, appr_mod.HTTPApprovalService(http_url, retries=retries, base_delay=base_delay))
                    else:
                        svc = cast(Any, appr_mod.InMemoryApprovalService())
                    req = ApprovalRequest(plan_id="dry-exec-plan", summary={"pretrade_ok": pre_ok}, requested_by="cli")
                    decision = svc.request(req)
                    _dd = getattr(decision, "data", None)
                    approved = bool(_dd and getattr(_dd, "approved", False))
                    appr_summary = {
                        "required": True,
                        "approved": approved,
                        "approver": "auto",
                    }
                    if report_path:
                        try:
                            appr_summary["report_path"] = str(Path(report_path).resolve())
                        except Exception:
                            appr_summary["report_path"] = str(report_path)
                    summary["approval"] = appr_summary
                except Exception:
                    appr_summary = {"required": True, "approved": False, "approver": "auto", "error": True}
                    report_path = os.environ.get("PMCC_APPROVAL_LOG")
                    if report_path:
                        try:
                            appr_summary["report_path"] = str(Path(report_path).resolve())
                        except Exception:
                            appr_summary["report_path"] = str(report_path)
                    summary["approval"] = appr_summary
            else:
                summary["approval"] = {"required": False}
            # 始终打印到 stdout，便于测试/管道对接
            print(json.dumps(summary, ensure_ascii=False))
            # 如指定输出文件，同时写入文件
            if args.summary_json_out:
                out_path = Path(args.summary_json_out)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8") as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
        print("加载与校验成功（未执行任何交易行为）。")
        sys.exit(0)
    except SchemaError as e:
        logger.error(f"[MAIN] Schema 校验失败: {e}")
        print(f"Schema 校验失败: {e}")
        sys.exit(4)
    except AssertionError as e:
        logger.error(f"[MAIN] 配置校验失败: {e}")
        print(f"配置校验失败: {e}")
        sys.exit(3)
    except Exception as e:
        logger.error(f"[MAIN] 运行出错: {e}")
        print(f"运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
