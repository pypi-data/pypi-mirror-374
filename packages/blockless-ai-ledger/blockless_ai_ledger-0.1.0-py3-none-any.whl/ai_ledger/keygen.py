"""
Key generation utility for AI Ledger validators.

Creates cryptographic keypairs and validator configurations.
"""

import json
import typer
from pathlib import Path
from colorama import init, Fore

from . import crypto
from . import params

init(autoreset=True)

app = typer.Typer()


@app.command()
def generate(
    count: int = typer.Option(params.N_VALIDATORS, "--count", "-c", help="Number of validators to generate"),
    output_dir: str = typer.Option("keys", "--output-dir", "-o", help="Output directory"),
    format_type: str = typer.Option("json", "--format", "-f", help="Output format (json)")
):
    """Generate validator keypairs and configuration."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"{Fore.CYAN}Generating {count} validator keypairs...")
    
    validators = []
    
    for i in range(count):
        # Generate keypair
        privkey, pubkey = crypto.generate_keypair()
        validator_id = crypto.create_validator_id(pubkey)
        
        validator_data = {
            "id": validator_id,
            "pubkey_hex": pubkey.hex(),
            "privkey_hex": privkey.hex(),
            "is_active": True,
            "reputation": params.INITIAL_VALIDATOR_REPUTATION
        }
        
        validators.append(validator_data)
        
        print(f"  {Fore.GREEN}Validator {i+1}: {validator_id[:8]}...")
    
    # Save to file
    validators_file = output_path / "validators.json"
    with open(validators_file, 'w') as f:
        json.dump({
            "schema_version": params.SCHEMA_VERSION,
            "validators": validators,
            "generated_at": crypto.generate_secure_nonce()  # Timestamp equivalent
        }, f, indent=2)
    
    print(f"\n{Fore.GREEN}✓ Saved {count} validators to {validators_file}")
    
    # Also create individual files for production use
    for i, validator in enumerate(validators):
        individual_file = output_path / f"validator_{i+1}.json"
        with open(individual_file, 'w') as f:
            json.dump(validator, f, indent=2)
    
    print(f"{Fore.GREEN}✓ Individual validator files created")
    print(f"\n{Fore.YELLOW}Security Note: Private keys are included in these files.")
    print(f"In production, distribute only public keys and keep private keys secure.")


@app.command()
def verify(
    validators_file: str = typer.Option("keys/validators.json", "--file", "-f", help="Validators file to verify")
):
    """Verify validator keypairs and signatures."""
    
    try:
        with open(validators_file, 'r') as f:
            data = json.load(f)
        
        validators = data.get("validators", [])
        print(f"{Fore.CYAN}Verifying {len(validators)} validators...")
        
        valid_count = 0
        
        for i, validator in enumerate(validators):
            validator_id = validator["id"]
            pubkey_hex = validator["pubkey_hex"]
            privkey_hex = validator.get("privkey_hex")
            
            # Verify ID matches public key
            pubkey = bytes.fromhex(pubkey_hex)
            expected_id = crypto.create_validator_id(pubkey)
            
            if validator_id != expected_id:
                print(f"  {Fore.RED}✗ Validator {i+1}: ID mismatch")
                continue
            
            # Test signature if private key available
            if privkey_hex:
                try:
                    privkey = bytes.fromhex(privkey_hex)
                    
                    # Create test signature
                    test_message = {"test": "message", "validator": validator_id}
                    signature = crypto.sign_message(test_message, privkey)
                    
                    # Verify signature
                    if crypto.verify_signature(signature, test_message, pubkey):
                        print(f"  {Fore.GREEN}✓ Validator {i+1}: {validator_id[:8]}... (keypair valid)")
                        valid_count += 1
                    else:
                        print(f"  {Fore.RED}✗ Validator {i+1}: Signature verification failed")
                except Exception as e:
                    print(f"  {Fore.RED}✗ Validator {i+1}: Signature test failed - {e}")
            else:
                print(f"  {Fore.YELLOW}? Validator {i+1}: {validator_id[:8]}... (no private key)")
                valid_count += 1
        
        print(f"\n{Fore.GREEN}✓ {valid_count}/{len(validators)} validators verified")
        
    except FileNotFoundError:
        print(f"{Fore.RED}Validators file not found: {validators_file}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"{Fore.RED}Verification failed: {e}")
        raise typer.Exit(1)


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()