args = commandArgs(trailingOnly=TRUE)
root = args[1]
sample = args[2]
daily_obs = args[3]

indir=paste0(root, '/s',sample,'/')
pdf(paste(indir,"evalplot_singleModel_season.pdf"),height=20, width=10)
par(mfrow=c(6,2))
require(wesanderson)


#indir = "/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc1_1D/"
#daily_obs  = '/home/joel/sim/qmap/GR_data/sim/g4//forcing/meteoc1_1D.csv' 
# the period to do quantile mapping over (obs and sim must overlap!)
startDateQmap = "1990-01-01"
endDateQmap = "1999-12-31"
# common historical period of models
startDateHist = "1979-01-01"
endDateHist = "2005-12-31"
# obs

obs=read.csv(daily_obs)
	# aggregate obs to daily resolution

qmap_files = list.files(path = paste0(indir,"/aqmap_results/"),full.names=TRUE )
results_qmap = qmap_files[ grep('_qmap_',qmap_files)]
results_nmap = qmap_files[ grep('_nmap_',qmap_files)]
results_season = qmap_files[ grep('_season_',qmap_files)]


# llop thru list of vars
myvars=c( 'tasmin', 'tasmax','pr', 'hurs', 'rsds','rlds' )#, 'uas', 'vas',, 'ps','tas',)

