import numpy as np


# Actually is a cross-correlation (no kernel flip)
# numberOfFilters, out_channels, kernel_size, stride
from utils import *


def convolve_2d(images, kernel, padding=0, stride=1):

    output_channels = kernel.shape[0]
    input_channels = kernel.shape[1]
    kernel_h = kernel.shape[2]
    kernel_w = kernel.shape[3]

    # Compute the expected output size (h,w)
    output_h = int(((images.shape[2] + 2 * padding - kernel.shape[2]) / stride) + 1)
    output_w = int(((images.shape[3] + 2 * padding - kernel.shape[3]) / stride) + 1)

    # Init the convolution matrix with random values
    # convolution_result = np.random.rand(images.shape[0], output_channels, output_h, output_w)
    # a = convolution_result.shape

    # Init the convolution matrix with zero values
    convolution_result = np.zeros((images.shape[0], output_channels, output_h, output_w),
                                  dtype=np.float)
    # Cycle all the images in the batch
    for image_idx in range(images.shape[0]):
        # Extract a single image
        current_image = images[image_idx, :, :, :]
        # Apply padding
        current_image = np.pad(current_image, ((0, 0), (padding, padding), (padding, padding)), mode='constant')

        # Cycle all the filters in the convolutional layer
        for filter_position in range(kernel.shape[0]):
            # Extract the current filter
            filter_selected = kernel[filter_position, :, :, :]

            # height index for the output activation
            output_h_idx = 0

            # Slide the image, starting from its height.
            #  - current_image.shape[0] = channels
            #  - current_image.shape[1] = height
            #  - current_image.shape[2] = width
            for i in range(0, current_image.shape[1], stride):
                # width index for the output activation
                output_w_idx = 0

                # Extract the sub-portion of the image
                # - get all channels
                # - height ==> from i to i + kernel_size
                # - width ==> all the width
                image_rectangle = current_image[:, i:i + kernel_h, :]
                if image_rectangle.shape[1] < kernel_h:
                    continue
                else:
                    for j in range(0, image_rectangle.shape[2], stride):
                        if j >= image_rectangle.shape[2]:
                            continue
                        image_portion = image_rectangle[:, :, j:j + kernel_w]
                        if image_portion.shape[2] < kernel_w:
                            continue
                        else:
                            # Perform the dot product
                            inner_result = np.multiply(filter_selected, image_portion)
                            convolution_result[image_idx, filter_position, output_h_idx, output_w_idx] = \
                                np.sum(inner_result)
                            output_w_idx += 1
                    output_h_idx += 1

    return convolution_result


def fast_convolve_2d(inputs, kernel, padding=0, stride=1):

    # Get required variables from the input shape
    n_images, n_channels, input_h, input_w = inputs.shape

    # Get required variables from the kernel shape
    out_channels, in_channels, kernel_h, kernel_w = kernel.shape

    # Compute the output size
    out_h = int((input_h + 2 * padding - kernel_h) / stride) + 1
    out_w = int((input_w + 2 * padding - kernel_w) / stride) + 1

    # Transform to matrix and reshape
    input_matrix = im2col_(inputs, kernel_h, kernel_w, stride, padding)

    # Reshape the kernel based on the number of channels
    # (e.g.: one channel = one row in the resulting matrix)
    kernel_matrix = kernel.reshape((out_channels, -1))

    # perform the matrix multiplication that emulates the convolution
    conv_matrix = kernel_matrix @ input_matrix

    # reshape to the expected shape after the convolution (2,2,3,3)
    conv_result = np.array(np.hsplit(conv_matrix, n_images))
    conv_result = conv_result.reshape((n_images, out_channels, out_h, out_w))

    return conv_result


