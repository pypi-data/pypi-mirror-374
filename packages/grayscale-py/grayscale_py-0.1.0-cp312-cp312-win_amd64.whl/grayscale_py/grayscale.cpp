#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

// Enable stb_image and stb_image_write implementation in this file
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_write.h"

#include <vector>
#include <string>
#include <stdexcept>

namespace py = pybind11;

// Convert image to grayscale and return NumPy array
py::array_t<unsigned char> rgb_to_grayscale(const std::string &filename)
{
    int width, height, channels;
    unsigned char *img = stbi_load(filename.c_str(), &width, &height, &channels, 3);
    if (!img)
        throw std::runtime_error("Failed to load image: " + filename);

    std::vector<unsigned char> gray(width * height);

    for (int i = 0; i < width * height; i++)
    {
        unsigned char R = img[i * 3 + 0];
        unsigned char G = img[i * 3 + 1];
        unsigned char B = img[i * 3 + 2];
        gray[i] = static_cast<unsigned char>(0.299 * R + 0.587 * G + 0.114 * B);
    }

    stbi_image_free(img);

    // Return as NumPy array (H, W)
    return py::array_t<unsigned char>({height, width}, gray.data());
}

// Save grayscale NumPy array to file
void save_grayscale(const py::array_t<unsigned char> &gray, const std::string &filename)
{
    auto buf = gray.request();
    if (buf.ndim != 2)
        throw std::runtime_error("Input array must be 2D (H x W)");

    int height = buf.shape[0];
    int width = buf.shape[1];
    unsigned char *data = static_cast<unsigned char *>(buf.ptr);

    if (!stbi_write_png(filename.c_str(), width, height, 1, data, width))
        throw std::runtime_error("Failed to write image: " + filename);
}

// Python bindings
PYBIND11_MODULE(grayscale, m)
{
    m.doc() = "RGB → Grayscale converter (C++ backend with stb)";
    m.def("rgb_to_grayscale", &rgb_to_grayscale, "Convert image to grayscale (returns NumPy array)");
    m.def("save_grayscale", &save_grayscale, "Save grayscale NumPy array to PNG file");
}
