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

#include <sys/types.h>
#include <iostream>

#include "FlexGR.h"
#include "stt/SteinerTreeBuilder.h"


using namespace std;
using namespace fr;

float FlexGR::evalRUDYCongestion(odb::dbDatabase* db)
{
  db_ = db;
  init();
  // resource analysis
  ra();
  // cmap->print(true);

  std::vector<std::vector<float> > rudyDemandH;
  std::vector<std::vector<float> > rudyDemandV;

  // initialize the rudyDemand
  int GCellCountX = cmap2D_->getGCellCountX();
  int GCellCountY = cmap2D_->getGCellCountY();

  // resize the vectors
  rudyDemandH.resize(GCellCountY, std::vector<float>(GCellCountX));
  rudyDemandV.resize(GCellCountY, std::vector<float>(GCellCountX));

  for (int y = 0; y < GCellCountY; y++) {
    for (int x = 0; x < GCellCountX; x++) {
      rudyDemandH[y][x] = 0.0;
      rudyDemandV[y][x] = 0.0;
    }
  }

  //logger_->report("RUDY congestion analysis started.");
  //reportCong2D();

  // update the rudyDemand
  for (auto& net : design_->getTopBlock()->getNets()) {
    updateNetRUDY(net.get(), rudyDemandH, rudyDemandV);
  }  

  // update cmap2D
  for (int y = 0; y < GCellCountY; y++) {
    for (int x = 0; x < GCellCountX; x++) {
      cmap2D_->addRawDemand(x, y, 0, frDirEnum::E, rudyDemandH[y][x]);
      cmap2D_->addRawDemand(x, y, 0, frDirEnum::N, rudyDemandV[y][x]);
    }
  }
  
  reportCong2D();
  logger_->report("RUDY congestion analysis done.");

  cmap2D_->cleanup();    
  return 0; // Add this line to return a value
}


