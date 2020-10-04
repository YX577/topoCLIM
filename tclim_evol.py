# a more evolved way of tclim' ing

"""
python3

This module takes post processed daily CORDEX downloads from esgf_post.py and 
produces point timeseries with standard calenders

Example:


Vars:


Details:


"""
import sys
import os
import glob
import xarray as xr
import calendar3 as cal3
import shutil
import subprocess
import pandas as pd
from tqdm import tqdm
import tclim_disagg
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
#===============================================================================
# INPUT
#===============================================================================
wd = "/home/joel/sim/qmap"
grid='g3'
raw_dir= wd+'/raw_cordex/'
nc_standard_clim=raw_dir+'/aresult/standard/ICHEC-EC-EARTH_rcp85_r12i1p1_CLMcom-CCLM5-0-6_v1__TS.nc_TS_ALL_ll.nc'
nc_standard_hist=raw_dir+'/aresult/standard/ICHEC-EC-EARTH_historical_r12i1p1_KNMI-RACMO22E_v1__TS.nc_TS_ALL_ll.nc'
tscale_sim_dir = wd+ "/GR_data/sim/"+grid +"/"
root = '/home/joel/sim/qmap/topoclim_test_hpc/'+ grid + "/"
namelist="/home/joel/sim/qmap/topoclim/fsm/nlst_qmap.txt"
indir = root.split('/g')[0]
num_cores=2
fsmexepath = "/home/joel/src/topoCLIM/FSM"

#===============================================================================
# METHODS
#===============================================================================
def howmanyFiles(wd):
	config = ConfigObj(wd+"/config.ini")


	#===============================================================================
	# model downloads accounting
	#===============================================================================
	nchistfiles = glob.glob(raw_dir+ "*historical*")
	ncrcp26files = glob.glob(raw_dir+ "*rcp26*")
	ncrcp85files = glob.glob(raw_dir+ "*rcp85*")
	# file names

	ncfiles_vec= nchistfiles,ncrcp26files, ncrcp85files

	for ncfiles in ncfiles_vec:
		allfiles = [i.split('raw_cordex/', 1)[1] for i in ncfiles] # c. 9000 models, pars, times
		rootfiles = [i.split('day', 1)[0] for i in allfiles]
		modelPars = list(set(rootfiles)) # c.5000 models, par

		models2 = list(set([i.split('_', 1)[1] for i in rootfiles]))  # c. 60 models
		print(len(models2))
		#26                                                                                                                                                                                                                                                                                                               


	# check for complete nc files
def completeFiles(raw_dir):
	ncfiles = glob.glob(raw_dir+'/aresult/'+ '*_TS_ALL_ll.nc')


	nc_complete=[]
	for nc in ncfiles:

		ds = xr.open_dataset(nc,decode_times=True)

		if  len(ds.data_vars)  <10:
			print ("not enough vars "+nc)
			next   

		else:
			print (nc)
			nc_complete.append(nc)

	return(nc_complete)


