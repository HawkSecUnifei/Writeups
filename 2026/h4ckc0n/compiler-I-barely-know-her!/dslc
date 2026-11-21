#!/usr/bin/env python3

import sys

KEYWORDS = {"let", "if", "else", "while", "return", "fn",
            "print", "register", "array", "concat", "len"}
OPS = ["==", "!=", "<=", ">=", "+", "-", "*", "/", "%", "<", ">", "=",
       "(", ")", "{", "}", "[", "]", ",", ";"]

class Tok:
    def __init__(self, kind, val, line): self.kind, self.val, self.line = kind, val, line

class LexError(Exception): pass
class ParseError(Exception): pass
class CompileError(Exception): pass

def lex(src):
    toks, i, line, n = [], 0, 1, len(src)
    while i < n:
        c = src[i]
        if c == "\n": line += 1; i += 1; continue
        if c in " \t\r": i += 1; continue
        if c == "#" or (c == "/" and i + 1 < n and src[i+1] == "/"):
            while i < n and src[i] != "\n": i += 1
            continue
        if c.isdigit():
            j = i
            if c == "0" and i + 1 < n and src[i+1] in "xX":
                j = i + 2
                while j < n and src[j] in "0123456789abcdefABCDEF_": j += 1
                val = int(src[i:j].replace("_", ""), 16)
            else:
                while j < n and (src[j].isdigit() or src[j] == "_"): j += 1
                val = int(src[i:j].replace("_", ""))
            toks.append(Tok("int", val & ((1 << 64) - 1), line)); i = j; continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"): j += 1
            w = src[i:j]
            toks.append(Tok("kw" if w in KEYWORDS else "id", w, line)); i = j; continue
        for op in OPS:
            if src.startswith(op, i):
                toks.append(Tok("op", op, line)); i += len(op); break
        else:
            raise LexError(f"line {line}: unexpected character {c!r}")
    toks.append(Tok("eof", None, line))
    return toks

class Node: pass
def _n(cls, *fields):
    def __init__(self, *a): [setattr(self, f, v) for f, v in zip(fields, a)]
    return type(cls, (Node,), {"__init__": __init__, "__slots__": fields})
Num         = _n("Num", "v")
Var         = _n("Var", "name")
Bin         = _n("Bin", "op", "l", "r")
Neg         = _n("Neg", "e")
Call        = _n("Call", "name", "args")
Builtin     = _n("Builtin", "name", "args")
Index       = _n("Index", "name", "idx")
Let         = _n("Let", "name", "e")
AssignVar   = _n("AssignVar", "name", "e")
AssignIndex = _n("AssignIndex", "name", "idx", "e")
If          = _n("If", "c", "t", "e")
While       = _n("While", "c", "b")
Return      = _n("Return", "e")
Print       = _n("Print", "e")
Register    = _n("Register", "name")
ExprStmt    = _n("ExprStmt", "e")
Fn          = _n("Fn", "name", "params", "body")