void FlexGR::updateNetRUDY(frNet* net, 
  std::vector<std::vector<float>>& rudyDemandH,
  std::vector<std::vector<float>>& rudyDemandV) {
  if (net->getNodes().empty()) {
    return;
  }

  if (net->getNodes().size() == 1) {
    net->setRoot(net->getNodes().front().get());
    return;
  }

  std::vector<frNode*> nodes(net->getNodes().size(), nullptr);  // 0 is source
  std::map<frBlockObject*, std::vector<frNode*>>
      pin2Nodes;  // vector order needs to align with map below
  std::map<frBlockObject*, std::vector<frRPin*>> pin2RPins;
  
  // Init nodes and populate pin2Nodes
  std::string errStr;
  unsigned sinkIdx = 1; // The first node is always the source (driver)
  auto& netNodes = net->getNodes();
  // init nodes and populate pin2Nodes
  for (auto& node : netNodes) {
    if (node->getPin()) {
      if (node->getPin()->typeId() == frcInstTerm) {
        auto ioType = static_cast<frInstTerm*>(node->getPin())
                          ->getTerm()
                          ->getDirection();
        // for instTerm, direction OUTPUT is driver
        if (ioType == dbIoType::OUTPUT && nodes[0] == nullptr) {
          nodes[0] = node.get();
        } else {
          if (sinkIdx >= nodes.size()) {
            sinkIdx %= nodes.size();
          }
          nodes[sinkIdx] = node.get();
          sinkIdx++;
        }
        pin2Nodes[node->getPin()].push_back(node.get());
      } else if (node->getPin()->typeId() == frcBTerm
                 || node->getPin()->typeId() == frcMTerm) {
        auto ioType = static_cast<frTerm*>(node->getPin())->getDirection();
        // for IO term, direction INPUT is driver
        if (ioType == dbIoType::INPUT && nodes[0] == nullptr) {
          nodes[0] = node.get();
        } else {
          if (sinkIdx >= nodes.size()) {
            sinkIdx %= nodes.size();
          }
          nodes[sinkIdx] = node.get();
          sinkIdx++;
        }
        pin2Nodes[node->getPin()].push_back(node.get());
      } else {
        errStr = "Error: unknown pin type in updateNetRUDY";
        break;
      }
    }
  }

  if (!errStr.empty()) {
    logger_->error(DRT, 1, errStr);
  }
  
  net->setRoot(nodes[0]);

  // populate pin2RPins
  for (auto& rpin : net->getRPins()) {
    if (rpin->getFrTerm()) {
      pin2RPins[rpin->getFrTerm()].push_back(rpin.get());
    }
  }
  
  // update nodes location based on rpin
  for (auto& [pin, nodes] : pin2Nodes) {
    if (pin2RPins.find(pin) == pin2RPins.end()) {
      logger_->error(DRT, 25, "Error: pin not found in pin2RPins");
    }
    if (pin2RPins[pin].size() != nodes.size()) {
      logger_->error(DRT, 40, "Error: mismatch in nodes and ripins size");
    }
    auto& rpins = pin2RPins[pin];
    auto rpinIter = rpins.begin();
    auto nodeIter = nodes.begin();
    while (rpinIter != rpins.end() && nodeIter != nodes.end()) {
      auto rpin = *rpinIter;
      auto node = *nodeIter;
      Point pt;
      if (rpin->getFrTerm()->typeId() == frcInstTerm) {
        auto inst = static_cast<frInstTerm*>(rpin->getFrTerm())->getInst();
        dbTransform shiftXform = inst->getTransform();
        shiftXform.setOrient(dbOrientType(dbOrientType::R0));
        pt = rpin->getAccessPoint()->getPoint();
        shiftXform.apply(pt);
      } else {
        pt = rpin->getAccessPoint()->getPoint();
      }
      node->setLoc(pt);
      node->setLayerNum(rpin->getAccessPoint()->getLayerNum());
      rpinIter++;
      nodeIter++;
    }
  }

  auto& gcellIdx2Nodes = net2GCellIdx2Nodes_[net];
  auto& gcellNode2RPinNodes = net2GCellNode2RPinNodes_[net];

  // prep for 2D topology generation in case two nodes are more than one rpin in
  // same gcell topology genration works on gcell (center-to-center) level
  for (auto node : nodes) {
    Point apLoc = node->getLoc();
    Point apGCellIdx = design_->getTopBlock()->getGCellIdx(apLoc);
    gcellIdx2Nodes[std::make_pair(apGCellIdx.x(), apGCellIdx.y())].push_back(
        node);
  }

  auto& gcellNodes = net2GCellNodes_[net];
  gcellNodes.resize(gcellIdx2Nodes.size(), nullptr);

  std::vector<std::unique_ptr<frNode>> tmpGCellNodes;
  sinkIdx = 1;
  unsigned rootIdx = 0;
  for (auto& [gcellIdx, localNodes] : gcellIdx2Nodes) {
    bool hasRoot = std::any_of(
        localNodes.begin(), localNodes.end(),
        [root = nodes[0]](frNode* node) { return node == root; });
    
    auto gcellNode = std::make_unique<frNode>();
    gcellNode->setType(frNodeTypeEnum::frcSteiner);
    
    Rect gcellBox = design_->getTopBlock()->getGCellBox(
        Point(gcellIdx.first, gcellIdx.second));
    Point loc((gcellBox.xMin() + gcellBox.xMax()) / 2,
              (gcellBox.yMin() + gcellBox.yMax()) / 2);
    gcellNode->setLayerNum(2);
    gcellNode->setLoc(loc);
    if (!hasRoot) {
      gcellNode->setId(net->getNodes().back()->getId() + sinkIdx + 1);
      gcellNodes[sinkIdx] = gcellNode.get();
      sinkIdx++;
    } else {
      gcellNode->setId(net->getNodes().back()->getId() + 1);
      gcellNodes[0] = gcellNode.get();
      rootIdx = tmpGCellNodes.size();
    }
    gcellNode2RPinNodes[gcellNode.get()] = localNodes;
    tmpGCellNodes.push_back(std::move(gcellNode));
  }

  net->setFirstNonRPinNode(gcellNodes[0]);
  std::swap(tmpGCellNodes[rootIdx], tmpGCellNodes[0]);
  for (auto& tmpGCellNode : tmpGCellNodes) {
    net->addNode(tmpGCellNode);
  }

  if (gcellNodes.size() <= 1) {
    return;
  }

  net->setRootGCellNode(gcellNodes[0]);

  // (1) create steiner tree
  auto& steinerNodes = net2SteinerNodes_[net];
  genSTTopology_FLUTE(gcellNodes, steinerNodes);

  // (2) connect rpin node to gcell center node
  //  Please do not change the order of Step (1) and Step (2)
  //  Step (1) will reset the parent-child relationship
  for (auto& [gcellNode, localNodes] : gcellNode2RPinNodes) {
    for (auto localNode : localNodes) {
      if (localNode == nodes[0]) {
        gcellNode->setParent(localNode);
        localNode->addChild(gcellNode);
      } else {
        gcellNode->addChild(localNode);
        localNode->setParent(gcellNode);
      }
    }
  }

  // traverse the tree to calculate the wirelength and rudy
  int minLx = std::numeric_limits<int>::max();
  int minLy = std::numeric_limits<int>::max();
  int maxUx = std::numeric_limits<int>::min();
  int maxUy = std::numeric_limits<int>::min();
  int hRSMT = 0;
  int vRSMT = 0;

  auto rootNode = net->getRootGCellNode();
  std::queue<frNode*> nodeQueue;
  nodeQueue.push(rootNode);

  while (!nodeQueue.empty()) {
    auto currNode = nodeQueue.front();
    nodeQueue.pop();
    Point loc = cmap2D_->getGCellIdx(currNode->getLoc());
    for (auto child : currNode->getChildren()) {
      nodeQueue.push(child);
      Point childLoc = cmap2D_->getGCellIdx(child->getLoc());
      if (loc.x() == childLoc.x()) {
        vRSMT += std::abs(loc.y() - childLoc.y());
      } else {
        hRSMT += std::abs(loc.x() - childLoc.x());
      }
    }

    minLx = std::min(minLx, loc.x());
    minLy = std::min(minLy, loc.y());
    maxUx = std::max(maxUx, loc.x());
    maxUy = std::max(maxUy, loc.y()); 
  }

  minLx = std::max(minLx, 0);
  minLy = std::max(minLy, 0);
  maxUx = std::min(maxUx, cmap2D_->getGCellCountX() - 1);
  maxUy = std::min(maxUy, cmap2D_->getGCellCountY() - 1);

  float hNetRUDY = float(hRSMT) / (maxUx - minLx + 1) / (maxUy - minLy + 1);
  float vNetRUDY = float(vRSMT) / (maxUx - minLx + 1) / (maxUy - minLy + 1);
  for (int y = minLy; y <= maxUy; y++) {
    for (int x = minLx; x <= maxUx; x++) {
      rudyDemandH[y][x] += hNetRUDY;
      rudyDemandV[y][x] += vNetRUDY;
    }
  }
}

