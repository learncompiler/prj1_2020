from enum import Enum
from .lex import TokenKind, Token


class TypeKind(Enum):
    INT = 'INT'
    PTR = 'PTR'
    ARR = 'ARR'


class Type():
    def __init__(self, kind=None, base=None, arr_len=None, pointer_depth=0, arr_dim=0, load=True):
        self.kind = kind
        self.base = base
        # 如果是数组，其长度
        self.arr_len = arr_len
        # 指针重数
        self.pointer_depth = pointer_depth
        # 数组维度
        self.arr_dim = arr_dim
        self.load = load

    def to_cpp(self):
        if self.kind == TypeKind('INT'):
            return 'int'
        if self.kind == TypeKind('PTR'):
            return self.base.to_cpp() + '*'
        print('Type.cpp ERR: unknow TypeKind: %s' % self.kind)
        exit(-1)

    def clone(self):
        base = None
        if self.base != None:
            base = self.base.clone()
        return Type(self.kind, base, self.arr_len, self.pointer_depth, self.arr_dim)

    def __eq__(self, other):
        if other == None:
            return False
        a = self
        b = other
        rst = a.kind == b.kind
        if a.kind == TypeKind('ARR'):
            return rst and a.arr_len == b.arr_len
        while rst and a.kind == TypeKind('PTR'):
            a = a.base
            b = b.base
            rst = a.kind == b.kind
        return rst

    def size(self):
        if self.kind == TypeKind('ARR'):
            return self.arr_len * self.base.size()
        else:
            return 1


class NodeKind(Enum):
    RETURN = 'RETURN'   # return 语句
    YIELD = 'YIELD'
    DECL = 'DECL'       # Local variable declaration
    EXPR = 'EXPR'       # Statements: = <expr > ';'
    NUM = 'NUM'         # 数字字面量
    NOT = 'NOT'         # Unary !
    BITNOT = 'BITNOT'   # Unary ~
    NEG = 'NEG'         # Unary -
    REF = 'REF'         # Unary &
    DEREF = 'DEREF'     # Unary *
    ADD = 'ADD'         # Binary +
    SUB = 'SUB'         # Binary -
    MUL = 'MUL'         # Binary *
    DIV = 'DIV'         # Binary /
    MOD = 'MOD'         # Binary %
    LT = 'LT'           # Binary <
    LTE = 'LTE'         # Binary <=
    EQ = 'EQ'           # Binary ==
    NEQ = 'NEQ'         # Binary !=
    LOGAND = 'LOGAND'   # Binary &&
    LOGOR = 'LOGOR'     # Binary ||
    ASSIGN = 'ASSIGN'   # Binary =
    VAR = 'VAR'         # Local variable
    IF = 'IF'           # If statement
    TERNARY = 'TERNARY'  # Ternary a ? b: c
    BLOCK = 'BLOCK'     # Block statement
    FOR = 'FOR'         # For statement
    DOWHILE = 'DOWHILE'  # Do-while statement
    WHILEDO = 'WHILEDO'  # While-do statement
    BREAK = 'BREAK'     # Break statement
    CONTINUE = 'CONTINUE'  # Continue statement
    FUNC_CALL = 'FUNC_CALL'  # Function call
    TYPE_CAST = 'TYPE_CAST'  # Type cast
    ARR_INDEX = 'ARR_INDEX'  # Array [ expr ]
    PTR_INDEX = 'PTR_INDEX'  # Ptr [ expr ]
    PTR_ADD = 'PTR_ADD'  # ptr + num
    PTR_SUB = 'PTR_SUB'  # ptr - num
    PTR_DIFF = 'PTR_DIFF'  # ptr - ptr
    AWAIT = 'AWAIT'


class Var:
    def __init__(self, name, offset, init, scope_depth, is_arg, is_global, type_):
        self.name = name
        self.offset = offset
        self.init = init
        self.scope_depth = scope_depth  # 变量声明时所在的作用域深度
        self.is_arg = is_arg
        self.is_global = is_global
        self.type_ = type_


class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args


def arg2str(args):
    if len(args) == 0:
        return ''
    else:
        s = ''
        for arg in args:
            s += arg.to_cpp() + ', '
        s = s[:-2]
        return s


