# Configuration Ubidots
$UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
$DEVICE_ID = "696c16da6b8f94fd52f77962"

# Fonction pour recuperer les donnees Ubidots
function Get-UbidotsVariables {
    try {
        $headers = @{
            "X-Auth-Token" = $UBIDOTS_TOKEN
            "Content-Type" = "application/json"
        }
        
        # Recuperer les variables du datasource
        $url = "https://industrial.api.ubidots.com/api/v1.6/datasources/$DEVICE_ID/variables/"
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -TimeoutSec 10
        
        $sensors = @{}
        
        # Extraire les resultats
        $variables = $response.results
        
        # Pour chaque variable, recuperer la derniere valeur
        foreach ($variable in $variables) {
            $varId = $variable.id
            $label = $variable.label
            
            # Recuperer la derniere valeur
            $valUrl = "https://industrial.api.ubidots.com/api/v1.6/variables/$varId/values/?page_size=1"
            $valResponse = Invoke-RestMethod -Uri $valUrl -Headers $headers -Method Get -TimeoutSec 10
            
            if ($valResponse.results -and $valResponse.results.Count -gt 0) {
                $lastValue = $valResponse.results[0]
                $sensors[$label] = @{
                    "value" = $lastValue.value
                    "timestamp" = $lastValue.timestamp
                }
            }
        }
        
        return $sensors
    }
    catch {
        Write-Host "Erreur de connexion: $_" -ForegroundColor Red
        return $null
    }
}

# Fonction pour afficher l'en-tete
function Show-Header {
    Clear-Host
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "         RESPIRIA - MONITEUR CAPTEURS EN TEMPS REEL          " -ForegroundColor Cyan
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Fonction pour afficher les donnees des capteurs
function Show-SensorData {
    param(
        [Parameter(Mandatory=$false)]
        [hashtable]$data
    )
    
    $now = Get-Date -Format "HH:mm:ss"
    
    Write-Host "  Lecture: $now | Device ID: $DEVICE_ID" -ForegroundColor Gray
    Write-Host "  ------------------------------------------------------------" -ForegroundColor Gray
    Write-Host ""
    
    if ($null -eq $data -or $data.Count -eq 0) {
        Write-Host "  Aucune donnee recue" -ForegroundColor Yellow
        return
    }
    
    # Variables pour les capteurs
    $spo2 = $null
    $bpm = $null
    $temp = $null
    $humidity = $null
    $eco2 = $null
    $tvoc = $null
    
    # Extraire les valeurs
    if ($data.ContainsKey('spo2')) { $spo2 = [math]::Round($data.spo2.value, 1) }
    if ($data.ContainsKey('bpm')) { $bpm = [math]::Round($data.bpm.value, 0) }
    if ($data.ContainsKey('temperature')) { $temp = [math]::Round($data.temperature.value, 1) }
    if ($data.ContainsKey('humidity')) { $humidity = [math]::Round($data.humidity.value, 1) }
    if ($data.ContainsKey('eco2')) { $eco2 = [math]::Round($data.eco2.value, 0) }
    if ($data.ContainsKey('tvoc')) { $tvoc = [math]::Round($data.tvoc.value, 0) }
    
    # Afficher MAX30102
    Write-Host "  [MAX30102 - Physiologique]" -ForegroundColor Magenta
    if ($null -ne $spo2) {
        $color = "Green"
        if ($spo2 -lt 90) { 
            $color = "Red" 
        }
        elseif ($spo2 -lt 95) { 
            $color = "Yellow" 
        }
        Write-Host "    SpO2: $spo2 %" -ForegroundColor $color
    }
    else {
        Write-Host "    SpO2: N/A" -ForegroundColor Gray
    }
    
    if ($null -ne $bpm) {
        $color = "Green"
        if ($bpm -gt 120 -or $bpm -lt 50) { 
            $color = "Red" 
        }
        elseif ($bpm -gt 100 -or $bpm -lt 60) { 
            $color = "Yellow" 
        }
        Write-Host "    BPM:  $bpm" -ForegroundColor $color
    }
    else {
        Write-Host "    BPM:  N/A" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # Afficher DHT11
    Write-Host "  [DHT11 - Environnement]" -ForegroundColor Blue
    if ($null -ne $temp) {
        $color = "Green"
        if ($temp -gt 35 -or $temp -lt 10) { 
            $color = "Red" 
        }
        elseif ($temp -gt 30 -or $temp -lt 15) { 
            $color = "Yellow" 
        }
        Write-Host "    Temp: $temp C" -ForegroundColor $color
    }
    else {
        Write-Host "    Temp: N/A" -ForegroundColor Gray
    }
    
    if ($null -ne $humidity) {
        $color = "Green"
        if ($humidity -gt 80 -or $humidity -lt 30) { 
            $color = "Yellow" 
        }
        Write-Host "    Hum:  $humidity %" -ForegroundColor $color
    }
    else {
        Write-Host "    Hum:  N/A" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # Afficher CJMCU-811
    Write-Host "  [CJMCU-811 - Qualite Air]" -ForegroundColor DarkYellow
    if ($null -ne $eco2) {
        $color = "Green"
        if ($eco2 -gt 2000) { 
            $color = "Red" 
        }
        elseif ($eco2 -gt 1000) { 
            $color = "Yellow" 
        }
        Write-Host "    eCO2: $eco2 ppm" -ForegroundColor $color
    }
    else {
        Write-Host "    eCO2: N/A" -ForegroundColor Gray
    }
    
    if ($null -ne $tvoc) {
        $color = "Green"
        if ($tvoc -gt 660) { 
            $color = "Red" 
        }
        elseif ($tvoc -gt 220) { 
            $color = "Yellow" 
        }
        Write-Host "    TVOC: $tvoc ppb" -ForegroundColor $color
    }
    else {
        Write-Host "    TVOC: N/A" -ForegroundColor Gray
    }
    
    # Detection fumee
    $smoke = $false
    if ($null -ne $eco2 -and $null -ne $tvoc) {
        if (($eco2 -gt 4000 -and $tvoc -gt 1000) -or $tvoc -gt 2000) {
            $smoke = $true
        }
    }
    
    if ($smoke) {
        Write-Host "    FUMEE: DETECTEE!" -ForegroundColor Red
    }
    else {
        Write-Host "    Fumee: Non" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Donnees brutes
    Write-Host "  [Donnees brutes]" -ForegroundColor DarkGray
    foreach ($key in $data.Keys) {
        $value = [math]::Round($data[$key].value, 2)
        $timestamp = [DateTimeOffset]::FromUnixTimeMilliseconds($data[$key].timestamp).LocalDateTime.ToString("HH:mm:ss")
        Write-Host "    $key : $value ($timestamp)" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "  Ctrl+C pour arreter | Refresh: 3s" -ForegroundColor Gray
}

# Boucle principale
Write-Host "Demarrage du moniteur..." -ForegroundColor Cyan
Start-Sleep -Seconds 1

while ($true) {
    Show-Header
    $sensorData = Get-UbidotsVariables
    Show-SensorData -data $sensorData
    Start-Sleep -Seconds 3
}
