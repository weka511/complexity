extensions [matrix]

globals [
  divisions      ;the factor by which the length of the fractal's line segments decreases (M in the Hausdorff dimension equation)
  fractal-dim    ;Hausdorff dimension of the fractal
  initial-length ;initial length of the line segments
  len            ;current length of the line segments (after iteration)
  old-box-count  ;number of red boxes covering parts of the fractal at the previous step
  new-box-count  ;current number of boxes (red) covering parts of the fractal
  x-axis-list    ;list of all the x-values for the log-log box-counting dimension plot
  y-axis-list    ;list of all the y-values for the log-log box-counting dimension plot
  box-size       ;current size of boxes
  explore?       ;whether or not the boxes need to move and find a portion of the fractal to cover
  iteration      ;counts the box-counting iteration
  iterations-to-go
  slope          ;slope of the box-counting log-log plot regression line, equal to the box-counting dimension
  r-square       ;r-squared value for the box-counting log-log plot regression line
  lin-reg-eq     ;linear regression equation for the log-log plot
  any-new-boxes?
  x-cor           ;initial x-coordinate for the first turtle
  y-cor            ;initial y-coordinate for the first turtle
  fractal-example ;the name of the fractal being drawn
]



;globals
; [divisions fractal-dim initial-length
;  len walk-count old-box-count
;  new-box-count x-axis-list y-axis-list
;  box-size explore? iteration
;  iterations-to-go slope lin-reg-eq
;  any-new-boxes? x-cor y-cor
;  ]

turtles-own   ;used only for making fractal examples and custom frctals if you choose.
  [new?]

breed         ;used only for taking box counting dimension of fractal examples.
 [boxes box]

boxes-own
  [past? present? future?]

patches-own [fractal?]

to startup
   setup
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;; Fractal Procedures ;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;Clears the world and sets up an initial turtle
to setup
  ;Initializing values
  set explore? false
  set x-axis-list [ ]
  set y-axis-list [ ]
  set fractal-dim "N/A" ;the first iteration has not yet been drawn, so we don't know what the Hausdorff dimension is

  ;Setting the initial turtle position
  if (fractal-example = "koch-curve" or fractal-example = "cantor-set") [set x-cor -150 set y-cor 0 set divisions 3]
  if(fractal-example = "levy-curve" or fractal-example = "dragon-curve") [set x-cor -60 set y-cor 0 set divisions sqrt 2]
  if(fractal-example = "sierpinski-triangle")[set x-cor -100 set y-cor 0]
  crt 1 ;creating the initial turtle
  ask turtles [
    ;initializing turtle properties
    set new? false
    set shape "circle"
    set size 1
    set color green
    setxy x-cor y-cor
    set heading 90
    ifelse(fractal-example != "tree")
    [
      set initial-length 100
      pd
      fd initial-length * divisions
      set len initial-length
      pu
      setxy x-cor y-cor
    ]
    [
      set divisions 2
      set initial-length 100
      set x-cor 0 set y-cor -150
      set len initial-length
      setxy x-cor y-cor
      set heading 0
      walk walk
    ]
  ]
  reset-ticks
  if fractal-example = "sierpinski-triangle" [iterate]
end

;Depending on the example chosen for the fractal, this will iterate the fractal
to iterate

  ;The tree fractal requires that the previous iterations remain on the screen
  if fractal-example != "tree" [clear-drawing]

  ;Creates standard Koch curve
  if fractal-example = "koch-curve"
  [
    ask patches [set pcolor black] ; clears screen
    ask turtles [
      set new? false ]
    t  walk l 60 t  walk r 120 t  walk l 60 t walk d ;l-system
    set divisions 3 ;the factor by which the length decreases
    set len (len / divisions)
    fractal-dimension  ;calculates & updates fracal dimension
    tick
  ]

  ;Creates same fractal tree as in simple fractals and the L-systems
  if fractal-example = "tree"
  [
    ;ask patches [set pcolor black]
    ask turtles[
      set new? false]
    r 15 walk  t r 180 skip len r 180 l 40 walk t
    ask turtles with [new? = false] [die]
    set divisions 2
    set len (len / divisions)
    fractal-dimension
    tick
  ]

  ;Creates the Levy C Curve
  if fractal-example = "levy-curve"
  [
    ask patches [set pcolor black]
    ask turtles[ set new? false]
    l 45 t walk r 90 t walk d
    set divisions sqrt 2
    set len (len / divisions)
    fractal-dimension
    tick
  ]


  ;Creates the Sierpinski triangle
  if fractal-example = "sierpinski-triangle"
  [
    ask patches [set pcolor black] ; clears screen
    ask turtles [set new? false pd]
    ;set len len / 2
    t walk t walk l 120 walk walk l 120 walk l 120 t r 120 walk d
    set divisions 2
    set len (len / divisions)
    fractal-dimension
    tick
  ]

  ;Creates the Cantor set
  if fractal-example = "cantor-set"
  [
    ask patches [set pcolor black] ; clears screen
    ask turtles [set new? false ]
    t walk
    skip len
    t walk
    d
    set divisions 3
    set len (len / divisions)
    fractal-dimension
    tick
  ]

  ;Creates the Heighway dragon curve
  if fractal-example = "dragon-curve"
  [
    ask patches [set pcolor black] ; clears screen
    ask turtles [
      set new? false ]
    r 45 t walk l 90  walk l 180 t d
    set divisions  sqrt 2
    set len (len / divisions)
    fractal-dimension
    tick
  ]
