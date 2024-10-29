#!/bin/bash
export pinCapScale_RVT=$1
export pinCapScale_LVT=$2
export pinCapScale_SLVT=$3
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_AO_LVT_TT_nldm_201020.lib  $pinCapScale_LVT  > asap7sc7p5t_AO_LVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_AO_RVT_TT_nldm_201020.lib  $pinCapScale_RVT  > asap7sc7p5t_AO_RVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_AO_SLVT_TT_nldm_201020.lib $pinCapScale_SLVT > asap7sc7p5t_AO_SLVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_INVBUF_LVT_TT_nldm_201020.lib  $pinCapScale_LVT  > asap7sc7p5t_INVBUF_LVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_INVBUF_RVT_TT_nldm_201020.lib  $pinCapScale_RVT  > asap7sc7p5t_INVBUF_RVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_INVBUF_SLVT_TT_nldm_201020.lib $pinCapScale_SLVT > asap7sc7p5t_INVBUF_SLVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_OA_LVT_TT_nldm_201020.lib  $pinCapScale_LVT   > asap7sc7p5t_OA_LVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_OA_RVT_TT_nldm_201020.lib  $pinCapScale_RVT   > asap7sc7p5t_OA_RVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_OA_SLVT_TT_nldm_201020.lib $pinCapScale_SLVT  > asap7sc7p5t_OA_SLVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SEQ_LVT_TT_nldm_201020.lib  $pinCapScale_LVT  > asap7sc7p5t_SEQ_LVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SEQ_RVT_TT_nldm_201020.lib  $pinCapScale_RVT  > asap7sc7p5t_SEQ_RVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SEQ_SLVT_TT_nldm_201020.lib $pinCapScale_SLVT > asap7sc7p5t_SEQ_SLVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SIMPLE_LVT_TT_nldm_201020.lib  $pinCapScale_LVT  > asap7sc7p5t_SIMPLE_LVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SIMPLE_RVT_TT_nldm_201020.lib  $pinCapScale_RVT  > asap7sc7p5t_SIMPLE_RVT_TT_nldm_201020.lib
python liberty_val_scale_pincap.py ./const_scaled/asap7sc7p5t_SIMPLE_SLVT_TT_nldm_201020.lib $pinCapScale_SLVT > asap7sc7p5t_SIMPLE_SLVT_TT_nldm_201020.lib
