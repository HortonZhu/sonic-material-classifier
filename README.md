# sonic-material-classifier
Material classification device that uses a transducer pair to determine if a material is metal, foam, or paper.
# SONIC: Sound Operating for Nodal Identification of Compositions

SONIC is a material classification device powered by an ESP32 microcontroller and an XGBoost classification model. It uses a pair of 40kHz transducers to fire an acoustic impulse that reflects off a target material, while the second transducer captures the response waveform. Then, acoustic signal features are extracted and evaluated in real time to classify the sampled material.

## Hardware & Circuit Diagram
Circuit diagrams are available in `hardware/docs/`.

### Hardware Requirements
* ESP32 Microcontroller
* 2x Ultrasonic Transducers (Transmitter & Receiver)
* USB connection to host computer (Mac/PC)
* Breadboard, jumper cables, resistors

## Project Layout
* `hardware/docs/`: Circuit diagrams
* `firmware/`: ESP32 C++ code for sampling data
* `scripts/`: Script to convert serial output to .csv data
* `src/`:
  * `live_demo.py`: Connects to ESP32 over serial for real-time sampling and classification using the pre-trained model
  * `extract_train_save.py`: Extract features from raw CSV data, train an XGBoost classifier, and export model weights
* `models/`: Pre-trained XGBoost classification model weights (`material_model.json`)
* `data/`: Recorded acoustic waveform CSV files
