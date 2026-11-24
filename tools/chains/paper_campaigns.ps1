<#
Campanas de experimentos del paper de BSG_BPP, en el orden y con las configuraciones con que se corrieron (3 semillas, 4 procesos, una campana
a la vez, prioridad baja). Cada campana escribe <nombre>_s<semilla>.csv en $env:BPP_OUT (por defecto results/bpp/campaigns).

Uso (desde la raiz del repo):
  powershell -File tools\chains\paper_campaigns.ps1 -List
  powershell -File tools\chains\paper_campaigns.ps1 -Only orig,quality -Seeds 1,2,3 -Exe build\BSG_BPP.exe
  powershell -File tools\chains\paper_campaigns.ps1 -Only ind_large -Instances D:\bpp\instances

Instancias (se generan con tools/instances, ver tools/README.md): <Instances>\blind2, <Instances>\large_mpv y <Instances>\cg (Instance_CG convertidas).
Configuraciones del paper: Fast  = -T 4 -t 0.005 --harvest 10 --milp 30
                           Balanced = -T 20 -t 0.005 --harvest 10 --milp 60
                           Quality  = -T 100 --milp 100
Notas: * Las campanas con -t 0.005 pueden fallar con el binario ANTERIOR al arreglo del greedy ("a box does not fit in the bin"); usar un binario con el arreglo.
       * 'sens' necesita un ejecutable con --swo_sigma y --swo_bins (no estan en el repo): pasarlo con -SensExe.
       * Las tablas se regeneran despues con tools/analysis (variable BPP_RESULTS).
#>
param(
    [string[]]$Only = @(),
    [int[]]$Seeds = @(1, 2, 3),
    [string]$Exe = "",
    [string]$SensExe = "",
    [string]$Instances = "",
    [int]$Procs = 4,
    [switch]$List
)
$tools = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $tools "runners\run_campaign.py"
$py = if ($env:BPP_PYTHON) { $env:BPP_PYTHON } else { "python" }
if (-not $Instances) { $Instances = Join-Path (Split-Path -Parent $tools) "results\bpp\campaigns\instances" }

$fast = "Fast|-T 4 -t 0.005 --harvest 10 --milp 30"
$bal  = "Balanced|-T 20 -t 0.005 --harvest 10 --milp 60"
$qual = "Quality|-T 100 --milp 100"
$rot  = @("Fast|-T 4 -t 0.005 --harvest 10 --milp 30 --rot", "Balanced|-T 20 -t 0.005 --harvest 10 --milp 60 --rot", "Quality|-T 100 --milp 100 --rot")
$b = "--kappa 1 --support area"
$sensBase = "-T 4 -t 0.005 --harvest 10 --milp 30"

