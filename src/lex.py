from enum import Enum
import re


class TokenKind(Enum):
    RESERVED = 'RESERVED'  # 保留字与符号
    IDENT = 'IDENT'  # 标识符
    NUM = 'NUM'  # 数字字面量
    EOF = 'EOF'  # s 结束标志


class Token:
    def __init__(self, kind, token_str, token_len, val=0):
        self.kind = kind
        self.val = val  # 如果是 TK_NUM，其代表的值
        self.token_str = token_str  # Token 字符串
        self.token_len = token_len  # Token 字符串长度

    def __str__(self):
        return '%-25s%s' % (self.kind, self.token_str)


def is_space(c):
    return c == '\n' or c == '\t' or c == ' '


def read_reserved(code: str, index: int):
    keyworks = ['return', 'int', 'if', 'else',
                'for', 'while', 'do', 'break', 'continue', 'yield', 'async', 'poll', 'generator', 'Future']
    for kw in keyworks:
        if code.startswith(kw, index) and not code[index + len(kw)].isalnum():
            return kw

    ops = ['==', '!=', '<=', '>=', '||', '&&']
    for op in ops:
        if code.startswith(op, index):
            return op
    return None


token_list = []


def gen_token(kind, token_str, token_len):
    token = Token(kind, token_str, token_len)
    token_list.append(token)
    return token


def read_int_literal(code: str, index: int):
    locate = re.match(r'\d+', code[index:])
    token = gen_token(TokenKind('NUM'), int(locate.group()),
                      len(locate.group()))
    token.val = int(locate.group())
    assert(token.val < 0x7fffffff)
    return token


def lexing(code: str):
    code_len = len(code)
    index = 0
    while index < code_len:
        # 空白符
        if is_space(code[index]):
            index += 1
            continue

        # 保留关键词
        kw = read_reserved(code, index)
        if kw != None:
            kw_len = len(kw)
            gen_token(TokenKind('RESERVED'), kw, kw_len)
            index += kw_len
            continue

        # 保留符号
        if not code[index].isalnum():
            gen_token(TokenKind('RESERVED'), code[index], 1)
            index += 1
            continue

        # 标识符
        if code[index].isalpha():
            start = index
            while code[index].isalnum() or code[index] == '_':
                index += 1
            inden = code[start:index]
            gen_token(TokenKind('IDENT'), inden, len(inden))
            continue

        # 数字字面量
        if code[index].isdigit():
            token = read_int_literal(code, index)
            index += token.token_len
            continue

        # 错误
        print('syntax error')
        exit(-1)
    gen_token(TokenKind('EOF'), '', 0)
    return token_list