class Parser:
    def __init__(self, toks): self.toks, self.p = toks, 0
    def peek(self): return self.toks[self.p]
    def next(self): t = self.toks[self.p]; self.p += 1; return t
    def at(self, k, v=None):
        t = self.peek(); return t.kind == k and (v is None or t.val == v)
    def eat(self, k, v=None):
        t = self.peek()
        if t.kind != k or (v is not None and t.val != v):
            raise ParseError(f"line {t.line}: expected {v or k}, got {t.val!r}")
        return self.next()

    def program(self):
        fns, stmts = [], []
        while not self.at("eof"):
            (fns if self.at("kw", "fn") else stmts).append(
                self.fn() if self.at("kw", "fn") else self.stmt())
        return fns, stmts

    def fn(self):
        self.eat("kw", "fn"); name = self.eat("id").val; self.eat("op", "(")
        params = []
        if not self.at("op", ")"):
            params.append(self.eat("id").val)
            while self.at("op", ","): self.next(); params.append(self.eat("id").val)
        self.eat("op", ")")
        return Fn(name, params, self.block())

    def block(self):
        self.eat("op", "{"); stmts = []
        while not self.at("op", "}"): stmts.append(self.stmt())
        self.eat("op", "}"); return stmts

    def stmt(self):
        t = self.peek()
        if t.kind == "kw":
            if t.val == "let":
                self.next(); name = self.eat("id").val; self.eat("op", "=")
                e = self.expr(); self.eat("op", ";"); return Let(name, e)
            if t.val == "if":
                self.next(); self.eat("op", "("); c = self.expr(); self.eat("op", ")")
                thn = self.block(); els = None
                if self.at("kw", "else"): self.next(); els = self.block()
                return If(c, thn, els)
            if t.val == "while":
                self.next(); self.eat("op", "("); c = self.expr(); self.eat("op", ")")
                return While(c, self.block())
            if t.val == "return":
                self.next(); e = self.expr(); self.eat("op", ";"); return Return(e)
            if t.val == "print":
                self.next(); self.eat("op", "("); e = self.expr()
                self.eat("op", ")"); self.eat("op", ";"); return Print(e)
            if t.val == "register":
                self.next(); self.eat("op", "("); name = self.eat("id").val
                self.eat("op", ")"); self.eat("op", ";"); return Register(name)
        if t.kind == "id":
            save = self.p; name = self.next().val
            if self.at("op", "="):
                self.next(); e = self.expr(); self.eat("op", ";")
                return AssignVar(name, e)
            if self.at("op", "["):
                self.next(); idx = self.expr(); self.eat("op", "]")
                if self.at("op", "="):
                    self.next(); e = self.expr(); self.eat("op", ";")
                    return AssignIndex(name, idx, e)
            self.p = save
        e = self.expr(); self.eat("op", ";"); return ExprStmt(e)

    def expr(self): return self.cmp()
    def cmp(self):
        l = self.add()
        while self.at("op") and self.peek().val in ("==","!=","<","<=",">",">="):
            op = self.next().val; l = Bin(op, l, self.add())
        return l
    def add(self):
        l = self.mul()
        while self.at("op") and self.peek().val in ("+","-"):
            op = self.next().val; l = Bin(op, l, self.mul())
        return l
    def mul(self):
        l = self.unary()
        while self.at("op") and self.peek().val in ("*","/","%"):
            op = self.next().val; l = Bin(op, l, self.unary())
        return l
    def unary(self):
        if self.at("op", "-"): self.next(); return Neg(self.unary())
        return self.primary()
    def primary(self):
        t = self.peek()
        if t.kind == "int": self.next(); return Num(t.val)
        if t.kind == "op" and t.val == "(":
            self.next(); e = self.expr(); self.eat("op", ")"); return e
        if t.kind == "kw" and t.val in ("array", "concat", "len"):
            self.next(); self.eat("op", "("); args = []
            if not self.at("op", ")"):
                args.append(self.expr())
                while self.at("op", ","): self.next(); args.append(self.expr())
            self.eat("op", ")"); return Builtin(t.val, args)
        if t.kind == "id":
            self.next(); name = t.val
            if self.at("op", "("):
                self.next(); args = []
                if not self.at("op", ")"):
                    args.append(self.expr())
                    while self.at("op", ","): self.next(); args.append(self.expr())
                self.eat("op", ")"); return Call(name, args)
            if self.at("op", "["):
                self.next(); idx = self.expr(); self.eat("op", "]")
                return Index(name, idx)
            return Var(name)
        raise ParseError(f"line {t.line}: unexpected token {t.val!r}")