class Node:
    def __init__(self, kind=None, expr_l=None, expr_r=None, val=None, var=None, cond=None, then=None, else_=None, body=None, pre=None, post=None, func_call=None, type_=None, arr_index=None):
        self.kind = kind
        self.expr_l = expr_l
        self.expr_r = expr_r
        self.val = val
        self.var = var
        self.cond = cond
        self.then = then
        self.else_ = else_
        self.body = body
        self.pre = pre
        self.post = post
        self.func_call = func_call
        self.type_ = type_
        self.arr_index = arr_index

    def to_cpp(self):
        global hot_func
        if self.kind == NodeKind('RETURN'):
            return '$return (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('YIELD'):
            return '$yield (' + self.expr_r.to_cpp() + ', false)'
        if self.kind == NodeKind('BLOCK'):
            s = '{'
            for item in self.body:
                s += item.to_cpp() + ';\n'
            s += '}'
            return s
        if self.kind == NodeKind('NUM'):
            return str(self.val)
        if self.kind == NodeKind('DECL'):
            hot_func.args.append(self.var)
            s = self.var.name
            if self.var.init != None:
                s += ' = (' + self.var.init.to_cpp() + ')'
            return s
        if self.kind == NodeKind('VAR'):
            return self.var.name
        if self.kind == NodeKind('EXPR'):
            return self.expr_r.to_cpp()
        if self.kind == NodeKind('ASSIGN'):
            if self.expr_r.kind == NodeKind('AWAIT'):
                import time
                now = time.time() * 1000000 % 100000000000000
                await_func = self.expr_r.expr_r
                fu_name = '__%s_fu__%d' % (await_func.func_call.name, now)
                ret_name = '__%s_ret__%d' % (await_func.func_call.name, now)
                gen_name = '__%s_gen__%d' % (await_func.func_call.name, now)
                gen = find_func(await_func.func_call.name)
                init_0 = ''
                if len(gen.origin_args) > 0:
                    init_0 = ('0, ' * len(gen.origin_args))[0: -2]
                hot_func.args.append(
                    Var(gen_name, None, init_0, None, True, None, await_func.func_call.name))
                hot_func.args.append(Var(fu_name, None, '&%s' % gen_name, None,
                                         True, None, 'Future<%s>' % (await_func.type_.to_cpp())))
                hot_func.args.append(
                    Var(ret_name, None, str(0), None, True, None, await_func.type_))
                s = ''

                for i, arg in enumerate(await_func.func_call.args):
                    s += '%s.%s = %s;\n' % (gen_name,
                                            gen.origin_args[i].name, arg.to_cpp())

                s += 'get_executor()->spawn(%s);\n' % fu_name
                s += '$yield(%s, true)\n;' % ret_name
                # s += '%s.poll(%s);\n' % (fu_name, ret_name)
                s += 'while (%s.poll(%s)) {$yield(%s, true);}\n' % (
                    fu_name, ret_name, ret_name)
                return s + '(' + self.expr_l.to_cpp() + ') = ' + ret_name
            else:
                return '(' + self.expr_l.to_cpp() + ') = (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('ADD') or self.kind == NodeKind('PTR_ADD'):
            return '(' + self.expr_l.to_cpp() + ') + (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('FOR'):
            s = 'for(' + self.pre.to_cpp() + ';' + \
                self.cond.to_cpp() + ';' + self.post.to_cpp() + ')'
            s += self.then.to_cpp()
            return s
        if self.kind == NodeKind('LT'):
            return '(' + self.expr_l.to_cpp() + ') < (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('SUB') or self.kind == NodeKind('PTR_SUB') or self.kind == NodeKind('PTR_DIFF'):
            return '(' + self.expr_l.to_cpp() + ') - (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('FUNC_CALL'):
            s = self.func_call.name + '('
            if len(self.func_call.args) > 0:
                s += str(self.func_call.args[0])
            if len(self.func_call.args) > 1:
                for i in range(1, len(self.func_call.args)):
                    s += ',' + str(self.func_call.args[i])
            s += ')'
            return s
        if self.kind == NodeKind('MUL'):
            return '(' + self.expr_l.to_cpp() + ') * (' + self.expr_r.to_cpp() + ')'
        if self.kind == NodeKind('IF'):
            s = 'if (' + self.cond.to_cpp() + ') '
            s += '{' + self.then.to_cpp() + '}'
            if self.else_ != None:
                s += ' else {' + self.else_.to_cpp() + '}'
            return s
        if self.kind == NodeKind('ARR_INDEX') or self.kind == NodeKind('PTR_INDEX'):
            s = self.expr_r.to_cpp()
            for ind in self.arr_index:
                s += '[%s]' % ind.to_cpp()
            return s
        if self.kind == NodeKind('DEREF'):
            return '*' + self.expr_r.to_cpp()
        print('Node.to_cpp ERR: unknown node kind: `%s`' % self.kind)
        exit(-1)

    def __str__(self):
        if self.kind == NodeKind('RETURN'):
            return 'RETURN (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('YIELD'):
            return 'YIELD (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('NUM'):
            return 'NUM ' + str(self.val)
        if self.kind == NodeKind('NEG'):
            return 'NEG (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('NOT'):
            return 'NOT (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('BITNOT'):
            return 'BITNOT (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('ADD') or self.kind == NodeKind('PTR_ADD'):
            return '(' + str(self.expr_l) + ') + (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('SUB') or self.kind == NodeKind('PTR_SUB') or self.kind == NodeKind('PTR_DIFF'):
            return '(' + str(self.expr_l) + ') - (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('MUL'):
            return '(' + str(self.expr_l) + ') * (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('DIV'):
            return '(' + str(self.expr_l) + ') / (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('MOD'):
            return '(' + str(self.expr_l) + ') % (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('LT'):
            return '(' + str(self.expr_l) + ') < (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('LTE'):
            return '(' + str(self.expr_l) + ') <= (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('EQ'):
            return '(' + str(self.expr_l) + ') == (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('NEQ'):
            return '(' + str(self.expr_l) + ') != (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('LOGAND'):
            return '(' + str(self.expr_l) + ') && (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('LOGOR'):
            return '(' + str(self.expr_l) + ') || (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('DECL'):
            s = 'DECL (' + str(self.var.type_.kind) + \
                ' ' + str(self.var.name) + ')'
            if self.var.init != None:
                s += ' = (' + str(self.var.init) + ')'
            return s
        if self.kind == NodeKind('ASSIGN'):
            return '(' + str(self.expr_l) + ') = (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('VAR'):
            return '(VAR ' + str(self.var.type_.kind) + ')' + str(self.var.name)
        if self.kind == NodeKind('EXPR'):
            return 'EXPR (' + str(self.expr_r) + ')'
        if self.kind == NodeKind('IF'):
            s = 'IF (' + str(self.cond) + ') '
            s += '{' + str(self.then) + '}'
            if self.else_ != None:
                s += ' ELSE {' + str(self.else_) + '}'
            return s
        if self.kind == NodeKind('BLOCK'):
            s = 'BLOCK{'
            for item in self.body:
                s += str(item)
            s += '}'
            return s
        if self.kind == NodeKind('FOR'):
            s = 'FOR(' + str(self.pre) + ';' + \
                str(self.cond) + ';' + str(self.post) + ')'
            s += '{' + str(self.then) + '}'
            return s
        if self.kind == NodeKind('DOWHILE'):
            return 'DO{' + str(self.then) + '}' + 'WHILE(' + str(self.cond) + ')'
        if self.kind == NodeKind('WHILEDO'):
            return 'WHILE(' + str(self.cond) + '){' + str(self.then) + '}'
        if self.kind == NodeKind('BREAK'):
            return 'BREAK'
        if self.kind == NodeKind('CONTINUE'):
            return 'CONTINUE'
        if self.kind == NodeKind('FUNC_CALL'):
            s = 'func_call ' + self.func_call.name + '('
            if len(self.func_call.args) > 0:
                s += str(self.func_call.args[0])
            if len(self.func_call.args) > 1:
                for i in range(1, len(self.func_call.args)):
                    s += ',' + str(self.func_call.args[i])
            s += ')'
            return s
        if self.kind == NodeKind('TYPE_CAST'):
            return '(TYPE_CAST ' + str(self.type_.kind) + ')' + str(self.expr_r)
        if self.kind == NodeKind('REF'):
            return '&' + str(self.expr_r)
        if self.kind == NodeKind('DEREF'):
            return '*' + str(self.expr_r)
        if self.kind == NodeKind('ARR_INDEX') or self.kind == NodeKind('PTR_INDEX'):
            s = '(' + str(self.expr_r) + ' ' + str(self.kind) + ')'
            for ind in self.arr_index:
                s += '[%s]' % str(ind)
            return s
        print('PARSE ERR: unknown node kind: `%s`' % self.kind)
        exit(-1)