end


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;Box-Counting-Dim;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to box-counting-setup
    set box-size initial-box-length
    set iteration iteration
    make-initial-box
end

to box-counting-go
   ask boxes ; clears screen in case there are any old boxes
   [die]
   set initial-length 100

    if box-size >= initial-length ;prevents boxes from getting too big for the world
     [stop]
    set box-size box-size + increment
    set iteration iteration + 1
    set iterations-to-go 91 - iteration
    set old-box-count 0
    set new-box-count 1    ;eliminates an error for first round
    make-initial-box
    make-neighbors-count-patches

end

 ;makes a starter box at the beginning of each run with present? = true.
 ;This box will then be used to make boxes with future? = true
 ;which will be used for the next run.
to make-initial-box
    create-boxes 1
  ask boxes [
    set shape "square"
    set size box-size
    setxy  x-cor y-cor
    set heading 90
    set color red
    set past? false
    set present? true
    set future? false
    ]
end

 ;makes a Moore neighborhood around the starter box and counts patches below each new box (exploit).
 ;If there are no new boxes with patches under them for a given run a box is sent outside the neighborhhod
 ;to cover non-contiguous patches (explore). If this box finds no new patches the run is complete.

to make-neighbors-count-patches
    ask boxes with [present? = true ]
    [make-neighbors]

    ask boxes with [future?  = true]
       [exploit]
       count-new-boxes
      if any-new-boxes?     = false
       [explore]

      if any-new-boxes? = false
       [calculate-box-counting-dimension
         stop]

      update-past-present-future-states
      tick
      if any-new-boxes? = true
      [make-neighbors-count-patches]
end

to make-neighbors
     hatch 1 [fd box-size rt 90
      set present? false set future? true
      hatch 1 [fd box-size rt 90
      set present? false set future? true
      hatch 1 [fd box-size
      set present? false set future? true
      hatch 1 [fd box-size rt 90
      set present? false set future? true
      hatch 1 [fd box-size
      set present? false set future? true
      hatch 1 [fd box-size rt 90
      set present? false set future? true
      hatch 1 [fd box-size
      set present? false set future? true
      hatch 1 [fd box-size
      set present? false set future? true
       ]]]]]]]]
end

to exploit
   if count boxes in-radius (box-size / 2) > 1  ; eliminates duplicates
   [die]

   if count patches-under-me = 0
   [ die ]
end

to-report patches-under-me
     report  patches in-radius  ( (1.4 * size ) / 2 )  with [pcolor = green]
end

to explore
 if count boxes with [present? = true] > 0 [
   ask patches with [pcolor = green] [
 ifelse count boxes in-radius  (  box-size ) = 0
  [set explore? true]
  [stop]
  ]
 ]

 if explore? [
 ask one-of boxes with [present? = true] [
  hatch 1 [
  set present? false set future? true
  move-to min-one-of patches with [pcolor = green and count boxes in-radius  ( box-size ) = 0 ]
  [distance myself]]
  ]
 ]
 count-new-boxes
 set explore? false
end

to count-new-boxes
 set old-box-count new-box-count
 set new-box-count count boxes
 ifelse old-box-count = new-box-count
 [set any-new-boxes? false]
 [set any-new-boxes?  true]
end

