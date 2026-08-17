# ============================================================
# 路径还原脚本 (restore_paths.ps1)
# ============================================================
# 作用：
#   查看店铺巡检动作 JSON 中的硬编码路径已在上传前替换为占位符：
#     {{QUICKER_ROOT}}  -> 项目资源根目录（原为 D:\Users\Administrator\Desktop）
#     {{ZINIAO_EXE}}    -> 紫鸟浏览器可执行文件路径
#   本脚本把占位符替换为你在本机上的真实路径，使动作可以正常导入运行。
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File restore_paths.ps1
#   或直接右键"使用 PowerShell 运行"。
#
# 说明：
#   1) 脚本会自动检测本机是否存在紫鸟浏览器（默认安装位置），
#      找不到时手动输入路径即可（留空则保持占位符不变）。
#   2) 生成的还原版 JSON 默认保存为 查看店铺巡检动作_本机路径版.json，
#      不会覆盖仓库中的可移植版，方便随时重新还原。
# ============================================================

param(
    [string]$ActionFile = (Join-Path $PSScriptRoot "action\查看店铺巡检动作.json"),
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ActionFile)) {
    Write-Host "[错误] 找不到动作文件: $ActionFile" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path $PSScriptRoot ("action\查看店铺巡检动作_本机路径版.json")
}

$content = Get-Content -Path $ActionFile -Raw -Encoding UTF8

# ---------- 1. 紫鸟浏览器路径 ----------
Write-Host ""
Write-Host "=== 紫鸟浏览器路径设置 ===" -ForegroundColor Cyan
$ziniao = "C:\Program Files\ziniao\ziniao.exe"
if (Test-Path $ziniao) {
    Write-Host "检测到默认安装路径: $ziniao"
} else {
    $ziniao = ""
    Write-Host "未检测到默认安装路径，请手动输入紫鸟浏览器 ziniao.exe 的完整路径（直接回车跳过）："
    $input = Read-Host
    if (-not [string]::IsNullOrWhiteSpace($input)) { $ziniao = $input.Trim('"') }
}

if (-not [string]::IsNullOrEmpty($ziniao)) {
    if (Test-Path $ziniao) {
        # JSON 字符串中反斜杠需要转义为双反斜杠
        $escaped = $ziniao.Replace('\', '\\')
        $content = $content.Replace('{{ZINIAO_EXE}}', $escaped)
        Write-Host "已替换 {{ZINIAO_EXE}} -> $ziniao" -ForegroundColor Green
    } else {
        Write-Host "[警告] 路径不存在，保持占位符不变: $ziniao" -ForegroundColor Yellow
    }
} else {
    Write-Host "未设置紫鸟路径，保持 {{ZINIAO_EXE}} 占位符不变（需在 Quicker 中手动设置）" -ForegroundColor Yellow
}

# ---------- 2. 资源根目录 ----------
Write-Host ""
Write-Host "=== 项目资源根目录设置 ===" -ForegroundColor Cyan
Write-Host "资源根目录需包含以下子目录："
Write-Host "  组件库\quicker位图\    (图像识别位图)"
Write-Host "  需改密码栏目\         (登录异常图标)"
Write-Host "  RMS记录\              (RMS截图输出)"
Write-Host "  邮件记录\             (邮件截图输出)"
Write-Host "  无人店铺操作表格.xlsx   (店铺巡检数据表)"
Write-Host ""
Write-Host "请输入资源根目录（例如 D:\项目\quicker-shop-inspection，直接回车使用仓库根目录）："
$root = Read-Host

if ([string]::IsNullOrWhiteSpace($root)) {
    $root = $PSScriptRoot
    Write-Host "使用仓库根目录: $root"
}

$root = $root.Trim('"').TrimEnd('\')

if (Test-Path $root) {
    $escapedRoot = $root.Replace('\', '\\')
    $content = $content.Replace('{{QUICKER_ROOT}}', $escapedRoot)
    Write-Host "已替换 {{QUICKER_ROOT}} -> $root" -ForegroundColor Green
} else {
    Write-Host "[错误] 目录不存在: $root" -ForegroundColor Red
    exit 1
}

# ---------- 3. 校验并写出 ----------
$remainingRoot = ([regex]::Matches($content, '{{QUICKER_ROOT}}')).Count
$remainingZiniao = ([regex]::Matches($content, '{{ZINIAO_EXE}}')).Count

try {
    $null = $content | ConvertFrom-Json
    Write-Host ""
    Write-Host "JSON 校验通过" -ForegroundColor Green
} catch {
    Write-Host "[错误] JSON 校验失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Set-Content -Path $OutputFile -Value $content -Encoding UTF8
Write-Host ""
Write-Host "还原完成！输出文件: $OutputFile" -ForegroundColor Green
Write-Host "剩余未替换占位符：{{QUICKER_ROOT}} x $remainingRoot, {{ZINIAO_EXE}} x $remainingZiniao"
Write-Host "在 Quicker 中导入 $OutputFile 即可使用。"
Write-Host ""
