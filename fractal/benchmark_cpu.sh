#!/usr/bin/env bash
# Sweep OMP thread counts, run ./solution under Slurm (srun) with limited parallelism,
# capture program-reported elapsed time from stdout, write cpu_benchmark_results.csv.
#
# Usage: ./benchmark_cpu.sh
# Env:
#   THREAD_COUNTS   space-separated thread counts (default: 1,2,4,... up to nproc, plus nproc if not already listed)
#   REPETITIONS     runs per configuration (default: 10)
#   SRUN_OPTS       extra srun arguments (e.g. "-p compute -t 10")
#   MAX_PARALLEL    max concurrent srun steps (default: 0 = unlimited)
#   BENCH_ROOT      work/output directory (default: <script-dir>/bench_runs)
#   CSV_OUT         output CSV path (default: <script-dir>/cpu_benchmark_results.csv)

set -euo pipefail

log_progress() {
	echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOLUTION="$SCRIPT_DIR/solution"
BENCH_ROOT="${BENCH_ROOT:-$SCRIPT_DIR/bench_runs}"
CSV_OUT="${CSV_OUT:-$SCRIPT_DIR/cpu_benchmark_results.csv}"
REPS="${REPETITIONS:-10}"
MAX_PARALLEL="${MAX_PARALLEL:-0}"

if [[ ! -x "$SOLUTION" ]]; then
	echo "Missing executable: $SOLUTION — build with: make -C \"$SCRIPT_DIR\"" >&2
	exit 1
fi
if ! command -v srun >/dev/null 2>&1; then
	echo "srun not found in PATH (Slurm required)." >&2
	exit 1
fi

if [[ -n "${THREAD_COUNTS:-}" ]]; then
	read -r -a THREAD_VALUES <<< "$THREAD_COUNTS"
else
	THREAD_VALUES=()
	n=$(nproc)
	v=1
	while [[ "$v" -le "$n" ]]; do
		THREAD_VALUES+=("$v")
		v=$((v * 2))
	done
	if ((${#THREAD_VALUES[@]} > 0)); then
		last="${THREAD_VALUES[$(( ${#THREAD_VALUES[@]} - 1 ))]}"
		if [[ "$last" -ne "$n" ]] && [[ "$n" -ge 1 ]]; then
			THREAD_VALUES+=("$n")
		fi
	fi
fi

num_configs=${#THREAD_VALUES[@]}
total_jobs=$((num_configs * REPS))
log_progress "benchmark_cpu: ${num_configs} thread configuration(s), ${REPS} run(s) each → ${total_jobs} job(s) total"
log_progress "thread counts: ${THREAD_VALUES[*]}"
if [[ "$MAX_PARALLEL" -eq 0 ]]; then
	log_progress "MAX_PARALLEL=0 (unlimited concurrent srun)"
else
	log_progress "MAX_PARALLEL=${MAX_PARALLEL}"
fi
[[ -z "${SRUN_OPTS:-}" ]] || log_progress "SRUN_OPTS=${SRUN_OPTS}"

parse_elapsed_from_file() {
	local f=$1
	local val
	val=$(sed -n 's/^Elapsed time: \([0-9.]*\)s$/\1/p' "$f" | head -1)
	[[ -n "$val" ]] || return 1
	printf '%s' "$val"
}

mkdir -p "$BENCH_ROOT"

declare -a pids=()
declare -i any_fail=0
declare -i job_queued=0

run_step() {
	local threads=$1 run=$2
	local wd out err
	wd="$BENCH_ROOT/wd_${threads}_${run}"
	out="$BENCH_ROOT/out_${threads}_${run}.txt"
	err="$BENCH_ROOT/err_${threads}_${run}.txt"
	mkdir -p "$wd"
	ln -sf "$SOLUTION" "$wd/solution"
	(
		cd "$wd"
		export OMP_NUM_THREADS="$threads"
		# shellcheck disable=SC2086
		srun -n 1 -c "$threads" ${SRUN_OPTS:-} ./solution >"$out" 2>"$err"
	) &
	pids+=($!)
	job_queued+=1
	log_progress "queued ${job_queued}/${total_jobs}: threads=${threads} run=${run} (pid=$!)"
}

log_progress "starting job steps (output under ${BENCH_ROOT})"
for threads in "${THREAD_VALUES[@]}"; do
	for ((run = 1; run <= REPS; run++)); do
		while [[ "$MAX_PARALLEL" -ne 0 && ${#pids[@]} -ge "$MAX_PARALLEL" ]]; do
			wait "${pids[0]}" || any_fail=1
			pids=("${pids[@]:1}")
			log_progress "job finished; ${#pids[@]} still in flight"
		done
		run_step "$threads" "$run"
	done
done

log_progress "waiting for remaining ${#pids[@]} job(s)…"
for pid in "${pids[@]}"; do
	wait "$pid" || any_fail=1
done

log_progress "all job steps finished"

if [[ "$any_fail" -ne 0 ]]; then
	echo "One or more srun steps failed; see $BENCH_ROOT/err_*.txt" >&2
	exit 1
fi

log_progress "writing CSV: ${CSV_OUT}"
{
	echo "threads,run,elapsed_seconds"
	for threads in "${THREAD_VALUES[@]}"; do
		for ((run = 1; run <= REPS; run++)); do
			out="$BENCH_ROOT/out_${threads}_${run}.txt"
			sec="$(parse_elapsed_from_file "$out")" || {
				echo "Could not parse Elapsed time from: $out" >&2
				exit 1
			}
			echo "$threads,$run,$sec"
		done
	done
} >"$CSV_OUT"

log_progress "done — wrote ${CSV_OUT} (${total_jobs} rows plus header)"