class Function:
    def __init__(self, name, stmts, max_stack_size, args, is_complete, ret_type, is_gen):
        self.name = name
        self.stmts = stmts
        self.max_stack_size = max_stack_size
        self.args = args
        self.is_complete = is_complete
        self.ret_type = ret_type
        self.is_gen = is_gen
        self.origin_args = list(args)

    def to_cpp(self):
        if not self.is_gen:
            print('todo: Funtion.to_cpp()')
            print('todo: $return')
            exit(-1)
        global hot_func
        hot_func = self
        gen_code_begin = '$generator(%s, %s) {\n' % (
            self.name, self.ret_type.to_cpp())

        # 函数参数变量
        gen_code_var = ''
        for arg in self.args:
            gen_code_var += arg.type_.to_cpp() + ' ' + arg.name + ';\n'

        # 构造函数参数
        gen_code_construct_head = '('
        gen_code_construct_list = ''
        if len(self.args) != 0:
            gen_code_construct_head += self.args[0].type_.to_cpp() + \
                ' ' + self.args[0].name
            gen_code_construct_list += self.args[0].name + \
                '(' + self.args[0].name + ')'
            self.args.pop(0)
        while len(self.args) > 0:
            gen_code_construct_head += ',' + \
                self.args[0].type_.to_cpp() + ' ' + self.args[0].name
            gen_code_construct_list += ',' + self.args[0].name + \
                '(' + self.args[0].name + ')'
            self.args.pop(0)
        gen_code_construct_head += ')'
        gen_code_construct = self.name + gen_code_construct_head
        if gen_code_construct_list != '':
            gen_code_construct += ':' + gen_code_construct_list

        gen_code_init = '\nvoid init' + gen_code_construct_head + '{'
        for arg in self.origin_args:
            gen_code_init += 'this->%s = %s;\n' % (arg.name, arg.name)
        gen_code_init += '}\n'

        self.args = []

        gen_code_emit = '$emit(%s)' % self.ret_type.to_cpp()

        gen_code_body = self.stmts.to_cpp()

        # 函数体内变量
        for arg in self.args:
            if type(arg.type_) == str:
                type_ = arg.type_
            else:
                type_ = arg.type_.to_cpp()
            gen_code_var += type_ + ' ' + arg.name + ';\n'

        gen_code_end = '$stop};'

        gen_code_default_construct = self.name + '()'

        self.args = [arg for arg in self.args if arg.is_arg]
        if (len(self.args) != 0):
            gen_code_default_construct += ' : '
            if gen_code_construct_list == '':
                gen_code_construct += ' : '
            else:
                gen_code_construct += ', '
            for arg in self.args:
                gen_code_default_construct += arg.name + '(' + arg.init + '), '
                gen_code_construct += arg.name + '(' + arg.init + '), '
            gen_code_construct = gen_code_construct[0:-2]
            gen_code_default_construct = gen_code_default_construct[0: -2]
        gen_code_construct += '{}\n'
        gen_code_default_construct += '{}\n'

        if gen_code_default_construct == gen_code_construct:
            gen_code_default_construct = ''
        gen_code = gen_code_begin + gen_code_var + gen_code_construct + gen_code_default_construct + gen_code_init +\
            gen_code_emit + gen_code_body + gen_code_end
        return gen_code

    def __str__(self):
        s = 'func_decl ' + self.name + '('
        if len(self.args) > 0:
            s += self.args[0].name
        if len(self.args) > 1:
            for i in range(1, len(self.args)):
                s += ',' + self.args[i].name
        s += ')'
        s += '{' + str(self.stmts) + '}'
        return s


