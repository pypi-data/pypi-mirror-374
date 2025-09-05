<div style="display: flex; align-items: center; gap: 20px;">
  <img src="docs/source/_static/logo.png" alt="HoloContour Logo" width="100"/>
</div>




## HoloContour

Holocontour is a small but capable toolkit that turns raw in‑line digital holograms into clean binary masks of planktonic particles. It couples intensity‑driven region growing with a contour‑refinement step, and wraps everything in a reproducible, YAML‑configurable pipeline built on top of [MorphoCut](https://github.com/morphocut/morphocut). Outputs ship in an archive ready for direct upload to [EcoTaxa](https://ecotaxa.obs-vlfr.fr/).

---

## 🚀 Features

- Contour-based object detection with:
  - Intensity filtering
  - Histogram matching (optional)
  - Region growing from intensity minima
- Optional plot saving of initial vs. refined masks
- Compatible with `EcoTaxaWriter`
- YAML-based configuration
- Safe fallback for empty masks

---

## 🖼 Example

The figure below shows an example of the pipeline's segmentation output:
  
<p align="left">
  <img src="docs/source/_static/sample.jpg" alt="Segmentation Result" width="400"/>
</p>


- **Red dashed**: Initial region estimate
- **Blue solid**: Refined segmentation contour

---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

