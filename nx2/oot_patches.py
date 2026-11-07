"""Changes to the lifted C for Ocarina of Time, applied by lift.py after it writes the code (and by hand: python -I nx2/oot_patches.py).

Each is a runtime switch where it can be, so the game's own path stays reachable.

- Dynamic resolution (Lichii's built-in "Max Resolution" patch, main+0x805BD0): the engine's config flag at +0x94 picks the path that
  follows the GPU-time controller; with hos_fixed_resolution set it takes the other path, the 3D at full scale. The controller made
  a new set of render targets at each size, ~11 images a frame at times, and held the GPU near its budget.
"""
import glob
import os
import sys

DECL = "extern volatile int hos_fixed_resolution;\nextern volatile uint32_t hos_fixed_scale_bits;\n"
OLD = "if (!((c->x[8] >> 0) & 1)) { goto L_8082640c; }"
NEW = "if (hos_fixed_resolution || !((c->x[8] >> 0) & 1)) { goto L_8082640c; }"
LABEL = "L_8082640c:;"
SCALE_OLD = "c->x[9] = 0x3f800000ULL;"
SCALE_NEW = "c->x[9] = hos_fixed_scale_bits;"   # (the fixed path's scale, 1.0 as shipped)


def apply(gen):
    done = 0
    for path in sorted(glob.glob(os.path.join(gen, "code_*.c"))):
        with open(path, encoding="utf-8", newline="") as f:
            s = f.read()
        if OLD not in s:
            continue
        s = s.replace(OLD, NEW, 1)
        at = s.index(LABEL)
        scale = s.index(SCALE_OLD, at)
        s = s[:scale] + SCALE_NEW + s[scale + len(SCALE_OLD):]
        s = s.replace('#include "a64.h"\n', '#include "a64.h"\n' + DECL, 1)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(s)
        done += 1
        print("oot_patches: dynamic resolution switch in", os.path.basename(path))
    if done != 1:
        print("oot_patches: WARNING: the dynamic resolution branch was found %d times" % done)
    if os.environ.get("OOT_DIV_PROBE"):
        div_probe(gen)


# Temporary diagnostic for the ultrawide work (branch ultrawide-43-18): log every float division whose
# quotient lands near 16:9 (1.77778) with the caller's host address, so a short play session lists the
# candidate camera-ascent sites (samap.py maps the addresses back to f_<guest> functions). Idempotent.
PROBE_MARK = "/* oot aspect-div probe (temporary: ultrawide-43-18) */"
PROBE_OLD = "A64_FPX_FN uint64_t a64_fpx_div32_div32(Ctx *A64_NOESC c, uint64_t a0, uint64_t a1) {"
PROBE_NEW = ('#include <stdio.h>\n#include <string.h>\n' + PROBE_MARK + '\n' + PROBE_OLD +
             ' { static int n; float fa, fb; memcpy(&fa, &a0, 4); memcpy(&fb, &a1, 4);'
             ' if (n < 500 && fb > 1.0f && fb < 8192.0f && fa > 1.0f && fa < 8192.0f)'
             ' { float q = fa / fb; if (q > 1.772f && q < 1.783f)'
             ' { n++; fprintf(stderr, "aspect-div q=%.6f a=%.3f b=%.3f at %p\\n", q, fa, fb, __builtin_return_address(0)); } } }')


def div_probe(gen):
    path = os.path.join(gen, "a64_fpx.h")
    with open(path, encoding="utf-8", newline="") as f:
        s = f.read()
    if PROBE_MARK in s:
        print("oot_patches: aspect-div probe already present")
        return
    if PROBE_OLD not in s:
        print("oot_patches: WARNING: div probe anchor not found in a64_fpx.h")
        return
    s = s.replace(PROBE_OLD, PROBE_NEW, 1)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("oot_patches: aspect-div probe installed in a64_fpx.h")


if __name__ == "__main__":
    apply(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "sa", "gen"))