for (var in myvars){
print(var)



#for (var in myvars){




	if(var=="tas"){obsindex <-11; convFact <-1} # K
	if(var=="tasmin"){obsindex <-14; convFact <-1} # K
	if(var=="tasmax"){obsindex <-13; convFact <-1} # K
		if(var=="pr"){obsindex <-6; convFact <-(1/3600)} # kgm-2s-1 obs are in mean mm/hr for that day convert to mm/s (cordex)
			if(var=="ps"){obsindex <-5; convFact <-1}# Pa
				if(var=="hurs"){obsindex <-8; convFact <-100} # % 0-100
					if(var=="rsds"){obsindex <-4; convFact <-1}	# Wm-2
						if(var=="rlds"){obsindex <-3; convFact <-1}# Wm-2
							if(var=="uas"){obsindex <-2; convFact <-1}# ms-1
								if(var=="vas"){obsindex <-2; convFact <-1}# ms-1

	# read and convert obs unit
	obs_var=obs[,obsindex]*convFact	

		# compute u and v here
	if(var=="uas"){
	ws <- obs$VW
	wd <- obs$DW
	    obs_var = ws * cos(wd)
	  }
	    if(var=="vas"){
	    ws <- obs$VW
		wd <- obs$DW
    	obs_var = ws * sin(wd)
    }

	# aggregate obs to daily resolution
	obs_datetime= strptime(obs$datetime,format="%Y-%m-%d")

	# cut obs to qmap period 
	start_obs = which(obs_datetime==startDateQmap)
	end_obs=which(obs_datetime==endDateQmap)
	obs_qmap_period= obs_var[start_obs: end_obs]

	# cut obs to cordex historical common  period 
	start_obs =1 # simply first ob as CORDEX hist period stats before 1980-01-01 otherwise use "end_obs=which(obs_datetime==startDateHist)"
	end_obs=which(obs_datetime==endDateHist)
	obs_cp_period= obs_var[start_obs: end_obs]
	obs_cp_dates = obs_datetime[start_obs: end_obs]









# filenames
load(results_season [grep(paste0('hist.*',var,'$'),results_season) ] )
hist_qmap_season_list = df
load(results_nmap [grep(paste0('hist.*',var,'$'),results_season) ] )
hist_nqmap= df
load(results_qmap [grep(paste0('hist.*',var,'$'),results_season) ] )
hist_qmap_list= df

load(results_season [grep(paste0('rcp26.*',var,'$'),results_season) ] )
rcp26_qmap_season_list= df
load(results_nmap [grep(paste0('rcp26.*',var,'$'),results_season) ] )
rcp26_nqmap=df
load(results_season [grep(paste0('rcp85.*',var,'$'),results_season) ] )
rcp85_qmap_season_list= df
load(results_nmap [grep(paste0('rcp85.*',var,'$'),results_season) ] )
rcp85_nqmap=df

cordex_dates_cp=hist_qmap_season_list$Date
greg_cal_rcp=rcp26_qmap_season_list$Date
#===============================================================================
# Plots
#===============================================================================
mycol = wes_palette("Zissou1", 3, type = "continuous")

#===============================================================================
# prepare data yearly
#===============================================================================

# extract data from list

# prepare data annual means and stats
df=as.data.frame(hist_qmap_season_list)
years_hist=( substr(cordex_dates_cp, 1, 4)) 
hist_year = aggregate(df, list(years_hist), mean)
hist_year$SD=apply(hist_year[,2:(dim(hist_year)[2]-1)],1, sd, na.rm = TRUE)
hist_year$MEAN=apply(hist_year[,2:(dim(hist_year)[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(hist_nqmap)
years_hist=( substr(cordex_dates_cp, 1, 4)) 
hist_year_nq = aggregate(df, list(years_hist), mean)
hist_year_nq$SD=apply(hist_year_nq[,2:(dim(hist_year_nq)[2]-1)],1, sd, na.rm = TRUE)
hist_year_nq$MEAN=apply(hist_year_nq[,2:(dim(hist_year_nq)[2]-2)],1, mean, na.rm = TRUE)

df=as.data.frame(rcp26_qmap_season_list)
years_rcp26=( substr( greg_cal_rcp, 1, 4)) 
rcp26_year = aggregate(df, list(years_rcp26), mean)
rcp26_year$SD=apply(rcp26_year[,2:(dim(rcp26_year)[2]-1)],1, sd, na.rm = TRUE)
rcp26_year$MEAN=apply(rcp26_year[,2:(dim(rcp26_year)[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(rcp26_nqmap)
years_rcp26=( substr( greg_cal_rcp, 1, 4)) 
rcp26_year_nq = aggregate(df, list(years_rcp26), mean)
rcp26_year_nq$SD=apply(rcp26_year_nq[,2:(dim(rcp26_year_nq)[2]-1)],1, sd, na.rm = TRUE)
rcp26_year_nq$MEAN=apply(rcp26_year_nq[,2:(dim(rcp26_year_nq)[2]-2)],1, mean, na.rm = TRUE)

df=as.data.frame(rcp85_qmap_season_list)
years_rcp85=( substr( greg_cal_rcp, 1, 4)) 
rcp85_year = aggregate(df, list(years_rcp85), mean)
rcp85_year$SD=apply(rcp85_year[,2:(dim(rcp85_year)[2]-1)],1, sd, na.rm = TRUE)
rcp85_year$MEAN=apply(rcp85_year[,2:(dim(rcp85_year)[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(rcp85_nqmap)
years_rcp85=( substr( greg_cal_rcp, 1, 4)) 
rcp85_year_nq = aggregate(df, list(years_rcp85), mean)
rcp85_year_nq$SD=apply(rcp85_year_nq[,2:(dim(rcp85_year_nq)[2]-1)],1, sd, na.rm = TRUE)
rcp85_year_nq$MEAN=apply(rcp85_year_nq[,2:(dim(rcp85_year_nq)[2]-2)],1, mean, na.rm = TRUE)

#obs
years_obs=( substr( obs_cp_dates, 1, 4)) 
obs_year = aggregate(obs_cp_period, list(years_obs), mean)

#===envelope plots========================================================================
if (var == 'tas'){

	pdf(paste(indir,var,"TS2.pdf"))
	# caption: Mean annual near surface air temperature at the Weissfluhjoch (2540m asl)  showing corrected historical, RCP2.6 and RCP8.5 timseries. Observations and uncorrected historical data are also shown for comparison. The coloured envelops indicate +/- 1 SD of the model spread and multi-modal mean is given by the bold line.
	lwd=3
	plot(rcp26_year$Group.1, rcp26_year$MEAN, xlim=c(1979,2100),ylim=c(270,280), type='l', col=mycol[1], lwd=lwd, ylab="Air temperacture (K)", xlab=" ")


	y = c(rcp26_year$MEAN- rcp26_year$SD,rev(rcp26_year$MEAN+ rcp26_year$SD))
	x=c((rcp26_year$Group.1),rev(rcp26_year$Group.1))
	polygon (x,y, col=rgb(0, 0, 1,0.5),border='NA')


	lines(rcp85_year$Group.1, rcp85_year$MEAN, ylim=c(270,280), type='l', col=mycol[3],lwd=lwd)
	y = c(rcp85_year$MEAN- rcp85_year$SD,rev(rcp85_year$MEAN+ rcp85_year$SD))
	x=c((rcp85_year$Group.1),rev(rcp85_year$Group.1))
	polygon (x,y, col=rgb(1, 0, 0,0.5),border='NA')


	lines(hist_year$Group.1, hist_year$MEAN, ylim=c(270,280), type='l', col=mycol[2],lwd=lwd)
	y = c(hist_year$MEAN- hist_year$SD,rev(hist_year$MEAN+ hist_year$SD))
	x=c((hist_year$Group.1),rev(hist_year$Group.1))
	polygon (x,y, col=rgb(0, 1, 0,0.5),border='NA')

	lines(hist_year_nq, ylim=c(270,280), type='l', col=mycol[2],lwd=lwd,lty=2)
	lines(obs_year,lwd=lwd)
	legend("bottomright", c("Hist", "RCP2.6", "RCP8.5", "Hist_uncorrected", "OBS"), col=c(rgb(0, 1, 0),mycol[1],mycol[3],mycol[2], "black"),lty=c(1,1,1,2,1),lwd=3)
	dev.off()

}

if (var == 'tas'){

	pdf(paste(indir,var,"TS2_NOQMAP.pdf"))
	# caption: Mean annual near surface air temperature at the Weissfluhjoch (2540m asl)  showing corrected historical, RCP2.6 and RCP8.5 timseries. Observations and uncorrected historical data are also shown for comparison. The coloured envelops indicate +/- 1 SD of the model spread and multi-modal mean is given by the bold line.
	lwd=3
	plot(rcp26_year$Group.1, rcp26_year$MEAN, xlim=c(1979,2100),ylim=c(270,280), type='l', col=mycol[1], lwd=lwd, ylab="Air temperacture (K)", xlab=" ")
	lines(rcp26_year_nq$Group.1, rcp26_year_nq$MEAN, ylim=c(270,280), type='l', col=mycol[1],lwd=lwd,lty=2)

	lines(rcp85_year$Group.1, rcp85_year$MEAN, ylim=c(270,280), type='l', col=mycol[3],lwd=lwd)
	lines(rcp85_year_nq$Group.1, rcp85_year_nq$MEAN, ylim=c(270,280), type='l', col=mycol[3],lwd=lwd,lty=2)


	lines(hist_year$Group.1, hist_year$MEAN, ylim=c(270,280), type='l', col=mycol[2],lwd=lwd)
	lines(hist_year_nq, ylim=c(270,280), type='l', col=mycol[2],lwd=lwd,lty=2)
	lines(obs_year,lwd=lwd)
	legend("bottomright", c("Hist", "RCP2.6", "RCP8.5", "Hist_uncorrected", "OBS"), col=c(rgb(0, 1, 0),mycol[1],mycol[3],mycol[2], "black"),lty=c(1,1,1,2,1),lwd=3)
	dev.off()

}


#===============================================================================
# prepare data monthly
#===============================================================================

# extract data from list

# prepare data annual means and stats
df=as.data.frame(hist_qmap_season_list)
months_hist=( substr(cordex_dates_cp, 1, 7)) 
hist_month = aggregate(df, list(months_hist), mean)
hist_month$SD=apply(hist_month[,2:(dim(hist_month)[2]-1)],1, sd, na.rm = TRUE)
hist_month$MEAN=apply(hist_month[,2:(dim(hist_month)[2]-2)],1, mean, na.rm = TRUE)


# extract data from list

# no season qmap
df=as.data.frame(hist_qmap_list)
months_hist=( substr(cordex_dates_cp, 1, 7)) 
hist_month_noseas = aggregate(df, list(months_hist), mean)
hist_month_noseas $SD=apply(hist_month_noseas [,2:(dim(hist_month_noseas )[2]-1)],1, sd, na.rm = TRUE)
hist_month_noseas $MEAN=apply(hist_month_noseas [,2:(dim(hist_month_noseas )[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(hist_nqmap)
months_hist=( substr(cordex_dates_cp, 1, 7)) 
hist_month_nq = aggregate(df, list(months_hist), mean)
hist_month_nq$SD=apply(hist_month_nq[,2:(dim(hist_month_nq)[2]-1)],1, sd, na.rm = TRUE)
hist_month_nq$MEAN=apply(hist_month_nq[,2:(dim(hist_month_nq)[2]-2)],1, mean, na.rm = TRUE)

df=as.data.frame(rcp26_qmap_season_list)
months_rcp26=( substr( greg_cal_rcp, 1, 7)) 
rcp26_month = aggregate(df, list(months_rcp26), mean)
rcp26_month$SD=apply(rcp26_month[,2:(dim(rcp26_month)[2]-1)],1, sd, na.rm = TRUE)
rcp26_month$MEAN=apply(rcp26_month[,2:(dim(rcp26_month)[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(rcp26_nqmap)
months_rcp26=( substr( greg_cal_rcp, 1, 7)) 
rcp26_month_nq = aggregate(df, list(months_rcp26), mean)
rcp26_month_nq$SD=apply(rcp26_month_nq[,2:(dim(rcp26_month_nq)[2]-1)],1, sd, na.rm = TRUE)
rcp26_month_nq$MEAN=apply(rcp26_month_nq[,2:(dim(rcp26_month_nq)[2]-2)],1, mean, na.rm = TRUE)

df=as.data.frame(rcp85_qmap_season_list)
months_rcp85=( substr( greg_cal_rcp, 1, 7)) 
rcp85_month = aggregate(df, list(months_rcp85), mean)
rcp85_month$SD=apply(rcp85_month[,2:(dim(rcp85_month)[2]-1)],1, sd, na.rm = TRUE)
rcp85_month$MEAN=apply(rcp85_month[,2:(dim(rcp85_month)[2]-2)],1, mean, na.rm = TRUE)

# no qmap
df=as.data.frame(rcp85_nqmap)
months_rcp85=( substr( greg_cal_rcp, 1, 7)) 
rcp85_month_nq = aggregate(df, list(months_rcp85), mean)
rcp85_month_nq$SD=apply(rcp85_month_nq[,2:(dim(rcp85_month_nq)[2]-1)],1, sd, na.rm = TRUE)
rcp85_month_nq$MEAN=apply(rcp85_month_nq[,2:(dim(rcp85_month_nq)[2]-2)],1, mean, na.rm = TRUE)

#obs
months_obs=( substr( obs_cp_dates, 1, 7)) 
obs_month = aggregate(obs_cp_period, list(months_obs), mean)



#===============================================================================
# summary stats
#===============================================================================
# cor(obs_month, hist_month$MEAN)
# cor(obs_month, hist_qmap_month$MEAN)

# rmse(obs_month, hist_month$MEAN)
# rmse(obs_month, hist_qmap_month$MEAN)

# mean(obs_month)
# mean(hist_month$MEAN)
# mean(hist_qmap_month$MEAN)

#===============================================================================
# ecdf
#===============================================================================
lwd=3
plot(ecdf(obs_month$x), ylab="cdf",  col=mycol[1], xlab="TA (K)", main=var, lwd=lwd,lty=1)
lines(ecdf(hist_month_nq[,2]),  col=mycol[2], lwd=lwd)
lines(ecdf(hist_month_noseas[,2]),  col=mycol[3], lwd=1)
lines(ecdf(hist_month[,2]),  col='green', lwd=1)
legend("topleft", c("OBS", "CLIM", "CLIM_QM", "CLIM_QMSEASON"), col=c(mycol[1],mycol[2], mycol[3], 'green'),lty=c(1,1,1,1) ,lwd=lwd)


#===============================================================================
# doy
#===============================================================================

# make doy vector (slightly different periods (+/- 1 year))
doy_hist=substr((cordex_dates_cp), 6,10)
doy_obs=substr((obs_cp_dates), 6,10)

# DOY obs
obs_doy = aggregate(obs_cp_period, list(doy_obs), mean)

# DOY SEASON QMAP

df=as.data.frame(hist_qmap_season_list)
hist_doy = aggregate(df, list(doy_hist), mean)
hist_doy$MEAN=apply(hist_doy[,2:(dim(hist_doy)[2]-1)],1, mean, na.rm = TRUE)

# DOY NO SEASON QMAP

df=as.data.frame(hist_qmap_list)
hist_doy_noseas = aggregate(df, list(doy_hist), mean)
hist_doy_noseas $MEAN=apply(hist_doy_noseas [,2:(dim(hist_doy_noseas )[2]-1)],1, mean, na.rm = TRUE)

# NO QMAP
df=as.data.frame(hist_nqmap)
hist_doy_nq = aggregate(df, list(doy_hist), mean)
hist_doy_nq$MEAN=apply(hist_doy_nq[,2:(dim(hist_doy_nq)[2]-1)],1, mean, na.rm = TRUE)


#
#pdf(paste(outdir,var,"DOY2.pdf"))
plot(obs_doy$x, type='l',col=mycol[1],lwd=lwd,lty=2, xlab='DOY', ylab='Air temperature [k]', main=var)
lines(hist_doy_nq$MEAN, type='l', col=mycol[2], lwd=lwd)
lines(hist_doy_noseas$MEAN ,type='l', col=mycol[3],lwd=lwd)
lines(hist_doy$MEAN, type='l', col='green',lwd=lwd)
#legend("topright", c("OBS", "CLIM", "CLIM_QM"), col=c(mycol[1],mycol[2], mycol[3]),lty=c(2,1,1) ,lwd=lwd)
legend("topright", c("OBS", "CLIM", "CLIM_QM", "CLIM_QMSEASON"), col=c(mycol[1],mycol[2], mycol[3], 'green'),lty=c(2,1,1,1) ,lwd=lwd)

}
dev.off()