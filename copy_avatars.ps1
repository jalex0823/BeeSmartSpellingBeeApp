# PowerShell script to copy avatar files with correct names
# Copies from source to static/assets/avatars/

$sourceBase = "C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\Avatars\3D Avatar Files"
$targetBase = "static\assets\avatars"

# Avatar mappings (folder -> avatar-id)
$avatars = @{
    "AlBee" = "al-bee"
    "AnxiousBee" = "anxious-bee"
    "BikerBee" = "biker-bee"
    "BrotherBee" = "brother-bee"
    "BuilderBee" = "builder-bee"
    "CoolBee" = "cool-bee"
    "DivaBee" = "diva-bee"
    "DoctorBee" = "doctor-bee"
    "ExplorerBee" = "explorer-bee"
    "KnightBee" = "knight-bee"
    "MascotBee" = "mascot-bee"
    "MonsterBee" = "monster-bee"
    "ProfessorBee" = "professor-bee"
    "QueenBee" = "queen-bee"
    "RoboBee" = "robo-bee"
    "RockerBee" = "rocker-bee"
    "Seabea" = "seabea"
    "Superbee" = "superbee"
}

Write-Host ("=" * 80)
Write-Host "📦 COPYING AVATAR FILES" -ForegroundColor Cyan
Write-Host ("=" * 80)
Write-Host ""

$copiedCount = 0
$failedCount = 0

foreach ($folder in $avatars.Keys) {
    $avatarId = $avatars[$folder]
    $srcDir = Join-Path $sourceBase $folder
    $dstDir = Join-Path $targetBase $avatarId
    
    # Create target directory
    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    
    Write-Host "📁 $folder -> $avatarId" -ForegroundColor Yellow
    
    # Copy .obj file
    $objFile = "$folder.obj"
    $srcObj = Join-Path $srcDir $objFile
    $dstObj = Join-Path $dstDir $objFile
    
    if (Test-Path $srcObj) {
        Copy-Item -Path $srcObj -Destination $dstObj -Force
        $sizeMB = [math]::Round((Get-Item $dstObj).Length / 1MB, 2)
        Write-Host "   ✅ $objFile ($sizeMB MB)" -ForegroundColor Green
        $copiedCount++
    } else {
        Write-Host "   ❌ $objFile - NOT FOUND" -ForegroundColor Red
        $failedCount++
    }
    
    # Copy .mtl file
    $mtlFile = "$folder.mtl"
    $srcMtl = Join-Path $srcDir $mtlFile
    $dstMtl = Join-Path $dstDir $mtlFile
    
    if (Test-Path $srcMtl) {
        Copy-Item -Path $srcMtl -Destination $dstMtl -Force
        Write-Host "   ✅ $mtlFile" -ForegroundColor Green
        $copiedCount++
    } else {
        Write-Host "   ⚠️ $mtlFile - NOT FOUND" -ForegroundColor Yellow
        $failedCount++
    }
    
    # Copy texture .png file
    $texFile = "$folder.png"
    $srcTex = Join-Path $srcDir $texFile
    $dstTex = Join-Path $dstDir $texFile
    
    if (Test-Path $srcTex) {
        Copy-Item -Path $srcTex -Destination $dstTex -Force
        $sizeMB = [math]::Round((Get-Item $dstTex).Length / 1MB, 2)
        Write-Host "   ✅ $texFile ($sizeMB MB)" -ForegroundColor Green
        $copiedCount++
    } else {
        Write-Host "   ⚠️ $texFile - NOT FOUND" -ForegroundColor Yellow
        $failedCount++
    }
    
    # Find and copy first PNG as thumbnail
    $pngFiles = Get-ChildItem -Path $srcDir -Filter "*.png" | Where-Object { $_.Name -ne $texFile }
    if ($pngFiles) {
        $thumbnail = $pngFiles[0]
        Copy-Item -Path $thumbnail.FullName -Destination (Join-Path $dstDir "thumbnail.png") -Force
        Write-Host "   ✅ thumbnail.png (from $($thumbnail.Name))" -ForegroundColor Green
        $copiedCount++
        
        # Create preview as copy of thumbnail
        Copy-Item -Path (Join-Path $dstDir "thumbnail.png") -Destination (Join-Path $dstDir "preview.png") -Force
        Write-Host "   ✅ preview.png (copy of thumbnail)" -ForegroundColor Green
        $copiedCount++
    }
    
    Write-Host ""
}

Write-Host ("=" * 80)
Write-Host "✅ COPY COMPLETE: $copiedCount files copied" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "⚠️ WARNING: $failedCount files failed or not found" -ForegroundColor Yellow
}
Write-Host ("=" * 80)