class CodeGen:
    def __init__(self, fns):
        self.funcs = {f.name: f for f in fns}
        self.reset()
    def reset(self):
        self.out, self.header, self.allocas = [], [], {}
        self.tmp = self.lbl = 0
    def t(self): self.tmp += 1; return f"%t{self.tmp}"
    def L(self, b): self.lbl += 1; return f"{b}{self.lbl}"
    def emit(self, s): self.out.append(s)

    def expr(self, e):
        if isinstance(e, Num): return (str(e.v), "int")
        if isinstance(e, Var):
            if e.name not in self.allocas:
                raise CompileError(f"use of undefined variable {e.name!r}")
            reg, ty = self.allocas[e.name]; r = self.t()
            self.emit(f"  {r} = load {'i64' if ty=='int' else 'ptr'}, ptr {reg}")
            return (r, ty)
        if isinstance(e, Neg):
            v, _ = self.expr(e.e); r = self.t()
            self.emit(f"  {r} = sub i64 0, {v}"); return (r, "int")
        if isinstance(e, Bin): return self.binop(e)
        if isinstance(e, Call): return self.call(e)
        if isinstance(e, Index):
            ep = self.elem_addr(*self.ref(e.name), e.idx); r = self.t()
            self.emit(f"  {r} = load i64, ptr {ep}"); return (r, "int")
        if isinstance(e, Builtin): return self.builtin(e)
        raise CompileError("unhandled expression")

    def binop(self, e):
        l, _ = self.expr(e.l); r, _ = self.expr(e.r); res = self.t()
        arith = {"+":"add","-":"sub","*":"mul","/":"sdiv","%":"srem"}
        cmp = {"==":"eq","!=":"ne","<":"slt","<=":"sle",">":"sgt",">=":"sge"}
        if e.op in arith:
            if e.op in ("/", "%"):
                nz = self.t(); ok = self.L("divok"); bad = self.L("divzero")
                self.emit(f"  {nz} = icmp eq i64 {r}, 0")
                self.emit(f"  br i1 {nz}, label %{bad}, label %{ok}")
                self.emit(f"{bad}:"); self.emit("  call void @rt_oob()")
                self.emit("  unreachable"); self.emit(f"{ok}:")
            self.emit(f"  {res} = {arith[e.op]} i64 {l}, {r}"); return (res, "int")
        self.emit(f"  {res} = icmp {cmp[e.op]} i64 {l}, {r}")
        z = self.t(); self.emit(f"  {z} = zext i1 {res} to i64"); return (z, "int")

    def call(self, e):
        if e.name not in self.funcs:
            raise CompileError(f"call to undefined function {e.name!r} "
                               f"(no builtin is callable by this name)")
        fn = self.funcs[e.name]
        if len(e.args) != len(fn.params):
            raise CompileError(f"{e.name}: expected {len(fn.params)} args, "
                               f"got {len(e.args)}")
        argr = ", ".join(f"i64 {self.expr(a)[0]}" for a in e.args)
        r = self.t(); self.emit(f"  {r} = call i64 @dsl_{e.name}({argr})")
        return (r, "int")

    def ref(self, name):
        if name not in self.allocas:
            raise CompileError(f"use of undefined variable {name!r}")
        reg, ty = self.allocas[name]
        if ty != "ref": raise CompileError(f"{name!r} is not an array")
        r = self.t(); self.emit(f"  {r} = load ptr, ptr {reg}"); return (r, "ref")

    def elem_addr(self, baseref, _bt, idxnode):
        idx, _ = self.expr(idxnode)
        ln = self.t(); self.emit(f"  {ln} = load i64, ptr {baseref}")
        ok = self.L("inb"); bad = self.L("oob"); chk = self.t()
        self.emit(f"  {chk} = icmp ult i64 {idx}, {ln}")
        self.emit(f"  br i1 {chk}, label %{ok}, label %{bad}")
        self.emit(f"{bad}:"); self.emit("  call void @rt_oob()")
        self.emit("  unreachable"); self.emit(f"{ok}:")
        data = self.t(); self.emit(f"  {data} = getelementptr i8, ptr {baseref}, i64 8")
        ep = self.t(); self.emit(f"  {ep} = getelementptr i64, ptr {data}, i64 {idx}")
        return ep

    def builtin(self, e):
        if e.name == "array":
            if len(e.args) != 1: raise CompileError("array(n) takes 1 arg")
            n, _ = self.expr(e.args[0]); r = self.t()
            self.emit(f"  {r} = call ptr @rt_array_alloc(i64 {n})"); return (r, "ref")
        if e.name == "len":
            if len(e.args) != 1: raise CompileError("len(a) takes 1 arg")
            a, at = self.expr(e.args[0])
            if at != "ref": raise CompileError("len() needs an array")
            r = self.t(); self.emit(f"  {r} = load i64, ptr {a}"); return (r, "int")
        if e.name == "concat":
            if len(e.args) != 2: raise CompileError("concat(a,b) takes 2 args")
            a, at = self.expr(e.args[0]); b, bt = self.expr(e.args[1])
            if at != "ref" or bt != "ref":
                raise CompileError("concat() needs two arrays")
            return self.concat(a, b)
        raise CompileError(f"unknown builtin {e.name}")

    def concat(self, a, b):
        la = self.t(); self.emit(f"  {la} = load i64, ptr {a}")
        lb = self.t(); self.emit(f"  {lb} = load i64, ptr {b}")
        la16 = self.t(); self.emit(f"  {la16} = trunc i64 {la} to i16")
        lb16 = self.t(); self.emit(f"  {lb16} = trunc i64 {lb} to i16")
        s = self.t(); self.emit(f"  {s} = add i16 {la16}, {lb16}")
        o = self.t(); self.emit(f"  {o} = icmp ult i16 {s}, {la16}")
        ok = self.L("ccok"); bad = self.L("ccof")
        self.emit(f"  br i1 {o}, label %{bad}, label %{ok}")
        self.emit(f"{bad}:"); self.emit("  call void @rt_oob()")
        self.emit("  unreachable"); self.emit(f"{ok}:")
        cap = self.t(); self.emit(f"  {cap} = zext i16 {s} to i64")
        total = self.t(); self.emit(f"  {total} = add i64 {la}, {lb}")
        c = self.t(); self.emit(f"  {c} = call ptr @rt_array_alloc(i64 {cap})")
        self.emit(f"  call void @rt_array_setlen(ptr {c}, i64 {total})")
        self.emit(f"  call void @rt_concat_copy(ptr {c}, ptr {a}, ptr {b}, "
                  f"i64 {cap}, i64 {la})")
        return (c, "ref")

    def stmt(self, s):
        if isinstance(s, Let):
            v, vt = self.expr(s.e); llty = "i64" if vt == "int" else "ptr"
            slot = f"%v_{s.name}_{len(self.allocas)}"
            self.header.append(f"  {slot} = alloca {llty}")
            self.allocas[s.name] = (slot, vt)
            self.emit(f"  store {llty} {v}, ptr {slot}")
        elif isinstance(s, AssignVar):
            if s.name not in self.allocas:
                raise CompileError(f"assignment to undefined variable {s.name!r}")
            slot, ty = self.allocas[s.name]; v, _ = self.expr(s.e)
            self.emit(f"  store {'i64' if ty=='int' else 'ptr'} {v}, ptr {slot}")
        elif isinstance(s, AssignIndex):
            ep = self.elem_addr(*self.ref(s.name), s.idx)
            v, _ = self.expr(s.e); self.emit(f"  store i64 {v}, ptr {ep}")
        elif isinstance(s, If):
            c, _ = self.expr(s.c); cc = self.t()
            self.emit(f"  {cc} = icmp ne i64 {c}, 0")
            tl = self.L("then"); el = self.L("else"); end = self.L("endif")
            self.emit(f"  br i1 {cc}, label %{tl}, label %{el if s.e else end}")
            self.emit(f"{tl}:")
            for st in s.t: self.stmt(st)
            self.emit(f"  br label %{end}")
            if s.e is not None:
                self.emit(f"{el}:")
                for st in s.e: self.stmt(st)
                self.emit(f"  br label %{end}")
            self.emit(f"{end}:")
        elif isinstance(s, While):
            cond = self.L("wcond"); body = self.L("wbody"); end = self.L("wend")
            self.emit(f"  br label %{cond}"); self.emit(f"{cond}:")
            c, _ = self.expr(s.c); cc = self.t()
            self.emit(f"  {cc} = icmp ne i64 {c}, 0")
            self.emit(f"  br i1 {cc}, label %{body}, label %{end}")
            self.emit(f"{body}:")
            for st in s.b: self.stmt(st)
            self.emit(f"  br label %{cond}"); self.emit(f"{end}:")
        elif isinstance(s, Return):
            v, _ = self.expr(s.e); self.emit(f"  ret i64 {v}")
            self.emit(f"{self.L('dead')}:")
        elif isinstance(s, Print):
            v, _ = self.expr(s.e); self.emit(f"  call void @rt_print(i64 {v})")
        elif isinstance(s, Register):
            if s.name not in self.funcs:
                raise CompileError(f"register() needs a defined fn, got {s.name!r}")
            self.emit(f"  call void @rt_register(ptr @dsl_{s.name})")
        elif isinstance(s, ExprStmt):
            self.expr(s.e)
        else:
            raise CompileError(f"unhandled statement {type(s).__name__}")

    def function(self, name, params, body, is_main):
        self.reset()
        decls = ", ".join(f"i64 %arg{i}" for i in range(len(params)))
        self.emit("entry:")
        for i, pn in enumerate(params):
            slot = f"%v_{pn}_p{i}"; self.header.append(f"  {slot} = alloca i64")
            self.allocas[pn] = (slot, "int")
            self.emit(f"  store i64 %arg{i}, ptr {slot}")
        for st in body: self.stmt(st)
        if is_main: self.emit("  call void @rt_finish()")
        self.emit("  ret i64 0")
        fname = "main" if is_main else f"dsl_{name}"
        return "\n".join([f"define i64 @{fname}({decls}) {{", "entry:",
                          *self.header, *self.out[1:], "}"])

