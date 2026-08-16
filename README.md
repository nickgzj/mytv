# 我的精选 IPTV

自动从 iptv-org 的 `index.m3u` 筛选并生成一个适合影视仓/TiviMate 的精选 M3U。

分组：
- CCTV
- 地方卫视
- 台湾
- 日本
- BBC
- 美国新闻财经

默认排除 iptv-org 标记为 `[Geo-blocked]` 和 `[Not 24/7]` 的线路，并保留频道 Logo、tvg-id 等信息。

## 自动更新
GitHub Actions 每天自动运行一次，也可以在 Actions 页面手动运行 `Update my IPTV playlist`。

将整个目录上传到自己的 GitHub 仓库后，开启 Actions。随后可通过 GitHub Raw / GitHub Pages 使用 `mytv.m3u`。

示例 Raw 地址：
`https://raw.githubusercontent.com/你的用户名/你的仓库/main/mytv.m3u`

注意：iptv-org 的公开流会变化，自动更新只能更新列表中的地址，不能保证每条流长期可播；部分频道存在地区限制。
