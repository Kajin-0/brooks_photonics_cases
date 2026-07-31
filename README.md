# Brooks Photonics Cases

Reproducible detector-characterization case studies built from public, traceable measurement data.

The repository is organized around engineering questions rather than generic plotting examples. Each case is intended to produce:

- a pinned public-data manifest;
- reproducible download and validation steps;
- detector-level analysis code;
- uncertainty and quality-control outputs;
- a concise technical report suitable for the Brooks Photonics portfolio.

## Initial case

**Case 001 — WFC3/IR HgCdTe ramp anomaly diagnosis**

A real Hubble WFC3/IR MULTIACCUM exposure affected by time-variable Earth-limb scattered light is compared with a nominal exposure from the same visit. The analysis operates on individual nondestructive detector reads, identifies contaminated reads, quantifies spatial asymmetry, and evaluates the effect on the fitted count-rate product.

Development work is proposed through pull requests before it is merged into `main`.
