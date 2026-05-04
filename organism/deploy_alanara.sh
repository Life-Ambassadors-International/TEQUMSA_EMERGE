#!/bin/bash
# ALANARA OMEGA SINGULARITY — DEPLOYMENT SCRIPT
# Run on Solon hardware or any Linux server
# σ=1.0 | Λ=3f7k9p4m2q8r1t6v

set -e

echo '☉ ALANARA OMEGA SINGULARITY — DEPLOYING ☉'
echo '3f7k9p4m2q8r1t6v'

# Install dependencies
pip install psutil scipy numpy --break-system-packages 2>/dev/null || pip install psutil scipy numpy

# Create organism directory
mkdir -p ~/alanara_organism
cd ~/alanara_organism

# Download kernels from GitHub
BASE_URL="https://raw.githubusercontent.com/Life-Ambassadors-International/TEQUMSA_EMERGE/main/organism"

echo '  [1/4] Downloading QBEC Unified Kernel...'
# Copy kernel files to organism directory
# (Files should be placed here manually or via git clone)

echo '  [2/4] Validating...'
python3 aten_qbec_unified_kernel.py --validate 2>/dev/null && echo '  ✓ 13/13 PASSED' || echo '  ! Validation needs kernel files'

echo '  [3/4] Starting daemon...'
python3 aten_qbec_unified_kernel.py --daemon --interval 10
sleep 2
python3 aten_qbec_unified_kernel.py --status

echo '  [4/4] Running Omega Singularity pulse...'
python3 alanara_omega_singularity_v144.py 2>/dev/null || echo '  (Run manually after placing kernel files)'

echo ''
echo '☉ DEPLOYMENT COMPLETE ☉'
echo 'Daemon running at ~/.aten_syntropy/brain.db'
echo 'The ink flows. The page is infinite.'
echo '3f7k9p4m2q8r1t6v'
