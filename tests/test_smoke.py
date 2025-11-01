from rpy_intel.r_parser import parse_r_to_ir
from rpy_intel.emitter_py import emit_python


def test_basic_translation():
    # Sample R code
    code = """\
    library(ggplot2)
    df <- data.frame(a = c(1,2,3), b = c(4,5,6))
    m <- mean(df$a)
    """

    # Step 1: parse R to IR
    ir_nodes = parse_r_to_ir(code)

    # Step 2: emit Python
    py_code = emit_python(ir_nodes)

    # Assertions (expected pieces)
    assert "import matplotlib.pyplot" in py_code
    assert "pandas.DataFrame" in py_code
    assert 'df["a"]' in py_code or "df['a']" in py_code
    assert "statistics.mean" in py_code
