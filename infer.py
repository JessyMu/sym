import numpy as np
import torch
import torch.nn as nn
import yaml
from munch import Munch
from torch.nn.parallel import DistributedDataParallel
import torch.distributed as dist
import argparse
import multiprocessing as mp
import os
import os.path as osp
import time
from functools import partial
from svgnet.data import build_dataloader, build_dataset
from svgnet.evaluation import PointWiseEval, InstanceEval
from svgnet.model.svgnet import SVGNet as svgnet
from svgnet.util import get_root_logger, init_dist, load_checkpoint
from visualize import seg1_line,seg2_all,cvt_all_color,cvt_line_color,count_stroke,save,onlySeeById

def get_args():
    parser = argparse.ArgumentParser("svgnet")
    parser.add_argument("--config", type=str, help="path to config file",default='data/svg_pointT.yaml')
    parser.add_argument("--checkpoint", type=str, help="path to checkpoint",default='data/best.pth')
    parser.add_argument("--out", type=str, help="directory for output results",default='/home/jesse/Project/SymPoint/data/out/split')
    
    parser.add_argument("--sync_bn", action="store_true", help="run with sync_bn")
    parser.add_argument(
        "--dist", action="store_true", help="run with distributed parallel"
    )
    parser.add_argument("--seed", type=int, default=200)
    parser.add_argument("--save_lite", action="store_true")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    cfg_txt = open(args.config, "r").read()
    cfg = Munch.fromDict(yaml.safe_load(cfg_txt))

    door = [0,1,2,3,4,5]
    window = [6,7,8]
    wall = [32,33]
    stair= [27,28,29]
    if args.dist:
        init_dist()
    logger = get_root_logger()
    out_dir = args.out
    model = svgnet(cfg.model).cuda()
    if args.sync_bn:
        nn.SyncBatchNorm.convert_sync_batchnorm(model)
    # logger.info(model)

    if args.dist:
        model = DistributedDataParallel(model, device_ids=[torch.cuda.current_device()])
    gpu_num = dist.get_world_size() if args.dist else 1

    logger.info(f"Load state dict from {args.checkpoint}")
    load_checkpoint(args.checkpoint, logger, model)

    val_set = build_dataset(cfg.data.test, logger)
    dataloader = build_dataloader(
        args, val_set, training=False, dist=args.dist, **cfg.dataloader.test
    )

    time_arr = []
    sem_point_eval = PointWiseEval(
        num_classes=cfg.model.semantic_classes,
        ignore_label=35,
        gpu_num=gpu_num,
    )
    instance_eval = InstanceEval(
        num_classes=cfg.model.semantic_classes,
        ignore_label=35,
        gpu_num=gpu_num,
    )

    with torch.no_grad():
        model.eval()
        for i, batch in enumerate(dataloader):
            t1 = time.time()
            path = dataloader.dataset.data_list[i]
            path = path.replace('.json','.svg').replace('/jsons/','/test/svg_gt/')
            if i % 10 == 0:
                step = int(len(val_set) / gpu_num)
                logger.info(f"Infer  {i+1}/{step}")
            torch.cuda.empty_cache()
            with torch.cuda.amp.autocast(enabled=cfg.fp16):
                res = model(batch, return_loss=False)

            t2 = time.time()
            time_arr.append(t2 - t1)
            sem_preds = torch.argmax(res["semantic_scores"], dim=1).cpu().numpy()
            sem_gts = res["semantic_labels"].cpu().numpy()
            
            ###
            semantic_preds=sem_preds.tolist()
            semantic_gts=sem_gts.tolist()
            # #Test1 Visual
            # semanticIds = seg1_line(semantic_preds,semantic_gts)
            # cvt_line_color(path,semanticIds,os.path.join(out_dir,'test1'))
            # Pred Visual
            stroke_num = count_stroke(path)
            semanticIds=seg2_all(semantic_preds,stroke_num)
            save(semanticIds,path,os.path.join(out_dir,'test',path.split('/')[-1]))
            # cvt_all_color(path,semanticIds,os.path.join(out_dir,'test'))

            # onlydoor = onlySeeById(door,semanticIds)
            # save(onlydoor,path,os.path.join(out_dir,'test',path.split('/')[-1].replace('.svg','_door.svg')))

            # onlywindow = onlySeeById(window,semanticIds)
            # save(onlywindow,path,os.path.join(out_dir,'test',path.split('/')[-1].replace('.svg','_window.svg')))

            # onlystair = onlySeeById(stair,semanticIds)
            # save(onlystair,path,os.path.join(out_dir,'test',path.split('/')[-1].replace('.svg','_stair.svg')))

            # onlywall = onlySeeById(wall,semanticIds)
            # save(onlywall,path,os.path.join(out_dir,'test',path.split('/')[-1].replace('.svg','_wall.svg')))
            # cvt_all_color(path,semanticIds,os.path.join(out_dir,'gt'))
            
            ##
            #GT Visual   
            stroke_num = count_stroke(path)
            semanticIds=seg2_all(semantic_gts,stroke_num)
            save(semanticIds,path,os.path.join(out_dir,'gt',path.split('/')[-1]))

            sem_point_eval.update(sem_preds, sem_gts)
            instance_eval.update(
                res["instances"],
                res["targets"],
                res["lengths"],
            )

    logger.info("Evaluate semantic segmentation")
    sem_point_eval.get_eval(logger)
    logger.info("Evaluate panoptic segmentation")
    #! instance_eval.get_eval(logger)
    #* 计算f1 precision recall
    instance_eval.get_eval_f1score(logger)

    mean_time = np.array(time_arr).mean()
    logger.info(f"Average run time: {mean_time:.4f}")

    


if __name__ == "__main__":
    main()
