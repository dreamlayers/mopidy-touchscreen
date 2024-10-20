import sys

dash = u"\u2013"

def find_common_chars(l, tailcut = 0):
    if len(l) < 2:
        return None

    # List of characters as long as the shortest string
    cl = min(map(len, l)) - tailcut
    if cl < 1:
        return None
    c = list(l[0][0:cl])
    for s in l[1:]:
        diffalpha = False
        for i in range(0, cl):
            if s[i] != c[i]:
                # Mismatching locations become None
                c[i] = None
                diffalpha = s[i].isalpha()
                if diffalpha:
                    # Don't split words at the end
                    for j in range(i-1,-1,-1):
                        if c[j] is None:
                            break
                        elif s[j].isalpha():
                            c[j] = None
                        else:
                            break
            elif diffalpha and s[i].isalpha():
                # Don't split words at the beginning
                c[i] = None
    return c

def common_tail(l):
    if len(l) < 2:
        return 0

    cl = min(map(len, l))
    cs = l[0]
    cs = cs[len(cs) - cl:]
    csl = cl
    for s in l[1:]:
        sl = len(s)
        for i in range(1, cl + 1):
            if s[sl - i] != cs[csl - i]:
                cl = i - 1
                if cl < 1:
                    return 0
                break
    return cl

def shortened_tail(l):
    if len(l) < 1:
        return 0

    ctl = common_tail(l);
    s = l[0]
    for i in range(ctl, 0, -1):
        c = s[-ctl]
        if c != ']' and c != ')' and not c.isalpha():
            return i
    return 0


def common_span_list(cl):
    if cl is None:
        return []

    csl = []
    s = None
    for i, c in enumerate(cl):
        if s is None:
            if c is not None:
                s = i
        elif s is not None:
            if c is None:
                csl.append((s, i - s))
                s = None
    return csl

def useparts_list(l, tailcut = 0):
    cl = find_common_chars(l, tailcut)
    if cl is None:
        return []
    csl = common_span_list(cl)
    upl = []
    s = l[0]
    p = 0
    for sp in csl:
        repl = None
        if sp[1] == 1 and cl[sp[0]].isnumeric():
            repl = ''
        if sp[1] == 2 and \
           (cl[sp[0]] == '.' or cl[sp[0]] == '-') and \
           (cl[sp[0]+1] == ' ' or cl[sp[0]+1] == '_'):
            repl = dash
        elif sp[1] > 3:
            if sp[0] > 0:
                repl = dash
            else:
                repl = ''
        if repl is not None:
            partlen = sp[1] - sp[0]
            if repl != '' or partlen > 0:
                upl.append((p, sp[0], repl))
            p = sp[0] + sp[1]
    upl.append((p, -1, ''))
    return upl

def abbreviate(l):
    l = list(map(lambda s: s.replace(' - ', dash).replace('_-_', dash), l))

    if len(l) < 2:
        return l

    ct = shortened_tail(l)
    upl = useparts_list(l, ct)

    nl = []
    for s in l:
        if ct > 0:
            s = s[:-ct]
        ns = ''
        for up in  upl:
            if up[1] >= 0:
                ns += s[up[0]:up[1]].strip(' _-') + up[2]
            else:
                ns += s[up[0]:].strip(' _-')
        nl.append(ns)
    return nl

if __name__ == "__main__":
    import os

    for path, dirs, files in os.walk(sys.argv[1]):
        print('DIR', path)
        names = dirs + list(filter(lambda x: x.endswith('.mp3'), files))
        print('\n'.join(abbreviate(names)))
