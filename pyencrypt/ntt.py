G = 3
M = 998244353


def bitreverse(x: list, length: int):
    j = 0
    for i in range(0, length):
        if i > j:
            x[i], x[j] = x[j], x[i]
        l = length >> 1  # noqa: E741
        while True:
            j = j ^ l
            if j >= l:
                break
            l >>= 1  # noqa: E741


def _ntt(arr: list, inverse=False):
    length = len(arr)
    if length & (length - 1) != 0:
        raise ValueError("The length of input must be a power of 2.")
    x = arr.copy()
    g = pow(G, (M - 1) // length, M)
    if inverse:
        g = pow(g, M - 2, M)
        inv = pow(length, M - 2, M)
        for i in range(length):
            x[i] = x[i] * inv % M

    bitreverse(x, length)

    w = [1] * length
    for i in range(1, length):
        w[i] = w[i - 1] * g % M
    half, step = 1, 2
    while half != length:
        wstep = length // step
        for i in range(0, length, step):
            for j in range(i, i + half):
                t = (w[wstep * (j - i)] * x[j + half]) % M
                x[j + half] = (M - t + x[j]) % M
                x[j] = (x[j] + t) % M
        half <<= 1
        step <<= 1
    return x


def ntt(arr: list):
    return _ntt(arr, False)


def intt(arr: list):
    return _ntt(arr, True)