# nombre = @{ set; classes; ns; insts; cfgs; dir; exe }  (set: original | flat | industrial)
$C = [ordered]@{
    orig        = @{ set = "original"; cfgs = @($fast, "Fastnh|-T 4 -t 0.005 --milp 30", $bal) }
    quality     = @{ set = "original"; cfgs = @($qual) }
    ctl         = @{ set = "original"; cfgs = @("SwoT7|-T 7 -t 0.005", "SwoT26|-T 26 -t 0.005", "SwoT111|-T 111") }
    cls23_fixed = @{ set = "original"; classes = "2,3"; cfgs = @($fast, $bal, $qual) }
    abl         = @{ set = "original"; cfgs = @("ConsK2|--no_swo --no_improve -t 0.005", "ConsK1|--no_swo --no_improve -t 0.005 --kappa 1", "Swo|-T 20 -t 0.005",
                      "SwoNoLearn|-T 20 -t 0.005 --swo_rate 0", "Milp|-T 20 -t 0.005 --milp 60", "Harvest|-T 20 -t 0.005 --harvest 10 --milp 60") }
    sens        = @{ set = "original"; insts = "1,2,3"; exe = "sens"; cfgs = @("Base|$sensBase", "Rho0.1|$sensBase --swo_rate 0.1", "Rho0.6|$sensBase --swo_rate 0.6",
                      "Rho1.0|$sensBase --swo_rate 1.0", "Sigma0|$sensBase --swo_sigma 0", "Sigma0.02|$sensBase --swo_sigma 0.02", "Sigma0.1|$sensBase --swo_sigma 0.1",
                      "Sigma0.2|$sensBase --swo_sigma 0.2", "Frac0.05|$sensBase --swo_bins 0.05", "Frac0.2|$sensBase --swo_bins 0.2", "Frac0.3|$sensBase --swo_bins 0.3",
                      "K1|-T 4 -t 0.005 --harvest 1 --milp 30", "K3|-T 4 -t 0.005 --harvest 3 --milp 30", "K30|-T 4 -t 0.005 --harvest 30 --milp 30",
                      "Thr0.8|$sensBase --harvest_thr 0.8", "Thr0.9|$sensBase --harvest_thr 0.9", "Thr0.99|$sensBase --harvest_thr 0.99",
                      "t0.002|-T 4 -t 0.002 --harvest 10 --milp 30", "t0.01|-T 4 -t 0.01 --harvest 10 --milp 30", "t0.02|-T 4 -t 0.02 --harvest 10 --milp 30") }
    rot_orig    = @{ set = "original"; cfgs = $rot }
    rot_cls23   = @{ set = "original"; classes = "2,3"; cfgs = $rot }
    rotctl      = @{ set = "original"; cfgs = @("F4rot|-T 33 --milp 60 --rot", "SwoT8rot|-T 8 -t 0.005 --rot", "SwoT27rot|-T 27 -t 0.005 --rot", "SwoT100rot|-T 100 --rot") }
    rotctl23    = @{ set = "original"; classes = "2,3"; cfgs = @("F4rot|-T 33 --milp 60 --rot", "SwoT12rot|-T 12 -t 0.005 --rot", "SwoT36rot|-T 36 -t 0.005 --rot", "SwoT120rot|-T 120 --rot") }
    qharv       = @{ set = "original"; cfgs = @("QualityHarvest|-T 100 --harvest 10 --milp 100") }
    equiv_new   = @{ set = "original"; cfgs = @($fast, $bal) }
    blind2rep   = @{ set = "flat"; dir = "blind2"; cfgs = @($fast, "FastNoHarvest|-T 4 -t 0.005 --milp 30", $bal, "BalancedPlain|-T 20 -t 0.005 --harvest 10 --milp 60 --milp_plain", "SwoT26|-T 26 -t 0.005") }
    large       = @{ set = "flat"; dir = "large_mpv"; cfgs = @($fast, $bal, $qual, "SwoT26|-T 26 -t 0.005", "SwoT111|-T 111") }
    ind_large   = @{ set = "industrial"; dir = "cg"; ns = "500,1000,1500,2000"; cfgs = @("C2|--no_improve -t 2 $b", "S02|-T 18 -t 0.2 $b", "S05|-T 18 -t 0.5 $b",
                      "P02|-T 18 -t 0.2 --harvest 10 --milp 20 --partition $b", "P05|-T 18 -t 0.5 --harvest 10 --milp 20 --partition $b",
                      "S05_60|-T 60 -t 0.5 $b", "P05_60|-T 60 -t 0.5 --harvest 10 --milp 30 --partition $b") }
    ind_small   = @{ set = "industrial"; dir = "cg"; ns = "50,100,150,200"; cfgs = @("Imp|-T 30 --swo_frac 0.3 --scratch --improve_time 2 $b", "C2|--no_improve -t 2 $b",
                      "S05|-T 10 -t 0.5 $b", "P05|-T 10 -t 0.5 --harvest 10 --milp 20 --partition $b") }
}

if ($List) { $C.Keys | ForEach-Object { "{0,-12} {1} configuraciones" -f $_, $C[$_].cfgs.Count }; return }
$todo = if ($Only.Count) { $Only } else { @($C.Keys) }
foreach ($name in $todo) {
    if (-not $C.Contains($name)) { Write-Error "campana desconocida: $name"; exit 1 }
    $c = $C[$name]
    foreach ($s in $Seeds) {
        $a = @($runner, "${name}_s$s", "--seed", $s, "--procs", $Procs, "--set", $c.set)
        if ($c.classes) { $a += @("--classes", $c.classes) }
        if ($c.insts)   { $a += @("--insts", $c.insts) }
        if ($c.ns)      { $a += @("--ns", $c.ns) }
        if ($c.dir)     { $a += @("--dir", (Join-Path $Instances $c.dir)) }
        $exe = if ($c.exe -eq "sens") { $SensExe } else { $Exe }
        if ($exe) { $a += @("--exe", $exe) }
        $a += $c.cfgs
        Write-Host ("{0}  start {1}_s{2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $name, $s)
        & $py @a
        Write-Host ("{0}  end   {1}_s{2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $name, $s)
    }
}
