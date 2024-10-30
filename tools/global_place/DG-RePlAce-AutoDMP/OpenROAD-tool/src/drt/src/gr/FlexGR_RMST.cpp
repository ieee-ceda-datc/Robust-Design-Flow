/* Authors: Zhiang Wang */
/*
 * Copyright (c) 2024, The Regents of the University of California
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the University nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <iostream>
#include <limits>

#include "FlexGR.h"
#include "stt/SteinerTreeBuilder.h"



using namespace std;
using namespace fr;

uint64_t FlexGR::evalRMSTWL(odb::dbDatabase* db, int ignore_net_threshold)
{
  uint64_t rsmtWL = 0;
  uint64_t HPWL = 0;
  auto block = db->getChip()->getBlock();
  auto nets = block->getNets();
  for (odb::dbNet* net : nets) {
    odb::dbSigType netType = net->getSigType();
    // escape nets with VDD/VSS/reset nets
    if (netType == odb::dbSigType::SIGNAL || netType == odb::dbSigType::CLOCK) {
      int numNodes = net->getITerms().size() + net->getBTerms().size();
      if (numNodes >= ignore_net_threshold) {
        continue;
      }

      std::vector<int> xs;
      std::vector<int> ys;

      xs.reserve(numNodes);
      ys.reserve(numNodes);
      int driverId = -1;
      int pinId = -1;

      for (odb::dbITerm* iTerm : net->getITerms()) {
        pinId++;
        if (iTerm->getIoType() == odb::dbIoType::OUTPUT) {
          driverId = pinId;
        }

        int offsetLx = std::numeric_limits<int>::max();
        int offsetLy = std::numeric_limits<int>::max();
        int offsetUx = std::numeric_limits<int>::min();
        int offsetUy = std::numeric_limits<int>::min();

        int offsetCx_ = 0;
        int offsetCy_ = 0;

        for (odb::dbMPin* mPin : iTerm->getMTerm()->getMPins()) {
          for (odb::dbBox* box : mPin->getGeometry()) {
            offsetLx = std::min(box->xMin(), offsetLx);
            offsetLy = std::min(box->yMin(), offsetLy);
            offsetUx = std::max(box->xMax(), offsetUx);
            offsetUy = std::max(box->yMax(), offsetUy);
          }
        }

        int lx = iTerm->getInst()->getBBox()->xMin();
        int ly = iTerm->getInst()->getBBox()->yMin();

        int instCenterX = iTerm->getInst()->getMaster()->getWidth() / 2;
        int instCenterY = iTerm->getInst()->getMaster()->getHeight() / 2;

        // Pin SHAPE is NOT FOUND;
        // (may happen on OpenDB bug case)
        if (offsetLx == INT_MAX || offsetLy == INT_MAX || offsetUx == INT_MIN
            || offsetUy == INT_MIN) {
          // offset is center of instances
          offsetCx_ = offsetCy_ = 0;
        } else {
          // offset is Pin BBoxs' center, so
          // subtract the Origin coordinates (e.g. instCenterX, instCenterY)
          //
          // Transform coordinates
          // from (origin: 0,0)
          // to (origin: instCenterX, instCenterY)
          //
          offsetCx_ = (offsetLx + offsetUx) / 2 - instCenterX;
          offsetCy_ = (offsetLy + offsetUy) / 2 - instCenterY;
        }

        int cx = lx + instCenterX + offsetCx_;
        int cy = ly + instCenterY + offsetCy_;

        xs.push_back(cx);
        ys.push_back(cy);
      }

      for (auto bTerm : net->getBTerms()) {
        pinId++;
        if (bTerm->getIoType() == odb::dbIoType::INPUT) {
          driverId = pinId;
        }
        
        int lx = std::numeric_limits<int>::max();
        int ly = std::numeric_limits<int>::max();
        int ux = std::numeric_limits<int>::min();
        int uy = std::numeric_limits<int>::min();

        for (odb::dbBPin* bPin : bTerm->getBPins()) {
          odb::Rect bbox = bPin->getBBox();
          lx = std::min(bbox.xMin(), lx);
          ly = std::min(bbox.yMin(), ly);
          ux = std::max(bbox.xMax(), ux);
          uy = std::max(bbox.yMax(), uy);
        }

        int cx = (lx + ux) / 2;
        int cy = (ly + uy) / 2;

        xs.push_back(cx);
        ys.push_back(cy);
      }
      
      stt_builder_->setAlpha(0);


      int minLx = std::numeric_limits<int>::max();
      int minLy = std::numeric_limits<int>::max();
      int maxUx = std::numeric_limits<int>::min();
      int maxUy = std::numeric_limits<int>::min();


      for (auto x : xs) {
        minLx = std::min(minLx, x);
        maxUx = std::max(maxUx, x);
      }

      for (auto y : ys) {
        minLy = std::min(minLy, y);
        maxUy = std::max(maxUy, y);
      }

      HPWL += maxUx - minLx + maxUy - minLy;
      auto fluteTree = stt_builder_->makeSteinerTree(xs, ys, driverId);
      
      // traverse the tree to calculate the wirelength
      uint64_t rsmtNet = 0;
      // iterate over the tree to calculate the wirelength
      for (int i = 0; i < numNodes * 2 - 2; i++) {
        auto& branch1 = fluteTree.branch[i];
        auto& branch2 = fluteTree.branch[branch1.n];
        rsmtNet += std::abs(branch1.x - branch2.x) + std::abs(branch1.y - branch2.y);
      }   

      rsmtWL += rsmtNet;
    }
  }

  double dbu = getDesign()->getTech()->getDBUPerUU();
  logger_->report("HPWL wirelength: {}", HPWL / dbu);
  logger_->report("RSMT wirelength: {}", rsmtWL / dbu);
  return rsmtWL;
}
