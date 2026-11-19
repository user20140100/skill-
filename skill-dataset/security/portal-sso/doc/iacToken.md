# 接口授权中心（IAC）

## v2.0 更新内容

1. 提供了用户门户，http://iac.cvteapi.com/ ，使用域账号登陆
2. 可以查看自己名下的 app 列表，可以进行编辑，并看到该 app 被授权调用的 system 列表
3. 可以查看自己名下的 system 列表，可以进行编辑，并对自己的 system 授权做管理
4. system 授权支持整个系统授权，以及分模块授权

## 背景

随着业务发展，各系统间接口的相互调用越来越多，接口间的调用和校验方式较为混乱，出现了很多种不同的，并且不是很安全的校验方式，令人头疼。

## 思路

参考微信公众平台的接口授权方式，采用一个授权中心来统一管理。

- 被调用者拥有一个 `systemId`，由系统生成
- 调用者拥有唯一的 `appId` 和 `appSecret`
- 调用者通过 `appId` 和 `appSecret` 向授权中心请求一个 `accessToken`，`accessToken` 的有效时长为 2 小时，调用者请求时，若 `accessToken` 存在且未过期，则会自动续期，否则生成一个全新的 `accessToken` 返回。调用者需要自己缓存这个 `accessToken`，并定时续命（建议每小时更新一次）
- 调用者调用接口时，除了本身请求的基本参数之外，再把 `accessToken` 加上
- 被调用者收到请求后，提取 `accessToken`，并且向授权中心询问该 `accessToken` 是否有效，是否有权限
- 被调用者有两种类型，公共类和非公共类。对于公共类的被调用者，只要是在授权中心中注册了的调用者均有权限调用；对于非公共类的被调用者，调用者除了在授权中心注册外，还需要被调用者在授权中心进行授权（提供管理员配置界面，让被调用者配置其类型或者进行调用者的授权），才有权限。

关于 `systemId` 与 `appId`、`appSecret` 申请，可以自行到 http://iac.cvteapi.com/ 创建即可。

---

## 接口

### 获取 accessToken

**描述**：调用者获取调用凭证

**请求语法**：

```
GET https://itapis.cvte.com/iac/app/access_token HTTP/1.1
```

**请求参数**：

| 名称 | 必填 | 说明 | 来源 |
|------|------|------|------|
| appid | 是 | 系统下发的 appId | query |
| secret | 是 | 系统下发的 appSecret | query |

**响应内容**：

成功返回：返回码 200，返回数据包括 accessToken 及其过期时间。

```json
{
  "status": 200,
  "errCode": 0,
  "errMsg": "",
  "data": {
    "accessToken": "418fba21-9f7b-483a-b267-9ad4701cd4c9",
    "accessTokenExpire": 1484555205178
  }
}
```

---

### 校验 accessToken

**描述**：被调用者根据调用凭证校验权限

**请求语法**：

```
GET https://itapis.cvte.com/iac/system/verify_token HTTP/1.1
```

**请求参数**：

| 名称 | 必填 | 说明 | 来源 |
|------|------|------|------|
| systemid | 是 | 系统下发的 systemId | query |
| token | 是 | 调用者发送请求附带的 accessToken | query |
| moduleid | 否 | 模块 id，模块由自己创建，可以分模块授权。不给默认是校验整个系统的权限。 | query |

**响应内容**：

成功返回：返回码 200，返回数据包括调用者的 appId。

```json
{
  "status": 200,
  "errCode": 0,
  "errMsg": "",
  "data": {
    "appId": "0007e1f6-91c6-42be-86e5-b8eeda1a0e2d"
  }
}
```

---

### 错误码集合

| 错误码 | 错误原因 |
|--------|----------|
| 40101 | 该 app 不存在 |
| 40102 | 该 system 不存在 |
| 40103 | 该 app 权限不足 |
| 40104 | 该 token 过期或不存在 |
| 40002 | 访问频率频繁 |
| 50001 | 系统内部错误 |
| 50002 | 系统内部错误 |
| 50003 | 系统内部错误 |