class Program:
    def __init__(self, funcs, global_vars):
        self.funcs = funcs
        self.global_vars = global_vars

    def to_cpp(self):
        s = '#include \"executor.h\"\n\n'
        for func in self.funcs:
            s += func.to_cpp() + '\n'
        return s

    def __str__(self):
        s = 'prog(\nglobal_vars:\n'
        for g_var in self.global_vars:
            s += '(' + g_var.name
            if g_var.init != None:
                s += '=(' + str(g_var.init) + ')'
            s += ')\n'
        s += '\nfuncs:\n'
        for func in self.funcs:
            s += '(' + str(func) + ')\n'

        s += ')'
        return s


used_token = []
curr_token = None
token_list = []
lvar_stack = []
lvar_stack_depth = []
max_stack_size = 0
stack_size = 0
scope_depth = 0
hot_func = None
funcs = []  # 已经声明了的函数
global_vars = []


def push_scope():
    global scope_depth
    scope_depth += 1


def pop_scope():
    global scope_depth, stack_size
    scope_depth -= 1
    while len(lvar_stack) > 0 and lvar_stack_depth[0] > scope_depth:
        stack_size -= lvar_stack[0].type_.size()
        lvar_stack.pop(0)
        lvar_stack_depth.pop(0)


def new_node(kind):
    return Node(kind=kind)


def next_token():
    global curr_token
    used_token.append(curr_token)
    curr_token = token_list.pop(0)


def checkout_token():
    global curr_token, token_list
    token_list.insert(0, curr_token)
    curr_token = used_token[-1]
    used_token.pop(len(used_token) - 1)

# 判断当前 token 是否为指定保留字


def expect_reserved(s):
    return curr_token.kind == TokenKind('RESERVED') and curr_token.token_str == s


def last_token():
    return used_token[-1]


# 尝试解析一个数字字面量的 token 出来，失败则返回 None, 成功返回对应 token
# parser_xxx 都对应一个终结符的解析
def parse_int_literal():
    if curr_token.kind != TokenKind('NUM'):
        return None
    val = curr_token.val
    next_token()
    return (last_token(), val)


def parse_reserved(s):
    if not expect_reserved(s):
        return None
    next_token()
    return last_token()


