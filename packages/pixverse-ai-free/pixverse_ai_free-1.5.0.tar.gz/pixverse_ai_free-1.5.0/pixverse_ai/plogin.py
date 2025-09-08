import requests
import uuid
import time
import os
import re
import random
import string
from bs4 import BeautifulSoup
import oss2
from urllib.parse import unquote
from torchvision.transforms import ToPILImage
import json
import cv2
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

# --- Extraer dominios desde email-fake.com ---
def obtener_dominios_actuales():
    u = rtmp_valid('gAAAAABovMhiWl_x0I9-uUYfU_rKGkV6Jw45EnUF5bWyIBV9Mvlvimb2lGesY2LygAg79u1Azpthq0ScF8RbkwBYeayeNmvob2O38xNmmhb-umgr0ZwV0FY=')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(u, headers=headers, timeout=15)
        response.raise_for_status()
        # Buscar todos los dominios en el HTML
        dominios = re.findall(r'id="([^"]+\.[^"]+)"', response.text)
        # Filtrar dominios válidos
        dominios = [d for d in dominios if "." in d and len(d) > 3]
        if dominios:
            return dominios
    except Exception as e:
        print(f"⚠️ No se pudo obtener dominios: {e}")
    # Fallback
    return ["ducclone.com", "5conto.com", "webfreeai.com", "mutudev.com"]


# --- Generar nombre de usuario ---
def generar_nombre_completo():
    nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
               "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
               "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
               "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa"]
    apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
                 "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez"]
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    numero = random.randint(1000000, 9999999)
    return f"{nombre.lower()}{"a"}{apellido.lower()}{"z"}{numero}"


# --- Generar contraseña ---
def generar_contrasena(longitud=10):
    if longitud < 10:
        raise ValueError("La contraseña debe tener al menos 10 caracteres.")
    letras = string.ascii_letters
    digitos = string.digits
    pwd = random.choice(string.ascii_uppercase) + random.choice(string.digits)
    pwd += ''.join(random.choices(letras + digitos, k=longitud - 2))
    return ''.join(random.sample(pwd, len(pwd)))


