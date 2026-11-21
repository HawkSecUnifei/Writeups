#!/usr/bin/env bash
set -u

CHAL_DIR=${CHAL_DIR:-/opt/chal}
CLANG=${CLANG:-/usr/lib/llvm/22/bin/clang}
DSLC=${DSLC:-$CHAL_DIR/dslc}
MAX_SRC_BYTES=${MAX_SRC_BYTES:-65536}
COMPILE_TIMEOUT=${COMPILE_TIMEOUT:-20}
RUN_TIMEOUT=${RUN_TIMEOUT:-5}

work=$(mktemp -d /tmp/chal.XXXXXX) || exit 1
cleanup() { rm -rf "$work"; }
trap cleanup EXIT
cd "$work" || exit 1

echo "== send your .dsl program, then a line containing only __EOF__ =="
: > prog.dsl
bytes=0
while IFS= read -r -t 30 line; do
    [ "$line" = "__EOF__" ] && break
    printf '%s\n' "$line" >> prog.dsl
    bytes=$((bytes + ${#line} + 1))
    if [ "$bytes" -gt "$MAX_SRC_BYTES" ]; then
        echo "error: source too large (> ${MAX_SRC_BYTES} bytes)"; exit 1
    fi
done
[ -s prog.dsl ] || { echo "error: empty source"; exit 1; }

cp "$CHAL_DIR/compilerIBarelyKnowHer.so" "$CHAL_DIR/runtime.o" "$work"/
cp "$CHAL_DIR/dslc" "$work"/dslc 2>/dev/null || true
ln -sf "$CHAL_DIR/flag.txt" "$work/flag.txt"

ulimit -v $((1024 * 1024))
ulimit -t 25
ulimit -f $((50 * 1024))
ulimit -u "${NPROC:-512}"

if ! python3 "$DSLC" prog.dsl -o prog.ll 2> dslc.log; then
    echo "== dslc failed =="; head -c 4000 dslc.log; exit 1
fi

if ! timeout "$COMPILE_TIMEOUT" "$CLANG" -O1 \
        -fpass-plugin=./compilerIBarelyKnowHer.so \
        -fstack-protector-strong -no-pie \
        -Wl,--section-start=.winsec=0x4010000 \
        prog.ll runtime.o -o prog 2> compile.log; then
    echo "== compile failed =="; head -c 4000 compile.log; exit 1
fi

echo "== running =="
if command -v unshare >/dev/null 2>&1 && unshare -n true 2>/dev/null; then
    timeout "$RUN_TIMEOUT" unshare -n ./prog
else
    timeout "$RUN_TIMEOUT" ./prog
fi
rc=$?
echo "== exit $rc =="
exit 0
