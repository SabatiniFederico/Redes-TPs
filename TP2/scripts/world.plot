# set terminal qt persist
set terminal svg
set output 'world.svg'
set format x '%D %E' geographic
set format y '%D %N' geographic
unset key
set style data lines
set yzeroaxis
set title 'Ubicación geográfica de los hops en las trazas analizadas'
set xrange [ -180.000 : 180.000 ] noreverse nowriteback
set x2range [ -180.000 : 180.000 ] noreverse nowriteback
set yrange [ -90.0000 : 90.0000 ] noreverse nowriteback
set y2range [ -90.0000 : 90.0000 ] noreverse nowriteback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
NO_ANIMATION = 1
plot 'world.dat'        with lines lc rgb 'dark-gray',     \
     'alexu.edu.eg.dat' with lines lc rgb 'blue',          \
     'fs.ru.is.dat'     with lines lc rgb 'dark-green',    \
     'itmo.ru.dat'      with lines lc rgb 'orange',        \
     'unisa.ac.za.dat'  with lines lc rgb 'red',           \
     'universities.dat' with points pt 'x' lc rgb 'black', \
     'universities.dat' using 1:($2+5):3 with labels font 'arial,8'
