import subprocess
import toml
import re
import os
import time
import json
import bittensor as bt

MAX_DAYS = 120
MAX_SIGNALS = 256
MERKLE_DEPTH = 8
SCALING_FACTOR = 10**7
RATIO_SCALE_FACTOR = 1_000_000
PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617


def log_verbose(verbose, level, message):
    if verbose:
        getattr(bt.logging, level)(message)


def get_attr(obj, attr):
    """Get attribute from object or dictionary"""
    return getattr(obj, attr) if hasattr(obj, attr) else obj[attr]


def run_command(command, cwd):
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        bt.logging.error(f"Command failed: {' '.join(command)}")
        bt.logging.error(f"stdout: {result.stdout}")
        bt.logging.error(f"stderr: {result.stderr}")
        raise RuntimeError(
            f"Command {' '.join(command)} failed with exit code {result.returncode}"
        )
    return result.stdout


def parse_circuit_output(output):
    if "[" in output and "]" in output and "MerkleTree" not in output:
        array_matches = re.findall(r"\[([^\]]+)\]", output)
        if array_matches:
            array_content = array_matches[-1]
            values = []
            for item in array_content.split(","):
                item = item.strip()
                if item.startswith("0x"):
                    try:
                        values.append(str(int(item, 16)))
                    except ValueError:
                        continue
                elif item.lstrip("-").isdigit():
                    values.append(item)
            if values:
                return values

    struct_start = output.find("{")
    struct_end = output.rfind("}")

    if struct_start == -1 or struct_end == -1:
        return re.findall(r"Field\(([-0-9]+)\)", output)

    struct_content = output[struct_start : struct_end + 1]

    if "MerkleTree" in output:
        tree = {}
        if "path_elements:" in struct_content:
            start = struct_content.find("path_elements:") + len("path_elements:")
            end = struct_content.find(", path_indices:")
            path_elem_section = struct_content[start:end].strip()
            tree["path_elements"] = parse_nested_arrays(path_elem_section)

        if "path_indices:" in struct_content:
            start = struct_content.find("path_indices:") + len("path_indices:")
            end = struct_content.find(", root:")
            path_idx_section = struct_content[start:end].strip()
            tree["path_indices"] = parse_nested_arrays(path_idx_section)

        if "root:" in struct_content:
            start = struct_content.find("root:") + len("root:")
            root_section = struct_content[start:].strip().rstrip("}")
            tree["root"] = root_section.strip()

        return tree

    values = []
    parts = re.split(r"[,\s]+", struct_content)
    for part in parts:
        part = part.strip("{}[](), \t\n\r")
        if not part:
            continue
        if part.startswith("0x") and len(part) > 2:
            try:
                values.append(str(int(part, 16)))
                continue
            except ValueError:
                pass
        if part.lstrip("-").isdigit():
            values.append(part)

    return values


def parse_nested_arrays(section):
    if not section.strip().startswith("["):
        return []

    arrays = []
    depth = 0
    current_array = ""

    for char in section:
        if char == "[":
            depth += 1
            if depth == 2:
                current_array = ""
            elif depth == 1:
                continue
        elif char == "]":
            depth -= 1
            if depth == 1:
                if current_array.strip():
                    arrays.append(
                        [x.strip() for x in current_array.split(",") if x.strip()]
                    )
                current_array = ""
            elif depth == 0:
                break
        elif depth == 2:
            current_array += char

    return arrays


def field_to_toml_value(f):
    return str(f + PRIME) if f < 0 else str(f)


def field_to_signed_int(field_str):
    val = int(field_str, 16) if field_str.startswith("0x") else int(field_str)
    return val - 2**64 if val >= 2**63 else val


