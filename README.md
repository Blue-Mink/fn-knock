# fn-knock for fnOS（飞牛定制版）

[敲门knock (fn-knock)](https://www.fnknock.cn/) 的飞牛 fnOS 应用中心（FPK）定制打包。

上游引擎与官方 FPK 由 [kci-lnk/fn-knock-turborepo](https://github.com/kci-lnk/fn-knock-turborepo) 提供（本仓库不修改任何业务逻辑、服务端二进制仅做窗口标题字符串的等长替换）。本项目在上游官方包基础上做了 **fnOS 使用体验定制**，版本号在官方 `2.4.12` 之后追加第四位区分。

## 当前版本

| | |
|---|---|
| 包版本 | **2.4.12.7**（基于官方 2.4.12）|
| FPK 下载 | [Releases](../../releases/latest) |
| SHA256 | `b6b7ab0c6daedaccee99901830cd0eed70bd90fb3915b361b56c8ca57c641aa2` |

## 桌面三入口

| 图标 | 行为 |
|---|---|
| 敲门knock | 官方控制台（原样）|
| 敲门应用 | **全屏应用图标页**：直达已配置应用，无需进入控制台、无需登录 |
| 敲门门户 | knock 原生门户（7999），窗口标题显示「敲门门户」|

## 定制内容（相对官方 FPK）

1. **全屏应用页**：控制台注入（仅 `?apps=1` 触发）——自动打开「应用」弹窗并整页化：隐藏控制台外壳、弹窗标题栏与关闭按钮；普通控制台入口零影响
2. **应用图标官方圆角**：应用页图标底板按飞牛官方 squircle（连续曲率超椭圆）曲线裁切（`mask-image`，mask 见 `assets/`），非普通圆角矩形
3. **门户窗口标题**：`go-reauth-proxy` 二进制**等长字符串补丁**——中文标题「选择访问入口」→「敲门门户」、6 处 ` - Go Reauth Proxy` 标题后缀移除；不改任何逻辑（补丁有版本锚点断言，官方升级后需重新核对锚点）
4. **桌面图标**：官方 squircle 圆角重制（沿用上游图案，5 个落点全量替换）
5. **manifest**：开发者链接指向 fn-knock-turborepo 项目、发布者链接 `https://www.fnknock.cn`

## 安装

1. 从 [Releases](../../releases/latest) 下载 `fn-knock-2.4.12.7-fnos-amd64.fpk`
2. 飞牛 应用中心 → 手动安装 → 选择 FPK
3. 向导端口保持默认即可：管理后端 `7998`、认证 `7997`、Go 管理 `7996`、Go 代理/门户 `7999`

> 更换过桌面图标后如果仍显示旧图：图标有 7 天强缓存，浏览器 `Ctrl+Shift+R` 强刷或退出重进桌面。

## 从源码构建

依赖：Python 3 + Pillow。

1. 获取上游官方 fnOS 包（v2.4.12.x）：https://github.com/kci-lnk/fn-knock-turborepo/releases
2. 构建：

   ```bash
   pip install pillow
   python3 scripts/build.py /path/to/official/fn-knock-xxx.fpk
   # 产出 dist/fn-knock-2.4.12.7-fnos-amd64.fpk
   ```

   脚本会校验上游字符串锚点（i18n / HTML 模板），官方大版本更新导致锚点变化时会直接报错而不是产出坏包。

## 仓库结构

```
assets/    注入素材（应用页 CSS/JS、官方 squircle mask）
scripts/   build.py 可复现构建脚本
dist/      本地构建产物（不入库，发布物在 Releases）
```

## 上游与致谢

- 官网：https://www.fnknock.cn/
- 文档：https://docs.fnknock.cn/
- 源码 / 作者：[kci-lnk/fn-knock-turborepo](https://github.com/kci-lnk/fn-knock-turborepo)
- QQ 群：1081609274

本仓库仅是 fnOS 打包与体验适配，knock 本体版权归原作者 kci-lnk 所有，遵循其上游许可证。
