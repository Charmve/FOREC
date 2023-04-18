import os

# ##########
# General Args
# ##########
exp_name = 'train_all'
data_augment_method = 'full_aug' # ['no_aug', 'full_aug', 'sel_aug'] 
sampling_method = 'equal' #'concat' or 'equal'

exp_name_com = f'{exp_name}_{sampling_method}' 

cur_data_path = 'DATA/' #'../DATA_FINAL_ELEC/'
exp_output_dir = 'EVAL/'

# $ which python
# conda_python_dir = '~/anaconda3/envs/forec/bin/python'
conda_python_dir = '/usr/local/anaconda3/envs/xmrec/bin/python'
# conda_python_dir = os.system('which python')
print("Use python:", conda_python_dir)

print(f'\n- experiment name: {exp_name_com}')
print(f'\t - data augmentation methods: {data_augment_method}')
print(f'\t - data sampling method: {sampling_method}')
print(f'\t - reading data: {cur_data_path}')
print(f'\t - writing evaluations: {exp_output_dir}')


# ##########
# Market selection
# all_markets = [ 'jp', 'in', 'de', 'fr', 'ca', 'mx', 'uk', 'us'] 
# ##########
# target_markets = ['de', 'fr']
# source_markets = ['uk'] #, 'us' for no_aug use 'xx'

target_markets = ['jp', 'in', 'de', 'fr', 'ca', 'mx', 'uk']
source_markets = ['jp', 'in', 'de', 'fr', 'ca', 'mx', 'uk', 'us'] #, 'us' for no_aug use 'xx'


print(f'-Working on below market pairs (target, augmenting with market):')
all_poss_pairs = []
for target_market in target_markets:
    for source_market in source_markets:
        if target_market==source_market:
            continue
        if data_augment_method=='no_aug':
            source_market='xx'
        all_poss_pairs.append((target_market, source_market))
        print(f'\t--> ({target_market}, {source_market})')
all_poss_pairs = list(set(all_poss_pairs))

# ##########
# Training Data fractions to use from each target and source 
# 1 means full data, and 2 means 1/2 of the training data to sample
# ##########
tgt_fractions = [1]
src_fractions = [1] #2, 3, 4, 5, 10

fractions = []
print('\n-Sampling below training data fractions:')
for tgt_fraction in tgt_fractions:
    for src_fraction in src_fractions:
        fractions.append((src_fraction, tgt_fraction))
        print(f'\t--> ({src_fraction}, {tgt_fraction})')

