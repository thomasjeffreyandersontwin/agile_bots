# Story IO PowerShell Wrapper Script
# Wrapper script for story_io CLI operations that handles path resolution and parameter passing
#
# Usage Examples:
#   .\story-io.ps1 render-outline -StoryGraph "demo/mm3e_animations/docs/story_graph.json" -Output "demo/mm3e_animations/docs/story-map-outline.drawio"
#   .\story-io.ps1 render-increments -StoryGraph "demo/mm3e_animations/docs/story_graph.json" -Output "demo/mm3e_animations/docs/story-map-increments.drawio"
#   .\story-io.ps1 sync-outline -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" -Original "demo/mm3e_animations/docs/story_graph.json" -Output "demo/mm3e_animations/docs/story_graph_synced.json"
#   .\story-io.ps1 search -StoryGraph "demo/mm3e_animations/docs/story_graph.json" -Query "Power" -Type "story"
#   .\story-io.ps1 add-user -StoryGraph "demo/mm3e_animations/docs/story_graph.json" -StoryName "Receive Power Characteristics" -UserName "GM" -Output "demo/mm3e_animations/docs/story-map-outline.drawio"
#   .\story-io.ps1 add-user -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" -UserName "GM" (adds to all stories, StoryName optional)
#   .\story-io.ps1 add-user -StoryGraph "demo/mm3e_animations/docs/story_graph.json" -UserName "GM" (adds to all stories, StoryName optional)

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('render-outline', 'render-increments', 'sync-outline', 'sync-increments', 'search', 'add-user', 'merge')]
    [string]$Command,
    
    # Common parameters
    [string]$StoryGraph,
    [string]$Json,
    [string]$DrawIOFile,
    [string]$Output,
    [string]$Layout,
    [string]$Original,
    
    # Search parameters
    [string]$Query,
    [ValidateSet('any', 'epic', 'feature', 'story')]
    [string]$Type,
    
    # Add user parameters
    [string]$StoryName,
    [string]$UserName,
    [string]$EpicName,
    [string]$FeatureName,
    
    # Merge parameters
    [string]$Extracted,
    [string]$ReportPath
)

# Get script directory and workspace root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptDir = if ([System.IO.Path]::IsPathRooted($ScriptDir)) { $ScriptDir } else { Resolve-Path $ScriptDir }

# Try to find workspace root by looking for common markers
$CurrentDir = $ScriptDir
$WorkspaceRoot = $null

# First, try going up from script directory to find workspace root
while ($CurrentDir) {
    $GitMarker = Join-Path $CurrentDir ".git"
    $DemoMarker = Join-Path $CurrentDir "demo"
    $AgileBotMarker = Join-Path $CurrentDir "agile_bot"
    
    if ((Test-Path $GitMarker) -or (Test-Path $DemoMarker) -or (Test-Path $AgileBotMarker)) {
        $WorkspaceRoot = $CurrentDir
        break
    }
    
    $Parent = Split-Path -Parent $CurrentDir
    if ($Parent -eq $CurrentDir) { break }
    $CurrentDir = $Parent
}

# Fallback to current working directory if not found
if (-not $WorkspaceRoot) {
    $WorkspaceRoot = Get-Location
    Write-Warning "Could not detect workspace root, using current directory: $WorkspaceRoot"
}

Write-Verbose "Workspace root: $WorkspaceRoot"
Write-Verbose "Script directory: $ScriptDir"

# Resolve Python module path
$StoryIOModulePath = Split-Path -Parent $ScriptDir

# Resolve paths relative to workspace root
function Resolve-StoryPath {
    param(
        [string]$Path,
        [switch]$MustExist
    )
    if ([string]::IsNullOrEmpty($Path)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Path)) { 
        if ($MustExist -and -not (Test-Path $Path)) {
            Write-Error "File not found: $Path"
            return $null
        }
        return $Path 
    }
    $Resolved = Join-Path $WorkspaceRoot $Path
    if ($MustExist -and -not (Test-Path $Resolved)) {
        Write-Error "File not found: $Resolved"
        return $null
    }
    return $Resolved
}

