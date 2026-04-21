#!/usr/bin/env bash
# Submit a VQA inference job to the SenseCore ACP platform.
set -euo pipefail

model_path=${MODEL_PATH:-/mnt/afs/wupenghao/workspace/Neo_plus_train/RUN/d20260415_Neo_unify_9B_mot_SFT_fromMT84K_ce01_res2k_lr2e-5_wd0_acc1_img128_seq27648_zs-1_wp16_sp1_gpu512/hf_step9000_ema_rl_ocr_penalty_joint_3200}
repo_root=${REPO_ROOT:-/mnt/afs/denghanming/Major/projects/neo/SenseNova-U1}
python_bin=${PYTHON_BIN:-/mnt/afs/denghanming/miniconda3/envs/sensenova_u1_test/bin/python}

echo "Submitting VQA inference job with model: ${model_path}"

source ~/.bashrc
sco acp jobs create \
    --workspace-name=a58d023b-de76-475f-89c2-7e50f7aa3c7a \
    --aec2-name=m-train-2 \
    --job-name=u1_vqa_example \
    --priority=HIGH \
    --container-image-url='registry.ms-sc-01.maoshanwangtech.com/ccr_2/cogvideox:20241128-19h44m09s' \
    --storage-mount='ce3b1174-f6eb-11ee-a372-82d352e10aed:/mnt/afs' \
    --training-framework=pytorch \
    --worker-nodes=1 \
    --worker-spec="N6lS.Iu.I80.1" \
    --command="${python_bin} ${repo_root}/examples/vqa/inference.py \
        --model_path ${model_path} \
        --image ${repo_root}/examples/vqa/data/images/test_random.jpg \
        --question 'Please describe this image in detail.' \
        --profile"

# Batch mode example:
# --command="${python_bin} ${repo_root}/examples/vqa/inference.py \
#     --model_path ${model_path} \
#     --jsonl ${repo_root}/examples/vqa/data/questions.jsonl \
#     --output_dir /mnt/afs/denghanming/Major/projects/neo/SenseNova-U1/examples/vqa/outputs/"
