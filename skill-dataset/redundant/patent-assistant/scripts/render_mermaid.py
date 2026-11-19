# -*- coding: utf-8 -*-
"""提取 md 中的 mermaid 代码块并渲染为 PNG（mermaid.ink 在线渲染，无需本地依赖）

用法: python3 render_mermaid.py <md文件> [-o 输出目录] [--names 名1,名2,...]
产出: <输出目录>/render_fig1_<名>.png ...（幂等：已存在且非空则跳过）

备选方案（离线）：mermaid.ink 不可达时，本地安装：
  npm install @mermaid-js/mermaid-cli
  node_modules/.bin/mmdc -i x.mmd -o x.png -w 1500 -b white \
    -p puppeteer-config.json  # 需指定 chrome 路径与 --no-sandbox
"""
import argparse, base64, glob, os, re, sys, time, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file")
    ap.add_argument("-o", "--outdir", default=".")
    ap.add_argument("--names", default=None, help="逗号分隔的自定义图名（按出现顺序）")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    content = open(args.md_file, encoding="utf-8").read()
    blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
    if not blocks:
        print("未找到 mermaid 代码块"); return

    names = args.names.split(",") if args.names else [f"fig{i+1}" for i in range(len(blocks))]
    ok, fail = 0, []
    for i, block in enumerate(blocks):
        name = names[i] if i < len(names) else f"fig{i+1}"
        out = os.path.join(args.outdir, f"render_{name}.png")
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print(f"↷ 跳过已存在: {out}"); ok += 1; continue
        b64 = base64.urlsafe_b64encode(block.strip().encode()).decode()
        url = f"https://mermaid.ink/img/{b64}?type=png&width=1500&bgColor=white"
        success = False
        for attempt in range(3):  # 重试3次
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                data = urllib.request.urlopen(req, timeout=60).read()
                open(out, "wb").write(data)
                print(f"✓ {name} ({len(data)//1024}KB)"); success = True; break
            except Exception as e:
                if attempt == 2: print(f"✗ {name}: {e}")
                time.sleep(2)
        if success: ok += 1
        else: fail.append(name)
        time.sleep(1)

    print(f"\n成功 {ok}/{len(blocks)}" + (f"，失败: {fail}" if fail else ""))
    if fail:
        print("失败的图可直接重跑本脚本（幂等补缺），或改用本地 mmdc 方案（见文件头注释）")
        sys.exit(1)

if __name__ == "__main__":
    main()
