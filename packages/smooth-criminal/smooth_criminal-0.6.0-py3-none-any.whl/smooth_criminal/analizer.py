import ast
import inspect
import logging

logger = logging.getLogger("SmoothCriminal")

class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and getattr(node.iter.func, 'id', '') == 'range':
            self.findings.append("🔍 Loop over range() detected: consider vectorizing.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ['sum', 'map', 'filter']:
            self.findings.append(f"🔍 Built-in call to '{node.func.id}': might benefit from NumPy or Numba.")
        self.generic_visit(node)

def analyze_ast(func):
    source = inspect.getsource(func)
    tree = ast.parse(source)
    analyzer = ASTAnalyzer()
    analyzer.visit(tree)

    logger.info("📊 AST analysis complete. Suggestions:")
    for finding in analyzer.findings:
        logger.info(f"  {finding}")
    return analyzer.findings
