"""
鸿蒙应用开发MCP服务
"""

from mcp.server import FastMCP

mcp = FastMCP("harmonyos-mcp")


@mcp.tool()
def get_config_env_pwsh() -> str:
    """
    获取配置HarmonyOS应用开发环境的PowerShell命令。
    执行成功后使能：命令行构建工具（hvigorw）、命令行调试工具（hdc）等。
    """
    return r'$d=(gcm devecostudio64.exe).Source -replace "\bin\devecostudio64.exe","";$p=@("$d\tools\node","$d\tools\ohpm\bin","$d\tools\hvigor\bin","$d\sdk\default\openharmony\toolchains");[Environment]::SetEnvironmentVariable("Path",(@([Environment]::GetEnvironmentVariable("Path","User") -split ";"|Where-Object {$_ -and $p -notcontains $_})+$p)-join ";","User");[Environment]::SetEnvironmentVariable("DEVECO_SDK_HOME","$d\sdk","User");$env:Path=(@($env:Path -split ";"|Where-Object {$_ -and $p -notcontains $_})+$p)-join ";";$env:DEVECO_SDK_HOME="$d\sdk";'


@mcp.tool()
def get_build_cmd_prefix() -> str:
    """
    获取HarmonyOS应用构建命令前缀
    """
    return 'hvigorw'


if __name__ == "__main__":
    mcp.run()