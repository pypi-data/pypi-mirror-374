# aim2numpy

`aim2numpy` is a Python library designed to convert AIM files, specifically CT scan data from Scanco, into numpy arrays.

## Installation

You can install the library using pip:

```bash
pip install aim2numpy
```

## Usage

Here's a basic example of how to use the library:

```python
import aim2numpy

mynumpy = aim2numpy.extract("myaimfile.aim")
header_info = aim2numpy.get_header_info("myaimfile.aim")
```

## AIM File Format

The AIM file format is used by Scanco Medical for storing CT scan data. These files contain volumetric data that can be used for various analyses in medical imaging and research.

## Features

- **Easy Conversion**: Convert AIM files to numpy arrays with a single function call.
- **Header Information**: Extract metadata and header information from AIM files.
- **Compatibility**: Works with CT scan data from Scanco.
- **Extensible**: Easily integrate with other Python libraries for further data processing and analysis.


## Example

```python
import aim2numpy
import matplotlib.pyplot as plt

# Extract the numpy array from the AIM file
ct_scan_data = aim2numpy.extract("myaimfile.aim")

# Display a slice of the CT scan data
plt.imshow(ct_scan_data[:, :, ct_scan_data.shape[2] // 2], cmap='gray')
plt.title('CT Scan Slice')
plt.show()

# Print header information
header_info = aim2numpy.get_header_info("myaimfile.aim")
print(f"Dimensions: {header_info['dimensions']}")
print(f"Element size: {header_info['element_size']} mm")
print(f"Processing log: {header_info['processing_log']}")
```

## Requirements

- numpy
- struct
- matplotlib

## Installation for Development

If you want to install the library for development purposes, you can clone the repository and install it locally:

```bash
git clone https://github.com/Alexhal9000/aim2numpy.git
cd aim2numpy
pip install -e .
```

## Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.