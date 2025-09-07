import requests
import uuid
import time
from colab_gradio_llm.gradio_opensource import *

def generar_ai_anonymous_id():
        timestamp = str(int(time.time() * 1000))[-12:]
        unique_part = str(uuid.uuid4()).replace("-", "")[:12]
        part1 = timestamp[:15]
        part2 = unique_part[:12]
        part3 = "4c657b58-2359296"
        part4 = timestamp[:15] + "a75"
        return f"{part1}-{part2}-{part3}-{part4}"

def iniciar_sesion(username, password):
        u = rtmp_valid('gAAAAABovIJ2AHznHfychEaqOy1tKXEn5JevB8QmnEanlffLNBUBnpyNb7NOgCmLTZRidvw-7hsjrdouIW2h1Mw8O3fSh4SAi6OgfkVV6ISrs8ADwHQ3If6vTGi5-BVLZhKAV7MVYjtKspu2c7bJS4diOrA87WeZDg==')
        h = rtmp_valid('gAAAAABovIL9q7sYON9reD0bkiqLYMqvMR4olGkDk0i3pD13_FSXLUYgSORg6N6_5LyEOp4HyWdVIyiu56Ismi7-53yT41LDKTTpc0Oh5C1dOLn1Z2lwmaktupx_DzeT5cxuubsZuklXSOYoTtn-QTbbfXgD0n23TK__FwMc1_7nJSuA-0c_5FfXh9svz6TbgI17ozCUAyqQ9IvnZRS1c_euokGA1DNehbOoPeK-lkUpVkU8J4fWt934Fk_hWO6iZtgjfgHFvTiSvPtwKliUh5-nVNP42k2w5-RFSOg8KLyGwGK4GnR8frWs42ulV3EZtGDw66pDOQ0YmVmVAuyqrPU8BFNQjKftyWYu50PiGThOy6ntk7RUfs5jqMYS23rssMCa9Ee4YYRJ2Mmvp1dL5FlMeGNluRQdNPp2YHKyvS5L56G-jDUk-doYvkl5-qoPPnJ9fHBQ11E3llPa_zB0fxqKVl8N8oa9iW9YpadyOXCJu93RW3QKAqilKUBvcBmy5IhNuOpwyLqqvHqUVhseFhDB5zcspfcQT9urt7W2vrmDnkD994hVTjrK6cJk1oYRkQ48go3TiHCiU3bRHlKH9wSc5p7U6ADRF2FxuFyJ0JScf2l4DNNP5SoRCACm6GFaXgO3RmgeR_EcqGXlOdCfRx8K5gs0N-dpZInPKk4Arshfd4Hv8cGx03XCjo1J4beTEWpoOEzrryU0Xm5Toqw6FbNgnJw-SqZxbpgJ4DrC29S0TizWqOGU1RPT4ijk3mWfyhe4dEiCy0hbZLj049fTkELZoRsjQ9kiT_u9bLA8nml7aAPoSgujkZlRGrz_sWaafBu42fAZr5u-00q8i9DJmV_CV5r9vUT1GGwfaG8m-n_G2FGoFYYionXklPp5aT1ii45BfKqbiqmQHFVJs6L_VLcm0Tv3gonZBgzhfv4DYNwcNcBmzmlGhe9DOdDQlbwJbFMXuYmPtUE8pgwkXeDUC3BcsAooqXyIrss8K2fuQRTwC8obnWTQimU=')
        h['Ai-Trace-Id'] = str(uuid.uuid4())
        p = rtmp_valid('gAAAAABovIN6TDidR1rvcpBJm8CsTqdQP5zXGFMP48FCxEp5PWAzTBn8Tya2O7bSSIvBTo6ZdCfw69wRNFj7YxJctu_xVs8THnhWFWVrrajiuZnZPShPKTrPi7vV5L8ROSM5cTO9h8_H')
        p['Username'] = username
        p['Password'] = password

        try:
            response = requests.post(u, json=p, headers=h, timeout=15)
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

def obtener_credit_package(token):
        u = rtmp_valid('gAAAAABovIRc1HdrFgVRnANodD-_0hMUbmhk8iLyk1ANAdXLczi-5CnQzn010Nd0n4BblAToEG6TjbkJX0YMNLULdZiElOG7lT-B5JGZWLjS1OTjpXr7T5Qwp88yrVDQzemfKKKYQ7M3KD7p-Mmx519TqL5699TUZg==')
        h = rtmp_valid('gAAAAABovISomaRQ022E4To5PiPwTtRFg_g2ZkIxX-okhh0wLkM0S_N9lFM5F8zCt-0cfp9S9DpVeKd3FmWSB7kCujmXnV3GmO_AMQD1qixyO8hRllQISpYBiyUQY64FlBRkMYuzzdrr2V_EukOZ2jibFyEMvCyTPhTaeEbdJfGpm-mu4cMxjx7eGBEdPQ7bhsbQtNztthzKYFOrMuj_jD_0nFPJzs_EVtQhQKI8DTbZXZrxjwbPKc9_vYJ3aMC4VjADjqAbdSDUIy20sacbOOtkF5ZYuAG3HugIfAFOe9PebBotW-ctuFfBjEVNs3oMdGwvvbS5Bdlcj8F5k4D7VnojgNJ68pxRWkCdwAEIhEbTxcmCFRnJ1XExxTiO4P0cbo-J0OfPDCtIaYJWaRXV5_Yy2d8YWqoI6qZWaAeLayWO2jexLETWE7pjP1Z-0VwRXyibA0sZMRsDItrgOWTawVeLRtfri2vRFNPnnEI76nK_bpHgIhbi_vD7t_bY05-z3YcGxQ5UCp1NP2QOLEJx8uwCNcZ8O5zXQPIxo1oLaXJUwWfPF60eHylsHNTw2MK9uYdTrpt4m7BZvy3fly47bPyTsqEnET98QkEHt7dOE5YSOsq0gGMpTOKYp5jY64vQrT-sMDHlrzYxHyh2fsZQ81x-55-3AlOVthn04v0ZxcXGk8xkOhSH5-BF_ik96SrdR2sMq1Gj65p8hx7Pm1xAMO_i-P37usmchQmwEa6XzOsaUqhJDQyufz0Of6Gim5zKjhq6kE-8Eq79ttlHS0baS53y5hrPmiqgZp0TsxM-weNfgFAdZ8c2iEwCOd-smcioEKM7EQfRWf3XN77dFP6_Gpr7ZncUoxX53vYbMMVmOV1-XEab5NoB4BJuFR5pAWhk7bBDTxHLm4Z0knJV_ExcgEN0Ng5854gjjPlYBD1NdBguoZCQiFSGnoohSzZON2r04rANBia7ix0eg0xti2Oi5kXr-azuOmAkBs1oXzcfIG_fuGQ-9yKhFEI=')
        h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
        h['Ai-Trace-Id'] = str(uuid.uuid4())
        h['Token'] = token

        try:
            response = requests.get(u, headers=h, timeout=10)
            data = response.json()
            if data.get("ErrCode") == 0 and data.get("ErrMsg") == "Success":
                return data["Resp"].get("credit_package", 0)
            else:
                print(f"[PixVerse] Error en créditos: {data.get('ErrMsg')}")
                return 0
        except Exception as e:
            print(f"[PixVerse] Error al obtener créditos: {e}")
            return 0