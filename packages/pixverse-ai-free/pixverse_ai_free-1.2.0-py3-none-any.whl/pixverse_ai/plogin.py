import requests
import uuid
import time

def iniciar_sesion(self, username, password):
        url = "https://app-api.pixverse.ai/creative_platform/login"
        headers = {
            "Host": "app-api.pixverse.ai",
            "Connection": "keep-alive",
            "X-Platform": "Web",
            "sec-ch-ua-platform": '"Windows"',
            "Accept-Language": "es-ES",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="137", "Edge";v="137"',
            "sec-ch-ua-mobile": "?0",
            "Ai-Trace-Id": str(uuid.uuid4()),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://app.pixverse.ai",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://app.pixverse.ai/",
            "Accept-Encoding": "gzip, deflate"
        }
        payload = {"Username": username, "Password": password}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"[PixVerse] Error HTTP {response.status_code}: {response.text}")
                return None

            data = response.json()
            if (
                data.get("ErrCode") == 0 and
                data.get("ErrMsg") == "Success" and
                "Resp" in data and
                "Result" in data["Resp"] and
                "Token" in data["Resp"]["Result"]
            ):
                return data["Resp"]["Result"]["Token"]
            else:
                error_msg = data.get("ErrMsg", "Desconocido")
                print(f"[PixVerse] Login fallido: {error_msg}")
                return None
        except Exception as e:
            print(f"[PixVerse] Excepción en login: {e}")
            return None

def obtener_credit_package(self, token):
        url = "https://app-api.pixverse.ai/creative_platform/user/credits"
        headers = {
            "Host": "app-api.pixverse.ai",
            "Connection": "keep-alive",
            "Ai-Anonymous-Id": self.generar_ai_anonymous_id(),
            "X-Platform": "Web",
            "sec-ch-ua-platform": '"Windows"',
            "Accept-Language": "es-ES",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="137", "Edge";v="137"',
            "sec-ch-ua-mobile": "?0",
            "Ai-Trace-Id": str(uuid.uuid4()),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Token": token,
            "Origin": "https://app.pixverse.ai",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://app.pixverse.ai/",
            "Accept-Encoding": "gzip, deflate"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if data.get("ErrCode") == 0 and data.get("ErrMsg") == "Success":
                return data["Resp"].get("credit_package", 0)
            else:
                print(f"[PixVerse] Error en créditos: {data.get('ErrMsg')}")
                return 0
        except Exception as e:
            print(f"[PixVerse] Error al obtener créditos: {e}")
            return 0