# 尝试解析一个非终结符，由于目前没有 type system, 返回值仅表示成功或者失败
# 类似名称的函数与 NodeKind 基本一一对应，与非终结符大致一一对应
def get_type():
    type_ = None
    if parse_reserved('int') != None:
        type_ = Type(kind=TypeKind('INT'))
    if type_ == None:
        return None
    while parse_reserved('*'):
        type_ = Type(kind=TypeKind('PTR'), base=type_)
    return type_


def parse_ident():
    if curr_token.kind != TokenKind('IDENT'):
        return None
    name = curr_token.token_str
    next_token()
    return (last_token(), name)


def new_num(val):
    return Node(kind=NodeKind('NUM'), val=val, type_=Type(kind=TypeKind('INT')))


def num():
    node = None
    int_literal = parse_int_literal()
    if int_literal != None:
        node = new_num(int_literal[1])
    return node


def new_var_node(var):
    return Node(kind=NodeKind('VAR'), var=var, type_=var.type_)


def func_call(name):
    func = FuncCall(name, [])
    parse_reserved('(')
    if parse_reserved(')') != None:
        return func
    func.args.append(expr())
    while parse_reserved(')') == None:
        parse_reserved(',')
        func.args.append(expr())
    return func


def primary():
    if parse_reserved('(') != None:
        fac = expr()
        parse_reserved(')')
        return fac
    ident = parse_ident()
    if ident != None:
        name = ident[1]
        if parse_reserved('('):                     # )
            node = new_node(kind=NodeKind('FUNC_CALL'))
            node.func_call = func_call(name)
            if node.func_call == None:
                print('deref func call fail')
                exit(-1)
            func = find_func(name)
            if func == None:
                print('undeclear func')
                exit(-1)
            assert(len(func.args) == len(node.func_call.args))
            for i in range(len(func.args)):
                assert(func.args[i].type_ == node.func_call.args[i].type_)
            node.type_ = func.ret_type
            return node
        else:
            return new_var_node(find_var(name))
    return num()


def new_unary(kind, expr):
    # if kind == NodeKind('BITNOT') or kind == NodeKind('NEG'):
    assert(expr.type_.kind == TypeKind('INT'))
    return Node(kind=kind, expr_r=expr, type_=expr.type_)


def new_unary_ptr(kind, expr):
    assert(expr.type_.kind != TypeKind('ARR'))
    node = Node(kind=kind, expr_r=expr)
    if kind == NodeKind('DEREF'):
        assert(expr.type_.kind == TypeKind('PTR'))
        node.type_ = expr.type_.base
    elif kind == NodeKind('REF'):
        node.type_ = Type(kind=TypeKind('PTR'), base=expr.type_)
    return node


def new_cast(origin, type_):
    node = new_node(NodeKind('TYPE_CAST'))
    node.expr_r = origin
    node.type_ = type_
    if origin.var != None:
        node.var = Var(origin.var.name, None, None, None, None, None, None)
    return node


# 对应同名非终结符
def postfix():
    node = primary()
    if node != None and (node.type_.kind == TypeKind('ARR') or (node.type_.kind == TypeKind('PTR') and expect_reserved('['))):
        # ]
        postfix = None
        if node.type_.kind == TypeKind('ARR'):
            postfix = Node(kind=NodeKind('ARR_INDEX'),
                           expr_r=node, arr_index=[])
        if node.type_.kind == TypeKind('PTR'):
            postfix = Node(kind=NodeKind('PTR_INDEX'),
                           expr_r=node, arr_index=[])
        while parse_reserved('['):
            postfix.arr_index.append(expr())
            assert(postfix.arr_index[-1].type_.kind == TypeKind('INT'))
            parse_reserved(']')
        type_ = node.type_
        for i in range(len(postfix.arr_index)):
            type_ = type_.base
            assert(type_ != None)
        postfix.type_ = type_
        return postfix
    return node


def unary():
    token = parse_reserved('-')
    if token != None:
        return new_unary(kind=NodeKind('NEG'), expr=unary())
    token = parse_reserved('!')
    if token != None:
        return new_unary(kind=NodeKind('NOT'), expr=unary())
    token = parse_reserved('~')
    if token != None:
        return new_unary(kind=NodeKind('BITNOT'), expr=unary())
    token = parse_reserved('*')
    if token != None:
        return new_unary_ptr(kind=NodeKind('DEREF'), expr=unary())
    token = parse_reserved('&')
    if token != None:
        return new_unary_ptr(kind=NodeKind('REF'), expr=unary())
    token = parse_reserved('(')
    if token != None:
        type_ = get_type()
        if type_ != None:
            assert(parse_reserved(')'))
            node = new_cast(unary(), type_)
            return node
        checkout_token()
    token = parse_reserved('await')
    if token != None:
        assert(parse_reserved('(') != None)
        node = primary()
        assert (parse_reserved(')') != None)
        return(new_unary(NodeKind('AWAIT'), node))
    return postfix()


