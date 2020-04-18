import subprocess

def cmp_img(a: str, b: str) -> float:
    out = subprocess.run(["compare", "-quiet", "-metric", "MSE", a, b, "/dev/null"], stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, check=False)

    # return code 1 is for dissimilar images, but we use our own threshold
    # since imagemagick is too strict
    if out.returncode == 2:
        class CompareError(Exception):
            def __init__(self, message):
                self.message = message

        raise CompareError("Compare failed on {}, {}".format(a, b))

    # The result is b"... (diff)"
    diff = out.stderr.split(b"(")[1][:-1]

    # out.stderr is a byte sequence, but float can take byte sequences
    return float(diff)
