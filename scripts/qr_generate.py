#!/usr/bin/env python3
"""qr_generate.py — 生成指向 GitHub Pages 仪表板的 QR 码。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")


def main():
    try:
        import qrcode
    except ImportError:
        print("qrcode not installed. Run: pip install qrcode[pil]")
        sys.exit(1)

    # Config — update this after creating GitHub repo
    github_username = "YOUR_GITHUB_USERNAME"
    repo_name = "agent-audit-case"
    url = f"https://{github_username}.github.io/{repo_name}/dashboard/"

    print(f"Generating QR code for: {url}")

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    output_path = PROJECT_ROOT / "output" / "qr_code.png"
    img.save(str(output_path))
    print(f"QR code saved to: {output_path.relative_to(PROJECT_ROOT)}")
    print(f"\nAdd this to your README.md:\n![QR Code](output/qr_code.png)")


if __name__ == "__main__":
    main()
