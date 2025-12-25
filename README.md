# 🚂 Railnet_Optimizer - Railway Delay Prediction & Optimization System

**Real-time cascade delay prevention with 4-phase progressive handling and 15% delay reduction**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Simulation](https://img.shields.io/badge/Simulation-Real--time-green)](https://github.com/SumanPete01/Railnet_Optimizer)
[![Delay Reduction](https://img.shields.io/badge/Delay_Reduction-15%25-yellow)](https://github.com/SumanPete01/Railnet_Optimizer)
[![Latency](https://img.shields.io/badge/Rescheduling-<500ms-orange)](https://github.com/SumanPete01/Railnet_Optimizer)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

## ✨ Key Features
- **4-Phase Progressive Delay Handling**: Monitor → Progressive Slowdown → Speed Matching → Emergency Stop
- **15% Cascade Delay Reduction**: Compared to traditional fixed scheduling
- **<500ms Rescheduling Latency**: Real-time dynamic scheduling
- **Universal Logic**: Works for ALL speed relationships (fast→slow, slow→fast, equal speed)
- **Chain Reaction Prevention**: Prevents secondary and tertiary delays
- **Interactive PyGame Visualization**: Real-time train movements with phase indicators
- **Scalable Simulation**: Handles 20+ concurrent trains with O(log n) spatial indexing


## 📊 4-Phase Delay Handling System

### **Phase 1: MONITOR (50-35km)**
- **Action**: Maintain original speed
- **Visual**: Green indicator
- **Logic**: Far from delayed train, monitor only

### **Phase 2: PROGRESSIVE (35-20km)**
- **Action**: Gradual speed reduction
- **Visual**: Orange indicator
- **Logic**: Linear interpolation between original and delayed train speed

### **Phase 3: SPEED MATCH (20-10km)**
- **Action**: Match delayed train speed exactly
- **Visual**: Blue indicator
- **Logic**: Prevent closing gap, maintain safe distance

### **Phase 4: EMERGENCY STOP (≤10km)**
- **Action**: Complete halt (0 km/h)
- **Visual**: Red flashing indicator
- **Logic**: Collision prevention, delay inheritance

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- 5 minutes

### Installation
```bash
# Clone repository
git clone https://github.com/SumanPete01/Railnet_Optimizer.git
cd Railnet_Optimizer

# Install dependencies
pip install -r requirements.txt

# Run simulation
python final.py
