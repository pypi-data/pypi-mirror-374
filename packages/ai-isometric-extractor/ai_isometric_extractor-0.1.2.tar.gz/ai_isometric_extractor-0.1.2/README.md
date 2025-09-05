# AI-Based Isometric Diagram Extraction

AI-Based Isometric Diagram Extraction is a Python package for extracting
meaningful structures from isometric diagrams using deep learning
models. It leverages pre-trained models such as YOLO and anomaly
detection autoencoders to detect, clean, and analyze diagrammatic
representations.

## Features

-   **Object Detection**: Uses YOLO-based model (`best.pt`) to identify
    components in isometric diagrams.\
-   **Anomaly Detection**: Uses autoencoder-based anomaly detection
    (`anomaly.keras`, `my_model.keras`).\
-   **Diagram Cleaning**: Removes noise and enhances extracted
    diagrams.\
-   **Easy Inference**: Run inference on any diagram image with a single
    function call.\
-   **Extensible**: Future support for fine-tuning models on custom
    datasets.

## Installation

You can install the package directly from source:

``` bash
git clone https://github.com/nbeeeel/AI_Based_Isometric_Diagram_Extraction.git
cd AI_Based_Isometric_Diagram_Extraction
pip install .
```

Or after publishing to PyPI:

``` bash
pip install ai-isometric-extractor
```

## Usage

### Python API

``` python
import ai_isometric_extractor as ai

# Run inference on an image
ai.run_inference("Test Pictures/334D92461.jpg")
```

### CLI (coming soon)

``` bash
ai-extractor input.jpg --output results/
```

## Project Structure

    AI_Based_Isometric_Diagram_Extraction/
    │── ai_isometric_extractor/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── models/
    │   │   ├── best.pt
    │   │   ├── anomaly.keras
    │   │   ├── my_model.keras
    │── README.md
    │── pyproject.toml
    │── requirements.txt
    │── LICENSE

## Roadmap

-   [x] Initial package setup\
-   [x] Support for YOLO + Autoencoder models\
-   [ ] CLI support\
-   [ ] Fine-tuning on custom datasets\
-   [ ] Extended visualization tools

## License

This project is licensed under the MIT License - see the
[LICENSE](LICENSE) file for details.

## Author

**Nabeel Ahmed**\
[GitHub Profile](https://github.com/nbeeeel)
