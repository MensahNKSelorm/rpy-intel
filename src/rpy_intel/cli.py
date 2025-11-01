import sys
from pathlib import Path
from .r_parser import parse_r_to_ir
from .emitter_py import emit_python


def main():
    if len(sys.argv) < 2:
        print("Usage: rpy-intel <file.R>")
        sys.exit(1)
    src = Path(sys.argv[1]).read_text()
    ir_nodes = parse_r_to_ir(src)
    py = emit_python(ir_nodes)
    print(py)


if __name__ == "__main__":
    main()