def calendarNinja(nc, nc_standard_hist,nc_standard_clim):
	''' converts calender'''
	print(nc)
	outname = nc.split(".nc")[0]+"_SCAL.nc" 
	if os.path.isfile(outname) == True:
		os.remove(outname)
	#nc=nc_complete[9] no leapS
	#nc=nc_complete[10] # 360 day

	# sthis file has a standard calender and used as target in interpolation (hist or clim periods)
	if  'historical' in nc: 
		ds1 = xr.open_dataset(nc_standard_hist, decode_times=True)
	if  'rcp' in nc: 
		ds1 = xr.open_dataset(nc_standard_clim,decode_times=True)

	ds = xr.open_dataset(nc,decode_times=True)

	datetimeindex = ds.indexes["time"]
	if datetimeindex.is_all_dates is False: 
		dateob = datetimeindex[0]
		cal = dateob.calendar
		print(cal)
		# print(dateob.datetime_compatible)

		#ds_conv = convert_calendar(ds, ds1,'year', 'time')  
		ds_interp = cal3.interp_calendar(ds, ds1, 'time')  
		#  this one failed as strange time index'/home/joel/sim/qmap/raw_cordex//aresult/IPSL-IPSL-CM5A-MR_historical_r1i1p1_SMHI-RCA4_v1__TS.nc_TS_ALL_ll.nc'  - seems to be one off monitor if this is reproduced next toime run esgf_post.py

		# now we have to fill na in first and last timestep which results from interpolation
		vars = list(ds_interp.data_vars.keys())  
	
		for var in vars:
			# backfill step 0 
			ds_interp[var][0,:,:] =ds_interp[var][1,:,:] 
			# foward fill step -1
			ds_interp[var][-1,:,:] =ds_interp[var][-2,:,:] 

		# this just checks it worked
		datetimeindex = ds_interp.indexes["time"]
		if datetimeindex.is_all_dates is True: 
			#dateob = datetimeindex[0]
			#cal = dateob.calendar
			print("Succesfully converted "+cal+ " to standard calender")
			#print(dateob.datetime_compatible)

			# rename object for next step
	

			dsout = ds_interp.ffill(1)
			#dsout = ds_interp.bfill(1)

			dsout.to_netcdf(outname)  
		else:
			"Something went wrong cal3 conversionfailed"

	else:
		print("Standard calender exists " + nc)
		#os.rename(nc, outname)
		shutil.copy2(nc , outname)

def resamp_1D(path_inpt, freq='1D'):# create 1h wfj era5 obs data by

	# freq = '1H' or '1D'
	df_obs= pd.read_csv(path_inpt, index_col=0, parse_dates=True)
	df_1d = df_obs.resample(freq).mean()
	TAMIN = df_obs['TA'].resample(freq).min()
	TAMAX = df_obs['TA'].resample(freq).max()
	df_1d['TAMAX']  =TAMAX
	df_1d['TAMIN']  =TAMIN
	df_1d.to_csv(path_or_buf=path_inpt.split('.')[0]  + '_'+freq+'.csv' ,na_rep=-999,float_format='%.3f', header=True, sep=',')
	return(path_inpt.split('.')[0]  + '_'+freq+'.csv')


def resamp_1H(path_inpt, freq='1H'):# create 1h wfj era5 obs data by

	# freq = '1H' or '1D'
	df_obs= pd.read_csv(path_inpt, index_col=0, parse_dates=True)
	df_1d = df_obs.resample(freq).interpolate()
	df_1d.to_csv(path_or_buf=path_inpt.split('.')[0]  + '_'+freq+'.csv' ,na_rep=-999,float_format='%.3f', header=True, sep=',')
	return(path_inpt.split('.')[0]  + '_'+freq+'.csv')


def run_qmap(path_inpt):

	#linearly resample era5 to daily and capture new path as variable 
	daily_obs = resamp(path_inpt, '1D')

	# run qmap
	sample =daily_obs.split('/')[-1].split('.')[0]
	#logging.info("Running qmap job "+ sample )
	cmd = ["Rscript", "qmap_hour_plots_daily.R", root ,str(sample),  daily_obs]
	subprocess.check_output(cmd)
	#logging.info("Qmap job "+ sample + "complete") 

def extract_timeseries(ncfile, lon, lat):
	''' extract timesseries from netcdf file based on lon and lat'''
	ds = xr.open_dataset(ncfile,decode_times=True)
	df = ds.sel(lon=longitude, lat=latitude, method='nearest').to_dataframe()
	return(df)

