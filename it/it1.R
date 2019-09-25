# Copyright (C) 2019 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

# Download daily Santa Fe, NM weather data for August 2016 from 
# https://figshare.com/s/de109f378939dfc0ed0b(santafe-temps.csv).
# Define X as a random variable that indicates whether it is hot on any given date
# (let X=hot when the MaxTemp for the day is greater than or equal to 80 degrees Fahrenheit and 
# X=not-hot otherwise). Define Y as a random variable that indicates whether there is rain on a given date
# (let Y=rain when Precipitation is greater than 0 and Y=no-rain otherwise).
# Compute the following information theoretic quantities: 
# I(X), I(Y), I(XY), I(X|Y), I(Y|X), and the mutual information I(X:Y)

rm (list=ls())
if (!require('entropy')){
  install.packages('entropy')
  library('entropy')
}

my.path  <- '~/../complexity/it'


raw.data <- read.csv(file.path(my.path,'santafe-temps.csv'))
X        <- unlist(lapply(raw.data$MaxTemp,function(t) {return (if (t>=80) 1 else 0)}))
Y        <- unlist(lapply(raw.data$Precipation,function(p) {return (if(p>0) 1 else 0)}))

IX       <- entropy(discretize(X,numBins = 2),unit='log2')
IY       <-entropy(discretize(Y,numBins = 2),unit='log2')

XY       <- discretize2d(X,Y,numBins1 = 2,numBins2 = 2)
IXY      <- entropy(XY,unit='log2')

IX_Y     <- IXY - IY
IY_X     <- IXY - IX
I_XY     <- IX + IY - IXY

print (sprintf('I(X)=%.3f,I(Y)=%.3f,I(XY)=%.3f',IX,IY,IXY))
print (sprintf('I(X|Y)=%.3f,I(Y|X)=%.3f,I(X:Y)=%.3f',IX_Y,IY_X,I_XY))

