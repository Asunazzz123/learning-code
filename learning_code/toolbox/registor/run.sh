clang++ ./learning_code/toolbox/registor/ax.s -o learning_code/toolbox/registor/ax
./learning_code/toolbox/registor/ax &
pid=$!
echo $pid
ps -p "$pid" -o pid,ppid,state,pri,%cpu,%mem,etime,command
sleep 0.2
# kill $pid
