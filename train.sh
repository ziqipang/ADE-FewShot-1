srun -p long --gres=gpu:4 --pty python train.py --comment jigsaw --ckpt ckpt/jigsaw/ --start_epoch 1 --num_epoch 5 --model_weight ../models/baseline.pth