#!/bin/bash
export constScale_RVT=$1
export constScale_LVT=$2
export constScale_SLVT=$3
python liberty_tbl_scale_const.py $constScale_LVT ./intPower_scaled/asap7sc7p5t_AO_LVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_AO_LVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_RVT ./intPower_scaled/asap7sc7p5t_AO_RVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_AO_RVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_SLVT ./intPower_scaled/asap7sc7p5t_AO_SLVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_AO_SLVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_LVT ./intPower_scaled/asap7sc7p5t_INVBUF_LVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_INVBUF_LVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_RVT ./intPower_scaled/asap7sc7p5t_INVBUF_RVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_INVBUF_RVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_SLVT ./intPower_scaled/asap7sc7p5t_INVBUF_SLVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_INVBUF_SLVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_LVT ./intPower_scaled/asap7sc7p5t_OA_LVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_OA_LVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_RVT ./intPower_scaled/asap7sc7p5t_OA_RVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_OA_RVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_SLVT ./intPower_scaled/asap7sc7p5t_OA_SLVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_OA_SLVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_LVT ./intPower_scaled/asap7sc7p5t_SEQ_LVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SEQ_LVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_RVT ./intPower_scaled/asap7sc7p5t_SEQ_RVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SEQ_RVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_SLVT ./intPower_scaled/asap7sc7p5t_SEQ_SLVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SEQ_SLVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_LVT ./intPower_scaled/asap7sc7p5t_SIMPLE_LVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SIMPLE_LVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_RVT ./intPower_scaled/asap7sc7p5t_SIMPLE_RVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SIMPLE_RVT_TT_nldm_201020.lib
python liberty_tbl_scale_const.py $constScale_SLVT ./intPower_scaled/asap7sc7p5t_SIMPLE_SLVT_TT_nldm_201020.lib > ./const_scaled/asap7sc7p5t_SIMPLE_SLVT_TT_nldm_201020.lib
