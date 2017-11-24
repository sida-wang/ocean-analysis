

wind_metric=tauu-nwloc
#tauu-swloc tauu-swmag tauu-nwloc tauu-nwmag
#tauu-seloc tauu-semag tauu-neloc tauu-nemag

wind_name=nh_westerly_location
# sh_westerly_location sh_westerly_magnitude nh_westerly_location nh_westerly_magnitude
# sh_easterly_location sh_easterly_magnitude nh_easterly_location nh_easterly_magnitude

tas_metric=tas-global-mean
#tas-ita tas-global-mean

tas_name=global_mean_temperature
#interhemispheric_temperature_asymmetry global_mean_temperature


outfile=/g/data/r87/dbi599/figures/wind_stress/${tas_metric}-vs-${wind_metric}_Ayr_ensemble_historicalGHG-historicalAA_rall_all.png

command="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python plot_trend_scatter.py air_temperature ${wind_name} ${outfile} --xfiles /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_CanESM2_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r3i1p1/tas/latest/${tas_metric}_Ayr_CanESM2_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r5i1p1/tas/latest/${tas_metric}_Ayr_CanESM2_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_CCSM4_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/atmos/r4i1p1/tas/latest/${tas_metric}_Ayr_CCSM4_historicalGHG_r4i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r2i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r3i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r4i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r4i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r5i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r6i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r6i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r7i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r7i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r8i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r8i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r9i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r9i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r10i1p1/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalGHG_r10i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_FGOALS-g2_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-CM3/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_GFDL-CM3_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-ESM2M/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_GFDL-ESM2M_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r2i1p1/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalGHG_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r3i1p1/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r4i1p1/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalGHG_r4i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r5i1p1/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/IPSL-CM5A-LR/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_IPSL-CM5A-LR_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalGHG/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_NorESM1-M_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r1i1p4/tas/latest/${tas_metric}_Ayr_CanESM2_historicalMisc_r1i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r2i1p4/tas/latest/${tas_metric}_Ayr_CanESM2_historicalMisc_r2i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r3i1p4/tas/latest/${tas_metric}_Ayr_CanESM2_historicalMisc_r3i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r4i1p4/tas/latest/${tas_metric}_Ayr_CanESM2_historicalMisc_r4i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r5i1p4/tas/latest/${tas_metric}_Ayr_CanESM2_historicalMisc_r5i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/atmos/r1i1p10/tas/latest/${tas_metric}_Ayr_CCSM4_historicalMisc_r1i1p10_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r1i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r2i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r2i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r3i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r3i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r4i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r4i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r5i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r5i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r6i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r6i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r7i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r7i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r8i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r8i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r9i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r9i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r10i1p4/tas/latest/${tas_metric}_Ayr_CSIRO-Mk3-6-0_historicalMisc_r10i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalMisc/yr/atmos/r2i1p1/tas/latest/${tas_metric}_Ayr_FGOALS-g2_historicalMisc_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r1i1p107/tas/latest/${tas_metric}_Ayr_GISS-E2-H_historicalMisc_r1i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r2i1p107/tas/latest/${tas_metric}_Ayr_GISS-E2-H_historicalMisc_r2i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r3i1p107/tas/latest/${tas_metric}_Ayr_GISS-E2-H_historicalMisc_r3i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r4i1p107/tas/latest/${tas_metric}_Ayr_GISS-E2-H_historicalMisc_r4i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r5i1p107/tas/latest/${tas_metric}_Ayr_GISS-E2-H_historicalMisc_r5i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r1i1p310/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalMisc_r1i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r2i1p310/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalMisc_r2i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r3i1p310/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalMisc_r3i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r4i1p310/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalMisc_r4i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r5i1p310/tas/latest/${tas_metric}_Ayr_GISS-E2-R_historicalMisc_r5i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/atmos/r1i1p1/tas/latest/${tas_metric}_Ayr_NorESM1-M_historicalMisc_r1i1p1_all.nc --yfiles /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r3i1p1/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalGHG/yr/atmos/r5i1p1/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_CCSM4_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/atmos/r4i1p1/tauu/latest/tauu-metrics_Ayr_CCSM4_historicalGHG_r4i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r2i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r3i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r4i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r4i1p1_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r5i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r6i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r6i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r7i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r7i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r8i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r8i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r9i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r9i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/atmos/r10i1p1/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalGHG_r10i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_FGOALS-g2_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-CM3/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_GFDL-CM3_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-ESM2M/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_GFDL-ESM2M_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalGHG_r1i1p1_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r2i1p1/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalGHG_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r3i1p1/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalGHG_r3i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r4i1p1/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalGHG_r4i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalGHG/yr/atmos/r5i1p1/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalGHG_r5i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/IPSL-CM5A-LR/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_IPSL-CM5A-LR_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalGHG/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_NorESM1-M_historicalGHG_r1i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r1i1p4/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalMisc_r1i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r2i1p4/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalMisc_r2i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r3i1p4/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalMisc_r3i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r4i1p4/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalMisc_r4i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/atmos/r5i1p4/tauu/latest/tauu-metrics_Ayr_CanESM2_historicalMisc_r5i1p4_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/atmos/r1i1p10/tauu/latest/tauu-metrics_Ayr_CCSM4_historicalMisc_r1i1p10_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r1i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r2i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r2i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r3i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r3i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r4i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r4i1p4_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r5i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r5i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r6i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r6i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r7i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r7i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r8i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r8i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r9i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r9i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/atmos/r10i1p4/tauu/latest/tauu-metrics_Ayr_CSIRO-Mk3-6-0_historicalMisc_r10i1p4_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalMisc/yr/atmos/r2i1p1/tauu/latest/tauu-metrics_Ayr_FGOALS-g2_historicalMisc_r2i1p1_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r1i1p107/tauu/latest/tauu-metrics_Ayr_GISS-E2-H_historicalMisc_r1i1p107_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r2i1p107/tauu/latest/tauu-metrics_Ayr_GISS-E2-H_historicalMisc_r2i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r3i1p107/tauu/latest/tauu-metrics_Ayr_GISS-E2-H_historicalMisc_r3i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r4i1p107/tauu/latest/tauu-metrics_Ayr_GISS-E2-H_historicalMisc_r4i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/atmos/r5i1p107/tauu/latest/tauu-metrics_Ayr_GISS-E2-H_historicalMisc_r5i1p107_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r1i1p310/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalMisc_r1i1p310_all.nc  /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r2i1p310/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalMisc_r2i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r3i1p310/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalMisc_r3i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r4i1p310/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalMisc_r4i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/atmos/r5i1p310/tauu/latest/tauu-metrics_Ayr_GISS-E2-R_historicalMisc_r5i1p310_all.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/atmos/r1i1p1/tauu/latest/tauu-metrics_Ayr_NorESM1-M_historicalMisc_r1i1p1_all.nc --time 1861-01-01 2005-12-31 --xlabel ${tas_name} --best_fit"

echo ${command}
${command}
echo ${outfile}