RUNTIME_DECLS = """\
; ---- runtime interface (runtime.o, compiled WITHOUT the plugin) ----
declare ptr  @rt_array_alloc(i64)
declare void @rt_array_setlen(ptr, i64)
declare void @rt_concat_copy(ptr, ptr, ptr, i64, i64)
declare void @rt_register(ptr)
declare void @rt_print(i64)
declare void @rt_oob()
declare void @rt_finish()
"""

def compile_src(src):
    fns, stmts = Parser(lex(src)).program()
    cg = CodeGen([Fn(f.name, f.params, f.body) for f in fns])
    pieces = ['target triple = "x86_64-pc-linux-gnu"', RUNTIME_DECLS]
    for f in fns:
        if f.name == "main": raise CompileError("'main' is reserved")
        pieces.append(cg.function(f.name, f.params, f.body, is_main=False))
    pieces.append(cg.function(None, [], stmts, is_main=True))
    return "\n\n".join(pieces) + "\n"

def main(argv):
    inp = out = None; i = 1
    while i < len(argv):
        if argv[i] == "-o": out = argv[i+1]; i += 2
        else: inp = argv[i]; i += 1
    if inp is None:
        sys.stderr.write("usage: dslc INPUT.dsl [-o OUT.ll]\n"); return 2
    with open(inp) as f: src = f.read()
    try:
        ir = compile_src(src)
    except (LexError, ParseError, CompileError) as e:
        sys.stderr.write(f"dslc: error: {e}\n"); return 1
    (open(out, "w").write(ir) if out else sys.stdout.write(ir))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
