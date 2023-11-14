# !/bin/bash
(time python main.py data) &> log_$(date +%Y%m%d_%H%M%S).txt