to update-past-present-future-states
 ask boxes [
  if present? = true
  [set past? true set present? false]
  if future?   = true
  [set future? false set present? true]
  ]
end

to calculate-box-counting-dimension

  if count boxes >= 1 [     ; eliminates potential error message if setup is pressed during a box-counting procedure
   set-current-plot "Box Counting Plot"
   set-current-plot-pen "default"
   let no-boxes log (count boxes ) 10
   let scale (log ( 1 / box-size ) 10 )
   plotxy scale no-boxes
   set x-axis-list lput scale x-axis-list
   set y-axis-list lput no-boxes y-axis-list
   ]

 stop
end

to fractal-dimension
 if ticks = 0 [
  if divisions > 0 [ ; eliminates potential error message
  let line-segments count turtles
  set fractal-dim precision(( log  line-segments  10 / log  divisions 10 ))3
  ]
 ]
 stop
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;; Fractal Commands ;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; walk moves a turtle forward by a length (len) and leaves a trail of green patches.

to walk
  ask turtles with [not new?]
  [
    set pcolor green
    let walk-count .1
    while [walk-count <= len]
    [
      fd .1
      set pcolor green
      set walk-count ( walk-count + .1)
    ]
  ]
  stop
end

;hatch a new turtle for all the turtles that are not new to the current iteration and set new? to be true

to t
  ask turtles with [not new?] [hatch 1 [set new? true]]
end

;turn each turtle that wasn't created during the current iteration to the right by degree degrees
to r [degree]
  ask turtles with [not new?] [rt degree]
end

;turn each turtle that wasn't created during the current iteration to the left by degree degrees
to l [degree]
  ask turtles with [not new?] [lt degree]
end

;move each turtle that wasn't created during the current iteration forward by steps but do not leave trail of green patches.
to skip [steps]
  ask turtles with [not new?] [ fd steps ]
end

;all non-new turtles die
to d
  ask turtles with [not new?] [die]
