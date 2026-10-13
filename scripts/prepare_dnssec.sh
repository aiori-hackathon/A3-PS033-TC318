#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DNS_DIR="$ROOT/config/dns"
cd "$DNS_DIR"

if ! command -v dnssec-keygen >/dev/null 2>&1 || ! command -v dnssec-signzone >/dev/null 2>&1; then
  cat >&2 <<'MSG'
BIND DNSSEC tools (dnssec-keygen and dnssec-signzone) are required.
On Debian/Ubuntu install: sudo apt-get install bind9-utils
Then rerun: ./scripts/prepare_dnssec.sh
No DNSSEC validation has been bypassed; this setup step cannot be skipped.
MSG
  exit 2
fi

if ! compgen -G 'Kps033.test.+013+*.key' >/dev/null; then
  dnssec-keygen -a ECDSAP256SHA256 -n ZONE -f KSK ps033.test >/dev/null
  dnssec-keygen -a ECDSAP256SHA256 -n ZONE ps033.test >/dev/null
fi

dnssec-signzone -S -o ps033.test -f ps033.test.signed ps033.test.zone
KSK_PUBLIC="$(grep -l 'DNSKEY 257 ' Kps033.test.+013+*.key | head -n 1)"
if [[ -z "$KSK_PUBLIC" ]]; then
  echo "Could not find generated KSK public DNSKEY" >&2
  exit 3
fi
cp "$KSK_PUBLIC" ps033-trust-anchor.key
chmod 644 ps033-trust-anchor.key ps033.test.signed
printf '\nDNSSEC zone generated: %s\nTrust anchor: %s\n' "$DNS_DIR/ps033.test.signed" "$DNS_DIR/ps033-trust-anchor.key"
printf 'Keep the private K*.private files secret; they are ignored by git.\n'
