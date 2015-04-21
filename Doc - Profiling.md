# PROFILING
===
## Attempt 1: Using a different compiler
### by 'cProfiler'
> This is the part of profiling the code. I tried using PyPy compiler and check to
> see if it's a better compiler for this program. The results though show that the
> default GCC compiler is better. So the compiler isn't an issue here.

```
Compiler info:
Python 2.7.2 (0e28b379d8b3, Feb 09 2012, 19:41:19)
[PyPy 1.8.0 with GCC 4.4.3]
Total Agents  Remarks
200            362111 function calls (359393 primitive calls) in 0.742 seconds
2000           824554 function calls (821836 primitive calls) in 1.072 seconds
20000          5284546 function calls (5281828 primitive calls) in 4.743 seconds
200000         50298385 function calls (50295667 primitive calls) in 285.059 seconds
```
```
Compiler info:
Python 2.7.6
2000000        50244368 function calls (50241610 primitive calls) in 116.695 seconds
```

******************************************************************************************************************************
## Attempt 2: Digging down to the code
### by 'line_profiler'
Interesting parts of the program to profile are based from the results of the
above attempt.
```
1000000    1.640    0.000    2.585    0.000 models.py:34(run)
 109339    0.199    0.000    2.905    0.000 models.py:73(run)
    200    0.540    0.003    6.031    0.030 models.py:79(run)
      1    0.017    0.017    6.524    6.524 manage.py:7(main)
      1    0.002    0.002    6.373    6.373 environment.py:47(simulate)
```
Results
```
Wrote profile results to manage.py.lprof
Timer unit: 1e-06 s

Total time: 4.26304 s
File: models.py
Function: run at line 34

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    34                                               @profile
    35                                               def run(self):
    36                                                   #: update attributes first
    37   1000000      1911410      1.9     44.8          self.pre_run()
    38
    39                                                   #: CASE: Currently infected so infection duration minimized
    40   1000000      2184948      2.2     51.3          if self.state is STATES.INFECTED:
    41     82878        63408      0.8      1.5              if self.infection_duration > 0:
    42     75350        67123      0.9      1.6                  self.infection_duration -= 1
    43                                                       #: CASE: Infection is over and now recover
    44                                                       else:
    45      7528        15045      2.0      0.4                  self.state = STATES.RECOVERED
    46      7528         5807      0.8      0.1                  self.is_latent = False
    47                                                           # update person manager
    48      7528         8175      1.1      0.2                  self.environment.person_manager.counter_recovered += 1
    49      7528         7126      0.9      0.2                  self.environment.person_manager.counter_infected -= 1

Total time: 3.64985 s
File: models.py
Function: run at line 74

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    74                                               @profile
    75                                               def run(self):
    76                                                   """
    77                                                   [1] Survivability of the mosquito depends whether it is dying
    78                                                   or not. If the mosquito is dying, remove from the environment
    79                                                   and trigger spawning of new mosquito.
    80                                                   [2] Bite persons
    81                                                   [3] Evaluate death by probability
    82                                                   """
    83                                                   #: Update attributes first
    84    110370       278640      2.5      7.6          self.pre_run()
    85
    86                                                   # TODO: If mosquito is dying, remove mosquito from manager
    87                                                   # TODO: CREATE ENVIRONMENT FIRST!
    88    110370        82767      0.7      2.3          if self.is_dying:
    89     10000       610600     61.1     16.7              self.environment.mosquito_manager.queue.remove(self)
    90                                                       # TODO: Trigger spawning
    91     10000         6949      0.7      0.2              return
    92
    93                                                   # bite persons!
    94    100370      2559380     25.5     70.1          self.bite_persons()
    95
    96                                                   # evaluate if dying
    97    100370       103433      1.0      2.8          if random.random() < self.death_probability:
    98     10000         8076      0.8      0.2              self.is_dying = True
```

===

> It seems reasonable for the `run` of human agent because it is only necessary
> to check if the person is infected to carry on all other actions.
> The mosquito takes a lot of Per Hit because of its removal of dying mosquitoes
> from the queue.

## Conclusion
Perhaps, poorly designed or, I could find a better way to handle `pre_run` and `run`,
this would serve as a limitation for ABEMpy. Currently 200,000 agents would run for
3 minutes (at worse) on a quad-core laptop. Improvements shall be done on the way.
Ambitiously, the target is to run millions of agents.