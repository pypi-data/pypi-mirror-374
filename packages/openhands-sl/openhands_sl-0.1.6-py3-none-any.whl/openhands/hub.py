import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../examples/configs")
MODELS = {
    # WLASL
    "wlasl_stgcn": {
        "config": "wlasl/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/wlasl_stgcn.zip"
    },
    "wlasl_decoupled_gcn": {
        "config": "wlasl/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/wlasl_slgcn.zip"
    },
    "wlasl_pose_lstm": {
        "config": "wlasl/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/wlasl_lstm.zip"
    },
    "wlasl_pose_finetune_dpc": {
        "config": "wlasl/pose_finetune_dpc.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/wlasl_dpc.zip"
    },

    # AUTSL
    "autsl_stgcn": {
        "config": "autsl/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/autsl_stgcn.zip"
    },
    "autsl_decoupled_gcn": {
        "config": "autsl/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/autsl_slgcn.zip"
    },
    "autsl_gcn_bert": {
        "config": "autsl/gcn_bert.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/autsl_bert.zip"
    },

    # CSL
    "csl_stgcn": {
        "config": "csl/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/csl_stgcn.zip"
    },
    "csl_decoupled_gcn": {
        "config": "csl/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/csl_slgcn.zip"
    },
    "csl_pose_lstm": {
        "config": "csl/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/csl_lstm.zip"
    },

    # DEVISIGN
    "devisign_stgcn": {
        "config": "devisign/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/devisign_stgcn.zip"
    },
    "devisign_decoupled_gcn": {
        "config": "devisign/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/devisign_slgcn.zip"
    },
    "devisign_pose_lstm": {
        "config": "devisign/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/devisign_lstm.zip"
    },
    "devisign_pose_finetune_dpc": {
        "config": "devisign/pose_finetune_dpc.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/devisign_dpc.zip"
    },

    # GSL
    "gsl_stgcn": {
        "config": "gsl/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/gsl_stgcn.zip"
    },
    "gsl_decoupled_gcn": {
        "config": "gsl/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/gsl_slgcn.zip"
    },
    "gsl_pose_lstm": {
        "config": "gsl/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/gsl_lstm.zip"
    },

    # INCLUDE
    "include_stgcn": {
        "config": "include/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/include_stgcn.zip"
    },
    "include_decoupled_gcn": {
        "config": "include/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/include_slgcn.zip"
    },
    "include_pose_lstm": {
        "config": "include/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/include_lstm.zip"
    },
    "include_pose_finetune_dpc": {
        "config": "include/pose_finetune_dpc.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/include_dpc.zip"
    },
    "include_gcn_bert": {
        "config": "include/gcn_bert.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/include_bert.zip"
    },

    # LSA64
    "lsa64_stgcn": {
        "config": "lsa64/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/lsa64_stgcn.zip"
    },
    "lsa64_decoupled_gcn": {
        "config": "lsa64/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/lsa64_slgcn.zip"
    },
    "lsa64_pose_lstm": {
        "config": "lsa64/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/lsa64_lstm.zip"
    },

    # MSASL
    "msasl_stgcn": {
        "config": "msasl/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/msasl_stgcn.zip"
    },
    "msasl_decoupled_gcn": {
        "config": "msasl/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/msasl_slgcn.zip"
    },
    "msasl_pose_finetune_dpc": {
        "config": "msasl/pose_finetune_dpc.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/msasl_dpc.zip"
    },

    # PHOENIX
    "phoenix_stgcn": {
        "config": "rwth-phoenix-weather-signer03-cutout/st_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/phoenix_stgcn.zip"
    },
    "phoenix_decoupled_gcn": {
        "config": "rwth-phoenix-weather-signer03-cutout/decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/phoenix_slgcn.zip"
    },
    "phoenix_pose_lstm": {
        "config": "rwth-phoenix-weather-signer03-cutout/pose_lstm.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/phoenix_lstm.zip"
    },
    "phoenix_pose_finetune_dpc": {
        "config": "rwth-phoenix-weather-signer03-cutout/pose_finetune_dpc.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/phoenix_dpc.zip"
    },

    # Pre-trained models for SSL
    "dpc_decoupled_gcn_raw": {
        "config": "ssl/pretrain_dpc_decoupled_gcn.yaml",
        "url": "https://github.com/AI4Bharat/OpenHands/releases/download/checkpoints_v1/raw_dpc.zip"
    },
}

def list_datasets():
    dataset_dirs = os.listdir(os.path.join(os.path.dirname(__file__), "datasets/assets"))
    return [d.replace("_metadata", "") for d in dataset_dirs if d.endswith("_metadata")]

def list_models():
    return list(MODELS.keys())
