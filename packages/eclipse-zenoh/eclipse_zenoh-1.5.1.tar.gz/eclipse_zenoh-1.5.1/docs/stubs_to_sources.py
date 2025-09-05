#
# Copyright (c) 2024 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#
"""Transform Python stubs into Python code.

Rename `*.pyi` to `*.py`. Also, because overloaded functions doesn't render nicely,
overloaded functions are rewritten in a non-overloaded form. Handler parameter types
are merged, and return type is unspecialized, while handler delegated methods are
kept without the `Never` overload. `serializer`/`deserializer` are kept untouched,
because it's ok.
Moreover, all function parameters annotations are stringified in order to allow
referencing a type not declared yet (i.e. forward reference)."""

import ast
import inspect
from collections import defaultdict
from pathlib import Path

PACKAGE = (Path(__file__) / "../../zenoh").resolve()
__INIT__ = PACKAGE / "__init__.py"
EXT = PACKAGE / "ext.py"


def _unstable(item):
    warning = ".. warning:: This API has been marked as unstable: it works as advertised, but it may be changed in a future release."
    if item.__doc__:
        item.__doc__ += "\n" + warning
    else:
        item.__doc__ = warning
    return item


class RemoveOverload(ast.NodeTransformer):
    def __init__(self):
        self.current_cls = None
        # only the first overloaded signature is modified, others are removed
        # modified functions are stored here
        self.overloaded_by_class: defaultdict[str | None, set[str]] = defaultdict(set)

    def visit_ClassDef(self, node: ast.ClassDef):
        # register the current class for method name disambiguation
        self.current_cls = node.name
        res = self.generic_visit(node)
        self.current_cls = None
        return res

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "overload":
                if node.name in self.overloaded_by_class[self.current_cls]:
                    # there is no implementation in stub, so one has to be added
                    # for (de)serializer
                    if node.name in ("serializer", "deserializer"):
                        func = ast.parse(
                            f"def {node.name}(arg, /): {ast.unparse(node.body[0])}"
                        )
                        return [node, func]
                    # remove already modified overloaded signature
                    return None
                self.overloaded_by_class[self.current_cls].add(node.name)
                # (de)serializer is kept overloaded
                if node.name in ("serializer", "deserializer"):
                    return node
                # remove overloaded decorator
                node.decorator_list.clear()
                if node.name not in ("recv", "try_recv", "__iter__"):
                    # retrieve the handled type (Scout/Reply/etc.) from the return type
                    assert isinstance(node.returns, ast.Subscript)
                    if isinstance(node.returns.slice, ast.Subscript):
                        # `Subscriber[Handler[Sample]]` case
                        tp = node.returns.slice.slice
                    else:
                        # `Handler[Reply]` case
                        tp = node.returns.slice
                    assert isinstance(tp, ast.Name)
                    # replace `handler` parameter annotation
                    annotation = f"_RustHandler[{tp.id}] | tuple[Callable[[{tp.id}], Any], Any] | Callable[[{tp.id}], Any] | None"
                    for arg in (*node.args.args, *node.args.kwonlyargs):
                        if arg.arg == "handler":
                            arg.annotation = ast.parse(annotation)
                    node.returns = node.returns.value
        # stringify all parameters and return annotation
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            if ann := arg.annotation:
                arg.annotation = ast.Constant(f"{ast.unparse(ann)}")
        if ret := node.returns:
            node.returns = ast.Constant(f"{ast.unparse(ret)}")
        return node


def main():
    fnames = [__INIT__, EXT]
    for fname in fnames:
        # remove *.py
        fname.unlink()
    # rename stubs
    for entry in PACKAGE.glob("*.pyi"):
        entry.rename(PACKAGE / f"{entry.stem}.py")
    for fname in fnames:
        # read stub code
        with open(fname) as f:
            stub: ast.Module = ast.parse(f.read())
            # replace _unstable
            for i, stmt in enumerate(stub.body):
                if isinstance(stmt, ast.FunctionDef) and stmt.name == "_unstable":
                    stub.body[i] = ast.parse(inspect.getsource(_unstable))
            # remove overload
            stub = RemoveOverload().visit(stub)
        # write modified code
        with open(fname, "w") as f:
            f.write(ast.unparse(stub))


if __name__ == "__main__":
    main()
