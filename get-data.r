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

# Extract data from a Netlogo BehaviourSpace experiment
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

extract.step.data<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3){
  mydata.canborrow <- if (can_borrow) "true" else "false"
  mydata.randomize_step <- if (randomize_step) "true" else "false"
  return (netlogo.data[netlogo.data$randomize_step==mydata.randomize_step & 
                         netlogo.data$can_borrow==mydata.canborrow &
                         netlogo.data$tau==tau &
                         netlogo.data$n_predictors==n_predictors &
                         netlogo.data$n_coefficients==n_coefficients,
                       ]) 
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

# Get names of input parameters that have more than one value in experiment file
get.names.of.varying.parameters<-function(data,min_col=2,max_col=17) {
  is.varying<-function(name){
    return (nrow(unique(data[name]))>1)
  }
  return (Filter(is.varying,colnames(data)[min_col:max_col]))
}

# Get total number of combinations of input parameters values
get.n.configurations<-function(data) {
  product = 1
  for (name in get.names.of.varying.parameters(data)) {
    product = product * nrow(unique(data[name]))
  }
  return (product)
}

get.n.repetitions<-function(data){
  return (  length(unique(data$X_run_number_)) / get.n.configurations(data))
}

get.ns<-function(data){
  f<-function(name){toString(unique(data[name]))}
  return (lapply(get.configurations(data),f))
}

get.netlogo.values<-function(data){
  get.param.values<-function(name){
      values<-unique(data[name])[[1]]
      return (paste(values,collapse=", "))
    }
  return (lapply(get.names.of.varying.parameters(data),get.param.values))
}

get.netlogo.params<-function(data){
  return ( data.frame(get.names.of.varying.parameters(data),
                      unlist(get.netlogo.values(data))) )
}

plot.errors<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3) {
  err<-extract.step.data(netlogo.data,can_borrow,randomize_step,tau,n_predictors,n_coefficients)
  plot(err$X_step_,err$mean__sum_squares_error__of_investors,
       xlab = "Step",ylab = "Squared error",pch=20,
       main=sprintf("n_predictors=%d, n_coefficients=%d",n_predictors,n_coefficients))
}

plot.wealth<-function(netlogo.data,can_borrow=TRUE,randomize_step=TRUE,tau=0,n_predictors=3,n_coefficients=3) {
  err<-extract.step.data(netlogo.data,can_borrow,randomize_step,tau,n_predictors,n_coefficients)
  plot(err$X_step_,err$mean__wealth__of_investors,
       xlab = "Step",ylab = "Wealth",pch=20,
       main=sprintf("n_predictors=%d, n_coefficients=%d",n_predictors,n_coefficients))
}
