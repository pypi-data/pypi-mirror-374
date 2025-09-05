import argparse
import sys

def run_node(ip: str, port: int):
    # 这里放你的节点启动逻辑
    print(f"[maze] starting node at {ip}:{port}")
    # TODO: 初始化网络、注册路由、启动事件循环等
    # ...
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maze_start",
        description="Maze node launcher"
    )
    # 你提到了希望支持 `-IP -port`，虽然不太常规，我这里同时支持：
    #   -IP / --ip
    #   -port / -p / --port
    parser.add_argument("-IP", "--ip", default="0.0.0.0",
                        help="IP address to bind (default: 0.0.0.0)")
    parser.add_argument("-port", "-p", "--port", type=int, default=8080,
                        help="Port to bind (default: 8080)")
    return parser

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_node(args.ip, args.port)

if __name__ == "__main__":
    sys.exit(main())