end


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;Linear Reg;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

 ;Linear regression is used to find the 'best-fit' line
 ;through all the tuples (box-size,number of boxes) plotted in the scatter plot.
 ;The slope of the line is the box counting dimension.

 to linear-regression

  if (count boxes >= 1) and (length x-axis-list > 1) [  ; eliminates potential error message if setup is pressed during a box-counting procedure
                                                        ; or if there is only one point in the log-log plot

    let regression matrix:regress matrix:from-column-list (list y-axis-list  x-axis-list)   ;using the regression tool from the matrix extension
    ;setting y-intercept and slope (measure of goodness of fit)
    let y-intercept item 0 (item 0 regression)
    set slope item 1 (item 0 regression)
    set r-square item 0 (item 1 regression)


    ; set the equation to the appropriate string
    set lin-reg-eq (word (precision slope 2) " * x + " (precision y-intercept 2))

    ;plotting the line on the log-log plot
    set-current-plot "Box Counting Plot"
    set-current-plot-pen "pen-4"
    plot-pen-reset
    auto-plot-off
    plotxy plot-x-min (plot-x-min * slope + y-intercept)
    plot-pen-down
    plotxy plot-x-max (plot-x-max * slope + y-intercept)
    plot-pen-up
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
270
15
801
567
260
260
1.0
1
10
1
1
1
0
1
1
1
-260
260
-260
260
1
1
1
ticks
30.0

PLOT
817
15
1084
270
Box Counting Plot
log [1 / box-length]
log number of boxes (N)
-2.0
-1.0
0.0
2.0
true
false
"" ""
PENS
"default" 1.0 2 -16777216 true "" ""
"pen-4" 1.0 0 -2674135 true "" ""

MONITOR
817
314
1084
359
Hausdorff Dimension (log N/log M)
fractal-dim
17
1
11

BUTTON
138
278
250
311
Box Counting Go
box-counting-go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
817
358
1084
391
NIL
linear-regression
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
817
269
949
314
Box-Counting Dim.
precision(slope)3
17
1
11

MONITOR
91
413
173
458
Box Length
precision(box-size)2
17
1
11

MONITOR
26
413
92
458
NIL
iteration
17
1
11

TEXTBOX
28
251
242
275
Box-Counting Controls
18
0.0
1

TEXTBOX
824
401
1086
443
The Box-Counting Dimension is the slope of the line that best fits the points.  Compare with the Hausdorff Dimension.
11
0.0
1

TEXTBOX
22
38
172
60
Fractal Examples
18
0.0
1

TEXTBOX
21
12
248
46
Box-Counting Dimension
18
95.0
1

BUTTON
73
184
187
233
NIL
iterate
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
25
310
250
343
initial-box-length
initial-box-length
.2
100
4
.1
1
NIL
HORIZONTAL

SLIDER
24
343
250
376
increment
increment
0
1
0.8
.1
1
NIL
HORIZONTAL

BUTTON
15
70
128
103
Koch Curve
ca\nset fractal-example \"koch-curve\"\nsetup\n
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
128
70
244
103
Cantor Set
ca\nset fractal-example \"cantor-set\"\nsetup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
15
102
128
135
Levy Curve
ca\nset fractal-example \"levy-curve\"\nsetup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
127
102
244
135
Sierpinsky Triangle
ca\nset fractal-example \"sierpinski-triangle\"\nsetup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
15
134
128
168
Dragon Curve
ca\nset fractal-example \"dragon-curve\"\nsetup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
127
134
245
168
Tree
ca\nset fractal-example \"tree\"\nsetup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
29
376
239
418
Amount that box lenth increases per iteration of box counting
11
0.0
1

MONITOR
173
413
244
458
# of Boxes
count boxes with [color = red]
17
1
11

BUTTON
25
278
140
311
Box Counting Setup
box-counting-setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
1029
269
1085
314
R^2
precision(r-square)2
17
1
11

MONITOR
928
269
1029
314
Equation of Line
lin-reg-eq
17
1
11

@#$#@#$#@
## WHAT IS IT?

This model investigates the box-counting dimension for a variety of fractals.

## HOW TO USE IT

The interface consists of three blocks: Fractal Examples, Box-Counting Controls and Plots/Results. Start by selecting one of the fractal examples, e.g., "Koch Curve".  Then click "Iterate".  Notice at the first iteration the Hausdorff dimension (1.262 for the Koch Curve) appears in a monitor on the right.   Click "Iterate" a few more times to get a developed fractal.  Now you are ready to apply box-counting to this fractal.

Under Box-Counting Controls, set "initial box length"  (i.e., length of side of each box) and "increment" (i.e., amount that box length increases per iteration of box counting). Press "Box Counting Setup" and then "Box Counting Go" and you should see small red boxes covering the fractal.  After the fractal has been completely covered, the log of number of boxes will be plotted versus the log of 1/box-length on the plot on the right.  These iterations will continue until you press "Box Counting Go" again to stop the process.  At that point you can press "linear-regression" on the right side (under the plot) to fit a line to the plotted points. The slope of this line is the box-counting dimension measured by your run; it appears in the monitor on the right, and can be compared with the Hausdorff dimension.

## THINGS TO NOTICE

The box-counting dimension becomes a more accurate approximation of Hausdorff dimension as the number of iterations increase. The accuracy also can depend on the initial settings for box-length and increment (you should experiment with all of these parameters).  However, you have probably noticed the iterations taking longer and longer to generate for each successive iteration.  This is because the number of line segments is increasing exponentially.  The Koch curve, for instance, begins with four line segments but has over a million line segments after ten iterations.

## CREDITS AND REFERENCES

This model is part of the Fractals series of the Complexity Explorer project.

Main Author:  John Driscoll

Contributions from: Vicki Niu, Melanie Mitchell

Netlogo:  Wilensky, U. (1999). NetLogo. http://ccl.northwestern.edu/netlogo/. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.

## HOW TO CITE

If you use this model, please cite it as: "Box Counting Dimension" model, Complexity Explorer project, http://complexityexplorer.org

## COPYRIGHT AND LICENSE

Copyright 2016 Santa Fe Institute.

This model is licensed by the Creative Commons Attribution-NonCommercial-ShareAlike International (http://creativecommons.org/licenses/). This states that you may copy, distribute, and transmit the work under the condition that you give attribution to ComplexityExplorer.org, and your use is for non-commercial purposes.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

square
false
0
Rectangle -7500403 true true -16 -9 310 311
Rectangle -7500403 true true 15 45 15 60
Rectangle -7500403 true true 46 0 300 242

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270

@#$#@#$#@
NetLogo 5.3.1
@#$#@#$#@
ballSetup
repeat 14 [ go ]
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

@#$#@#$#@
0
@#$#@#$#@
