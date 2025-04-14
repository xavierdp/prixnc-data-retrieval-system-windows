# Script pour ajouter Python au PATH système de façon permanente
# À exécuter en tant qu'administrateur

# Chemins à ajouter au PATH
$pythonPath = "C:\Users\xavier\AppData\Local\Programs\Python\Python310"
$pythonScriptsPath = "C:\Users\xavier\AppData\Local\Programs\Python\Python310\Scripts"

# Vérifier si les chemins existent
if (-not (Test-Path $pythonPath)) {
    Write-Host "Erreur: Le chemin Python $pythonPath n'existe pas." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $pythonScriptsPath)) {
    Write-Host "Erreur: Le chemin Scripts Python $pythonScriptsPath n'existe pas." -ForegroundColor Red
    exit 1
}

# Obtenir le PATH actuel pour l'utilisateur
$currentUserPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Vérifier si les chemins sont déjà dans le PATH
$pathsToAdd = @()
if ($currentUserPath -notlike "*$pythonPath*") {
    $pathsToAdd += $pythonPath
}
if ($currentUserPath -notlike "*$pythonScriptsPath*") {
    $pathsToAdd += $pythonScriptsPath
}

# Si aucun chemin à ajouter, sortir
if ($pathsToAdd.Count -eq 0) {
    Write-Host "Python est déjà dans votre PATH." -ForegroundColor Green
    exit 0
}

# Ajouter les chemins au PATH
$newPath = $currentUserPath
foreach ($path in $pathsToAdd) {
    if ($newPath) {
        $newPath = "$newPath;$path"
    } else {
        $newPath = $path
    }
}

# Mettre à jour le PATH pour l'utilisateur
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

Write-Host "Python a été ajouté à votre PATH avec succès!" -ForegroundColor Green
Write-Host "Vous devrez redémarrer votre terminal ou votre ordinateur pour que les changements prennent effet." -ForegroundColor Yellow
