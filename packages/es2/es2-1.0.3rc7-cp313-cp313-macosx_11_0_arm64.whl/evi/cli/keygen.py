import argparse
import sys
from pathlib import Path

import evi


def ensure_dir_empty(path_str: str) -> None:
    p = Path(path_str).expanduser().resolve()

    if p.exists() and p.is_file():
        print(f"[ERROR] '{p}' is file. This should be directory.")
        sys.exit(1)

    if p.exists() and any(p.iterdir()):
        print(f"[ERROR] '{p}' directory is NOT empty. Key generation canceled.")
        sys.exit(1)


def ensure_kek_loaded(args, parser) -> evi.SealInfo:
    if args.seal_mode == "none":
        return evi.SealInfo(evi.SealMode.NONE)
    elif args.seal_mode != "aes":
        raise ValueError(f"Invalid seal mode: {args.seal_mode}. Choose from 'none' or 'aes'.")

    if args.seal_key_path:
        with open(args.seal_key_path, "rb") as f:
            kek_bytes = f.read()
    else:
        if not args.seal_key_stdin:
            parser.error(
                "--seal_mode aes requires --seal_key_stdin (read KEK from stdin) or --seal_key_path (read KEK from file)."
            )

        if sys.stdin.isatty():
            print("Enter AES KEK (32 bytes):", file=sys.stderr)
        kek_bytes = sys.stdin.buffer.read(32)

    if len(kek_bytes) < 32:
        raise ValueError(f"KEK must be 32 bytes, got {len(kek_bytes)} bytes.")
    if len(kek_bytes) > 32:
        print("[WARN] KEK longer than 32 bytes; only the first 32 bytes will be used.", file=sys.stderr)
        kek_bytes = kek_bytes[:32]

    return evi.SealInfo(evi.SealMode.AES_KEK, kek_bytes)


def string_to_preset(preset: str) -> evi.ParameterPreset:
    if preset == "runtime":
        return evi.ParameterPreset.RUNTIME
    elif preset == "ip0" or preset == "ip":
        return evi.ParameterPreset.IP0
    elif preset == "qf0" or preset == "qf":
        return evi.ParameterPreset.QF0
    elif preset == "qf1":
        return evi.ParameterPreset.QF1
    elif preset == "qf2":
        return evi.ParameterPreset.QF2
    elif preset == "qf3":
        return evi.ParameterPreset.QF3
    else:
        raise ValueError(f"Invalid preset: {preset}. Choose from 'runtime', 'ip0', 'qf0', 'qf1', 'qf2', or 'qf3'.")


def string_to_eval_mode(eval_mode: str) -> evi.EvalMode:
    if eval_mode == "none":
        return evi.EvalMode.NONE
    elif eval_mode == "rmp":
        return evi.EvalMode.RMP
    else:
        raise ValueError(f"Invalid evaluation mode: {eval_mode}. Choose from 'none' or 'rmp'.")


def generate_key(dim_list, outdir, seal_info, preset, eval_mode):
    converted_preset = string_to_preset(preset)
    converted_eval_mode = string_to_eval_mode(eval_mode)
    contexts = [evi.make_context(converted_preset, evi.DeviceType.CPU, d, converted_eval_mode) for d in dim_list]
    keygen = evi.MultiKeyGenerator(contexts, outdir, seal_info)

    print("Generating key...")
    keygen.generate_keys()

    print("Key generated with")
    print(f"  Dim: {dim_list}")
    print(f"  Preset: {preset}")
    print(f"  Seal Mode: {seal_info.sMode.name}")
    print(f"  Path: {outdir}")


def main():
    parser = argparse.ArgumentParser(description="Generate a key for the ES2 API.")
    parser.add_argument(
        "--dim",
        type=int,
        nargs="+",
        default=[32, 64, 128, 256, 512, 1024, 2048, 4096],
        help="Dimension(s) of the key (default: All). You can specify multiple values, e.g., --dim 512 1024",
    )
    parser.add_argument(
        "--key_path", type=str, default="./keys", help="Output directory for the key (default: './keys')"
    )
    parser.add_argument("--key_id", type=str, default=None, help="Key ID for the key (default: None)")
    parser.add_argument(
        "--seal_mode",
        type=str,
        default="none",
        choices=["none", "aes"],
        help="Sealing mode for the key (default: 'none')",
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="ip",
        choices=["runtime", "ip", "ip0", "qf", "qf0", "qf1", "qf2", "qf3"],
        help="Parameter preset for the key (default: 'ip')",
    )
    parser.add_argument(
        "--eval_mode",
        type=str,
        default="none",
        choices=["none", "rmp"],
        help="Evaluation mode for the key (default: 'none')",
    )
    parser.add_argument(
        "--seal_key_path",
        type=str,
        help="When using --seal_mode aes, read KEK from file.",
    )
    parser.add_argument(
        "--seal_key_stdin",
        action="store_true",
        help="When using --seal_mode aes, read KEK from standard input (must be exactly 32 bytes).",
    )

    args = parser.parse_args()
    outdir = args.key_path + "/" + args.key_id if args.key_id else args.key_path

    ensure_dir_empty(outdir)
    s_info = ensure_kek_loaded(args, parser)
    generate_key(args.dim, outdir, s_info, args.preset, args.eval_mode)


if __name__ == "__main__":
    main()
