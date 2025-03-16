# PCPro

## Overview
PCPro is a high-performance point cloud processing tool designed for efficient 3D data manipulation and analysis. Built using Python 3.12+ and Open3D, it enables users to process, visualize, and analyze large-scale point clouds with ease.

## Features
- **Point Cloud Processing**: Load, filter, and manipulate point cloud data.
- **Visualization**: Render 3D point clouds with interactive controls.
- **Segmentation & Clustering**: Extract meaningful structures from raw data.
- **Transformation Tools**: Apply scaling, rotation, and translation.
- **File Format Support**: Work with PLY, LAS, and other common formats.

## Promo
[PCPro3_intro.mp4](videos/PCPro3_intro.mp4)

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

---
# Changelog

---


## Version [1.0.0] Major Release
**Release Date:** [Under Development]

### New Features:
- #41 Users can now submit issues, questions, requests under the About dropdown, these are logged directly in the GitHub Repo for assessment.
- #30 Updated the default theme to the Orange-Black theme, now called Obsidian Flame
- #29 Added a preferences dialogue
- #30 Added several themes
- #29 Added the option to change the 3D Viewer background colour in the preferences
- #36 Added the splash screen
- #35 Improved user experience 
  - CTRL + A 
  - Click in blank space deselects all 
  - ESC deselects all 
  - SHIFT + Click selects a range (only works on parent items)
  - CTRL + Click to drag item to reorder in the contents pane
- #13 XYZ Axis added
- #31 Bounding Box added
- #28 Added example 3 to the documentation
- #23 Added example 2 to the documentation
- #25 Reordering of menu items implemented

### Bug Fixes:
- #19 Normal calculation steps no longer added to the menu
- [Bug fix 2 description]

### Performance Improvements:
- Cleaned up the log messages
- [Performance improvement 2 description]

### Compatibility Updates:
- [Compatibility update description]

### Known Issues:
- [Known issue description]
- [Known issue description]

### Upgrade Notes:
- [Upgrade instruction or notes for users]

### Coming Soon:
- [Feature or update planned for next version]

### Deprecation Notices:
- [Deprecated feature or upcoming removal notice]

### Special Thanks:
- [Contributor name] for [contribution description]

---

## Version 0.1.2 
**Release Date:** 2025-03-02 [Current]

### New Features:
- Added option to customize point cloud colors and revert to the default colors
- Included a link to GitHub documentation under the Help menu
- Added Example 1 to the documentation
- Introduced "About" and "Keyboard Shortcuts" options in the menu
- Added the ability to change the pointcloud colours
- Added the ability to revert colours back to their original state
- Mesh properties
- Mesh Volume calculation in its properties
- Added the Pointcloud Substitution function

### Bug Fixes:
- Resolved issue where point cloud colours weren't saving on export
- Mesh can now display properties

### Known Issues:
- #1 Convexhull3D filter assigning filtered pointcloud to the wrong pointcloud
- #20 Crashes when getting properties for a mesh
- #24 Mesh cannot change colour 
- Mesh properties takes a while to load

### Special Thanks:
- Catherine Scott for raising enhancement requests
- Christopher Roosevelt for raising enhancement requests

---


## Version 0.1.1
Release Date: 2025-02-25
### New Features:
- Added ability to compute normals
- Added option to invert normals
- Added functionality to export mesh as PLY
- added the ability to perform surface reconstruction

### Compatibility Updates:
- Updated mesh export to support latest version of PLY format

---

## Version 0.1.0
Release Date: 2025-02-19
### New Features:
- PCPro launched
- Initial release with core features
