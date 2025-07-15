Did this for a task to join a robotics club, and I think this also turned out to be a fun litte project... so here you have it.

I have implemented a PID controller with an autotuner using genetic algorithm, with a perlin noise terrain generator for more realistic testing. The random terrain generator also ensures the controller works for most types of terrain without growing unstable.

The math:
first the average height is 10. then, let the ground height or depth at the 4 legs be, some g1 to g4. right. now

Given, average total heights of the legs is supposed to be maintained at 10.
let, h1 to h4 be the heights of eagh leg. let H1 to H4 be the total heights of each leg. let g1 to g4 be the heights of the ground.

then, summation of H1 to H4 / 4 = 10
or, summation of H1 to H4 = 40
or, summation of h1 to h4 = 40 - summation of g1 to g4 -- (1)

also given that the pitch is to be zero,

(h1+h2) / 2 - (h3+h4) / 2 = 0
or, h1 + h2 = h3 + h4 -- (2)

from (1) and (2)

h1 + h2 = h3 + h4 = 20 - summation of g1 to g4 / 2

now I did assume no shape to the bot, and thus i couldn't really solve it further and set individual targets for each leg. thus, i just did a crude work around.

h1 = 20 - summmation of g1 to g4 / 2 - h2
h2 = 20 - summmation of g1 to g4 / 2 - h1
h3 = 20 - summmation of g1 to g4 / 2 - h4
h4 = 20 - summmation of g1 to g4 / 2 - h3

now there are 4 controllers with 4 separate targets for each leg.
the problem with this method however is, the legs are of same height in the end.

auto tuning:
to tune the PID controller, I implemented genetic algorithm. and a few of them are noted down in selectedParams.txt

terrain generation:
I have also implemented a random terrain generator using perlin noise using alexandr-gnrk's 1D perlin noise generator (https://github.com/alexandr-gnrk/perlin-1d). This helps to visulaize the stability of a system in a rough terrain, and also helped training the genetic algorithm, as each iteration provides us with a new terrain to work on, making sure of stability in any terrain.

running it:
to run the genetic algorithm, just run genetic.py
to manually tune the PID and run it, run PID.py

to modify all parameters, change the values in config.toml
