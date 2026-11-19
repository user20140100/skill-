"""diff-analysis-report 固化脚本：用例文案特征串批量预检索。

用法: python -I grep_features.py <xmind解析txt> <仓库目录> <目标分支> <输出md> [pathspec...]
- 从解析 txt 中提取引号文案（「」/“”/""，长度>=4），过滤纯数字/IP/标记串
- 对目标分支执行一次 `git grep -n -F -e <串1> -e <串2> ...`，按特征串归组命中
- 产出 markdown 命中表（命中 file:line / 未命中清单），供判定子代理做语义甄别（命中≠实现），
  不必逐条现场 grep
"""
import sys
import re
import subprocess
from pathlib import Path


def extract_strings(dump_text):
    raw = []
    raw += re.findall(r'「([^」\n]{2,80})」', dump_text)
    raw += re.findall(r'“([^”\n]{2,80})”', dump_text)
    raw += re.findall(r'"([^"\n]{2,80})"', dump_text)
    seen, out = set(), []
    for s in raw:
        s = s.strip()
        if not s or s in seen:
            continue
        seen.add(s)
        if "【" in s or "】" in s:
            continue
        has_cjk = bool(re.search(r'[一-鿿]', s))
        # 纯数字/IP/坐标类噪声
        if re.fullmatch(r'[\d\.\s\-:]+', s):
            continue
        # 短英文串（如 admin、KDS32）grep 价值低
        if not has_cjk and len(s) < 4:
            continue
        # 短中文串（<4 字）按钮词如「下一步」「已选」噪声大
        if has_cjk and len(re.findall(r'[一-鿿]', s)) < 3 and len(s) < 6:
            continue
        out.append(s)
    return out


def main():
    dump_path, repo, branch, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    pathspecs = sys.argv[5:]
    dump_text = Path(dump_path).read_text(encoding="utf-8")
    strings = extract_strings(dump_text)

    cmd = ["git", "-c", "core.quotepath=false", "grep", "-n", "-F"]
    for s in strings:
        cmd += ["-e", s]
    cmd += [branch, "--"] + pathspecs
    p = subprocess.run(cmd, cwd=repo, capture_output=True)
    hits_raw = p.stdout.decode("utf-8", errors="replace").splitlines()

    hits = {s: [] for s in strings}
    for line in hits_raw:
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        _ref, path, lineno, text = parts
        for s in strings:
            if s in text and len(hits[s]) < 5:
                hits[s].append("%s:%s" % (path, lineno))

    lines = ["# 特征串命中表（%s @ %s，共 %d 个特征串）" % (repo, branch, len(strings)), ""]
    miss = []
    for s in strings:
        if hits[s]:
            lines.append("- `%s` -> %s" % (s, "；".join(hits[s])))
        else:
            miss.append(s)
    lines.append("")
    lines.append("## 未命中（%d 个，候选实现缺失/文案不符证据，需读上下文复核）" % len(miss))
    for s in miss:
        lines.append("- `%s`" % s)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    sys.exit(0)


if __name__ == "__main__":
    main()
