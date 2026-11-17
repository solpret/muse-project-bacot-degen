import json, base64, struct, subprocess, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paper_lp_dlmm import dlmm_L_for_capital, bin_bounds

HERE = os.path.dirname(os.path.abspath(__file__))

def rpc(method, params, timeout=90):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    r = subprocess.run(["curl","-s","-m",str(timeout),"-X","POST","https://api.mainnet-beta.solana.com",
                        "-H","Content-Type: application/json","-d",payload], capture_output=True, text=True)
    return json.loads(r.stdout)

PROGRAM = "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"

def fetch(pool_addr, path):
    if os.path.exists(path):
        return json.load(open(path))
    res = rpc("getProgramAccounts", [PROGRAM, {"encoding": "base64", "filters": [
        {"dataSize": 10136}, {"memcmp": {"offset": 24, "bytes": pool_addr}}]}])
    out = []
    for a in res.get("result", []):
        data = base64.b64decode(a["account"]["data"][0])
        idx = struct.unpack_from("<q", data, 8)[0]
        for i in range(70):
            off = 56 + i*144
            ax = struct.unpack_from("<Q", data, off)[0]
            ay = struct.unpack_from("<Q", data, off+8)[0]
            price = int.from_bytes(data[off+16:off+32], "little")
            liq = int.from_bytes(data[off+32:off+48], "little")
            out.append({"bin_id": idx*70+i, "amount_x": ax, "amount_y": ay, "price_u128": price, "liq": liq})
    json.dump(out, open(path, "w"))
    return out

for name, pool, active, reserve_usd, pos_usd in [
    ("stank", "91iHWaWXneUyoNDJhSno7ezxQg1VW5P6PdarNGyFfPCz", -369, 141996, 12.19),
    ("amd",   "3uijTWAzhQKnqZ59Wwgay7sccFWAk5reEibKg2ZRAGZ9", -497, 16149, 12.19)]:
    bins = fetch(pool, os.path.join(HERE, f"bin_arrays_{name}.json"))
    bd = {b["bin_id"]: b for b in bins}
    print(f"== {name.upper()}: {len(bins)} bin, aktif {active} ==")
    for k in [active-1, active, active+1]:
        b = bd.get(k)
        if not b: print(f"  {k}: tidak ada"); continue
        praw = (1.01**k)*1e-3
        p64 = b["price_u128"]/2**64
        print(f"  bin {k}: amount_x {b['amount_x']:.3e} amount_y {b['amount_y']:.3e} liq {b['liq']:.3e} | price_u128/2^64={p64:.6e} price_raw={praw:.6e} rasio={p64/praw:.4f}")
    # cek hubungan liq vs amount dgn harga Q64.64: bin di bawah aktif (Y saja)
    print("  cek liq* (sqrt(p_hi)-sqrt(p_lo)) / amount_y  (harus ~1 bila liq=amount/w):")
    for k in [active-1, active-5, active-20, active-100]:
        b = bd.get(k)
        if not b or b["amount_y"] == 0: continue
        p_lo = bd[k]["price_u128"]/2**64
        p_hi = bd[k+1]["price_u128"]/2**64 if k+1 in bd else p_lo*1.01
        w = math.sqrt(p_hi)-math.sqrt(p_lo)
        print(f"   bin {k}: {b['liq']*w/b['amount_y']:.4f}")
    print("  cek liq* (1/sqrt(p_lo)-1/sqrt(p_hi)) / amount_x  (bin di atas aktif, X saja):")
    for k in [active+1, active+5, active+20, active+100]:
        b = bd.get(k)
        if not b or b["amount_x"] == 0: continue
        p_lo = bd[k]["price_u128"]/2**64
        p_hi = bd[k+1]["price_u128"]/2**64 if k+1 in bd else p_lo*1.01
        w = 1/math.sqrt(p_lo)-1/math.sqrt(p_hi)
        print(f"   bin {k}: {b['liq']*w/b['amount_x']:.4f}")