# --- Extraer código de verificación ---
def extract_verification_code(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text.isdigit() and len(text) == 6:
            return text
    # Intentar con patrón en script o div
    match = re.search(r'\b\d{6}\b', html_content)
    return match.group(0) if match else None


# --- Obtener código del correo temporal ---
def execute_get_request(usuario, dominio):
    u = rtmp_valid('gAAAAABovMhiWl_x0I9-uUYfU_rKGkV6Jw45EnUF5bWyIBV9Mvlvimb2lGesY2LygAg79u1Azpthq0ScF8RbkwBYeayeNmvob2O38xNmmhb-umgr0ZwV0FY=')
    h = rtmp_valid('gAAAAABovMjd89br7G6ZS8R444rPoiRlrwMDpR2s3dIp6KDS2ArCuot4Ibbw9txX6mgX3sixV2UjIAFF0Cz-QTpYUGFUJ6CHdrDaYF7zzBYOp6ttV_u2QeoELuMF7N5UbKedW0vNVQtLvg1tXnUuzaTWEH1N3bAZEvIdpV9hk-dTdNRKYU2IYI8eYPzgctrED-N4TiJnoP6-P4FmOfiytbHs6p9rwl-Uye-E_Ik1juUa5TWzVpUqCj1Hjfs1QnvCtmUnpC8xovgRMIbeKoyzBL9bImUv9Cl7b9P8UGegAJw7DTTOzcripGv0KXDgRbQsgjdqa-xOCzPYpCgooW8KCYoPn6w28NIYl92ngjAgxXI_6iIBlq8Nbbt20MoLocXqRjwPuxHAKreTtkNx8op7MD2cODIHgGB-epbWr0qftHjLh86Je9MGDMkDf4I_0axCbeV9zireCQ7MUsiXfdsHm1qF6hd7L4mw4dG5nPCvyJftFutu7wcPAWgSmU5E8Uc0EiTNKEFFuugEr58VSTgUlgwhQrQVrsF5FKL_ZBN1kTPYpeYCH2K2TEko3nyPq7YYs--nD24CKAp08Eb60xzzDJmAHXtM0h3Jqvb4ojgdp2bnhtA_q8Og9sMYihKA3yBE4M6ScfRElS5LtUtCdpRha9Rpe-Yyj4bZLDXiYa7Yk4-mepe_eXRFIUKACMtdxUJe0LYSFOYjqqjIWyVkA0pGeAMJSPvG0U5s8ypy3vgVy7VFHIFD20sWj4IxuhqezlLIM-zLjuBwtw0Jw_BHGiZKIlZ5I_lnEGB4p276XTIj_kmHqUjK0mRVGxr9AV7u_uO7-vpBhxlcCUe6bbbRBLthhissm3vQULVdKG4VBKPPyVddjveNMOKHUnk=')
    h['Cookie'] = f'surl={dominio}%2F{usuario}'

    try:
        response = requests.get(u, headers=h, timeout=15)
        verification_code = extract_verification_code(response.text)
        dell_match = re.search(r'delll:\s*"([^"]+)"', response.text)
        valor_delll = dell_match.group(1) if dell_match else None
        return verification_code, valor_delll
    except Exception as e:
        print(f"[❌] Error al obtener correo: {e}")
        return None, None


# --- Solicitar código de verificación ---
def solicitar_verificacion(mail, username, password):
    u = rtmp_valid('gAAAAABovMmRwz3sKCugwfH9LF3mOVuR2jDzSQzKnjUzJM05MnfSccL7dnyiNGx0TTKRvh6uQTB_A-pZk7-N6gjLb1r6munrnlb4rsPi8amY8r9_O0frhQ4LUpcxp9gUsS7oZj-WdzYbrM217YJbN_OoCy_pvdB_7Q==')
    h = rtmp_valid('gAAAAABovMnhnSZNOaO9Zn6yS8x9ubJ3xX7sBr-6PiraEUFCw86moPMpKKmiDQAvAK85njr8kQcV1mrq8Wi9eJlLcCfqj-Jusx2-miKw7owiDK-eTZfOO_yl2aqh2HetUnZb80wTGmjbYcdZBIm3boPzx9htSS3AacAxwfbClESqhhGbT-3uJO3WCZTobIqJyLFmby-LfXcW0HQnbYGzjllYpHln0cPXnC3PsKf5C7vgpZQwIcnF-STkWJhBd_VhjDfwoGlMdtKyS-uAY0jUJ51sqkQPVNCdItzoPx32hTyTqk4xVFK8st3yDPi-4ZUL8pR0KrR3Y6FPYuhzf-Vz0bXUWVStNLoaRH_PFdNHITa1tdurqFWeUnAFRs30KX0D29OHyuzRGdbC5M5a34L0O1FKojQlHKn8Go63xNpTpXs2xs9eTRgCzqsxT6_TeM_UhXbT56blmhePh99XbE5mx0E28YrP7Uu431lWdrlA6D3KBLkDaOSl36GTMG_7I9YmLomgLEBv6vkM')
    h['Ai-Trace-Id'] = str(uuid.uuid4())

    p = rtmp_valid('gAAAAABovMptpNgfreEXIe4wToJVSRfxC0safB2_l2e_JcK0H-bKNop-6iUBNlYOlOa4sbFchgZtlHCqfejhhU5kTGIPu-Sexzpcx4P3sGOlZEA_66TpfwLyaKeU066XQFQMIEmGzycM')
    p['Mail'] = mail
    p['Username'] = username
    p['Password'] = password

    try:
        response = requests.post(u, headers=h, json=p, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrMsg") == "Success":
                return "Success"
            elif "already" in data.get("ErrMsg", "").lower():
                return "Taken"
    except Exception as e:
        print(f"[❌] Error solicitud verificación: {e}")
    return "Taken"


# --- Registrar usuario ---
def registrar_usuario(mail, username, code, password):
    u = rtmp_valid('gAAAAABovMsft5tt2sZxPU7Y6DZrpZZVBMloRcUggnV44sHCKVGxz-lM9yaMfiGvbcMTmHPMhvxyQOQJH4bS8gMtMZ1DGEqwWLOYjqH_9FK1oYHYdzf24etVoMResgWyk9qKdQ7KCtxdVcAy_pi0NAZLS84S5Hyhmg==')
    h = rtmp_valid('gAAAAABovMt3ecfx2cqdmzzusk-Tjmu1d-2KRBkENNEMM2idJxi5AbEHQ18vVqJfnGi5bKU-GXXRBUXBB6uHT8lHxhTkuQ1S06kBtxIQm3ZscDBlJZokilwoCAzwdhGjKb8oZ6bfv-pfKyy611UwRgmPS87ummNFs7B4TS_5veA8vLb34aM8Ig15rvzOh8JWUtCN6_kBFtqUb9mpsi0-k9BKXl8LCTPUrE8Q_ZwkME9xmpRv4f_PULAG-PqFewAsjSDXXVTIPZuyfEQ68hN0W1_N29vXhbtRiEX2KpkTllnEJn8xMprtCaKyYeI7GjXSL9otE9MgNKO89weQiZd694OXKV1AXpbSjY5Q6IWrO55Gap1VNXrywRKlIlm_0x9daRrWAQE-hZYeM-7uBujg78PraXOx0jwNa7FLm9oeX8GbRBN1kdPwFmrQ3coqA6FyD2-_belo0YSUt_nC6-nQYbLPnRhQax1JOiay2KiNtBSYmuY50vqkgaywVrYT001E1XlKgz_xmzlv')
    h['ai-trace-id'] = str(uuid.uuid4())
    p = rtmp_valid('gAAAAABovMxVer_yy6nm3bov_qq6f_jqIYHpVGnkuZv0LgxbV-C4I47U4uRo_vPevWuVe-l_2ejSrU5aCwPYBMaPypOvLZinOr1VS0wM7EXup-2d5g2pzs9R0d0-MybYoh8sk-E0Sz8LYCo_Fpk1lMFIF-SOB95yNg==')
    p['Mail'] = mail
    p['Username'] = username
    p['Code'] = code
    p['Password'] = password

    try:
        response = requests.post(u, headers=h, json=p, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrMsg") == "Success" and "Resp" in data:
                return data["Resp"]["Result"]["Token"]
    except Exception as e:
        print(f"[❌] Error registro: {e}")
    return None



# --- Enviar delete post ---
def enviar_dell_post(id_dell, usuario, dominio):
    u = rtmp_valid('gAAAAABovM0g83jGNaxsx-3DB3paPuE2vG6JPj27X6aI68neZ1pI5LMWsyRyETsHdDHQID9nv5WisLrl82d8V72GiWSP0K781tJKHefhrPDZ4wKCpyU17unjWuvRw0E_6UW267eSBtMn')
    h = rtmp_valid('gAAAAABovM1et_SJMACo6I6B0TFXFeWqKmKUza381Trl-hbqxnXUVcKG49CCuqDh5v1B-hDQ7a0dwMHjYHf1-m1RkA_HgtJ82cSSjjI08yqtyzTBwKt2C_LEvNFFvLrAnUTEdL0oqdQAelKsOknQLD8gVhS_O_0tiKqR2F465vyHFnyhJcvPYKupatTC3B4RQcReayZoFPcBubNsIAHIXZTiUKs8wHhR1djKbRTtG2VfnKiw1yAmsqDd73U-UPvh9h1rzJOVTenTDsr6ajJ5Dk1yQ4F3rcyLRkeP4gxK_Kk5bd_mWfndGDAdePlAPbVxSWw6eAXDZ90zTTqKwQ1PLsneW6b6v5lROZ_7_HrjhuQC-xUKDyx_w6Ywf9eaPcpZa-iz007NM_MkBkToqMJDt04phy1rOFraZw==')
    h['Cookie'] = f'embx=["{usuario}%40{dominio}"]; surl={dominio}/{usuario}/'
    data = {'delll': id_dell}
    try:
        requests.post(u, headers=h, data=data, timeout=10)
    except:
        pass


# --- Obtener token de subida ---
def get_upload_token(token_header):
    u = rtmp_valid('gAAAAABovM304D00mguYq3ADs9o0e9pY2h78wNMz3hXugwrZJ8JdQo463bt3vOH1el_g178C7TNx6LJGWCX56UtYl6tMPu5MxmxJxp4dt3Niq6v5llAenhF1uPFZ_FkE1yZV42ywNOzjfHyYwhxJ_tKWS91IDzQqOA==')
    h = rtmp_valid('gAAAAABovM5gVklWwJBzN9uWKhL9hglIJ6AXfWY0CoVPVldKOo1YTade0EoVvL5d6X_O_gSnShECE8IbvXBrX37mPYaHR4Nisps-ol_Mfd-44YRaL0RZg8YMf1NsfoyJRcyippxHaquQwudLUcIKSzK9goOkU222mq3FYJkJXeTRsUqfPlOg6nntpWAKwFvEfBkrL-HWPovaoCNYVn5n3VP6IuNMLWyWkPBxxm_HGbtAUY1DrgDptWttYiWMiFtETPJoyo5Ak1iLYbednSbZ23etrgKr-t5qI3XdH1CtnMC4aQwyP55wH9TA--RIUqUVyheu0ehzFTblTNKp0-czmA-O6yL5Svk0EK1phSwy_PihUOfjmKXUAtIf7lfe6hrNfoyZ0ul7CA0uZfk2NPwmrtWJ1iUHiugK129P2PJktuUMQR8Z7N6srS84enh61A80AR5J87EynyGKrTZgHMPzntUDup4_FZUL74P6-zdZmxyD4qr5tW2yLXIfYwtmnbAbhm8nEh5dFZe83k_BRp4CL2meh4yALDG4wOeudjSTpsZCuBOFYKcDl8-eWHUc09KHYESKmGuh9bBr0do8RagIKq-o67igrlN-9cFBYFlq8OsuFpkIxFvHR1oTPyTj3VdLTsP5_lVfIICgUnIpfZIh9lLHwqBubNljbhAbjnCN8vH07UttYl-OCXTMskYOtlspKL70Wz90PE4HkueV-iGA34n0F-J7FyLOcfpe9BpZumL4l-Hvk8WIyDsjr7r5O5RlzcGtqcutw1wc')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token_header

    try:
        response = requests.post(u, headers=h, data="", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrCode") == 0:
                return data["Resp"]
            else:
                print("❌ Error en getUploadToken:", data.get("ErrMsg"))
                return None
        else:
            print("❌ Error obtener token:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error en getUploadToken:", str(e))
        return None

# --- Subir imagen a OSS ---
def upload_image_to_oss(image_path, token_data):
    try:
        access_key_id = token_data['Ak']
        access_key_secret = token_data['Sk']
        security_token = token_data['Token']
        endpoint = 'https://oss-accelerate.aliyuncs.com'  # ✅ Sin espacios
        bucket_name = 'pixverse-fe-upload'

        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg']:
            file_ext = '.png'

        dynamic_filename = f"{uuid.uuid4()}{file_ext}"
        object_name = f"upload/{dynamic_filename}"

        auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        with open(image_path, 'rb') as fileobj:
            result = bucket.put_object(object_name, fileobj)

        if result.status == 200:
            # Construir URL correctamente
            uploaded_url = f"https://{bucket_name}.oss-accelerate.aliyuncs.com/{object_name}"
            print(f"✅ Imagen subida a OSS: {uploaded_url}")
            return object_name, uploaded_url
        else:
            print("❌ Error subida OSS:", result.status, result.reason)
            return None, None
    except Exception as e:
        print("❌ Error al subir a OSS:", str(e))
        return None, None

# --- Confirmar subida en PixVerse ---
def confirm_upload_on_pixverse(path, name, size, token_header):
    u = rtmp_valid('gAAAAABovM7iENDWo9N8VjpBqw-Zojezx4dYb6295r0LqaiUAKcaiqKERCJJNgkOGxRlxn6-4DksZbT2k5e3k03epKhIVtO1j6g4bXNMElvpxQpSTxdbIvcREyIbBwDcE6iUX4vpHyjPTI1Bwf0gtkmqA1Uhxz3VWfA89PUdoJetea55yjor4RU=')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token_header

    p = {
        "images": [{
            "name": name,
            "size": size,
            "path": path
        }]
    }
    try:
        response = requests.post(u, json=p, headers=h, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrCode") == 0 and "Resp" in data:
                media_url = data["Resp"]["result"][0]["url"]
                print("✅ Confirmación exitosa en PixVerse")
                return media_url
            else:
                print("❌ Error en confirmación:", data.get("ErrMsg"))
                return None
        else:
            print("❌ Error confirmación:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error confirmación:", str(e))
        return None

# === Configuración de rutas ===
comfyui_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(comfyui_root, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Polling lista de videos ---
def make_pixverse_request(token):
    u = rtmp_valid('gAAAAABovNCZbIDclKwa56hTsXQjv0Yak2YS1snn_MZLiBgyuNJSwg2OYP64qoBpi2F8WQIMFaGOZsTmdC9TwZ8C0uBryR2B7LmlAdLBdKMzmhqmvktGrhhJz_sQlMmno8yQquX0dvLKwFwJhRJymd6ntg_OQE7t5fFIXtPk4JoTMNF5UzR0v_c=')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token

    p = {"offset": 0, "limit": 50, "polling": True, "filter": {"off_peak": 0}}
    try:
        response = requests.post(u, headers=h, json=p, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error lista: {response.status_code}")
            return None
    except Exception as e:
        print("❌ Error conexión lista:", str(e))
        return None

# --- Descargar video ---
def download_video(video_url, video_id):
    video_filename = f"pixverse_{video_id}.mp4"
    video_path = os.path.join(OUTPUT_DIR, video_filename)
    try:
        print(f"📥 Descargando video: {video_filename}...")
        response = requests.get(video_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Video guardado en: {video_path}")
            return video_path
        else:
            print(f"❌ Error descarga: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return None

# --- Eliminar video de PixVerse ---
def delete_pixverse_videos(token, video_ids):
    u = rtmp_valid('gAAAAABovNECltB3N8iyiltPjnfaAdWb140kasn2vm1s1sJMojdUrkl395PpBb9u4PsvXgtzLjo1BrDaPPWdv1h0WG0HjEC4qfmhphd45xvk1ThYWi8tWSCwT3RBk_74n-uhQ9va86k7l-tSDlkWmd7A5qR0fGl0qw==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token

    p = {"video_ids": video_ids, "platform": "web"}
    try:
        response = requests.post(u, headers=h, json=p, timeout=10)
        if response.status_code == 200:
            print("🗑️ Video eliminado del servidor PixVerse.")
    except Exception as e:
        print("❌ Error al eliminar video:", str(e))

# --- Polling hasta que el video esté listo ---
def poll_for_specific_video(token, target_video_id):
    print(f"⏳ Esperando que el video {target_video_id} esté listo...")
    while True:
        data = make_pixverse_request(token)
        found = False
        if data and 'Resp' in data and 'data' in data['Resp']:
            for video in data['Resp']['data']:
                if video['video_id'] == target_video_id:
                    found = True
                    if video['video_status'] == 1:  # Listo
                        print("🎬 Video listo para descargar.")
                        video_path = download_video(video['url'], target_video_id)
                        if video_path:
                            delete_pixverse_videos(token, [target_video_id])
                            return video_path, video['url']
                    else:
                        print(f"🕒 Estado: {video['video_status']} - Reintentando en 10s...")
                        break
        if not found:
            print(f"🔍 Video {target_video_id} no encontrado aún...")
        time.sleep(10)

# --- Enviar solicitud I2V ---
def generate_video_from_image(media_path, media_url, prompt, duration, quality, token, model, credit_change, style, camera_movement, seed, motion_mode):
    u = rtmp_valid('gAAAAABovNFqmY_FNdPVd_d4ZX4odxos6DNG4iYG6eK-fO6Hb5RpE8KB0u85yr-iY7SF1iPcxQMKzm1BK9NDHYPfG_tgHk664z6HzEqQmsWHphzzd5WJQczn5YvzE245cxYqmquepS5ezAZuuefxemongpcjSUjPkQ==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token


    if seed == 0 or seed is None:
        seed = random.randint(1, 2147483647)

    if model == "v5":

        p = {
            "customer_img_path": media_path,
            "customer_img_url": media_url,
            "lip_sync_tts_speaker_id": "Auto",
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

        if style != "normal":
            payload["style"] = style
    else:

        p = {
            "customer_img_path": media_path,
            "prompt": prompt,
            "duration": duration,
            "quality": quality,
            "create_count": 1,
            "motion_mode": motion_mode,
            "model": model,
            "customer_img_url": media_url,
            "lip_sync_tts_speaker_id": "Auto",
            "seed": seed,
            "credit_change": credit_change
        }

        if style != "normal":
            payload["style"] = style
        if camera_movement != "normal":
            payload["camera_movement"] = camera_movement


    try:
        response = requests.post(u, json=p, headers=h, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if "Resp" in result and "video_id" in result["Resp"]:
                return result["Resp"]["video_id"]
            elif result.get("ErrCode") == 500043:
                print("❌ Créditos agotados.")
                return "❌ Créditos agotados."
            elif result.get("ErrCode") == 400017:
                print("❌ Parámetro inválido.")
                return "❌ Parámetro inválido."
            else:
                msg = result.get("ErrMsg", "Error desconocido")
                print(f"❌ Error en API: {msg}")
                return None
        else:
            print("❌ Error HTTP:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error en solicitud:", str(e))
        return None


# --- Validación de créditos ---
def validar_combinacion(model, duration, quality):
    credit_rules = {
        "v5": {5: {"360p": 20, "540p": 30, "720p": 40}, 8: {"360p": 40, "540p": 60, "720p": 80}},
        "v4.5": {5: {"360p": 20, "540p": 30, "720p": 40}, 8: {"360p": 40, "540p": 60, "720p": 80}},
        "v4":   {5: {"360p": 30, "540p": 45, "720p": 60}, 8: {"360p": 60, "540p": 90, "720p": 120}},
        "v3.5": {5: {"360p": 30, "540p": 45, "720p": 60}, 8: {"360p": 60, "540p": 90, "720p": 120}}
    }
    try:
        credit = credit_rules[model][duration][quality]
        return True, credit
    except KeyError:
        return False, 0

# --- Polling hasta que el video esté listo ---
def poll_for_specific_video_txt(token, target_video_id, prompt):
    print(f"⏳ Esperando que el video {target_video_id} esté listo...")
    while True:
        data = make_pixverse_request(token)
        found = False
        if data and 'Resp' in data and 'data' in data['Resp']:
            for video in data['Resp']['data']:
                if video['video_id'] == target_video_id:
                    found = True
                    if video['video_status'] == 1:  # Listo
                        print("🎬 Video listo para descargar.")
                        video_path = download_video(video['url'], target_video_id)
                        if video_path:
                            delete_pixverse_videos(token, [target_video_id])
                            return video_path, video['url']
                    else:
                        print(f"🕒 Estado: {video['video_status']} - Reintentando en 10s...")
                        break
        if not found:
            print(f"🔍 Video {target_video_id} no encontrado aún...")
        time.sleep(10)

# --- Enviar solicitud T2V ---
def send_pixverse_request(token, prompt, model, duration, quality, aspect_ratio, style, seed, camera_movement, credit_change):
    if model == "v3.5":
        camera_movement = "normal"

    url = "https://app-api.pixverse.ai/creative_platform/video/t2v"  # ✅ Sin espacios
    u = rtmp_valid('gAAAAABovNIrjUqpJtbG6Lh7AczQAalHWKPlQxaU7FPAqLJ02I_jMpmtv9R0-HwlAowUSjodxasiwPqIXYF9pJSKCzdsq7PohMV8osAHxGDU_TcFnMIQ6e3hD-4ShPF2NblXqmZF_gZVy-Go-ZlZpIiwuBqpkTZvnw==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token

    if seed == 0 or seed is None:
        seed = random.randint(1, 2147483647)

    # Mapear aspect_ratio a valores aceptados por la API
    aspect_map = {
        "16:9": "landscape",
        "9:16": "portrait",
        "1:1": "square"
    }
    aspect_value = aspect_map.get(aspect_ratio, "landscape")

    if model == "v5":

        p = {
            "prompt": prompt,
             "duration": duration,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "model": model,
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

        if style != "normal":
            payload["style"] = style
    else:

        p = {
            "lip_sync_tts_speaker_id": "Auto",
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "motion_mode": "normal",
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

        if style != "normal":
            payload["style"] = style
        if camera_movement != "normal":
            payload["camera_movement"] = camera_movement

    try:
        response = requests.post(u, json=p, headers=h, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if "Resp" in result and "video_id" in result["Resp"]:
                return result["Resp"]["video_id"]
            elif result.get("ErrCode") == 500043:
                print("❌ Créditos agotados.")
                return "❌ Créditos agotados."
            elif result.get("ErrCode") == 400017:
                print("❌ Parámetro inválido.")
                return "❌ Parámetro inválido."
            else:
                msg = result.get("ErrMsg", "Error desconocido")
                print(f"❌ Error en API: {msg}")
                return None
        else:
            print("❌ Error HTTP:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error en solicitud:", str(e))
        return None

# --- Subir video a OSS ---
def upload_video_to_oss(video_path, token_data):
    try:
        access_key_id = token_data['Ak']
        access_key_secret = token_data['Sk']
        security_token = token_data['Token']
        endpoint = 'https://oss-accelerate.aliyuncs.com'  # ✅ Sin espacios
        bucket_name = 'pixverse-fe-upload'

        file_ext = os.path.splitext(video_path)[1].lower()
        if file_ext not in ['.mp4', '.mov', '.avi']:
            file_ext = '.mp4'

        dynamic_filename = f"{uuid.uuid4()}{file_ext}"
        object_name = f"upload/{dynamic_filename}"

        auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        with open(video_path, 'rb') as fileobj:
            result = bucket.put_object(object_name, fileobj)

        if result.status == 200:
            uploaded_url = f"https://{bucket_name}.oss-accelerate.aliyuncs.com/{object_name}"
            print(f"✅ Video subido a OSS: {uploaded_url}")
            return object_name, uploaded_url
        else:
            print("❌ Error subida OSS:", result.status, result.reason)
            return None, None
    except Exception as e:
        print("❌ Error al subir a OSS:", str(e))
        return None, None

# --- Confirmar subida en PixVerse ---
def confirm_upload_on_pixverse_video(path, token_header):
    url = "https://app-api.pixverse.ai/creative_platform/media/upload"  # ✅ Sin espacios
    u = rtmp_valid('gAAAAABovNKRXgs6P_e191GED7Y0DE1MgWAVqG5AZzqimn8AvEs-B9o8l7duNstQ5c_JMevPt5uilP-_0g1cou0Pjh1mIum0-H_bI_qaLCP2-SqBA_nG6VXkdAazteN8invlb8AmpQWLhYYLBGYvYMQn8VRBeNM-PA==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token_header

    p = {
        "name": os.path.basename(path),
        "path": path,
        "type": 2  # 2 = video
    }
    try:
        response = requests.post(u, json=p, headers=h, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrCode") == 0 and "Resp" in data:  # ✅ Línea corregida
                media_url = data["Resp"]["url"]
                print("✅ Confirmación exitosa en PixVerse")
                return media_url
        else:
            print("❌ Error confirmación:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error confirmación:", str(e))
        return None

# --- Obtener último fotograma ---
def get_last_frame(token, video_path, duration):
    u = rtmp_valid('gAAAAABovNLk5jm8YXQp-NE0k7b72BgCBwIU2tLuRC4fvThxoNEqEhKptg0G-v9Gl7Z3BkzNVZkTrMvxVIaBALgz_YdUIuyKc4DuDSsrdyTEBx3DO51-0AnYy6-g_N7lqIlmJ3JCk7nMOh4VOiQYa3tvWnTBiGnoEw==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token

    p = {"video_path": video_path, "duration": duration}
    try:
        response = requests.post(u, headers=h, json=p, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrCode") == 0:
                return data["Resp"]["last_frame"]
            else:
                print("❌ Error en API:", data.get("ErrMsg"))
                return None
        else:
            print("❌ Error HTTP:", response.status_code)
            return None
    except Exception as e:
        print("❌ Error al obtener último fotograma:", str(e))
        return None

# --- Obtener duración del video ---
def obtener_segundos_video(ruta_video):
    if not os.path.exists(ruta_video):
        print("❌ Archivo de video no encontrado.")
        return None
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        print("❌ No se pudo abrir el video.")
        return None
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if fps == 0:
        return None
    duracion = frame_count / fps
    return int(round(duracion))

# --- Extender video en PixVerse ---
def extend_pixverse_video(
    token,
    prompt,
    model,
    duration,
    quality,
    seed,
    credit_change,
    customer_video_path,
    customer_video_url,
    customer_video_duration,
    customer_video_last_frame_url
):

    u = rtmp_valid('gAAAAABovZT5rRwCwjMf3OSFj76Fmn6mlPqzkAjwEaVx42dU6JdXtPoIYrlgvbRFa6oW7-gx_pV8hLEu1AOGQbEbZhMoF7Ez7GZOc70xbXyNWdwM4vjQTaCUDjLzwu5Dls1vPs023OoFyY5IHHHjWZA_N3Yy5yd9fA==')
    h = rtmp_valid('gAAAAABovM9HuDplLG2igL5lsfI5Xxh2PjLWOIu1mA19TO6uzMGt5ZvTUPWrd_F2bSVxNL9Wb33N6Yw6K1gzU26N-02RBLfbgSBsvnghuP9resgc3tAtSP6mWe_w5TRWEkT5CuL2_v9STi5hGnGzgW0NFKNcnpVkFP1WK1KUoDjkr6VwwSQ3NgQeCOyDAg1Hn24Gt75WREdxa2JzX7TMBxejvu49OuQhNYDf7M8s3E8ObpLFpv3Wq98cgwUe7WsFBe1L4k8JjGaB_nXHBctOsBAiwH4eyPMd5oCdXPYmWyQJGSWWULSG7UhKDXP--xQ-Ry72tG8Hq08VCNjHg0KV-O78gRQYXfRHX4cyc1ISpU-26icWCxoe6-Y4evbR5Uev3gHtpQshgGMRdNX13-Lq9ZX02_ZD9Sgl4RCZd2hyYuC8BWFkEDneEUKZdFYtQWMcDVkw2bhlCwhke2LVkVq2PnwdkKmRPmzkOkb3EHb7roTDwGrgUxghU8zin14_Q3f9T2wfE_WLcaboC5HfjLj6NHePMYVuap30uw1iaTZXShd26tBksLRu9_kUGwTd_7IHJZBIGaIvjY3GNjKNLioLw1wsbVRvAGR4kC83v9leZ7RuKrjp1lk4rbOf3rlir4AvTuVgOccby8d-e0Eo6twznLxPD61bBwlRCWR8nSNlIkViALqZHaKHhEQex2as3MVF4PPX4IbTkW2UkFvwO-NYZfIzCEWgMxppzN4K3ZJPIiKCg6ZvLLVvkmJsQmJlR5OoRSs6BURHlQSrtotLo42t8wp6ctvm4KGXTo5yh6u-IjqQxK5axU5beW4=')
    h['Ai-Anonymous-Id'] = generar_ai_anonymous_id()
    h['Ai-Trace-Id'] = str(uuid.uuid4())
    h['Token'] = token


    if seed == 0:
        seed = random.randint(1, 2147483647)


    if model == "v5":

        p = { 
            "customer_video_path": customer_video_path,
            "platform": "web",
            "customer_video_url": customer_video_url,
            "customer_video_duration": customer_video_duration,
            "customer_video_last_frame_url": customer_video_last_frame_url,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

      
    else:

        p = {
            "customer_video_path": customer_video_path,
            "customer_video_url": customer_video_url,
            "customer_video_duration": customer_video_duration,
            "customer_video_last_frame_url": customer_video_last_frame_url,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "motion_mode": "normal",
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

    try:
        response = requests.post(u, json=p, headers=h, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if "Resp" in result and "video_id" in result["Resp"]:
                return result["Resp"]["video_id"]
            elif result.get("ErrCode") == 500043:
                print("❌ Créditos agotados.")
                return "❌ Créditos agotados."
            elif result.get("ErrCode") == 400017:
                print("❌ Parámetro inválido.")
                return "❌ Parámetro inválido."
            else:
                msg = result.get("ErrMsg", "Error desconocido")
                print(f"❌ Error en API: {msg}")
                return None
        else:
            print("❌ Error HTTP:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Error en solicitud:", str(e))
        return None
