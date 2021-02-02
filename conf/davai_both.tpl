[DEFAULT]
namespace           = vortex.cache.fr
ref_xpid            = G48Y
ref_namespace       = vortex.multi.fr
# git
IAL_git_ref         = <IAL_git_ref>
IAL_repository      = <IAL_repository>
# shelves
commonenv           = uenv:cy48.commons.03@mary
appenv_global       = uenv:cy48.global@davai.08@mary
appenv_LAM          = uenv:cy48.LAM@davai.08@mary
appenv_clim         = cy43t2_clim-op2.02
input_store_global  = store_cy47t1_global.01@davai
input_store_LAM     = store_cy47t1_lam.01@davai
# Davai options
usecase             = <usecase>
davai_server        = http://intra.cnrm.meteo.fr/gws/davai
expertise_fatal_exceptions = False
profiling           = True
ignore_reference    = False
# default profile
MPIAUTOCONFIG       = /home/gmap/mrpe/mary/.mpiautorc/mpiauto.SUPERTIME_RSS.conf
time                = 00:10:00
ntasks              = 1
nnodes              = 1
openmp              = 1
# gmkpack (used for packname guessing)
gmkpack_packtype    = incr
gmkpack_compiler_label = MIMPIIFC1805
gmkpack_compiler_flag = 2y
# vortex defaults
model               = ifs

# === SETUP === #

[ciboulai_xpsetup]
comment             = Test CY48 nu via mkjob
partition           = transfert
mem                 = 1000
exclusive           = oversubscribe
namespace           = vortex.multi.fr

# === BUILD === #

[packbuild]
# date of release of base cycle ?
rundate             = 2020090300
time                = 02:00:00
building_system     = gmkpack

[gitref2pack]
# in case of main pack:
# todo: populate_filter_file & link_filter_file
# in case of incr pack:
preexisting_pack    = True
cleanpack           = True

[pack_compile_link]
threads             = 40
Ofrt                = 4
regenerate_ics      = False
# when to raise error: __finally__, __none__, __any__
fatal_build_failure = __finally__
cleanpack           = False


# === TESTS === #

[global]
appenv              = &{appenv_global}
input_store         = &{input_store_global}

[LAM]
appenv              = &{appenv_LAM}
input_store         = &{input_store_LAM}



[DEFAULT_SUZAT]
cycle               = uget:cy43t2_clim-bf.05.testsNewOroHdr.02@suzat
xpid                = G2DP
vortex_conf         = davai
vortex_app          = arpifs
time                = 05:05:00
ntasks              = 1
nnodes              = 1
openmp              = 1
usecase             = NRV
comment             = blabla
ref_xpid            = G2BA
#pack                = /home/gmap/mrpe/arbogaste/pack/46t1_bf.03.IMPIFC1801.2y
pack                = /home/gmap/mrpa/suzat/pack/46t1_bf-dev.03.IMPIIFC1805.2y/
#pack                = /home/gmap/mrpe/arbogaste/pack/46t1_bf.03.IMPIFC1801.2y/
#pack                = /home/gmap/mrpa/suzat/pack/cy46t1_bf.03.IMPIIFC1805.2y.pack/
DAVAI_SERVER        = http://intra.cnrm.meteo.fr/gws/davai
MPIAUTOCONFIG       = /home/gmap/mrpe/mary/.mpiautorc/mpiauto.SUPERTIME_RSS.conf
input_store         = store_cy46t1.02@davai
expertise_fatal_exceptions = False
commonenv           = uenv:cy46t1.commons.04@mary
appenv		    = uenv:cy46t1.global@davai.05@mary
obs_npools          = 16
obs_paraconst       = float(dict(airs:110,0.45 atms:27,0.2 conv:999999,0.5 cris:42,0.13 default:1000,1 geow:30,0.6 gmi:33,0.13 gps:30,0.8 gpssol:10,0.55 iasi:40,0.17 mwhsx:50,0.4 mwri:40,0.2 odim:80,4 radar:80,1 radar1:80,1 scat:55,0.35 sev:45,0.45 ssmis:48,0.4 tovsa:110,0.7 tovsb:26,0.15 tovsh:72,0.4))

timestep            = 1800

#  -------------------------------------
obstype        = conv,airsbt,atms


[b01]
block             = global/obsprep/raw2odb/4D/batodb_singleobs/conv
ymdh		  = 2017121006          
model		  = arpege
cutoff		  = assim
geometry          = globalupd149
expert1           = dict(kind:bator_profile)
expert2           = dict(kind:bator_obscount)
ignore_reference  = False
mapstages         = build
obstype		  = conv
obs_tslots        = 7/-PT3H/PT6H

[b02]
block             = global/obsprep/raw2odb/4D/batodb
ymdh		  = 2017121006          
model		  = arpege
cutoff		  = assim
geometry          = globalupd149
expert1           = dict(kind:bator_profile)
expert2           = dict(kind:bator_obscount)
ignore_reference  = False
mapstages         = build
obs_tslots        = 7/-PT3H/PT6H

[b03]
block             = global/obsprep/raw2odb/4D/batodb_singleobs/conv
ymdh		  = 2017121006          
model		  = arpege
cutoff		  = assim
geometry          = globalupd149
expert1           = dict(kind:bator_profile)
expert2           = dict(kind:bator_obscount)
ignore_reference  = False
mapstages         = build
obs_tslots        = 7/-PT3H/PT6H


[e01]
block             = global/obsprep/make_ccma/3D/by_obstype
ymdh		  = 2017121006          
model		  = arpege
cutoff		  = assim
#class_obs_in      = global/obsprep/raw2odb/3D/batodb
class_obs_in      = global/obsprep/raw2odb/4D/batodb
mapstages         = build
obstype 	  = airs
geometry          = globalupd149
init_term         = 6
nd                = 4D
profiling         = True
test_family       = op_obs_file
test_type         = test_hop
obs_tslots        = 1/-PT1H/PT2H

[s01]
profiling         = True
block             = global/assim/screening/4D/CNT0/mix_obstypes/screening
obs_tslots        = 13/-PT3H/PT6H
ignore_reference  = False
ymdh              = 2017121006
cutoff            = assim
model             = arpege
mapstages         = build
geometry          = globalupd149
timestep          = 1800
class_obs_in      = global/obsprep/raw2odb/4D/batodb
expert1           = dict(kind:joTables)
obstype           = airs,atms,conv,cris,geow,gmi,gps,gpssol,iasi,scat,sev,ssmis,tovsa,tovsb,tovsh
init_term         = 6

[s02]
profiling         = True
block             = global/assim/screening/4D/CNT0/mix_obstypes/screening
obs_tslots        = 13/-PT3H/PT6H
ignore_reference  = False
ymdh              = 2017121006
cutoff            = assim
model             = arpege
mapstages         = build
geometry          = globalupd149
timestep          = 1800
class_obs_in      = global/obsprep/raw2odb/4D/batodb
expert1           = dict(kind:joTables)
obstype           = ssmis
init_term         = 6