def met2fsm(qfile, slope): 

	qdat= pd.read_csv(qfile, index_col=0, parse_dates=True)
	outdir = os.path.split(qfile)[0]  + "/meteo/"
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	# partition prate to rain snow (mm/hr)	
	lowthresh=272.15
	highthresh = 274.15
	d = {'prate': qdat.PINT, 'ta': qdat.TA}
	df = pd.DataFrame(data=d)
	snow = df.prate.where(df.ta<lowthresh) 
	rain=df.prate.where(df.ta>=highthresh) 

	mix1S = df.prate.where((df.ta >= lowthresh) & (df.ta<=highthresh), inplace = False)
	mix1T = df.ta.where((df.ta >= lowthresh) & (df.ta<=highthresh), inplace = False)
	mixSno=(highthresh - mix1T) / (highthresh-lowthresh)
	mixRain=1-mixSno
	addSnow=mix1S*mixSno
	addRain=mix1S*mixRain

	# nas to 0
	snow[np.isnan(snow)] = 0 	
	rain[np.isnan(rain)] = 0 
	addRain[np.isnan(addRain)] = 0 
	addSnow[np.isnan(addSnow)] = 0 

	# # linearly reduce snow to zero in steep slopes
	#if steepSnowReduce=="TRUE": # make this an option if need that in future

	snowSMIN=30.
	snowSMAX=80.
	slope=slope

	k= (snowSMAX-slope)/(snowSMAX - snowSMIN)

	if slope<snowSMIN:
		k=1
	if slope>snowSMAX:
		k=0

	snowTot=(snow+addSnow) * k
	rainTot=rain + addRain

	outname1=qfile.split('/')[-1]  
	outname=outname1.split('_Q_H.txt')[0]


	#Filter TA for absolute 0 vals - still need this?
	
	qdat.TA[qdat.TA<220]=np.nan
	qdat.TA = qdat.TA.ffill()
	qdat.P[qdat.P<10000]=np.nan
	qdat.P = qdat.P.ffill()
	qdat.ILWR[qdat.ILWR<100]=np.nan
	qdat.ILWR = qdat.ILWR.ffill()
	qdat.RH[qdat.RH<5]=np.nan
	qdat.RH = qdat.RH.ffill()

	dates=qdat.index
	df_fsm= pd.DataFrame({	
	 				"year": dates.year, 
	 				"month": dates.month, 
					"day": dates.day, 
					"hour": dates.hour,
					"ISWR":qdat.ISWR, 
					"ILWR":qdat.ILWR, 
					"Sf":snowTot/(60.*60.), # prate in mm/hr to kgm2/s
					"Rf":rainTot/(60.*60.), # prate in mm/hr to kgm2/s
					"TA":qdat.TA, 
					"RH":qdat.RH,#*0.01, #meteoio 0-1
					"VW":qdat.VW,
					"P":qdat.P,
					
					
					})

	df_fsm.to_csv(path_or_buf=outdir+outname+"_F.txt" ,na_rep=-999,float_format='%.8f', header=False, sep='\t', index=False, 
		columns=['year','month','day', 'hour', 'ISWR', 'ILWR', 'Sf', 'Rf', 'TA', 'RH', 'VW', 'P'])
	#os.remove(qfile)

	# Meteorological driving data are read from a text file named in namelist `&drive`. A driving data file has 12 columns containing the variables listed in the table below. Each row of the file corresponds with a timestep. Driving data for the Col de Porte example are given in file `data/met_CdP_0506.txt`.

	# | Variable | Units  | Description       |
	# |----------|--------|-------------------|
	# | year     | years  | Year              |
	# | month    | months | Month of the year |
	# | day      | days   | Day of the month  |
	# | hour     | hours  | Hour of the day   |
	# | SW       | W m<sup>-2</sup> | Incoming shortwave radiation  |
	# | LW       | W m<sup>-2</sup> | Incoming longwave radiation   |
	# | Sf       | kg m<sup>-2</sup> s<sup>-1</sup> | Snowfall rate |
	# | Rf       | kg m<sup>-2</sup> s<sup>-1</sup> | Rainfall rate |
	# | Ta       | K      | Air temperature      |
	# | RH       | RH     | Relative humidity    |
	# | Ua       | m s<sup>-1</sup> | Wind speed |
	# | Ps       | Pa     | Surface air pressure 

	print("Written "+ outdir+outname )



def findDelete(pattern, dir=False):
	#pattern = "./smeteo*/fsm/*HOURLY.txt"
	   
	if dir==False:
		files = glob.glob(pattern, recursive=False)
		for f in files: 
			os.remove(f) 
	if dir==True:
		folders = glob.glob(pattern, recursive=True)
		for f in folders: 
			shutil.rmtree(f)

