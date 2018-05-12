# MIT License
# 
# Copyright (c) 2018 Simon Crase
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

rm(list=ls())

setwd ("C:/Users/Weka/201804/Experiments")
my.df<-read.table("take2 experiment-table.csv",
                  header = T,   # set columns names true
                  sep = ",",    # define the separator between       columns
                  skip = 6,     # skip first 6 rows 
                  quote = "\"", # correct the column separator
                  fill = TRUE ) # add blank fields if rows

# [1] "X.run.number."                            "max.payoff.high"                         
# [3] "n.ticks"                                  "p.start.low"                             
# [5] "n.history"                                "benefit.weight"                          
# [7] "n.investors"                              "p.start.high"                            
# [9] "p.payoff.low"                             "p.payoff.high"                           
# [11] "sigma.mutation"                           "randomize.step"                          
# [13] "tau"                                      "n.predictors"                            
# [15] "max.payoff.low"                           "n.coefficients"                          
# [17] "X.step."                                  "census.POOL.STABLE"                      
# [19] "outgoings.POOL.STABLE"                    "census.POOL.LOW"                         
# [21] "outgoings.POOL.LOW"                       "census.POOL.HIGH"                        
# [23] "outgoings.POOL.HIGH"                      "mean..wealth..of.investors"              
# [25] "standard.deviation..wealth..of.investors"

names(my.df)[24]<-"mean_wealth_of_investors"

