institution=MIROC
model=MIROC-ES2L
cmip_version=v20190823
scenario_version=v20190823
fx_version=v20190823
grid=gn
ripf=r1i1p1f2
end_future_date=210012
fx_exp=historical


cmip_exp=historical
scenario_exp=ssp585

start_date=185001
end_hist_date=201412

python="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python -W ignore"
script_dir=/home/599/dbi599/ocean-analysis/data_processing

cmip_dir=/g/data1b/oi10/replicas/CMIP6/CMIP/${institution}/${model}
scenario_dir=/g/data1b/oi10/replicas/CMIP6/ScenarioMIP/${institution}/${model}
r87_cmip_dir=/g/data/r87/dbi599/CMIP6/CMIP/${institution}/${model}
r87_scenario_dir=/g/data/r87/dbi599/CMIP6/ScenarioMIP/${institution}/${model}

cmip_tfiles=(`ls ${cmip_dir}/${cmip_exp}/${ripf}/Omon/thetao/${grid}/${cmip_version}/thetao_Omon_${model}_${cmip_exp}_${ripf}_${grid}_??????-??????.nc`)
cmip_sfiles=(`ls ${cmip_dir}/${cmip_exp}/${ripf}/Omon/so/${grid}/${cmip_version}/so_Omon_${model}_${cmip_exp}_${ripf}_${grid}_??????-??????.nc`)
cmip_wfo_files=(`ls ${cmip_dir}/${cmip_exp}/${ripf}/Omon/wfo/${grid}/${cmip_version}/wfo_Omon_${model}_${cmip_exp}_${ripf}_${grid}_??????-??????.nc`)
cmip_tos_files=(`ls ${cmip_dir}/${cmip_exp}/${ripf}/Omon/tos/${grid}/${cmip_version}/tos_Omon_${model}_${cmip_exp}_${ripf}_${grid}_??????-??????.nc`)
scenario_tfiles=(`ls ${scenario_dir}/${scenario_exp}/${ripf}/Omon/thetao/${grid}/${scenario_version}/thetao_Omon_${model}_${scenario_exp}_${ripf}_${grid}_??????-??????.nc`)
scenario_sfiles=(`ls ${scenario_dir}/${scenario_exp}/${ripf}/Omon/so/${grid}/${scenario_version}/so_Omon_${model}_${scenario_exp}_${ripf}_${grid}_??????-??????.nc`)

# Basin file

basin_dir=${r87_cmip_dir}/${fx_exp}/${ripf}/Ofx/basin/${grid}/${cmip_version}
mkdir -p ${basin_dir}
basin_file=${basin_dir}/basin_Ofx_${model}_${fx_exp}_${ripf}_${grid}.nc
basin_command="${python} ${script_dir}/calc_basin.py ${cmip_tfiles[0]} sea_water_potential_temperature ${basin_file}" 
echo ${basin_command}
${basin_command}

# Volume file

## Use actual volume file
#volume_file=${cmip_dir}/${fx_exp}/${ripf}/Ofx/volcello/${grid}/${fx_version}/volcello_Ofx_${model}_${fx_exp}_${ripf}_${grid}.nc

## Generate from areacello data
areacello_file=${cmip_dir}/${fx_exp}/${ripf}/Ofx/areacello/${grid}/${fx_version}/areacello_Ofx_${model}_${fx_exp}_${ripf}_${grid}.nc
volume_dir=${r87_cmip_dir}/${fx_exp}/${ripf}/Ofx/volcello/${grid}/${fx_version}
mkdir -p ${volume_dir}
volume_file=${volume_dir}/volcello_Ofx_${model}_${fx_exp}_${ripf}_${grid}.nc
volume_command="${python} ${script_dir}/calc_volcello.py ${cmip_tfiles[0]} sea_water_potential_temperature ${volume_file} --area_file ${areacello_file}"
echo ${volume_command}
${volume_command}


# Area profiles

cmip_wm_dir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/water-mass/${grid}/${cmip_version}
mkdir -p ${cmip_wm_dir}

scenario_wm_dir=${r87_scenario_dir}/${scenario_exp}/${ripf}/Omon/water-mass/${grid}/${scenario_version}
mkdir -p ${scenario_wm_dir}

## Each file individually

#cmip_awm_command="bash ${script_dir}/calc_water_mass_components_by_area.sh ${areacello_file} ${basin_file} ${cmip_tfiles[@]}"
#echo ${cmip_awm_command}
#${cmip_awm_command}

