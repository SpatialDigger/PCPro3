# PCPro

## Overview
PCPro is a high-performance point cloud processing tool designed for efficient 3D data manipulation and analysis. Built using Python 3.12+ and Open3D, it enables users to process, visualize, and analyze large-scale point clouds with ease.

## Features
- **Point Cloud Processing**: Load, filter, and manipulate point cloud data.
- **Visualization**: Render 3D point clouds with interactive controls.
- **Segmentation & Clustering**: Extract meaningful structures from raw data.
- **Transformation Tools**: Apply scaling, rotation, and translation.
- **File Format Support**: Work with PLY, LAS, and other common formats.

## Installation

### Prerequisites
- Python 3.12+
- Open3D and other dependencies (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

### Clone the Repository
```bash
git clone https://github.com/SpatialDigger/PCPro3.git
cd pcpro
```

## Usage
Run the main script to start processing point clouds:
```bash
python pcpro.py --input data.ply
```

### Running the Executable
Pre-built executable files are available in the `build` folder. Simply double-click `pcpro.exe` to launch the graphical user interface.

## Feature Requests
Have an idea for a new feature? We’d love to hear from you! Please submit your feature requests by opening a **GitHub Issue** [here](https://github.com/SpatialDigger/PCPro3/issues).

## Contributing
Contributions are welcome! Follow these steps:
1. Fork the repository.
2. Create a new branch (`feature-branch`)
3. Commit your changes.
4. Push to your fork and create a pull request.

## Acknowledgments
This project was developed in collaboration with the **Kaymakçı Archaeological Project** at **Koç University** and **ANAMED (Research Center for Anatolian Civilizations)**. Special thanks to the research team for their support and contributions.

## Publications
* Nobles, Gary R., and Roosevelt, Christopher H. "Filling the Void in Archaeological Excavations: 2D Point Clouds to 3D Volumes." Open Archaeology, vol. 7, no. 1, 2021, pp. 589-614. https://doi.org/10.1515/opar-2020-0149
* Scott, Catherine B., Roosevelt, Christopher H., Nobles, Gary R., and Luke, Christina. "Born-Digital Logistics: Impacts of 3D Recording on Archaeological Workflow, Training, and Interpretation." Open Archaeology, vol. 7, no. 1, 2021, pp. 574-588. https://doi.org/10.1515/opar-2020-0150

## License
This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the [LICENSE](LICENSE) file for details.

## Contact
For questions or suggestions, reach out at garynobles20@gmail.com or open an issue on GitHub.
