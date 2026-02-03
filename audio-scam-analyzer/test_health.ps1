#!/usr/bin/env pwsh
<#
.SYNOPSIS
Test the health check endpoint with proper PowerShell syntax

.DESCRIPTION
This script tests the audio scam analyzer API health check.
Works correctly with PowerShell 5.1+ (Windows native PowerShell)

.EXAMPLE
.\test_health.ps1
#>

Write-Host "🔷 Testing Audio Scam Analyzer Health Check" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

$url = "http://localhost:8000/health"

Write-Host "📡 Sending request to: $url`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $url -Method Get -ContentType "application/json"
    
    Write-Host "✅ SUCCESS! Response received:" -ForegroundColor Green
    Write-Host ""
    Write-Host ($response | ConvertTo-Json -Depth 10)
    Write-Host ""
    Write-Host "🎯 API is healthy and responding!" -ForegroundColor Green
}
catch {
    Write-Host "❌ ERROR: Connection failed" -ForegroundColor Red
    Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the API is running:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python app.py" -ForegroundColor Yellow
    exit 1
}