#cmip_awmfiles=(`ls ${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/water-mass/${grid}/${cmip_version}/surface-water-mass*.nc`)
#cmip_merge_command="${python} ${script_dir}/merge_files.py ${cmip_awmfiles[@]} /g/data/r87/dbi599/zika/surface-water-mass_Omon_${model}_${cmip_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc --variables Grid-Cell_Area_binned_by_temperature Sea_Water_Salinity_times_Grid-Cell_Area_binned_by_temperature Sea_Water_Potential_Temperature_times_Grid-Cell_Area_binned_by_temperature Grid-Cell_Area_binned_by_salinity Sea_Water_Salinity_times_Grid-Cell_Area_binned_by_salinity Sea_Water_Potential_Temperature_times_Grid-Cell_Area_binned_by_salinity"
#echo ${cmip_merge_command}
#${cmip_merge_command}

#scenario_awm_command="bash ${script_dir}/calc_water_mass_components_by_area.sh ${areacello_file} ${basin_file} ${scenario_tfiles[@]}"
#echo ${scenario_awm_command}
#${scenario_awm_command}

#scenario_awmfiles=(`ls ${r87_scenario_dir}/${scenario_exp}/${ripf}/Omon/water-mass/${grid}/${scenario_version}/surface-water-mass*.nc`)
#scenario_merge_command="${python} ${script_dir}/merge_files.py ${scenario_awmfiles[@]} /g/data/r87/dbi599/zika/surface-water-mass_Omon_${model}_${scenario_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc --variables Grid-Cell_Area_binned_by_temperature Sea_Water_Salinity_times_Grid-Cell_Area_binned_by_temperature Sea_Water_Potential_Temperature_times_Grid-Cell_Area_binned_by_temperature Grid-Cell_Area_binned_by_salinity Sea_Water_Salinity_times_Grid-Cell_Area_binned_by_salinity Sea_Water_Potential_Temperature_times_Grid-Cell_Area_binned_by_salinity"
#echo ${scenario_merge_command}
#${scenario_merge_command}

## All files at once

