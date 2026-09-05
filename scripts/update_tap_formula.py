import hashlib
import sys
import urllib.request
from pathlib import Path

REPOSITORY = "Sergio-prog/fram"
TEMPLATE = Path(__file__).resolve().parents[1] / "packaging" / "homebrew" / "fram.rb.tmpl"


def main() -> None:
    version, out_path = sys.argv[1], Path(sys.argv[2])
    url = f"https://github.com/{REPOSITORY}/archive/refs/tags/v{version}.tar.gz"
    with urllib.request.urlopen(url) as resp:
        sha256 = hashlib.sha256(resp.read()).hexdigest()
    formula = TEMPLATE.read_text().replace("{{URL}}", url).replace("{{SHA256}}", sha256)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(formula)
    print(f"wrote {out_path} for fram {version}")


if __name__ == "__main__":
    main()