command_dict = {}
for tgt_market, src_market in all_poss_pairs:
    for tgt_frac, src_fra in fractions:
        cur_cmd_dict = {}
        cur_exp_name = f'{exp_name_com}_{tgt_market}_{src_market}_{data_augment_method}_ftgt{tgt_frac}_fsrc{src_fra}'
        
        # 'train_base.py'
        py_file_main = 'train_base.py'
        cur_exp_out_file = f'{exp_output_dir}base-{cur_exp_name}.json'
        pre_set_args = {
            "--data_dir %s"%(cur_data_path),
            "--tgt_market %s"%(tgt_market),
            "--aug_src_market %s"%(src_market),
            "--exp_name %s"%(cur_exp_name),
            "--exp_output %s"%(cur_exp_out_file),

            "--num_epoch %i"%(25),  
            "--batch_size %i"%(1024),
            # "--cuda "

            "--data_augment_method %s"%(data_augment_method),
            "--data_sampling_method %s"%(sampling_method),

            "--tgt_fraction %i"%(tgt_frac),  
            "--src_fraction %i"%(src_fra),  
        }
        myargumets = ' '.join(pre_set_args)
        command_pieces = [conda_python_dir, py_file_main, myargumets]
        final_cmd = ' '.join(command_pieces)
        cur_cmd_dict['base'] = final_cmd
        
        if data_augment_method=='no_aug':
            command_dict[cur_exp_name] = cur_cmd_dict
            continue
        
        # 'train_maml.py'
        py_file_main = 'train_maml.py'
        fast_lr_tune = '0.1'
        shots = 20 #512, 200, 100, 50, 20
        cur_exp_out_file = f'{exp_output_dir}maml-{cur_exp_name}_shots{shots}.json'
        pre_set_args = {
            "--data_dir %s"%(cur_data_path),
            "--tgt_market %s"%(tgt_market),
            "--aug_src_market %s"%(src_market),
            "--exp_name %s"%(cur_exp_name),
            "--exp_output %s"%(cur_exp_out_file),

            "--num_epoch %i"%(25),  
            "--batch_size %i"%(shots),
            "--cuda "

            "--data_sampling_method %s"%(sampling_method),
            "--fast_lr %s"%(fast_lr_tune),
            "--tgt_fraction %i"%(tgt_frac),  
            "--src_fraction %i"%(src_fra),  
        }
        myargumets = ' '.join(pre_set_args)
        command_pieces = [conda_python_dir, py_file_main, myargumets]
        final_cmd = ' '.join(command_pieces)
        cur_cmd_dict['maml'] = final_cmd
        
        # 'train_forec.py'
        py_file_main = 'train_forec.py'
        cur_exp_out_file = f'{exp_output_dir}forec-{cur_exp_name}_shots{shots}.json'
        pre_set_args = {
            "--data_dir %s"%(cur_data_path),
            "--tgt_market %s"%(tgt_market),
            "--aug_src_market %s"%(src_market),
            "--exp_name %s"%(cur_exp_name),
            "--exp_output %s"%(cur_exp_out_file),

            "--num_epoch %i"%(25),  
            "--batch_size %i"%(shots),
            "--cuda "

            "--data_sampling_method %s"%(sampling_method),
            "--fast_lr %s"%(fast_lr_tune),
            "--tgt_fraction %i"%(tgt_frac),  
            "--src_fraction %i"%(src_fra),  
        }
        myargumets = ' '.join(pre_set_args)
        command_pieces = [conda_python_dir, py_file_main, myargumets]
        final_cmd = ' '.join(command_pieces)
        cur_cmd_dict['forec'] = final_cmd
        
        command_dict[cur_exp_name] = cur_cmd_dict
        
print(f'Generated {len(command_dict)} experiments:')
for k, v in command_dict.items():
    print(f'{k}')
    print(f'\t{list(v.keys())}')


import os
sh_files = 'scripts/'
sh_logs = os.path.join(sh_files,'logs')
checkpoints_dir = 'checkpoints/'
if not os.path.exists(sh_logs):
    os.mkdir(sh_files)
    os.mkdir(sh_logs)
if not os.path.exists(exp_output_dir):
    os.mkdir(exp_output_dir)
if not os.path.exists(checkpoints_dir):
    os.mkdir(checkpoints_dir)

gpu_num = 1
gpu_type = '1080ti-long' #'titanx-short', 'm40-short'

master_file = open(os.path.join(sh_files,'master.sh'), 'w')

for cur_exp_name, v in command_dict.items():

    bash_file_name = f'{cur_exp_name}-run.sh'
    bash_file = open(os.path.join(sh_files,bash_file_name), 'w')
    cur_log_file = os.path.join('logs', f'{cur_exp_name}.out')
    
    bash_file.write('#!/bin/sh'+'\n')
    bash_file.write('#SBATCH --partition=%s'%(gpu_type) + '\n')
    bash_file.write('#SBATCH --ntasks=%s'%(1) + '\n')
    bash_file.write('#SBATCH --gres=gpu:%s'%(str(gpu_num)) + '\n')
    bash_file.write('#SBATCH --mem=%iG'%(50*gpu_num) + '\n')
    bash_file.write('#SBATCH --output=%s'%(cur_log_file) + '\n')

    bash_file.write('\ncd ..\n')
    if 'base' in v:
        bash_file.write(v['base'] + '\n\n')
    if 'maml' in v:
        bash_file.write(v['maml'] + '\n\n')
    if 'forec' in v:
        bash_file.write(v['forec'] + '\n\n')

    bash_file.close()
    master_file.write(f'bash {bash_file_name}\n')
    print(cur_exp_name + ' bash is created!')

master_file.close()

print("\nWill start to train all model ...")

os.system('cd scripts/ && chmod +x *.sh && ./master.sh')
