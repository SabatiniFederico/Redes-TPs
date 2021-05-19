set terminal qt persist
# set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
# set output 'world.1.png'
set format x "%D %E" geographic
set format y "%D %N" geographic
unset key
set style data lines
set yzeroaxis
set title "Gnuplot Correspondences\ngeographic coordinate system" 
set xrange [ -180.000 : 180.000 ] noreverse nowriteback
set x2range [ -180.000 : 180.000 ] noreverse nowriteback
set yrange [ -90.0000 : 90.0000 ] noreverse nowriteback
set y2range [ -90.0000 : 90.0000 ] noreverse nowriteback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
NO_ANIMATION = 1
plot 'world.dat'      with lines lc rgb "blue", \
     'traceroute.dat' with lines lc rgb "red"
#     'ru.is.dat'      with lines lc rgb "red"
#     'mit.edu.dat'    with lines lc rgb "red",  \
#     'uba.ar.dat'     with lines lc rgb "red",  \
#     'unc.edu.ar.dat' with lines lc rgb "red",  \
