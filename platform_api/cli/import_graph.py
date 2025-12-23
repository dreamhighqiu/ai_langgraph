import argparse
import json
from pathlib import Path

from sqlalchemy import select

from ..database import SessionLocal, init_db
from ..models import Agent


def load_graph_file(graph_path: Path) -> dict[str, str]:
    with graph_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    return data.get("graphs", {})


def import_agents(graph_path: Path) -> None:
    init_db()
    graphs = load_graph_file(graph_path)

    with SessionLocal() as session:
        for slug, payload in graphs.items():
            module_path, entrypoint = (
                payload.get("path", "").split(":", maxsplit=1) + ["agent"]
            )[:2]
            module_path = module_path.strip("./")
            if module_path.startswith("src/"):
                module_path = module_path[4:]
            if module_path.endswith(".py"):
                module_path = module_path[:-3]
            module_path = module_path.replace("/", ".")
            entrypoint = entrypoint or "agent"

            exists = session.execute(select(Agent).where(Agent.slug == slug)).scalar_one_or_none()
            if exists:
                continue

            agent = Agent(
                slug=slug,
                name=slug,
                description=f"Imported from graph.json entry \"{slug}\"",
                graph_module=module_path,
                graph_entrypoint=entrypoint,
                owner="imported",
            )
            session.add(agent)
        session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 graph.json 中的 agent 配置")
    parser.add_argument(
        "-g",
        "--graph",
        type=Path,
        default=Path("testing-deep-agents-service/graph.json"),
        help="graph.json 文件路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    graph_file = args.graph
    if not graph_file.exists():
        raise FileNotFoundError(f"{graph_file} 不存在")
    import_agents(graph_file)
    print("Agent 配置已成功导入数据库")


if __name__ == "__main__":
    main()