def generate_bb_proof(circuit_dir):
    try:
        subprocess.run(["bb", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        bt.logging.error(
            "bb (Barretenberg) not found. Install with: curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/master/barretenberg/cpp/installation/install | bash"
        )
        return None, False

    target_dir = os.path.join(circuit_dir, "target")
    proof_dir = os.path.join(circuit_dir, "proof")
    os.makedirs(proof_dir, exist_ok=True)

    witness_file = os.path.join(target_dir, "witness.gz")
    circuit_file = os.path.join(target_dir, "circuits.json")

    prove_start = time.time()
    prove_result = subprocess.run(
        ["bb", "prove", "-b", circuit_file, "-w", witness_file, "-o", proof_dir],
        capture_output=True,
        text=True,
        cwd=circuit_dir,
    )
    prove_time = time.time() - prove_start

    if prove_result.returncode != 0:
        bt.logging.error(f"bb prove failed: {prove_result.stderr}")
        return None, False

    return prove_time, True


def generate_proof(
    data=None,
    miner_hotkey=None,
    verbose=None,
    annual_risk_free_percentage=4.19,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    witness_only=False,
    account_size=None,
):
    is_demo_mode = data is None
    if verbose is None:
        verbose = is_demo_mode

    log_verbose(
        verbose,
        "info",
        f"generate_proof called with miner_hotkey={miner_hotkey[:8] if miner_hotkey else None}",
    )
    log_verbose(
        verbose,
        "info",
        f"Mode: {'Demo' if is_demo_mode else 'Production'}, verbose={verbose}",
    )

    try:
        if data is None:
            log_verbose(
                verbose, "info", "Loading data from validator_checkpoint.json..."
            )
            with open("validator_checkpoint.json", "r") as f:
                data = json.load(f)
    except Exception as e:
        bt.logging.error(f"Failed to load data {e}")

    if miner_hotkey is None:
        miner_hotkey = list(data["perf_ledgers"].keys())[0]
        log_verbose(
            verbose,
            "info",
            f"No hotkey specified, using first available: {miner_hotkey}",
        )
    else:
        log_verbose(verbose, "info", f"Using specified hotkey: {miner_hotkey}")

    if miner_hotkey not in data["perf_ledgers"]:
        raise ValueError(
            f"Hotkey '{miner_hotkey}' not found in data. Available: {list(data['perf_ledgers'].keys())}"
        )

    positions = data["positions"][miner_hotkey]["positions"]
    log_verbose(verbose, "info", "Preparing circuit inputs...")

    # Use daily returns calculated by PTN
    daily_log_returns = data.get("daily_returns", [])
    n_returns = len(daily_log_returns)

    if n_returns > MAX_DAYS:
        log_verbose(
            verbose,
            "warning",
            f"Truncating {n_returns} daily returns to {MAX_DAYS} (circuit limit)",
        )
        daily_log_returns = daily_log_returns[:MAX_DAYS]
        n_returns = MAX_DAYS

    # Scale log returns for the circuit
    scaled_log_returns = [int(ret * SCALING_FACTOR) for ret in daily_log_returns]

    # Pad to MAX_DAYS
    scaled_log_returns += [0] * (MAX_DAYS - len(scaled_log_returns))

    log_verbose(verbose, "info", f"Using {n_returns} daily returns from PTN")

    all_orders = []
    for pos in positions:
        all_orders.extend(get_attr(pos, "orders"))

    signals_count = len(all_orders)
    if signals_count > MAX_SIGNALS:
        log_verbose(
            verbose,
            "warning",
            f"Truncating {signals_count} signals to {MAX_SIGNALS} (circuit limit)",
        )
        all_orders = all_orders[:MAX_SIGNALS]
        signals_count = MAX_SIGNALS

    trade_pair_map = {}
    trade_pair_counter = 0

    signals = []
    for order in all_orders:
        trade_pair = get_attr(order, "trade_pair")
        trade_pair_str = (
            str(trade_pair).split(".")[1]
            if hasattr(trade_pair, "name")
            else str(trade_pair)
        )
        if trade_pair_str not in trade_pair_map:
            trade_pair_map[trade_pair_str] = trade_pair_counter
            trade_pair_counter += 1

        order_type = get_attr(order, "order_type")
        order_type_str = (
            str(order_type).split(".")[1]
            if hasattr(order_type, "name")
            else str(order_type)
        )
        order_type_map = {"SHORT": 2, "LONG": 1, "FLAT": 0}
        price = int(get_attr(order, "price") * SCALING_FACTOR)
        order_uuid = get_attr(order, "order_uuid")
        bid = int(get_attr(order, "bid") * SCALING_FACTOR)
        ask = int(get_attr(order, "ask") * SCALING_FACTOR)
        processed_ms = get_attr(order, "processed_ms")

        signals.append(
            {
                "trade_pair": str(trade_pair_map[trade_pair_str]),
                "order_type": str(order_type_map.get(order_type_str, 0)),
                "leverage": str(int(abs(get_attr(order, "leverage")) * SCALING_FACTOR)),
                "price": str(price),
                "processed_ms": str(processed_ms),
                "order_uuid": f"0x{order_uuid.replace('-', '')}",
                "bid": str(bid),
                "ask": str(ask),
            }
        )

    # Pad signals too
    signals += [
        {
            "trade_pair": "0",
            "order_type": "0",
            "leverage": "0",
            "price": "0",
            "processed_ms": "0",
            "order_uuid": "0x0",
            "bid": "0",
            "ask": "0",
        }
    ] * (MAX_SIGNALS - len(signals))

    log_verbose(
        verbose,
        "info",
        f"Prepared {n_returns} daily returns and {signals_count} signals for circuit",
    )

    if verbose:
        bt.logging.info(f"Circuit daily returns count: {n_returns}")
        bt.logging.info("Sample daily returns:")
        for i in range(min(5, n_returns)):
            bt.logging.info(
                f"  [{i}] return={daily_log_returns[i]:.6f} (scaled={scaled_log_returns[i]})"
            )
        if daily_log_returns:
            mean_return = sum(daily_log_returns) / len(daily_log_returns)
            bt.logging.info(f"Mean daily return: {mean_return:.6f}, count={n_returns}")
        bt.logging.info(f"Circuit Config: MAX_DAYS={MAX_DAYS}, DAILY_CHECKPOINTS=2")

    log_verbose(verbose, "info", "Running tree_generator circuit...")
    bt.logging.info(f"Generating tree for hotkey {miner_hotkey[:8]}...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tree_generator_dir = os.path.join(current_dir, "tree_generator")

    tree_prover_input = {"signals": signals, "actual_len": str(signals_count)}
    os.makedirs(tree_generator_dir, exist_ok=True)
    with open(os.path.join(tree_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(tree_prover_input, f)

    output = run_command(
        ["nargo", "execute", "--silence-warnings"],
        tree_generator_dir,
    )

    tree = parse_circuit_output(output)
    try:
        path_elements = tree["path_elements"]
        path_indices = tree["path_indices"]
        signals_merkle_root = tree["root"]
    except Exception:
        raise RuntimeError(
            "Unexpected tree_generator output structure, expected MerkleTree dict with leaf_hashes, path_elements, path_indices, and root"
        )

    log_verbose(
        verbose, "info", f"Generated signals Merkle root: {signals_merkle_root}"
    )
    log_verbose(
        verbose, "info", "Returns Merkle root will be calculated within circuit"
    )
    log_verbose(verbose, "info", f"Number of daily returns: {n_returns}")
    log_verbose(verbose, "info", "Running main proof of portfolio circuit...")
    bt.logging.info(f"Generating witness for hotkey {miner_hotkey[:8]}...")
    main_circuit_dir = os.path.join(current_dir, "circuits")

    # Pass annual risk-free rate (to match ann_excess_return usage)
    annual_risk_free_decimal = annual_risk_free_percentage / 100
    risk_free_rate_scaled = int(annual_risk_free_decimal * SCALING_FACTOR)

    # Finally, LFG
    main_prover_input = {
        "log_returns": [str(r) for r in scaled_log_returns],
        "n_returns": str(n_returns),
        "signals": signals,
        "signals_count": str(signals_count),
        "path_elements": [
            [
                field_to_toml_value(
                    int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                )
                for x in p
            ]
            for p in path_elements
        ],
        "path_indices": [
            [
                int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                for x in p
            ]
            for p in path_indices
        ],
        "signals_merkle_root": (
            signals_merkle_root
            if isinstance(signals_merkle_root, str)
            else str(signals_merkle_root)
        ),
        "risk_free_rate": str(risk_free_rate_scaled),
        "use_weighting": str(int(use_weighting)),
        "bypass_confidence": str(int(bypass_confidence)),
        "account_size": str(account_size if account_size is not None else 1000000),
    }

    os.makedirs(main_circuit_dir, exist_ok=True)
    with open(os.path.join(main_circuit_dir, "Prover.toml"), "w") as f:
        toml.dump(main_prover_input, f)

    log_verbose(verbose, "info", "Executing main circuit to generate witness...")
    witness_start = time.time()
    output = run_command(
        ["nargo", "execute", "witness", "--silence-warnings"], main_circuit_dir
    )
    witness_time = time.time() - witness_start
    log_verbose(verbose, "info", f"Witness generation completed in {witness_time:.3f}s")

    fields = parse_circuit_output(output)
    log_verbose(verbose, "info", f"Circuit output: {output}")
    log_verbose(verbose, "info", f"Parsed fields: {fields}")
    if len(fields) < 9:
        raise RuntimeError(
            f"Expected 9 output fields from main circuit, got {len(fields)}: {fields}"
        )

    avg_daily_pnl_raw = fields[0]
    sharpe_raw = fields[1]
    drawdown_raw = fields[2]
    calmar_raw = fields[3]
    omega_raw = fields[4]
    sortino_raw = fields[5]
    stat_confidence_raw = fields[6]
    pnl_score_raw = fields[7]
    returns_merkle_root_raw = fields[8]

    def field_to_signed_int(field_str):
        if isinstance(field_str, str) and field_str.startswith("0x"):
            val = int(field_str, 16)
        else:
            val = int(field_str)

        # Noir's i64 as u64 casting uses standard two's complement
        # Convert from u64 back to i64 using two's complement
        if val >= 2**63:  # If the high bit is set, it's negative
            return val - 2**64  # Convert from unsigned to signed
        else:
            return val  # Positive values unchanged

    avg_daily_pnl_value = field_to_signed_int(avg_daily_pnl_raw)
    sharpe_ratio_raw = field_to_signed_int(sharpe_raw)
    max_drawdown_raw = field_to_signed_int(drawdown_raw)
    calmar_ratio_raw = field_to_signed_int(calmar_raw)
    omega_ratio_raw = field_to_signed_int(omega_raw)
    sortino_ratio_raw = field_to_signed_int(sortino_raw)
    stat_confidence_raw = field_to_signed_int(stat_confidence_raw)
    pnl_score_value = field_to_signed_int(pnl_score_raw)

    # Process returns merkle root (it's a Field, not signed)
    if isinstance(returns_merkle_root_raw, str) and returns_merkle_root_raw.startswith(
        "0x"
    ):
        returns_merkle_root = returns_merkle_root_raw
    else:
        returns_merkle_root = f"0x{int(returns_merkle_root_raw):x}"

    RATIO_SCALE_FACTOR = 1_000_000

    avg_daily_pnl_scaled = avg_daily_pnl_value / SCALING_FACTOR
    avg_daily_pnl_ptn_scaled = avg_daily_pnl_scaled * 365 * 100
    sharpe_ratio_scaled = sharpe_ratio_raw / RATIO_SCALE_FACTOR
    max_drawdown_scaled = max_drawdown_raw / SCALING_FACTOR
    calmar_ratio_scaled = calmar_ratio_raw / RATIO_SCALE_FACTOR
    omega_ratio_scaled = omega_ratio_raw / RATIO_SCALE_FACTOR
    sortino_ratio_scaled = sortino_ratio_raw / RATIO_SCALE_FACTOR
    stat_confidence_scaled = stat_confidence_raw / RATIO_SCALE_FACTOR
    pnl_score_scaled = (
        pnl_score_value  # PnL is already in USD, don't divide by SCALING_FACTOR
    )

    if witness_only:
        prove_time, proving_success = None, True
        log_verbose(
            verbose,
            "info",
            "Skipping barretenberg proof generation (witness_only=True)",
        )
    else:
        try:
            prove_time, proving_success = generate_bb_proof(main_circuit_dir)
            if prove_time is None:
                bt.logging.error("Barretenberg proof generation failed")
                prove_time, proving_success = None, False
        except Exception as e:
            bt.logging.error(f"Exception during proof generation: {e}")
            prove_time, proving_success = None, False

    # Always print key production info: hotkey and verification status
    bt.logging.info(f"Hotkey: {miner_hotkey}")
    bt.logging.info(f"Orders processed: {signals_count}")
    bt.logging.info(f"Signals Merkle Root: {signals_merkle_root}")
    bt.logging.info(f"Returns Merkle Root: {returns_merkle_root}")
    bt.logging.info(f"Average Daily PnL: {avg_daily_pnl_scaled:.9f}")
    bt.logging.info(f"Sharpe Ratio: {sharpe_ratio_scaled:.9f}")
    # Convert drawdown factor to percentage: drawdown% = (1 - factor) * 100
    drawdown_percentage = (1 - max_drawdown_scaled) * 100
    bt.logging.info(
        f"Max Drawdown: {max_drawdown_scaled:.9f} ({drawdown_percentage:.6f}%)"
    )
    bt.logging.info(f"Calmar Ratio: {calmar_ratio_scaled:.9f}")
    bt.logging.info(f"Omega Ratio: {omega_ratio_scaled:.9f}")
    bt.logging.info(f"Sortino Ratio: {sortino_ratio_scaled:.9f}")
    bt.logging.info(f"Statistical Confidence: {stat_confidence_scaled:.9f}")
    bt.logging.info(f"PnL Score: {pnl_score_scaled:.9f}")

    if verbose:
        bt.logging.info("\n--- Proof Generation Complete ---")
        bt.logging.info("\n=== MERKLE ROOTS ===")
        bt.logging.info(f"Signals Merkle Root: {signals_merkle_root}")
        bt.logging.info(f"Returns Merkle Root: {returns_merkle_root}")

        bt.logging.info("\n=== DATA SUMMARY ===")
        bt.logging.info(f"Daily returns processed: {n_returns}")
        bt.logging.info(f"Trading signals processed: {signals_count}")
        bt.logging.info("PnL calculated from cumulative returns in circuit")

        bt.logging.info("\n=== PROOF GENERATION RESULTS ===")
        bt.logging.info(f"Witness generation time: {witness_time:.3f}s")
        if not witness_only:
            if prove_time is not None:
                bt.logging.info(f"Proof generation time: {prove_time:.3f}s")
            else:
                bt.logging.info("Unable to prove due to an error.")

    # Return structured results for programmatic access
    return {
        "merkle_roots": {
            "signals": signals_merkle_root,
            "returns": returns_merkle_root,
        },
        "portfolio_metrics": {
            "avg_daily_pnl_raw": avg_daily_pnl_value,
            "avg_daily_pnl_scaled": avg_daily_pnl_scaled,
            "avg_daily_pnl_ptn_scaled": avg_daily_pnl_ptn_scaled,
            "sharpe_ratio_raw": sharpe_ratio_raw,
            "sharpe_ratio_scaled": sharpe_ratio_scaled,
            "max_drawdown_raw": max_drawdown_raw,
            "max_drawdown_scaled": max_drawdown_scaled,
            "max_drawdown_percentage": (1 - max_drawdown_scaled) * 100,
            "calmar_ratio_raw": calmar_ratio_raw,
            "calmar_ratio_scaled": calmar_ratio_scaled,
            "omega_ratio_raw": omega_ratio_raw,
            "omega_ratio_scaled": omega_ratio_scaled,
            "sortino_ratio_raw": sortino_ratio_raw,
            "sortino_ratio_scaled": sortino_ratio_scaled,
            "stat_confidence_raw": stat_confidence_raw,
            "stat_confidence_scaled": stat_confidence_scaled,
            "pnl_score_raw": pnl_score_value,
            "pnl_score_scaled": pnl_score_scaled,
        },
        "data_summary": {
            "daily_returns_processed": n_returns,
            "signals_processed": signals_count,
            "returns_processed": n_returns,
        },
        "proof_results": {
            "witness_generation_time": witness_time,
            "proof_generation_time": prove_time,
            "proving_success": proving_success,
            "proof_generated": prove_time is not None or witness_only,
        },
    }
