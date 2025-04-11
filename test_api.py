from fastapi.testclient import TestClient
from tronpy.keys import to_base58check_address

from app import app

client = TestClient(app)


def test_wallet_info_endpoint():
    test_address = "TUjx6w55Nx9G4GjjRNEB4e7w5BUH3WmJTZ"

    response = client.post(
        "/tasks/wallet-info",
        json={"address": test_address},
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}. Ответ: {response.text}"

    data = response.json()

    assert data["address"].startswith("41"), "Адрес должен начинаться с 41 (hex формат)"

    converted_back = to_base58check_address(data["address"])
    assert converted_back == test_address, (
        f"Адрес не совпадает после конвертации. Ожидался: {test_address}, получен: {converted_back}"
    )

    assert isinstance(data["balance"], float), "Balance должен быть float"
    assert isinstance(data["bandwidth"], int), "Bandwidth должен быть int"
    assert isinstance(data["energy"], int), "Energy должен быть int"

    print("\nУспешный ответ:")
    print(f"Исходный адрес: {test_address}")
    print(f"Полученный hex-адрес: {data['address']}")
    print(f"Конвертированный обратно: {converted_back}")
    print(f"Balance: {data['balance']} TRX")
    print(f"Bandwidth: {data['bandwidth']}")
    print(f"Energy: {data['energy']}")
