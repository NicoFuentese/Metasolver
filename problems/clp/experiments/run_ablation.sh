#!/bin/bash
# Ablacion de BSG_BPP en las 240 instancias originales de Martello, Pisinger y Vigo (clases 1, 4-8).
# Cada trabajo es (semilla, instancia) y corre todas las configuraciones una tras otra en el mismo
# proceso (mismo protocolo que las campanas del paper). Guarda la salida completa de cada corrida
# (.out), valida cada solucion con validate_bpp.py y agrega una fila a <dir>/runs.csv.
# uso: run_ablation.sh <dir> <semillas, ej. "1 2 3"> <procesos>
# (BSG_BIN: ejecutable; por defecto build/BSG_BPP, compilado con HiGHS)
dir=$1; seeds=$2; procs=$3
root=$(cd "$(dirname "$0")/../../.." && pwd)
export BSG_BIN=${BSG_BIN:-$root/build/BSG_BPP} ROOT=$root DIR=$dir
mkdir -p "$dir/out" "$dir/sol"
[ -f "$dir/runs.csv" ] || echo "config,seed,instance,class,n,i,bins,lb,construction,swo,time,milp_improved,valid" > "$dir/runs.csv"

# configuraciones (Balanced: T=20 s, t=0.005 s)
cat > "$dir/configs.txt" <<'EOF'
constr_k1 -t 0.005 -T 20 --kappa 1 --no_improve
constr_k2 -t 0.005 -T 20 --no_improve
swo_rho0 -t 0.005 -T 20 --swo_rate 0
swo -t 0.005 -T 20
swo_T26 -t 0.005 -T 26
recomb -t 0.005 -T 20 --milp 60
harvest -t 0.005 -T 20 --milp 60 --harvest 10
EOF

run_job(){
	seed=$1; c=$2; n=$3; i=$4
	f=$ROOT/problems/clp/benchs/MPV/original/class$c/$n.txt
	name=c${c}_${n}_${i}
	while read cfg opts; do
		key=${cfg}_s${seed}_${name}
		grep -q "^$cfg,$seed,$name," "$DIR/runs.csv" && continue
		"$BSG_BIN" "$f" -i "$i" --seed "$seed" -o "$DIR/sol/$key.csv" $opts > "$DIR/out/$key.out" 2>&1
		v=$(python3 -I "$ROOT/problems/clp/validate_bpp.py" "$f" "$DIR/sol/$key.csv" -i "$i" 2>&1 | tail -1)
		awk -v cfg=$cfg -v s=$seed -v name=$name -v c=$c -v n=$n -v i=$i -v v="$v" '
			/^n_bins/{b=$2; lb=$4; co=$6; sw=$8; t=$12}
			/^milp/{m=$6}
			END{print cfg","s","name","c","n","i","b","lb","co","sw","t","(m==""?"":m)","v}' "$DIR/out/$key.out" >> "$DIR/runs.csv"
	done < "$DIR/configs.txt"
}
export -f run_job

for s in $seeds; do for c in 1 4 5 6 7 8; do for n in 50 100 150 200; do for i in $(seq 1 10); do
	echo "$s $c $n $i"
done; done; done; done | xargs -P "$procs" -L 1 bash -c 'run_job "$@"' _
