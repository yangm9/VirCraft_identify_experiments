# train 
mkdir train
cat train_sample.list |while read i
do
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate && virCraft.py identify -a ../../07_fragment_subsample/train/${i}.fasta -t 64 -o train/${i}_identify -f permissive -m vs2-vb-dvf-gn -l 1000
    checkv end_to_end ../../07_fragment_subsample/train/${i}.fasta train/${i}_identify/work_files/checkv_all -d ~/database/checkvDB/checkv-db-v1.5 -t 64
    proviral_predict.py ../../07_fragment_subsample/train/${i}_identify/work_files/candidate_viral_ctgs.info.tsv train/${i}_identify/work_files/checkv_all
done

# val
mkdir val
cat val_sample.list |while read i
do
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate && virCraft.py identify -a ../../07_fragment_subsample/val/${i}.fasta -t 64 -o val/${i}_identify -f permissive -m vs2-vb-dvf-gn -l 1000
    checkv end_to_end ../../07_fragment_subsample/val/${i}.fasta val/${i}_identify/work_files/checkv_all -d ~/database/checkvDB/checkv-db-v1.5 -t 64
    proviral_predict.py ../../07_fragment_subsample/val/${i}_identify/work_files/candidate_viral_ctgs.info.tsv val/${i}_identify/work_files/checkv_all
done

# test
mkdir test
cat test_sample.list |while read i
do
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate && virCraft.py identify -a ../../07_fragment_subsample/test/${i}.fasta -t 64 -o test/${i}_identify -f permissive -m vs2-vb-dvf-gn -l 1000
    checkv end_to_end ../../07_fragment_subsample/test/${i}.fasta test/${i}_identify/work_files/checkv_all -d ~/database/checkvDB/checkv-db-v1.5 -t 64
    proviral_predict.py ../../07_fragment_subsample/test/${i}_identify/work_files/candidate_viral_ctgs.info.tsv test/${i}_identify/work_files/checkv_all
done