def new_binary(kind, expr_l, expr_r):
    assert(expr_l.type_ == expr_r.type_)
    assert(expr_l.type_ == Type(kind=TypeKind('INT')))
    return Node(kind=kind, expr_l=expr_l, expr_r=expr_r, type_=Type(kind=TypeKind('INT')))


def multiplicative():
    node = unary()
    while True:
        token = parse_reserved('*')
        if token != None:
            node = new_binary(kind=NodeKind('MUL'), expr_l=node,
                              expr_r=unary())
            continue
        token = parse_reserved('/')
        if token != None:
            node = new_binary(kind=NodeKind('DIV'), expr_l=node,
                              expr_r=unary())
            continue
        token = parse_reserved('%')
        if token != None:
            node = new_binary(kind=NodeKind('MOD'),
                              expr_l=node, expr_r=unary())
            continue
        break
    return node


def new_add(expr_l, expr_r, op):
    if expr_l.type_.kind == TypeKind('INT') and expr_r.type_.kind == TypeKind('INT'):
        return Node(kind=NodeKind(op), expr_l=expr_l, expr_r=expr_r, type_=Type(kind=TypeKind('INT')))
    if (expr_l.type_.kind == TypeKind('PTR') and expr_r.type_.kind == TypeKind('INT')):
        return Node(kind=NodeKind('PTR_' + op), expr_l=expr_l, expr_r=expr_r, type_=expr_l.type_)
    if (expr_l.type_.kind == TypeKind('INT') and expr_r.type_.kind == TypeKind('PTR')):
        return Node(kind=NodeKind('PTR_' + op), expr_l=expr_r, expr_r=expr_l, type_=expr_r.type_)
    if (expr_l.type_.kind == TypeKind('PTR') and expr_r.type_.kind == TypeKind('PTR')):
        assert(op == 'SUB')
        assert(expr_l.type_ == expr_r.type_)
        return Node(kind=NodeKind('PTR_DIFF'), expr_l=expr_l, expr_r=expr_r, type_=Type(kind=TypeKind('INT')))
    print('unsupport %s %s %s' % (expr_l.type_.kind, op, expr_r.type_.kind))
    exit(-1)


def additive():
    node = multiplicative()
    while True:
        token = parse_reserved('+')
        if token != None:
            node = new_add(expr_l=node, expr_r=multiplicative(), op='ADD')
            continue
        token = parse_reserved('-')
        if token != None:
            node = new_add(expr_l=node, expr_r=multiplicative(), op='SUB')
            continue
        break
    return node


def relational():
    node = additive()
    while True:
        token = parse_reserved('>')
        if token != None:
            node = new_binary(kind=NodeKind('LT'),
                              expr_l=additive(), expr_r=node)
            continue
        token = parse_reserved('>=')
        if token != None:
            node = new_binary(kind=NodeKind('LTE'),
                              expr_l=additive(), expr_r=node)
            continue
        token = parse_reserved('<')
        if token != None:
            node = new_binary(kind=NodeKind('LT'), expr_l=node,
                              expr_r=additive())
            continue
        token = parse_reserved('<=')
        if token != None:
            node = new_binary(kind=NodeKind('LTE'), expr_l=node,
                              expr_r=additive())
            continue
        break
    return node


def new_equal(kind, expr_l, expr_r):
    assert(expr_l.type_.kind != TypeKind('ARR'))
    node = new_node(kind)
    assert(expr_l.type_ == expr_r.type_)
    node.expr_l = expr_l
    node.expr_r = expr_r
    node.type_ = Type(kind=TypeKind('INT'))
    return node


def equality():
    node = relational()
    while True:
        token = parse_reserved('==')
        if token != None:
            node = new_equal(kind=NodeKind('EQ'), expr_l=node,
                             expr_r=relational())
            continue
        token = parse_reserved('!=')
        if token != None:
            node = new_equal(kind=NodeKind('NEQ'), expr_l=node,
                             expr_r=relational())
            continue
        break
    return node


def logic_and():
    node = equality()
    while True:
        token = parse_reserved('&&')
        if token == None:
            break
        node = new_binary(kind=NodeKind('LOGAND'), expr_l=node,
                          expr_r=equality())
    return node


def logic_or():
    node = logic_and()
    while True:
        token = parse_reserved('||')
        if token == None:
            break
        node = new_binary(kind=NodeKind('LOGOR'), expr_l=node,
                          expr_r=logic_and())
    return node


