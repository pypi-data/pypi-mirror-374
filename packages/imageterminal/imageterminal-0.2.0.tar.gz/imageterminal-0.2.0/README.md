# Image Terminal

A powerful terminal-based image manipulation program built with Python and Textual. Image Terminal provides an intuitive interface for advanced image processing tasks including format conversion, background removal, and AI-powered upscaling.

![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## Features

### 🔄 Format Conversion
Convert between multiple image formats with ease:
- **Supported formats**: PNG, JPG, JPEG, BMP, WEBP, AVIF
- **Smart format detection**: Automatically detects current format
- **Quality preservation**: Maintains image quality during conversion

### 🎨 Background Removal
Remove backgrounds from images using advanced AI:
- **AI-powered**: Uses the `rembg` library for precise background removal
- **Transparent backgrounds**: Creates PNG files with transparent backgrounds
- **Format compatibility**: Handles JPEG/JPG with white background fallback
- **High quality**: Preserves subject details and edges

### 🚀 AI Image Upscaling
Enhance image resolution with deep learning:
- **Multiple scale factors**: 2x, 3x, and 4x upscaling options
- **EDSR models**: Uses Enhanced Deep Super-Resolution models
- **Quality enhancement**: Improves both resolution and image quality
- **Format support**: Works with all major image formats

# imageterminal

## Installation

**Requirements**  
- Python 3.8+

### From PyPI

```
pip install imageterminal
```

### From Source

```
git clone https://github.com/yourusername/imageterminal.git
cd imageterminal
pip install -e .
```

## Usage

Run the app from your terminal:
```
imageterminal
```

### Basic Steps

1. **Start the app:**  
   Run `imageterminal` in your terminal.

2. **Upload your image:**  
   Click "Upload Image!" and select a file.

3. **Pick a tool:**  
   - Change Filetype
   - Remove Background
   - Scale Image

4. **Save your result:**  
   Choose where to save the processed image.

### Supported Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- WEBP (.webp)
- AVIF (.avif)

**That's it! You're ready to use imageterminal.**

## Technical Details

### Dependencies
- **Textual**: Modern terminal UI framework
- **Pillow**: Python Imaging Library
- **OpenCV**: Computer vision and image processing
- **rembg**: AI background removal
- **NumPy**: Numerical computing
- **PyTorch**: Deep learning framework (via rembg)

### Performance Notes
- **Background removal**: Typically takes 5-15 seconds depending on image size
- **AI upscaling**: Can take 1-5 minutes depending on scale factor and image size
- **Format conversion**: Near-instantaneous for most operations

### System Requirements
- **RAM**: Minimum 4GB (8GB+ recommended for large images)
- **Storage**: ~500MB for dependencies and models
- **CPU**: Multi-core processor recommended for faster processing

## File Structure
```
imageterminal/
├── main.py              # Main application file
├── style.tcss           # Textual CSS styling
├── EDSR_x2.pb          # 2x upscaling model
├── EDSR_x3.pb          # 3x upscaling model
├── EDSR_x4.pb          # 4x upscaling model
├── pyproject.toml      # Project configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/Iantaw/imageterminal/blob/main/LICENSE) file for details.

## Acknowledgments

- **Textual** - For the excellent terminal UI framework
- **OpenCV** - For computer vision capabilities
- **rembg** - For AI background removal
- **EDSR** - For super-resolution models
- **Pillow** - For image processing utilities

## Author

Ian Tawileh

---

*Image Terminal - Transform your images with the power of AI, all from your terminal.*