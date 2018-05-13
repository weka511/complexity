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

read.nlogo.experiment<-function(path.name="C:/Users/Weka/201804/Experiments",file.name="take2 experiment-table.csv"){
    my.df <-
      read.table(
        file.path(path.name,file.name),
        header = T,
        sep = ",",
        skip = 6,
        quote = "\"",
        fill = TRUE
      )
    i <- 1
    for (name in colnames(my.df)) {
      new_name <- gsub("\\.", "_", name)
      names(my.df)[i] <- new_name
      i = i + 1
    }
    return (my.df)
  }
  
get.tau <-
  function (path.name="C:/Users/Weka/201804/Experiments",file.name="take2 experiment-table.csv") {
    my.df = read.nlogo.experiment(path.name,file.name)
    return(my.df[my.df$X_step_ == max(my.df$X_step_), ])
  }
  
extract.tau<-function(tau.data,can_borrow=TRUE,randomize_step=TRUE){
  mydata.canborrow <- if (can_borrow) "true" else "false"
  mydata.randomize_step <- if (randomize_step) "true" else "false"
  return (tau.data[tau.data$randomize_step==mydata.randomize_step&tau.data$can_borrow==mydata.canborrow,]) 
}

extract.wealth.vs.tau<-function(tau.data,can_borrow=TRUE,randomize_step=TRUE) {
  tau.data<-extract.tau(tau.data,can_borrow,randomize_step)
  tau.data.end<-tau.data[tau.data$X_step_==tau.data$n_ticks,]
  return (aggregate(tau.data.end,by=list(tau.data.end$tau),FUN=mean,na.rm=TRUE))
}

extract.errors.vs.tau<-function(tau.data,tau=0,can_borrow=TRUE,randomize_step=TRUE) {
  tau.data<-extract.tau(tau.data,can_borrow,randomize_step)
  return (tau.data[tau.data$tau==tau,])
}

get.configurations<-function(data,min_col=2,max_col=17) {
  is.varying<-function(name){
    return (nrow(unique(data[name]))>1)
  }
  return (Filter(is.varying,colnames(data)[min_col:max_col]))
}

get.n.configurations<-function(data) {
  product = 1
  for (name in get.configurations(data)) {
    product = product * nrow(unique(data[name]))
  }
  return (product)
}

get.n.repetitions<-function(data){
  return (  length(unique(data$X_run_number_)) / get.n.configurations(data))
}