# gradient_values coming from the backproagation in progress
# X original input of the layer
def convolution_backprop(X, kernel, gradient_values, padding=0, stride=1):

    output_channels = kernel.shape[0]
    input_channels = kernel.shape[1]
    kernel_h = kernel.shape[2]
    kernel_w = kernel.shape[3]

    # Initializing dX, dW with the correct shapes
    #dX = np.zeros(X.shape)
    dW = np.zeros(kernel.shape)
    dW_shape = dW.shape

    # Cycle all the images in the batch
    for image_idx in range(X.shape[0]):
        # Cycle all the filters in the convolutional layer
        # Extract a single image
        current_image = X[image_idx, :, :, :]
        # Apply padding
        current_image = np.pad(current_image, ((0, 0), (padding, padding), (padding, padding)), mode='constant')
        a = current_image.shape
        # We have to compute the derivative for every filter which is in the layer
        for filter_position in range(kernel.shape[0]):

            # Slide the image, starting from its height.
            #  - current_image.shape[0] = channels
            #  - current_image.shape[1] = height
            #  - current_image.shape[2] = width
            for i in range(0, current_image.shape[1], stride):

                # Extract the sub-portion of the image
                # - get all channels
                # - height ==> from i to i + kernel_size
                # - width ==> all the width
                image_rectangle = current_image[:, i:i + kernel_h, :]
                if image_rectangle.shape[1] < kernel_h:
                    continue
                else:
                    for j in range(0, image_rectangle.shape[2], stride):
                        if j >= image_rectangle.shape[2]:
                            continue
                        image_portion = image_rectangle[:, :, j:j + kernel_w]
                        if image_portion.shape[2] < kernel_w:
                            continue
                        else:
                            # Each channel in the input must be considered independently
                            for channel in range(image_portion.shape[0]):
                                out = image_portion[channel, :, :] * gradient_values[image_idx, filter_position, i, j]
                                dW[filter_position, channel, :, :] += out

    return dW


def fast_convolution_backprop(inputs, kernel, gradient_values, padding=0, stride=1):

    # Get required variables from the kernel shape
    out_channels, in_channels, kernel_h, kernel_w = kernel.shape

    X_col = im2col_(inputs, kernel_h, kernel_w, stride, padding)
    w_col = kernel.reshape((out_channels, -1))

    m, _, _, _ = inputs.shape

    # Compute bias gradient.
    #self.b['grad'] = np.sum(gradient_values, axis=(0, 2, 3))
    # Reshape dout properly.
    w_col_shape = w_col.shape
    gradient_values_shape = gradient_values.shape
    dout = gradient_values.reshape(gradient_values.shape[0] * gradient_values.shape[1], gradient_values.shape[2] * gradient_values.shape[3])
    dout = np.array(np.vsplit(dout, m))
    dout = np.concatenate(dout, axis=-1)
    # Perform matrix multiplication between reshaped dout and w_col to get dX_col.
    w_col_shape = w_col.shape
    dout_shape = dout.shape
    dX_col = w_col.T @ dout
    # Perform matrix multiplication between reshaped dout and X_col to get dW_col.
    dw_col = dout @ X_col.T
    # Reshape back to image (col2im).
    # dX = col2im(dX_col, inputs, kernel_h, kernel_w, stride, padding)
    # Reshape dw_col into dw.
    dW = dw_col.reshape((dw_col.shape[0], in_channels, kernel_h, kernel_w))

    return dW


def init_random_kernel(input_channels=3, output_channels=16, kernel_h=5, kernel_w=5, random=True):

    if random:
        # return np.random.rand(output_channels, input_channels, kernel_h, kernel_w) * np.sqrt(1./3.)
        n = input_channels
        for k in (kernel_h, kernel_w):
            n *= k
        stdv = 1. / np.sqrt(n)
        return np.random.uniform(low=-stdv, high=stdv, size=(output_channels, input_channels, kernel_h, kernel_w))

    else:
        return np.ones((output_channels, input_channels, kernel_h, kernel_w)) * 2


def test_convolution():
    data = [
        [[3, 1, 7, 2, 5], [5, 1, 0, 9, 2], [8, 2, 4, 9, 3], [4, 3, 1, 1, 4]],
        [[3, 1, 7, 2, 5], [9, 1, 0, 3, 2], [5, 2, 4, 8, 3], [4, 3, 1, 1, 4]],
        [[3, 1, 7, 2, 5], [5, 1, 0, 9, 2], [8, 2, 4, 9, 3], [4, 3, 1, 1, 4]]
    ]
    data = np.asarray(data, dtype=np.float64)
    data = np.expand_dims(data, axis=0)
    pad = 1

    edge_detection_kernel = np.array([
        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]  # sobel
    ], dtype=np.float64)

    edge_detection_kernel = edge_detection_kernel.reshape((1, 1, 3, 3))

    res = convolve_2d(data, edge_detection_kernel, padding=pad, stride=2)
    res = np.squeeze(res, axis=0)
    print(res)
    print()