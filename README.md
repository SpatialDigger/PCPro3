# PCPro

# ☕️ Help Support This Project

I maintain and develop this project alongside my full-time job.  
It takes a lot of evenings, weekends, and dedication to keep it growing and improving.  

If you find this project valuable, please consider [**supporting my work**](https://buymeacoffee.com/pointcloud3).  
Your support helps cover development costs and allows me to dedicate more time to making this project even better — thank you for helping keep it alive!

<br>

[![Support Me on Buy Me a Coffee](https://img.shields.io/badge/Support%20Me-Buy%20Me%20a%20Coffee-FF813F?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white)](https://buymeacoffee.com/pointcloud3)




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
- Run the installer, then double click the PCPro3.exe file.
- This will open in demo mode, you will have all the functionality except export.
- To get the full version 

## Minimum System Requirements

- Operating System
  - **Windows 7** or later (Windows 11 reconmended)
- Processor
  - **2 GHz** or faster multi-core processor.
- Memory (RAM)
  - **2 GB RAM** minimum
    - **4 GB RAM** recommended for smoother performance.

- Disk Space
  - At least **1 GB** of free disk space for installation and operation.

## Feature Requests
Have an idea for a new feature? We’d love to hear from you! Please submit your feature requests by opening a **GitHub Issue** [here](https://github.com/SpatialDigger/PCPro3/issues).

## Acknowledgments
This project was developed in collaboration with the **Kaymakçı Archaeological Project** at **Koç University** and **ANAMED (Research Center for Anatolian Civilizations)**. Special thanks to the research team for their support and contributions.

## Publications
* Nobles, Gary R., and Roosevelt, Christopher H. "Filling the Void in Archaeological Excavations: 2D Point Clouds to 3D Volumes." Open Archaeology, vol. 7, no. 1, 2021, pp. 589-614. https://doi.org/10.1515/opar-2020-0149
* Scott, Catherine B., Roosevelt, Christopher H., Nobles, Gary R., and Luke, Christina. "Born-Digital Logistics: Impacts of 3D Recording on Archaeological Workflow, Training, and Interpretation." Open Archaeology, vol. 7, no. 1, 2021, pp. 574-588. https://doi.org/10.1515/opar-2020-0150

## License
This project is licensed under a bespoke license, there are commercial and educational licences.

## Contact
For questions or suggestions, reach out at garynobles20@gmail.com or open an issue on GitHub.

Website in development: [PCPro3](https://spatialdigger.github.io/pcpro.github.io/)

---
# Changelog

---
## Version 1.2.0 [Minor Version]
**Release Date:** [In Developmet]

### New Features:
- #21 #51 Metadata recording, metadata viewer, metadata export 
- #21 Automatic metadata updating in the viewer
- #54 Support added to read .laz files
- 

### Bug Fixes:
- #56 Fixed relative positioning when importing landscape scale pointclouds
- #1 Fixed: Convexhull3D filter assigning filtered pointcloud to the wrong pointcloud

### Performance Improvements:
- [Performance improvement 1 description]
- [Performance improvement 2 description]

### Compatibility Updates:
- [Compatibility update description]

### Known Issues:
- [Known issue description]
- [Known issue description]

### Upgrade Notes:
- [Upgrade instruction or notes for users]
- Backwards compatibility with version 1.1.0 licences

### Coming Soon:
- [Feature or update planned for next version]

### Deprecation Notices:
- [Deprecated feature or upcoming removal notice]

### Special Thanks:
- 

---
## Version 1.1.0 [Minor Version]
**Release Date:** 2025-04-27 [current]

### New Features:
- #49 Viewports
  - #46 Set views implemented
  - #48 Viewpoint preserved when adding in new datasets, analysis, and bounding boxes
- #9 licencing updated

---

## Version 1.0.0 [Major Release]
**Release Date:** 2015-03-23 

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
- #37 Implement licencing

### Bug Fixes:
- #19 Normal calculation steps no longer added to the menu

### Special Thanks:
- Catherine Scott for raising enhancement requests
- Christopher Roosevelt for raising enhancement requests

---

## Version 0.1.2 
**Release Date:** 2025-03-02

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
