<!--
 * @Author: huangweihong huangweihong@cvte.com
 * @Date: 2026-03-17 10:56:38
 * @LastEditors: huangweihong huangweihong@cvte.com
 * @LastEditTime: 2026-03-17 10:56:45
 * @FilePath: /tz-app/Users/huangweihong/work/skills/portal-sso-skills/doc/备注.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->

SSO 流程
方案：用户直接访问目标业务系统，利用门户做权限校验

1、目标业务系统通过 cookie 校验用户会话是否过期，若过期，则需要跳转至门户提供的 oauth 接口，并带上门户派发的 appId 和重定向地址

2、用户在门户登陆授权后，如果具有访问目标业务系统的权限，则会跳转至上一步所提供的重定向地址，并携带 ticket，ticket 有效期为 120 秒

3、目标业务系统获取到 ticket，再加上门户派发的 appId，调用门户提供的 ticket 校验接口，换取用户信息和 jwt

4、目标业务系统获取到用户信息和 jwt 之后，自行设置 cookie，保存用户会话

注：门户返回的 jwt 是对接统一 jwt 服务的，目标系统可以在合适的时候自行调用 jwt 服务提供的刷新接口

SSO 对接
准备工作

测试环境联系 黄威鸿 ，正式环境在itsm上提单给IT客服，开通应用对接权限，提供的信息包括

1、应用类型：可选值为为 公共、研发、商务、供应链、其他

2、应用名称：如ZPB

3、应用描述：如校园招聘管理系统

4、是否展示在门户的应用列表：如果选择展示，则用户登录门户时会在应用列表中看到该应用（有权限时）

5、应用访问地址：从应用列表点击后跳转的地址，如果采用方式一，则需要提供 SSO 初始化接口的地址，否则直接提供应用访问地址

6、可见范围：全员、或者某个组织架构、或者某些员工，根据实际需要提供
