from __init__ import *

algopython_init()

light(1,1,5,"RED",False)
move('ABC',1,5,1)
rotations('C',1,10,1)
move('AB',1,5,-1)
light(1,1,5,"BLUE")
move('A',1,5,1)
# move('AC',1,5,-1)
# move('ABC',1,5,1)

algopython_exit()




# move(port='A', duration=2.0, power=5, direction=1)
# move(port='AB', duration=1.5, power=8, direction=-1)
# rotations(port='C', rotations=3, power=10, direction=1)
# light(port=1, duration=2.0, power=5, color="red")
# light(port=1, duration=FOREVER, power=7, color="green", is_blocking=False)
# lightStop(1)
# light(port=2, duration=3.0, power=10, color="cyan")
# light(port=1, duration=FOREVER, power=7, color="green", is_blocking=False)
# lightStop(1)
# wait_sensor(sensor_port=1, min=2, max=8)
# move(port='A', duration=2.0, power=5, direction=1)