cmip_awm_file=${cmip_wm_dir}/surface-water-mass_Omon_${model}_${cmip_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc
cmip_awm_command="${python} ${script_dir}/calc_water_mass_components.py ${areacello_file} ${basin_file} ${cmip_awm_file} --salinity_files ${cmip_sfiles[@]} --temperature_files ${cmip_tfiles[@]}"
echo ${cmip_awm_command}
${cmip_awm_command}

scenario_awm_file=${scenario_wm_dir}/surface-water-mass_Omon_${model}_${scenario_exp}_${ripf}_${grid}_201501-${end_future_date}.nc
scenario_awm_command="${python} ${script_dir}/calc_water_mass_components.py ${areacello_file} ${basin_file} ${scenario_awm_file} --salinity_files ${scenario_sfiles[@]} --temperature_files ${scenario_tfiles[@]}"
echo ${scenario_awm_command}
${scenario_awm_command}


# Volume profiles

## Each file individually

#cmip_vwm_command="bash ${script_dir}/calc_water_mass_components_by_volume.sh ${volume_file} ${basin_file} ${cmip_tfiles[@]}"
#echo ${cmip_vwm_command}
#${cmip_vwm_command}

#cmip_vwmfiles=(`ls ${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/water-mass/${grid}/${cmip_version}/water-mass*.nc`)
#cmip_merge_command="${python} ${script_dir}/merge_files.py ${cmip_vwmfiles[@]} /g/data/r87/dbi599/zika/water-mass_Omon_${model}_${cmip_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc --variables Ocean_Grid-Cell_Volume_binned_by_temperature Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature Ocean_Grid-Cell_Volume_binned_by_salinity Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_salinity Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_salinity"
#echo ${cmip_merge_command}
#${cmip_merge_command}

#scenario_vwm_command="bash ${script_dir}/calc_water_mass_components_by_volume.sh ${volume_file} ${basin_file} ${scenario_tfiles[@]}"
#echo ${scenario_vwm_command}
#${scenario_vwm_command}

#scenario_vwmfiles=(`ls ${r87_scenario_dir}/${scenario_exp}/${ripf}/Omon/water-mass/${grid}/${scenario_version}/water-mass*.nc`)
#scenario_merge_command="${python} ${script_dir}/merge_files.py ${scenario_vwmfiles[@]} /g/data/r87/dbi599/zika/water-mass_Omon_${model}_${scenario_exp}_${ripf}_${grid}_201501-${end_future_date}.nc --variables Ocean_Grid-Cell_Volume_binned_by_temperature Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature Ocean_Grid-Cell_Volume_binned_by_salinity Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_salinity Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_salinity"
#echo ${scenario_merge_command}
#${scenario_merge_command}

## All files at once

cmip_vwm_file=${cmip_wm_dir}/water-mass_Omon_${model}_${cmip_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc
cmip_vwm_command="${python} ${script_dir}/calc_water_mass_components.py ${volume_file} ${basin_file} ${cmip_vwm_file} --salinity_files ${cmip_sfiles[@]} --temperature_files ${cmip_tfiles[@]}"
echo ${cmip_vwm_command}
${cmip_vwm_command}

scenario_vwm_file=${scenario_wm_dir}/water-mass_Omon_${model}_${scenario_exp}_${ripf}_${grid}_201501-${end_future_date}.nc
scenario_vwm_command="${python} ${script_dir}/calc_water_mass_components.py ${volume_file} ${basin_file} ${scenario_vwm_file} --salinity_files ${scenario_sfiles[@]} --temperature_files ${scenario_tfiles[@]}"
echo ${scenario_vwm_command}
${scenario_vwm_command}


# T-S distributions

r87_tdir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/thetao/${grid}/${cmip_version}
mkdir -p ${r87_tdir}
tclim_file=${r87_tdir}/thetao_Omon_${model}_${cmip_exp}_${ripf}_${grid}_2005-2014-monthly-clim.nc
tclim_command="${python} ${script_dir}/calc_monthly_climatology.py ${cmip_tfiles[@]} ${tclim_file} --time_bounds 2005-01-01 2014-12-31" 
echo ${tclim_command}
${tclim_command}

r87_sdir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/so/${grid}/${cmip_version}
mkdir -p ${r87_sdir}
sclim_file=${r87_sdir}/so_Omon_${model}_${cmip_exp}_${ripf}_${grid}_2005-2014-monthly-clim.nc
sclim_command="${python} ${script_dir}/calc_monthly_climatology.py ${cmip_sfiles[@]} ${sclim_file} --time_bounds 2005-01-01 2014-12-31" 
echo ${sclim_command}
${sclim_command}

r87_vdist_dir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/volo/${grid}/${cmip_version}
mkdir -p ${r87_vdist_dir}
vdist_file=${r87_vdist_dir}/volo-tsdist_Omon_${model}_${cmip_exp}_${ripf}_${grid}_2005-2014-monthly-clim.nc
vdist_command="${python} ${script_dir}/calc_vol_ts_dist.py ${tclim_file} ${sclim_file} ${volume_file} ${basin_file} ${vdist_file}"
echo ${vdist_command}
${vdist_command}

r87_adist_dir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/areao/${grid}/${cmip_version}
mkdir -p ${r87_adist_dir}
adist_file=${r87_adist_dir}/areao-tsdist_Omon_${model}_${cmip_exp}_${ripf}_${grid}_2005-2014-monthly-clim.nc
adist_command="${python} ${script_dir}/calc_vol_ts_dist.py ${tclim_file} ${sclim_file} ${areacello_file} ${basin_file} ${adist_file}"
echo ${adist_command}
${adist_command}


# Surface water flux

r87_wfo_dir=${r87_cmip_dir}/${cmip_exp}/${ripf}/Omon/wfo/${grid}/${cmip_version}
mkdir -p ${r87_wfo_dir}
cmip_wfo_tos_file=${r87_wfo_dir}/wfo-tos-binned_Omon_${model}_${cmip_exp}_${ripf}_${grid}_${start_date}-${end_hist_date}.nc
cmip_wfo_tos_command="${python} ${script_dir}/calc_surface_flux_histogram.py ${cmip_wfo_files[@]} water_flux_into_sea_water ${areacello_file} ${basin_file} ${cmip_wfo_tos_file} --bin_files ${cmip_tos_files[@]} --bin_var sea_surface_temperature"
echo ${cmip_wfo_tos_command}
${cmip_wfo_tos_command}


ls -l ${vdist_file}
ls -l ${adist_file}
ls -l ${cmip_vwm_file}
ls -l ${cmip_awm_file}
ls -l ${scenario_vwm_file}
ls -l ${scenario_awm_file}
ls -l ${cmip_wfo_tos_file}

