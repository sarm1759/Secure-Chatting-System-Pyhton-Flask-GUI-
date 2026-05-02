import math

# Agent Key Generator (Aapka logic)
def generate_agent_key(u, xL, b, xG, y, xT, a, xS, length):
    temp = int(
        (u*1000 + xL*10000 + b*1000 + xG*10000 +
         y*1000 + xT*1000 + a*1000 + xS*10000) % 256
    )
    return [format(temp, "02X")] * length

# ASCII Mapping table (Exactly as provided in your code)
ascii_chars = [
    "CI","CJ","CK","CL","CM","CN","CO","CP","CQ","CR", "CS","CT","CU","CV","CW","CX","CY","CZ","DA","DB", 
    "DC","DD","DE","DF","DG","DH","DI","DJ","DK","DL", "DM","DN","DO","DP","DQ","DR","DS","DT","DU","DV",
    "DW","DX","DY","DZ","EA","EB","EC","ED","EE","EF","EG","EH","EI","EJ","EK","EL","EM","EN","EO","EP", 
    "EQ","ER","ES","ET","EU","EV","EW","EX","EY","EZ", "aa","ab","ac","ad","ae","af","ag","ah","ai","aj", 
    "ak","al","am","an","ao","ap","aq","ar","as","at","40","41","42","43","44","45","46","47","48","49",
    "50","51","52","53","54","55","56","57","58","59", "60","61","62","63","64","65","66","67","68","69", 
    "au","av","aw","ax","ay","az","ba","bb","bc","bd","be","bf","bg","bh","bi","bj","bk","bl","bm","bn",
    "bo","bp","bq","br","bs","bt","bu","bv","bw","bx", "by","bz","ca","cb","cc","cd","ce","cf","cg","ch", 
    "AA","AB","AC","AD","AE","AF","AG","AH","AI","AJ", "AK","AL","AM","AN","AO","AP","AQ","AR","AS","AT", 
    "AU","AV","AW","AX","AY","AZ","BA","BB","BC","BD","BE","BF","BG","BH","BI","BJ","BK","BL","BM","BN", 
    "bO","bP","bQ","bR","bS","bT","bU","bV","bW","bX", "bY","bZ","cA","cB","cC","cD","cE","cF","cG","cH", 
    "BO","BP","BQ","BR","BS","BT","BU","BV","BW","BX","BY","BZ","CA","CB","CC","CD","CE","CF","CG","CH", 
    "aA","aB","aC","aD","aE","aF","aG","aH","aI","aJ", "aK","aL","aM","aN","aO","aP","aQ","aR","aS","aT", 
    "aU","aV","aW","aX","aY","aZ","bA","bB","bC","bD","bE","bF","bG","bH","bI","bJ","bK","bL","bM","bN",
]

# MAIN ENCRYPTION FUNCTION (Flask calling)
def encrypt_hybrid(pText, params):
    # Params user se aayenge: u, xL, b, xG, y, xT, a, xS
    u, xL, b, xG, y, xT, a, xS = params
    pTextLen = len(pText) * 8
    valL, valG, valT, valS = xL, xG, xT, xS
    vonOnLSB = []

    # Chaos Sequence Generation
    while len(vonOnLSB) < pTextLen:
        xnL, xnG, xnT, xnS = [], [], [], []
        for i in range(len(pText)):
            valL = u * valL * (1 - valL)
            xnL.append(int((valL * 1000) % 256))
            valG = -b * valG * math.log(valG)
            xnG.append(int((valG * 1000) % 256))
            if valT < 0.5: valT = y * (valT/2)
            else: valT = y * ((1 - valT)/2)
            xnT.append(int((valT * 1000) % 256))
            valS = a * (math.sin(3.14*valS)/4)
            xnS.append(int((valS * 1000) % 256))

        for i in range(len(xnL)):
            l_xor_g = xnL[i] ^ xnG[i]
            t_xor_s = xnT[i] ^ xnS[i]
            l_lsb = bin(l_xor_g)[-1]
            t_lsb = bin(t_xor_s)[-1]
            if l_lsb == '1' and t_lsb == '0': vonOnLSB.append(1)
            elif l_lsb == '0' and t_lsb == '1': vonOnLSB.append(0)

    # Key Formatting
    vonOnLSBFin = vonOnLSB[:pTextLen]
    hex_key = [format(int(''.join(str(j) for j in vonOnLSBFin[i:i+8]), 2), "02X") for i in range(0, len(vonOnLSBFin), 8)]
    
    # Encrypted Key Generation (For transmission)
    Ka_list = generate_agent_key(u, xL, b, xG, y, xT, a, xS, len(hex_key))
    encrypted_key = ''.join(format(int(hex_key[i],16) ^ int(Ka_list[i],16), "02X") for i in range(len(hex_key)))

    # Final Text Encryption using Map
    pT_hex = [format(ord(ch), "02X") for ch in pText]
    heavy_encrypt = "".join([ascii_chars[int(hex_key[i], 16) ^ int(pT_hex[i], 16)] for i in range(len(hex_key))])

    return heavy_encrypt, encrypted_key

# MAIN DECRYPTION FUNCTION
def decrypt_hybrid(eText, enc_key_str, params):
    u, xL, b, xG, y, xT, a, xS = params
    
    # Recover Original Key
    enc_key_list = [enc_key_str[i:i+2] for i in range(0, len(enc_key_str), 2)]
    Ka_list = generate_agent_key(u, xL, b, xG, y, xT, a, xS, len(enc_key_list))
    recovered_key = [format(int(enc_key_list[i], 16) ^ int(Ka_list[i], 16), "02X") for i in range(len(enc_key_list))]

    # Extract original text from ASCII Map
    eTextLis = [eText[i:i+2] for i in range(0, len(eText), 2)]
    decrypted_text = ""
    for i in range(len(eTextLis)):
        xor_val = ascii_chars.index(eTextLis[i])
        original_char_code = xor_val ^ int(recovered_key[i], 16)
        decrypted_text += chr(original_char_code)
    
    return decrypted_text