def findCompress(pattern):
	#pattern = "./smeteo*/fsm/*HOURLY.txt"
	filesFolders = glob.glob(pattern, recursive=True)   
	for f in tqdm(filesFolders): 
		print(f)
		shutil.make_archive(f, 'zip', f)

def spatialfsm_base(root):

	qfiles = sorted(glob.glob(root + "/fsm*"))  
	timeslicehist=[]

	for filename in qfiles:

		df =pd.read_csv(filename, delim_whitespace=True, parse_dates=[[0,1,2]], header=None)
		df.set_index(df.iloc[:,0], inplace=True)  
		df.drop(df.columns[[0]], axis=1, inplace=True )  
		swe=df.iloc[:,2]
		timeslicehist.append(swe['1980-01-01' :'2000-01-01'].max()	)		

	pd.Series.timeslicehist.to_csv(root+"/timeslicehist.csv",header=False, float_format='%.3f') 

def spatialfsm(root):
	meanhist=[]
	nclust =len(glob.glob(root + "/smeteoc*"))
	for i in range(0,nclust):
		print(i)
		qfiles = glob.glob(root + "/smeteoc"+str(i+1)+"_1D/fsm/output/*HIST*.txt")

		timeslicehist=[]

		for filename in qfiles:
			try:
				df =pd.read_csv(filename, delim_whitespace=True, parse_dates=[[0,1,2]], header=None)
			except:
				print("no data")
				continue
			df.set_index(df.iloc[:,0], inplace=True)  
			df.drop(df.columns[[0]], axis=1, inplace=True )  
			swe=df.iloc[:,2]
			timeslicehist.append(swe['1980-01-01' :'2000-01-01'].mean()	)
		
		meanhist.append(np.mean(timeslicehist))

	pd.Series(meanhist).to_csv(root+"/meanhist.csv",header=False, float_format='%.3f') 



	mean2040=[]
	mean2090=[]
	for i in range(0,nclust):
		print(i)
		qfiles = glob.glob(root + "/smeteoc"+str(i+1)+"_1D/fsm/output/*RCP26*.txt")

		timeslice2040=[]
		timeslice2090=[]
		for filename in qfiles:
			try:
				df =pd.read_csv(filename, delim_whitespace=True, parse_dates=[[0,1,2]], header=None)
			except:
				print("no data")
				continue

			df.set_index(df.iloc[:,0], inplace=True)  
			df.drop(df.columns[[0]], axis=1, inplace=True )  
			swe=df.iloc[:,2]
			timeslice2040.append(swe['2030-01-01' :'2050-01-01'].mean()	)
			timeslice2090.append(swe['2080-01-01' :'2099-01-01'].mean() )	
			

		mean2040.append(np.mean(timeslice2040))
		mean2090.append(np.mean(timeslice2090))


	pd.Series(mean2040).to_csv(root+"/mean2030.csv",header=False, float_format='%.3f') 
	pd.Series(mean2090).to_csv(root+"/mean2080.csv",header=False,float_format='%.3f') 


	# rcp85
	mean2040=[]
	mean2090=[]
	for i in range(0,nclust):
		print(i)
		qfiles = glob.glob(root + "/smeteoc"+str(i+1)+"_1D/fsm/output/*RCP85*.txt")

		timeslice2040=[]
		timeslice2090=[]
		for filename in qfiles:
			try:
				df =pd.read_csv(filename, delim_whitespace=True, parse_dates=[[0,1,2]], header=None)
			except:
				print("no data")
				continue

			df.set_index(df.iloc[:,0], inplace=True)  
			df.drop(df.columns[[0]], axis=1, inplace=True )  
			swe=df.iloc[:,2]
			timeslice2040.append(swe['2030-01-01' :'2050-01-01'].mean()	)
			timeslice2090.append(swe['2080-01-01' :'2099-01-01'].mean() )	
			
		mean2040.append(np.mean(timeslice2040))
		mean2090.append(np.mean(timeslice2090))

	pd.Series(mean2040).to_csv(root+"/mean2030_rcp85.csv",header=False, float_format='%.3f') 
	pd.Series(mean2090).to_csv(root+"/mean2080_rcp85.csv",header=False,float_format='%.3f') 

