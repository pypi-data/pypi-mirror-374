import importlib, logging
from typing import Dict, Callable, Any, List

logger = logging.getLogger(__name__)

def load_connectors(cfg) -> Dict[str, Callable[[], Any]]:
    conns = {}
    connectors_cfg = cfg.get("connectors", {})
    mapping = {
        "superops": ("sc_orchestrator.connectors.superops", "fetch_inventory"),
        "veeam": ("sc_orchestrator.connectors.veeam", "fetch_backup_status"),
        "galactic": ("sc_orchestrator.connectors.galactic", "fetch_vulns"),
    }
    loaded_connectors = []
    for key, (mod_path, func_name) in mapping.items():
        if key in connectors_cfg:
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
            def make_fetch(f, section):
                return lambda: f(connectors_cfg[section])
            conns[key] = make_fetch(func, key)
            loaded_connectors.append(key)
    
    logger.debug(f"Loaded connectors: {loaded_connectors}")
    return conns

def load_agents(cfg, modules_override: List[str] | None) -> Dict[str, Callable[..., bool]]:
    enabled = {k: v for k, v in cfg.get("modules", {}).items() if v.get("enabled")}
    if modules_override:
        enabled = {k: v for k, v in enabled.items() if k in set(modules_override)}
    agents: Dict[str, Callable[..., bool]] = {}
    loaded_agents = []
    for name in enabled.keys():
        mod = importlib.import_module(f"sc_orchestrator.agents.{name}")
        agents[name] = getattr(mod, "run")
        loaded_agents.append(name)
    
    logger.debug(f"Loaded agents: {loaded_agents}")
    return agents
