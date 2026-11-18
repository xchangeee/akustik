import sys, glob, os, numpy as np
from scipy.io import wavfile
for f in sorted(sys.argv[1:]):
    sr, x = wavfile.read(f)
    x = x.astype(float); i = int(np.argmax(abs(x)))
    noise = 20*np.log10(np.sqrt(np.mean(x[-8000:]**2))/abs(x[i]))
    print(f"{os.path.basename(f):45s} sr={sr} n={len(x)} ({len(x)/sr:.2f}s) peak@{i} ({(i-256)/sr*1000:.3f} ms after t0) val={x[i]:+.4f} tailnoise={noise:.1f} dB")