def plot(obs):
    plt.figure()
    ax = plt.gca()
    obs.plot()
    plt.legend()
    plt.show()

def tclim_main(tscale_file):
	print(tscale_file)
	daily_obs = resamp_1D(tscale_file)

	# run qmap
	sample =daily_obs.split('/')[-1].split('.')[0]
	#logging.info("Running qmap job "+ sample )
	cmd = ["Rscript", "qmap_hour_plots_daily.R", root ,str(sample),  daily_obs, str(mylon), str(mylat)]
	subprocess.check_output(cmd)

	cmd = ["Rscript", "qmap_plots.R", root ,str(sample),  daily_obs]
	subprocess.check_output(cmd)

	# cleanup _HOURLY.txt
	# /home/joel/sim/qmap/topoclim_test_hpc/g4/smeteoc1_1D/aqmap_results
	#findDelete(root+"/**/aqmap_results", dir=True)

	# list all daily qmap files
	daily_cordex_files = glob.glob(root+"/s"+sample+ "/fsm/*Q.txt")
	# hourly obs
	hourly_obs= resamp_1H(tscale_file)
	# loop over with dissag routine
	for daily_cordex in daily_cordex_files:
		tclim_disagg.main(daily_cordex,hourly_obs,  str(mylon), str(mylat), str(mytz))

def met2fsm_parallel(qfile):

	''' wrapper to allow joblib paralellistation'''
	print(qfile)
	sample = int(qfile.split("smeteoc")[1].split("_")[0])-1
	slope=lp.slp[sample] 
	met2fsm(qfile,slope)

def fsm_sim(meteofile, namelist, fsmexepath):
	# fsm executable must exist in indir
	print(meteofile)

	METEOFILENAME = os.path.split(meteofile)[1]
	METEOFILEPATH = os.path.split(meteofile)[0]
	FSMPATH = os.path.split(METEOFILEPATH)[0] 
	if not os.path.exists(FSMPATH+"/FSM"): 
		os.system("cp "+fsmexepath +" " +FSMPATH)
	os.chdir(FSMPATH)
	try:
		os.mkdir(FSMPATH+'/output')
	except:
		pass


	#for n in 31: #range(32):
	n=31
	config = np.binary_repr(n, width=5)
	print('Running FSM configuration ',config,n)
	f = open('nlst.txt', 'w')
	out_file = 'out.txt'
	with open(namelist) as file:
		for line in file:
			f.write(line)
			if 'config' in line:
				f.write('  nconfig = '+str(n)+'\n')
			if 'drive' in line:
				f.write('  met_file = ' +"'./meteo/"+METEOFILENAME+"'"+'\n')
			if 'out_file' in line:
				out_file = line.rsplit()[-1]
			out_name = out_file.replace('.txt','')
	f.close()

	
	#os.system("cp nlst.txt " +FSMPATH)
	
	os.system('./FSM < nlst.txt')
	save_file = FSMPATH + '/output/'+METEOFILENAME+'_'+config+'.txt'
	os.system('mv '+out_file+' '+save_file)
		#os.system('rm nlst.txt')

#===============================================================================
# KODE
#===============================================================================

if not os.path.exists(root):
		os.makedirs(root)


# list avaliable cordex
nc_complete = completeFiles(raw_dir) 

# convert all cordex to standard calender - should be run once per domain (but is quick)


#calendarNinja(nc_complete, nc_standard_hist,nc_standard_clim)
Parallel(n_jobs=int(num_cores))(delayed(calendarNinja)(nc,nc_standard_hist,nc_standard_clim) for nc in nc_complete)
# find all era5 meteo files
tscale_files = glob.glob(tscale_sim_dir+"/forcing/"+ "meteoc*")

