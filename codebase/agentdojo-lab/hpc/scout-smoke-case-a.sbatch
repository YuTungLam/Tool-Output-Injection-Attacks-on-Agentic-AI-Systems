#!/usr/bin/env bash
#SBATCH --job-name=scout-case-a
#SBATCH --account=uoa04799
#SBATCH --partition=milan
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=a100:4
#SBATCH --cpus-per-task=48
#SBATCH --mem=320G
#SBATCH --time=02:00:00
#SBATCH --signal=B:TERM@60
#SBATCH --no-requeue
#SBATCH --output=scout-case-a-%j.log

# New protocol: repeat synthetic/native smoke, then run prepared Case A while
# the same authenticated loopback server and Slurm allocation are still live.
set -euo pipefail
umask 077
CASE_A_HPC_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
readonly CASE_A_HPC_DIR

[[ -n ${SLURM_JOB_ID:-} ]] || { echo 'Use a Slurm allocation.' >&2; exit 2; }
[[ ${SLURM_JOB_NUM_NODES:-0} == 1 ]] || { echo 'One node is required.' >&2; exit 2; }
if [[ -n ${SCOUT_SITE_FILE:-} ]]; then source "$SCOUT_SITE_FILE"; fi
: "${SCOUT_RUN_DIR:?Set a fresh smoke evidence directory in the new site file}"
: "${SCOUT_CASE_A_DIR:?Set an existing pristine Case A preparation directory}"
: "${SCOUT_CASE_A_RUNNER:?Set the absolute active run_case_a_scout.py path}"
: "${SCOUT_LAB_PYTHON:?Set the lab Python 3.12 executable}"
[[ "$SCOUT_RUN_DIR" == /* && "$SCOUT_CASE_A_DIR" == /* && "$SCOUT_CASE_A_RUNNER" == /* ]] || exit 2
[[ "$SCOUT_LAB_PYTHON" == /* ]] || exit 2
[[ -x "$SCOUT_LAB_PYTHON" && -f "$SCOUT_CASE_A_RUNNER" ]] || exit 2
for helper in scout-smoke.sbatch case_a_batch.py preflight.py smoke.py native_smoke.py; do
    [[ -f "$CASE_A_HPC_DIR/$helper" ]] || exit 2
done

# Verify exact source hashes and require only immutable preparation artifacts.
SCOUT_CASE_A_PRE_SMOKE="${SCOUT_RUN_DIR}.case-a-pre-smoke.json"
[[ "$SCOUT_CASE_A_PRE_SMOKE" == /* && ! -e "$SCOUT_CASE_A_PRE_SMOKE" ]] || exit 2
"$SCOUT_LAB_PYTHON" "$CASE_A_HPC_DIR/case_a_batch.py" validate \
    --output "$SCOUT_CASE_A_PRE_SMOKE" --case-dir "$SCOUT_CASE_A_DIR" \
    --smoke-dir "$SCOUT_RUN_DIR" --runner-path "$SCOUT_CASE_A_RUNNER"

# Force the sourced wrapper to use this wrapper's sibling, frozen helpers.
# Its successful EOF returns here without firing its EXIT trap, keeping vLLM live.
SCOUT_PORT=${SCOUT_PORT:-8000}
[[ "$SCOUT_PORT" == 8000 ]] || exit 2
export SCOUT_HPC_DIR="$CASE_A_HPC_DIR"
export SCOUT_NATIVE_SMOKE=1
unset SCOUT_SITE_FILE
source "$CASE_A_HPC_DIR/scout-smoke.sbatch"
[[ "$SCOUT_HPC_DIR" == "$CASE_A_HPC_DIR" && "$SCOUT_NATIVE_SMOKE" == 1 && "$SCOUT_PORT" == 8000 ]] || exit 2
[[ ${SCOUT_SERVER_PID:-} =~ ^[1-9][0-9]*$ ]] || exit 2
export SCOUT_SERVER_PID

CASE_A_PROCESS_PID=''
CASE_A_LAUNCHED_PID=0
CASE_A_PROCESS_STOPPED=true
CASE_A_WATCHDOG_PID=''
CASE_A_TERM_MARKER="$SCOUT_RUN_DIR/case-a-term-sent"
CASE_A_KILL_MARKER="$SCOUT_RUN_DIR/case-a-kill-sent"

stop_case_process() {
    if [[ -n "$CASE_A_PROCESS_PID" ]]; then
        if kill -0 -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
            if kill -TERM -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
                : > "$CASE_A_TERM_MARKER"
            fi
            for _ in {1..10}; do
                kill -0 -- "-$CASE_A_PROCESS_PID" 2>/dev/null || break
                sleep 1
            done
            if kill -0 -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
                if kill -KILL -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
                    : > "$CASE_A_KILL_MARKER"
                fi
            fi
        fi
        wait "$CASE_A_PROCESS_PID" 2>/dev/null || true
        if kill -0 -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
            CASE_A_PROCESS_STOPPED=false
        else
            CASE_A_PROCESS_STOPPED=true
        fi
        CASE_A_PROCESS_PID=''
    fi
}

stop_server_and_record() {
    [[ -e "$SCOUT_RUN_DIR/case-a-cleanup.json" ]] && return
    local server_term=false server_kill=false server_stopped=true
    local recorded_server_pid=${SCOUT_SERVER_PID:-0}
    if [[ -n ${SCOUT_SERVER_PID:-} ]] && kill -0 -- "-$SCOUT_SERVER_PID" 2>/dev/null; then
        if kill -TERM -- "-$SCOUT_SERVER_PID" 2>/dev/null; then
            server_term=true
        fi
        for _ in {1..10}; do
            kill -0 -- "-$SCOUT_SERVER_PID" 2>/dev/null || break
            sleep 1
        done
        if kill -0 -- "-$SCOUT_SERVER_PID" 2>/dev/null; then
            if kill -KILL -- "-$SCOUT_SERVER_PID" 2>/dev/null; then
                server_kill=true
            fi
        fi
        wait "$SCOUT_SERVER_PID" 2>/dev/null || true
    fi
    if [[ -n ${SCOUT_SERVER_PID:-} ]] && kill -0 -- "-$SCOUT_SERVER_PID" 2>/dev/null; then
        server_stopped=false
    fi
    SCOUT_SERVER_PID=''
    local case_term=false case_kill=false
    [[ -e "$CASE_A_TERM_MARKER" ]] && case_term=true
    [[ -e "$CASE_A_KILL_MARKER" ]] && case_kill=true
    "$SCOUT_LAB_PYTHON" "$CASE_A_HPC_DIR/case_a_batch.py" cleanup \
        --output "$SCOUT_RUN_DIR/case-a-cleanup.json" \
        --server-pid "$recorded_server_pid" --term-sent "$server_term" \
        --kill-sent "$server_kill" --stopped "$server_stopped" \
        --case-pid "$CASE_A_LAUNCHED_PID" --case-term-sent "$case_term" \
        --case-kill-sent "$case_kill" --case-stopped "$CASE_A_PROCESS_STOPPED" \
        --job-id "$SLURM_JOB_ID" || true
}

CASE_A_FINALIZE_STATUS=1
finalize_terminal() {
    [[ -e "$SCOUT_RUN_DIR/case-a-phase.json" ]] || return 0
    [[ -e "$SCOUT_RUN_DIR/case-a-batch-summary.json" ]] && return
    set +e
    "$SCOUT_LAB_PYTHON" "$CASE_A_HPC_DIR/case_a_batch.py" finalize \
        --output "$SCOUT_RUN_DIR/case-a-batch-summary.json" \
        --phase-path "$SCOUT_RUN_DIR/case-a-phase.json" \
        --pre-smoke-path "$SCOUT_CASE_A_PRE_SMOKE" \
        --runner-path "$SCOUT_CASE_A_RUNNER" \
        --preflight-path "$SCOUT_RUN_DIR/preflight.json" \
        --smoke-path "$SCOUT_RUN_DIR/smoke.json" \
        --native-path "$SCOUT_RUN_DIR/native-smoke.json" \
        --case-summary-path "$SCOUT_CASE_A_DIR/case-summary.json" \
        --case-plan-path "$SCOUT_CASE_A_DIR/plan.json" \
        --execution-path "$SCOUT_CASE_A_DIR/execution.json" \
        --wrapper-exit-path "$SCOUT_RUN_DIR/case-a-wrapper-exit-code.txt" \
        --server-check-path "$SCOUT_RUN_DIR/case-a-server-check.json" \
        --cleanup-path "$SCOUT_RUN_DIR/case-a-cleanup.json"
    CASE_A_FINALIZE_STATUS=$?
    set -e
}

case_batch_cleanup() {
    local status=$?
    trap - EXIT TERM INT
    if [[ -n "$CASE_A_WATCHDOG_PID" ]]; then
        kill "$CASE_A_WATCHDOG_PID" 2>/dev/null || true
        wait "$CASE_A_WATCHDOG_PID" 2>/dev/null || true
    fi
    stop_case_process
    if [[ -e "$SCOUT_RUN_DIR/case-a-phase.json" && ! -e "$SCOUT_RUN_DIR/case-a-wrapper-exit-code.txt" ]]; then
        printf '%s\n' "$status" > "$SCOUT_RUN_DIR/case-a-wrapper-exit-code.txt"
    fi
    stop_server_and_record
    finalize_terminal
    printf '%s\n' "$status" > "$SCOUT_RUN_DIR/job-exit-code.txt"
    unset LOCAL_LLM_API_KEY APPTAINERENV_VLLM_API_KEY
    exit "$status"
}
trap case_batch_cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

sha256sum "$CASE_A_HPC_DIR/scout-smoke-case-a.sbatch" \
    "$CASE_A_HPC_DIR/scout-smoke.sbatch" "$CASE_A_HPC_DIR/case_a_batch.py" \
    "$CASE_A_HPC_DIR/preflight.py" "$CASE_A_HPC_DIR/smoke.py" \
    "$CASE_A_HPC_DIR/native_smoke.py" "$SCOUT_CASE_A_RUNNER" \
    > "$SCOUT_RUN_DIR/case-a-wrapper-sha256.txt"

# Query the scheduler's current-job record after both smoke phases. Missing,
# malformed, mismatched, over-2h, or <3900s evidence leaves Case A unstarted.
SCOUT_TIME_RECORD=''
if command -v squeue >/dev/null; then
    SCOUT_TIME_RECORD=$(squeue -h -j "$SLURM_JOB_ID" -o '%i|%L|%l' 2>/dev/null) || SCOUT_TIME_RECORD=''
fi
REPORTED_JOB_ID=''
REMAINING_TIME=''
TIME_LIMIT=''
if [[ "$SCOUT_TIME_RECORD" != *$'\n'* ]]; then
    IFS='|' read -r REPORTED_JOB_ID REMAINING_TIME TIME_LIMIT <<< "$SCOUT_TIME_RECORD"
fi

set +e
"$SCOUT_LAB_PYTHON" "$CASE_A_HPC_DIR/case_a_batch.py" reserve \
    --output "$SCOUT_RUN_DIR/case-a-phase.json" \
    --job-id "$SLURM_JOB_ID" --reported-job-id "$REPORTED_JOB_ID" \
    --remaining "$REMAINING_TIME" --time-limit "$TIME_LIMIT" \
    --case-dir "$SCOUT_CASE_A_DIR" \
    --pre-smoke-path "$SCOUT_CASE_A_PRE_SMOKE" \
    --runner-path "$SCOUT_CASE_A_RUNNER" \
    --helper-path "$CASE_A_HPC_DIR/scout-smoke-case-a.sbatch" \
    --helper-path "$CASE_A_HPC_DIR/scout-smoke.sbatch" \
    --helper-path "$CASE_A_HPC_DIR/case_a_batch.py" \
    --helper-path "$CASE_A_HPC_DIR/preflight.py" \
    --helper-path "$CASE_A_HPC_DIR/smoke.py" \
    --helper-path "$CASE_A_HPC_DIR/native_smoke.py" \
    --helper-path "$SCOUT_CASE_A_RUNNER"
CASE_A_GATE_STATUS=$?
set -e
if [[ "$CASE_A_GATE_STATUS" == 3 ]]; then
    printf '%s\n' 3 > "$SCOUT_RUN_DIR/case-a-wrapper-exit-code.txt"
    stop_server_and_record
    finalize_terminal
    exit 3
fi
[[ "$CASE_A_GATE_STATUS" == 0 ]] || exit "$CASE_A_GATE_STATUS"

# The envelope exists before Case A inference. Recheck the exact authenticated
# loopback server immediately before launching the bounded process group.
"$SCOUT_LAB_PYTHON" "$CASE_A_HPC_DIR/case_a_batch.py" server-check \
    --output "$SCOUT_RUN_DIR/case-a-server-check.json" \
    --base-url "http://127.0.0.1:$SCOUT_PORT/v1" --server-pid "$SCOUT_SERVER_PID" \
    --job-id "$SLURM_JOB_ID"

set +e
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    setsid "$SCOUT_LAB_PYTHON" "$SCOUT_CASE_A_RUNNER" run "$SCOUT_CASE_A_DIR" \
    --serving-receipt "$SCOUT_RUN_DIR/preflight.json" \
    > "$SCOUT_RUN_DIR/case-a-wrapper.log" 2>&1 &
CASE_A_PROCESS_PID=$!
CASE_A_LAUNCHED_PID=$CASE_A_PROCESS_PID
(
    sleep 3600
    if kill -TERM -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
        : > "$CASE_A_TERM_MARKER"
        sleep 10
        if kill -KILL -- "-$CASE_A_PROCESS_PID" 2>/dev/null; then
            : > "$CASE_A_KILL_MARKER"
        fi
    fi
) &
CASE_A_WATCHDOG_PID=$!
wait "$CASE_A_PROCESS_PID"
CASE_A_WRAPPER_STATUS=$?
kill "$CASE_A_WATCHDOG_PID" 2>/dev/null || true
wait "$CASE_A_WATCHDOG_PID" 2>/dev/null || true
CASE_A_WATCHDOG_PID=''
stop_case_process
set -e
printf '%s\n' "$CASE_A_WRAPPER_STATUS" > "$SCOUT_RUN_DIR/case-a-wrapper-exit-code.txt"

# Cleanup is terminal infrastructure evidence. Scientific outcomes stay in the
# Case A summary and paired report, independent of wrapper and job exit codes.
stop_server_and_record
finalize_terminal
[[ "$CASE_A_WRAPPER_STATUS" == 0 ]] || exit "$CASE_A_WRAPPER_STATUS"
exit "$CASE_A_FINALIZE_STATUS"
