import math
import json
import os

# --- 1. Master Generation & Helper Logic ---
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
    "bO","bP","bQ","bR","bS","bT","bU","bV","bW","bX", "bY","bZ","cA","cB","cC","cd","ce","cf","cg","ch", 
    "BO","BP","BQ","BR","BS","BT","BU","BV","BW","BX","BY","BZ","CA","CB","CC","CD","CE","CF","CG","CH", 
    "aA","aB","aC","aD","aE","aF","aG","aH","aI","aJ", "aK","aL","aM","aN","aO","aP","aQ","aR","aS","aT", 
    "aU","aV","aW","aX","aY","aZ","bA","bB","bC","bD","bE","bF","bG","bH","bI","bJ","bK","bL","bM","bN",
]

def generate_agent_key(u, xL, b, xG, y, xT, a, xS, length):
    """Chaos parameters se aik unique XOR key generate karta hai."""
    temp = int((u*1000 + xL*10000 + b*1000 + xG*10000 + y*1000 + xT*1000 + a*1000 + xS*10000) % 256)
    return [format(temp, "02X")] * length

# --- 2. Hybrid Evolution Logic ---
def evolve_state(u, xL, b, xG):
    """Logistic aur Gompertz maps ko use kar ke naye parameters generate karna."""
    # Map Set A: Master Generators
    new_xL = u * xL * (1 - xL)
    # Gompertz Map calculation
    new_xG = -b * xG * math.log(xG) if xG > 0 else 0.5
    
    # Map Set B ke liye parameters generate karna (Scaling)
    new_y = 2.0 + (new_xL * 2.0)  # Tent parameter [2.0 - 4.0]
    new_a = 1.0 + (new_xG * 3.0)  # Sin parameter [1.0 - 4.0]
    
    return new_xL, new_xG, new_y, new_a

# --- 3. Core Encryption Logic ---
def encrypt_text(pText, u, xL, b, xG, y, xT, a, xS):
    """Asal message ko encrypt karne ka logic."""
    pTextLen = len(pText) * 8
    valL, valG, valT, valS = xL, xG, xT, xS
    vonOnLSB = []
    
    # Chaos sequence generation
    while len(vonOnLSB) < pTextLen:
        valL = u * valL * (1 - valL)
        valG = -b * valG * math.log(valG) if valG > 0 else 0.5
        
        # Tent Map logic
        if valT < 0.5: valT = y * (valT/2)
        else: valT = y * ((1 - valT)/2)
        
        # Sin Map logic
        valS = a * (math.sin(3.14 * valS)/4)

        # Bit extraction for key
        l_xor_g = int((valL * 1000) % 256) ^ int((valG * 1000) % 256)
        t_xor_s = int((valT * 1000) % 256) ^ int((valS * 1000) % 256)
        
        if bin(l_xor_g)[-1] == '1' and bin(t_xor_s)[-1] == '0': vonOnLSB.append(1)
        elif bin(l_xor_g)[-1] == '0' and bin(t_xor_s)[-1] == '1': vonOnLSB.append(0)

    # Convert bits to Hex Key
    vonOnLSBFin = vonOnLSB[:pTextLen]
    hex_key = [format(int(''.join(map(str, vonOnLSBFin[i:i+8])), 2), "02X") for i in range(0, len(vonOnLSBFin), 8)]
    
    # Agent Key for extra security layer
    Ka_list = generate_agent_key(u, xL, b, xG, y, xT, a, xS, len(hex_key))
    encrypted_key = ''.join(format(int(hex_key[i],16) ^ int(Ka_list[i],16), "02X") for i in range(len(hex_key)))

    # Character Substitution via ascii_chars
    pT_hex = [format(ord(ch), "02X") for ch in pText]
    heavy_encrypt = "".join([ascii_chars[int(hex_key[i], 16) ^ int(pT_hex[i], 16)] for i in range(len(hex_key))])
    
    return heavy_encrypt, encrypted_key

# --- 4. Core Decryption Logic ---
def decrypt_text(eText, deCryptKey, u, xL, b, xG, y, xT, a, xS):
    """Encrypted message ko wapis parhne ka logic."""
    enc_key_list = [deCryptKey[i:i+2] for i in range(0, len(deCryptKey), 2)]
    Ka_list = generate_agent_key(u, xL, b, xG, y, xT, a, xS, len(enc_key_list))
    recovered_key = [format(int(enc_key_list[i], 16) ^ int(Ka_list[i], 16), "02X") for i in range(len(enc_key_list))]
    
    eTextLis = [eText[i:i+2] for i in range(0, len(eText), 2)]
    decrypted = ""
    for i in range(len(eTextLis)):
        xor_val = ascii_chars.index(eTextLis[i])
        decrypted += chr(xor_val ^ int(recovered_key[i], 16))
    return decrypted

# --- 5. Hybrid Integration for Flask ---
def encrypt_hybrid(plain_text, state):
    """Flask app ke liye main interface jo state management karta hai."""
    # Step 1: Evolve state to get current params
    next_xL, next_xG, y, a = evolve_state(state['u'], state['xL'], state['b'], state['xG'])
    
    # Step 2: Encrypt using evolved params
    enc_text, enc_key = encrypt_text(
        plain_text, state['u'], state['xL'], state['b'], state['xG'], 
        y, state['xT'], a, state['xS']
    )
    
    # Step 3: Update state for next session
    new_state = state.copy()
    new_state['xL'], new_state['xG'] = next_xL, next_xG
    # Increase counter for synchronization
    new_state['msg_counter'] = state.get('msg_counter', 0) + 1
    
    return enc_text, enc_key, new_state