# Handle custom commands - just pass through to Python CLI
if ($Command -eq 'add-user') {
    # Build Python CLI arguments
    $PythonArgs = @("add-user", "--user-name", $UserName)
    
    if ($StoryGraph) {
        $ResolvedPath = Resolve-StoryPath -Path $StoryGraph -MustExist
        if ($ResolvedPath) {
            $PythonArgs += "--story-graph", $ResolvedPath
        } else {
            exit 1
        }
    }
    
    if ($DrawIOFile) {
        $ResolvedPath = Resolve-StoryPath -Path $DrawIOFile -MustExist
        if ($ResolvedPath) {
            $PythonArgs += "--drawio-file", $ResolvedPath
        } else {
            exit 1
        }
    }
    
    if ($StoryName) {
        $PythonArgs += "--story-name", $StoryName
    }
    
    if ($EpicName) {
        $PythonArgs += "--epic-name", $EpicName
    }
    
    if ($FeatureName) {
        $PythonArgs += "--feature-name", $FeatureName
    }
    
    if ($Output) {
        $ResolvedPath = Resolve-StoryPath -Path $Output
        if ($ResolvedPath) {
            $PythonArgs += "--output", $ResolvedPath
        }
    }
    
    # Call Python CLI - let it handle validation and errors
    $env:PYTHONPATH = $StoryIOModulePath
    & python -m story_io.story_io_cli $PythonArgs
    exit $LASTEXITCODE
}

if ($Command -eq 'merge') {
    # Build Python CLI arguments - let Python handle validation
    $PythonArgs = @("merge")
    
    if ($Extracted) {
        $ResolvedPath = Resolve-StoryPath -Path $Extracted -MustExist
        if ($ResolvedPath) {
            $PythonArgs += "--extracted", $ResolvedPath
        } else {
            exit 1
        }
    }
    
    if ($Original) {
        $ResolvedPath = Resolve-StoryPath -Path $Original -MustExist
        if ($ResolvedPath) {
            $PythonArgs += "--original", $ResolvedPath
        } else {
            exit 1
        }
    }
    
    if ($Output) {
        $ResolvedPath = Resolve-StoryPath -Path $Output
        if ($ResolvedPath) {
            $PythonArgs += "--output", $ResolvedPath
        }
    }
    
    if ($ReportPath) {
        $ResolvedPath = Resolve-StoryPath -Path $ReportPath
        if ($ResolvedPath) {
            $PythonArgs += "--report-path", $ResolvedPath
        }
    }
    
    # Call Python CLI - let it handle validation and errors
    $env:PYTHONPATH = $StoryIOModulePath
    & python -m story_io.story_io_cli $PythonArgs
    exit $LASTEXITCODE
}

# Build Python command arguments for standard CLI commands (using module invocation)
$PythonArgs = @("-m", "story_io.story_io_cli", $Command)

# Add common parameters
if (-not [string]::IsNullOrEmpty($StoryGraph)) {
    $ResolvedPath = Resolve-StoryPath -Path $StoryGraph -MustExist
    if (-not $ResolvedPath) { exit 1 }
    $PythonArgs += "--story-graph"
    $PythonArgs += $ResolvedPath
}

if (-not [string]::IsNullOrEmpty($Json)) {
    $ResolvedPath = Resolve-StoryPath -Path $Json -MustExist
    if (-not $ResolvedPath) { exit 1 }
    $PythonArgs += "--json"
    $PythonArgs += $ResolvedPath
}

if (-not [string]::IsNullOrEmpty($DrawIOFile)) {
    $ResolvedPath = Resolve-StoryPath -Path $DrawIOFile
    $PythonArgs += "--drawio-file"
    $PythonArgs += $ResolvedPath
}

if (-not [string]::IsNullOrEmpty($Output)) {
    $ResolvedPath = Resolve-StoryPath -Path $Output
    $PythonArgs += "--output"
    $PythonArgs += $ResolvedPath
}

if (-not [string]::IsNullOrEmpty($Layout)) {
    $ResolvedPath = Resolve-StoryPath -Path $Layout -MustExist
    if (-not $ResolvedPath) { exit 1 }
    $PythonArgs += "--layout"
    $PythonArgs += $ResolvedPath
}

if (-not [string]::IsNullOrEmpty($Original)) {
    $ResolvedPath = Resolve-StoryPath -Path $Original -MustExist
    if (-not $ResolvedPath) { exit 1 }
    $PythonArgs += "--original"
    $PythonArgs += $ResolvedPath
}

# Command-specific parameters
if ($Command -eq 'search') {
    if ($Query) {
        $PythonArgs += $Query
    }
    if ($Type) {
        $PythonArgs += "--type"
        $PythonArgs += $Type
    }
}

# Verify Python module path exists
if (-not (Test-Path $StoryIOModulePath)) {
    Write-Error "Story IO module path not found: $StoryIOModulePath"
    exit 1
}

# Set PYTHONPATH to include the parent directory for module imports
$Env:PYTHONPATH = $StoryIOModulePath

# Execute Python command as a module
$PythonCommand = "python $($PythonArgs -join ' ')"

Write-Host "Executing: $PythonCommand" -ForegroundColor Cyan
Write-Verbose "PYTHONPATH: $Env:PYTHONPATH"

Invoke-Expression $PythonCommand

exit $LASTEXITCODE

