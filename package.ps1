# Define exclusion lists
$excludeItems = @("node_modules", ".git", "__pycache__", ".DS_Store", ".venv", "dist", "tmp")

# Create a temporary deployment directory
$deployDir = "addoc_deploy"
if (Test-Path $deployDir) {
    Remove-Item -Path $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Function to copy files with exclusion
function Copy-WithExclude {
    param (
        [string]$Source,
        [string]$Destination
    )
    
    # Create destination directory if it doesn't exist
    if (!(Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination | Out-Null
    }
    
    Get-ChildItem -Path $Source | ForEach-Object {
        $item = $_
        if ($excludeItems -notcontains $item.Name) {
            if ($item.PSIsContainer) {
                # Recursively copy directories
                Copy-WithExclude -Source $item.FullName -Destination (Join-Path $Destination $item.Name)
            } else {
                # Copy files
                Copy-Item -Path $item.FullName -Destination $Destination
            }
        }
    }
}

Write-Host "Packaging project..."

# Copy Backend
Write-Host "Copying backend..."
Copy-WithExclude -Source "backend" -Destination (Join-Path $deployDir "backend")

# Copy Frontend
Write-Host "Copying frontend..."
Copy-WithExclude -Source "frontend" -Destination (Join-Path $deployDir "frontend")

# Copy Config Files
Write-Host "Copying config files..."
Copy-Item "nginx.conf" -Destination $deployDir
Copy-Item "docker-compose.yml" -Destination $deployDir

# Create Zip
$zipFile = "addoc_deploy.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Write-Host "Creating archive..."
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipFile

# Cleanup
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "Done! Deployment package created at: $PWD\$zipFile"
