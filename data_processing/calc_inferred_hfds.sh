
model=CanESM2
experiments=(historicalMisc)
rips=(r1i1p4)

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

sftlf_file=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_rip}.nc
rsds_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rsds/latest/rsds_Amon_${model}_${experiment}_${rip}_*.nc
rsus_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rsus/latest/rsus_Amon_${model}_${experiment}_${rip}_*.nc
rlds_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rlds/latest/rlds_Amon_${model}_${experiment}_${rip}_*.nc
rlus_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rlus/latest/rlus_Amon_${model}_${experiment}_${rip}_*.nc
hfss_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/hfss/latest/hfss_Amon_${model}_${experiment}_${rip}_*.nc
hfls_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/hfls/latest/hfls_Amon_${model}_${experiment}_${rip}_*.nc

hfsithermds_files=${ua6_dir}/${experiment}/mon/ocean/${rip}/hfsithermds/latest/hfsithermds_Omon_${model}_${experiment}_${rip}_*.nc

command="${python} ${script_dir}/calc_inferred_hfds.py ${sftlf_file} --rsds_files ${rsds_files} --rsus_files ${rsus_files} --rlds_files ${rlds_files} --rlus_files ${rlus_files} --hfss_files ${hfss_files} --hfls_files ${hfls_files} --hfsithermds ${hfsithermds_files}"
# --hfsithermds ${hfsithermds_files}

echo ${command}
${command}

done
done