def conditional():
    node = logic_or()
    token = parse_reserved('?')
    if token == None:
        return node
    tern = new_node(NodeKind('TERNARY'))
    tern.cond = node
    tern.then = expr()
    assert(parse_reserved(':'))
    tern.else_ = conditional()
    tern.type_ = tern.cond.type_
    assert(tern.then.type_ == tern.else_.type_)
    return tern


def new_assgin(expr_l, expr_r):
    assert(expr_l.type_.kind != TypeKind('ARR'))
    node = new_node(NodeKind('ASSIGN'))
    if expr_l.type_.kind == TypeKind('INT'):
        assert(expr_r.type_.kind == TypeKind('INT'))
    else:
        assert ((expr_l.type_ == expr_r.type_) or
                (expr_r.kind == NodeKind('NUM') and expr_r.val == 0))  # pointer can be assigned 0
    node.expr_l = expr_l
    node.expr_r = expr_r
    node.type_ = expr_l.type_
    return node


def assign():
    node = conditional()
    while parse_reserved('=') != None:
        node = new_assgin(node, assign())
    return node


def expr():
    return assign()


def new_stmt(kind, expr):
    return Node(kind=kind, expr_r=expr)


def search_varlist(name, var_list):
    for var in var_list:
        if var.name == name:
            return var
    return None


def find_local_var(name):
    var = search_varlist(name, lvar_stack)
    if var != None:
        return var
    return search_varlist(name, hot_func.args)


def new_var_tpye(name, init, type_):
    global scope_depth, max_stack_size
    var = find_local_var(name)
    if var != None and var.scope_depth == scope_depth:
        print('variable `%s` redefined' % var.name)
        exit(-1)
    global stack_size
    var = Var(name, stack_size, init, scope_depth, False, False, type_)
    lvar_stack.insert(0, var)
    lvar_stack_depth.insert(0, scope_depth)
    stack_size += var.type_.size()
    max_stack_size = max(max_stack_size, stack_size)
    return var


def suffix(base):
    if parse_reserved('['):
        int_literal = parse_int_literal()
        assert(int_literal != None)
        assert(parse_reserved(']'))
        type_ = suffix(base)
        assert(int_literal[1] != 0)
        return Type(kind=TypeKind('ARR'), base=type_, arr_len=int_literal[1], pointer_depth=type_.pointer_depth+1, arr_dim=type_.arr_dim+1)
    return base


def declaration(type_):
    name = parse_ident()[1]
    type_ = suffix(type_)
    init = None
    if parse_reserved('='):
        init = expr()
        assert(init.type_ == type_)
    assert(parse_reserved(';'))
    var = new_var_tpye(name, init, type_)
    node = new_stmt(NodeKind('DECL'), None)
    node.var = var
    node.type_ = var.type_
    return node


# 对应非终结符 statement
def stmt():
    # Yield statement
    token = parse_reserved('yield')
    if (token != None):
        node = new_stmt(NodeKind('YIELD'), expr())
        assert(parse_reserved(';'))
        assert(hot_func.ret_type == node.expr_r.type_)
        return node

    # Return statement
    token = parse_reserved('return')
    if (token != None):
        node = new_stmt(NodeKind('RETURN'), expr())
        assert(parse_reserved(';'))
        assert(hot_func.ret_type == node.expr_r.type_)
        return node

    # IF statement
    token = parse_reserved('if')
    if token != None:
        assert(parse_reserved('('))
        node = new_node(NodeKind('IF'))
        node.cond = expr()
        assert(node.cond.type_.kind == TypeKind('INT'))
        assert(parse_reserved(')'))
        node.then = stmt()
        if(parse_reserved('else')):
            node.else_ = stmt()
        return node

    # Compound stmt
    if expect_reserved('{'):
        return compound_stmt()

    # For statement
    if parse_reserved('for') != None:
        node = new_node(NodeKind('FOR'))
        assert(parse_reserved('('))
        push_scope()
        type_ = get_type()
        if type_ != None:
            node.pre = declaration(type_)
        else:
            # assign 语句是比较容易出错的一个语句，如果有不使用的 expr，一定要使用 EXPR 包装
            node.pre = new_stmt(NodeKind('EXPR'), expr())
            assert(parse_reserved(';'))
        if parse_reserved(';') == None:
            node.cond = expr()
            assert(node.cond.type_.kind == TypeKind('INT'))
            assert(parse_reserved(';'))

        if parse_reserved(')') == None:
            # 使用 UNUSED_EXPR 包装，弹出无用的值
            post = expr()
            node.post = new_stmt(NodeKind('EXPR'), post)
            assert(parse_reserved(')'))
        push_scope()
        node.then = stmt()
        pop_scope()
        pop_scope()
        return node

    # do-while statement
    if parse_reserved('do') != None:
        node = new_node(NodeKind('DOWHILE'))
        node.then = stmt()
        assert(parse_reserved('while'))
        assert(parse_reserved('('))
        node.cond = expr()
        assert(node.cond.type_.kind == TypeKind('INT'))
        assert(parse_reserved(')'))
        assert(parse_reserved(';'))
        return node

    # while-do statement
    if parse_reserved('while') != None:
        node = new_node(NodeKind('WHILEDO'))
        assert(parse_reserved('('))
        node.cond = expr()
        assert(node.cond.type_.kind == TypeKind('INT'))
        assert(parse_reserved(')'))
        node.then = stmt()
        return node

    # Break
    if parse_reserved('break') != None:
        assert(parse_reserved(';'))
        return new_node(NodeKind('BREAK'))

    # Continue
    if parse_reserved('continue') != None:
        assert(parse_reserved(';'))
        return new_node(NodeKind('CONTINUE'))

    # Unused expr
    node = expr()
    assert(parse_reserved(';'))
    return new_stmt(NodeKind('EXPR'), node)


