import ast
import posixpath
import re
from dataclasses import dataclass,field

HTTP_METHODS={"get","post","put","delete","patch","head","options"}
JS_EXTS={'.js','.jsx','.ts','.tsx'}

JS_IMPORT=re.compile(
    r"""(?:import\s+(?:[^'"]*?\s+from\s+)?|require\(\s*|import\(\s*)['"]([^'"]+)['"]""")
JS_FUNC = re.compile(
    r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>)")
JS_ROUTE = re.compile(r"""\b(?:app|router)\.(get|post|put|delete|patch)\(\s*['"]([^'"]+)['"]""")