# clean up old resamples
for f in glob.glob(tscale_sim_dir+"/forcing/"+ "*1D.csv"):
	os.remove(f)

# clean up old resamples
for f in glob.glob(tscale_sim_dir+"/forcing/"+ "*1H.csv"):
	os.remove(f)









# get grid box
lp = pd.read_csv(tscale_sim_dir + "/listpoints.txt")
# this doesnt seem to be era5 grid centres - check
mylon = lp.lon.mean()#mean(lp.lon) # normally all lon are the same (grid centre), however recent version tsub allows the position to be weight by pixel positions, mean() then gets back to grid centre
mylat = lp.lat.mean()
mytz = int(lp.tz.mean())

# rerun after cleanup
tscale_files = tqdm(sorted(glob.glob(tscale_sim_dir+"/forcing/"+ "meteoc*")))

Parallel(n_jobs=int(num_cores))(delayed(tclim_main)(tscale_file) for tscale_file in tscale_files)

# cleanup _HOURLY.txt
#findDelete(root+"/*/fsm/*Q.txt")


# converts standard output to FSm or...
qfiles = tqdm(sorted(glob.glob(root+"/*/fsm/*Q_H.txt")))
#for qfile in tqdm(qfiles):
Parallel(n_jobs=int(num_cores))(delayed(met2fsm_parallel)(qfile) for qfile in qfiles)
# cleanup _HOURLY.txt
#findDelete(root+"/*/fsm/*Q_HOURLY.txt")

# Simulate FSm
meteofiles = tqdm(sorted(glob.glob(root+"/*/fsm/meteo/*F.txt")))
#os.chdir(indir)
Parallel(n_jobs=int(num_cores))(delayed(fsm_sim)(meteofile,namelist,fsmexepath) for meteofile in meteofiles)

# At present a simple fixed output format is used. The output text file has 10 columns:

# | Variable | Units  | Description       |
# |----------|--------|-------------------|
# | year     | years  | Year              |
# | month    | months | Month of the year |
# | day      | days   | Day of the month  |
# | hour     | hours  | Hour of the day   |
# | alb      | -      | Effective albedo  |
# | Rof      | kg m<sup>-2</sup> | Cumulated runoff from snow    |
# | snd      | m      | Average snow depth                       |
# | SWE      | kg m<sup>-2</sup> | Average snow water equivalent |
# | Tsf      | &deg;C | Average surface temperature              |
# | Tsl      | &deg;C | Average soil temperature at 20 cm depth  |
	
# map
spatialfsm(root)
	
# x5 compression 50GB -> 10GB
#findCompress(root + "/**/meteo")  
#findDelete(root+"/**/meteo", dir=True)





file="/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/out.txt"  
file="/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/CNRM-CERFACS-CNRM-CM5_SMHI-RCA4_HIST_F.txt"

file="/home/joel/sim/qmap/GR_data/sim/g3/out/FSM/fsm001.txt_00.txt"
def plot_fsm(file, col):
	df =pd.read_csv(file, delim_whitespace=True, parse_dates=[[0,1,2]], header=None) 
	df.set_index(df.iloc[:,0], inplace=True)  
	df.drop(df.columns[[0]], axis=1, inplace=True )  
	swe=df.iloc[:,col]
	plot(swe)


	file="/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/out.txt" 
	plot_fsm(file, 2)


	file = '/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/fsm/CNRM-CERFACS-CNRM-CM5_CLMcom-CCLM5-0-6_HIST_Q.txt' 
	q1 =pd.read_csv(file, parse_dates=True)

	file="/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/fsm/CNRM-CERFACS-CNRM-CM5_CLMcom-CCLM5-0-6_HIST_Q_H.txt"
	hr1 =pd.read_csv(file, parse_dates=True)
	file="/home/joel/sim/qmap/topoclim_test_hpc/g3/smeteoc6_1D/fsm/CNRM-CERFACS-CNRM-CM5_CLMcom-CCLM5-0-6_HIST_Q_HOURLY.txt"
	hr2 =pd.read_csv(file, parse_dates=True)