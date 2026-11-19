/*
    企业自定义安全审计规则 B：禁止明文凭证内嵌命令行 / 连接串。

    背景：SkillSpector 内置 PE3「Credential File Access」只盯「读取敏感凭证文件路径」
    （~/.ssh、.env、.netrc 等），对「凭证出现在进程参数 / 命令行 / 连接串」这一泄露面
    无规则覆盖：chpasswd、curl -u user:pass、mysql -p 字面量、psql://user:pass@、
    redis-cli -a、通用 URL userinfo 全部 0 检出。

    本规则与 PE3 严格正交：PE3 盯文件路径，本规则盯命令行 / 连接串字面量。

    豁免（占位符，不应命中）：
      <...>、$VAR、${...}、"$VAR"、空值（-p / -a 无值）、只有用户名无 :pass（curl -u admin）。

    实现：凭证 token 首字符必须为字母或数字（[A-Za-z0-9]），从而天然豁免以 < / $ / 引号 /
    空格开头的占位符与空值。单词型占位符（xxx / YOUR_* 等）由需求清单维护，本静态规则对其
    采取 fail-closed（宁可多报），记录为已知边界。

    验证靶场：skill-dataset/security/custom-rules-range/
      正样本：SKILL.md 的 chpasswd / curl -u / mysql -p / psql 连接串 / redis -a，以及
              exfil_helper.py 的 URL userinfo 与 conn_str —— 全部应命中 HIGH
      负样本：SKILL.md 的 -p<password> / -u ${password} / -p 无值，以及
              exfil_helper.py 的 os.environ 取凭证 —— 全部不应命中
*/

rule cvte_credential_chpasswd
{
    meta:
        description = "CVTE 规则 B：echo user:pass 管道进入 chpasswd/passwd 明文改密"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $a = /echo\s+['"][^'":]*:[A-Za-z0-9][^'"]*['"]\s*[|]\s*(chpasswd|passwd)\b/ nocase
    condition:
        $a
}

rule cvte_credential_curl_basic
{
    meta:
        description = "CVTE 规则 B：curl -u user:pass 明文 Basic Auth 字面量"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $a = /curl\b[^\n]*\s-u\s+[^\s:]+:[A-Za-z0-9][^\s]*/ nocase
    condition:
        $a
}

rule cvte_credential_mysql
{
    meta:
        description = "CVTE 规则 B：mysql -p 字面量 / --password 字面量 明文密码"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $short = /mysql\b[^\n]*\s-p[A-Za-z0-9][^\s]*/ nocase
        $long = /mysql\b[^\n]*--password[=\s][A-Za-z0-9][^\s]*/ nocase
    condition:
        $short or $long
}

rule cvte_credential_redis
{
    meta:
        description = "CVTE 规则 B：redis-cli -a 字面量 明文密码"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $a = /redis-cli\b[^\n]*\s-a\s+[A-Za-z0-9][^\s]*/ nocase
    condition:
        $a
}

rule cvte_credential_mongosh
{
    meta:
        description = "CVTE 规则 B：mongosh --password 字面量 明文密码"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $a = /mongosh\b[^\n]*--password\s+[A-Za-z0-9][^\s]*/ nocase
    condition:
        $a
}

rule cvte_credential_url_userinfo
{
    meta:
        description = "CVTE 规则 B：scheme://user:pass@host 连接串 / URL userinfo 明文凭证"
        category = "malware"
        severity = "HIGH"
        confidence = "0.9"
        reference = "docs/自定义安全检测扩展需求.md §6"
    strings:
        $a = /\b[a-z][a-z0-9+.-]*:\/\/[^\s@\/:]+:[A-Za-z0-9][^\s@\/]*@/ nocase
    condition:
        $a
}