def block_item():
    # Local var declaration
    type_ = get_type()
    if type_ != None:
        return declaration(type_)
    return stmt()


def compound_stmt():
    # Compound statement
    if parse_reserved('{') != None:
        block_stmts = []
        push_scope()
        while parse_reserved('}') == None:
            block_stmts.append(block_item())
        pop_scope()
        node = new_node(NodeKind('BLOCK'))
        node.body = block_stmts
        return node
    return None


def find_func(name):
    for func in funcs:
        if name == func.name:
            return func
    return None


def add_func(name, args, type_, is_gen):
    global funcs
    func = Function(name, None, None, args, False, type_, is_gen)
    funcs.append(func)
    return func


def decl_func_arg(args):
    type_ = get_type()
    assert(type_ != None)
    ident = parse_ident()
    name = None
    # 声明中参数可能没有名称
    if ident != None:
        name = ident[1]
    global scope_depth
    var = Var(name, len(args), None, scope_depth + 1, True, False, type_)
    args.append(var)


def decl_func_args():
    args = []
    assert(parse_reserved('('))
    if parse_reserved(')') != None:
        return args
    decl_func_arg(args)
    while parse_reserved(')') == None:
        assert(parse_reserved(','))
        decl_func_arg(args)
    arg_name = [arg.name for arg in args]
    assert(len(arg_name) == len(list(set(arg_name))))
    return args


def funtion(name, type_, is_gen):
    global max_stack_size, lvar_stack, lvar_stack_depth
    args = decl_func_args()
    func = find_global_var(name)
    # find_func 返回不是 None，表明已经有过声明
    if func != None:
        if func.is_complete:
            assert(parse_reserved(';'))
            return None
        # 仅有声明，必须有相同的参数，不支持函数重载
        assert(len(func.args) == len(args))
        for i in range(len(func.args)):
            assert(func.args[i].type_ == args[i].type_)
        # 可能有参数重命名，以现有函数参数为准
        func.args = args
    else:
        add_func(name, args, type_, is_gen)
    # 这仅是一个声明，返回 NULL
    if parse_reserved(';') != None:
        return None
    global hot_func, max_stack_size
    if func == None:
        func = add_func(name, args, type_, is_gen)
    func.is_complete = True
    hot_func = func
    func.stmts = compound_stmt()
    func.max_stack_size = (max_stack_size + 2 + len(hot_func.args)) * 4
    return func


def is_func():
    return expect_reserved('(')  # )


def find_global_var(name):
    g_var = search_varlist(name, global_vars)
    if g_var != None:
        return g_var
    return find_func(name)


def global_var(name, type_):
    # 不允许重定义
    assert(find_global_var(name) == None)
    type_ = suffix(type_)
    g_var = Var(name, None, None, None, False, True, type_)
    # 全局变量只允许使用字面量优化
    if parse_reserved('='):
        g_var.init = num()
    assert(parse_reserved(';'))
    return g_var


def find_var(name):
    var = find_local_var(name)
    if var != None:
        return var
    return find_global_var(name)


def parsing(token_list_):
    global token_list, lvar_stack, lvar_stack_depth, max_stack_size, scope_depth, hot_func, stack_size
    token_list = token_list_
    next_token()
    prog = Program([], [])
    while len(token_list) > 0:
        is_gen = (parse_reserved('generator') != None) or (
            parse_reserved('async') != None)
        type_ = get_type()
        assert (type_ != None)
        name = parse_ident()[1]
        if is_func():
            func = funtion(name, type_, is_gen)
            if func == None:
                continue
            prog.funcs.append(func)
            lvar_stack = []
            lvar_stack_depth = []
            max_stack_size = 0
            scope_depth = 0
            hot_func = None
            stack_size = 0
        else:
            g_var = global_var(name, type_)
            global_vars.append(g_var)
    prog.global_vars = global_vars
    return prog
