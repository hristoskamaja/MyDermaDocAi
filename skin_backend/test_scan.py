"""
Брз тест на /api/analyses/scan-skin/ со реалниот истрениран модел.

Користење:
    python test_scan.py <email> <password> <патека_до_слика.jpg>

Пример:
    python test_scan.py admin@skinscan.ai mojaLozinka123 "C:\\Users\\Maja\\Downloads\\zr7vgbcyr2-1\\images\\imgs_part_1\\PAT_8_15_820.png"

Ако немаш при рака патека до слика, најди било која .jpg/.png слика на кожа
(на пр. од распакуваната PAD-UFES-20 папка во Downloads) и залепи ја патеката.
"""
import sys
import requests

BASE_URL = "http://127.0.0.1:8000/api"


def main():
    if len(sys.argv) != 4:
        print("Користење: python test_scan.py <email> <password> <патека_до_слика>")
        sys.exit(1)

    email, password, image_path = sys.argv[1], sys.argv[2], sys.argv[3]

    print("1) Најава...")
    login_resp = requests.post(
        f"{BASE_URL}/jwt-auth/login/",
        json={"email": email, "password": password},
    )
    if login_resp.status_code != 200:
        print("Најавата не успеа:", login_resp.status_code, login_resp.text)
        sys.exit(1)

    token = login_resp.json().get("access")
    if not token:
        print("Нема 'access' токен во одговорот:", login_resp.json())
        sys.exit(1)
    print("   OK, добиен токен.")

    print("2) Праќам слика на /analyses/scan-skin/ ...")
    with open(image_path, "rb") as f:
        scan_resp = requests.post(
            f"{BASE_URL}/analyses/scan-skin/",
            headers={"Authorization": f"Bearer {token}"},
            files={"image": f},
        )

    print("Статус код:", scan_resp.status_code)
    try:
        print("Одговор:")
        import json
        print(json.dumps(scan_resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(scan_resp.text)


if __name__ == "__main__":
    main()
