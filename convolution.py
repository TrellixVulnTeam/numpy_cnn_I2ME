import numpy as np

def test_convolution():
    data = [
        [[3, 1, 7, 2, 5], [5, 1, 0, 9, 2], [8, 2, 4, 9, 3], [4, 3, 1, 1, 4]],
        [[3, 1, 7, 2, 5], [9, 1, 0, 3, 2], [5, 2, 4, 8, 3], [4, 3, 1, 1, 4]],
        [[3, 1, 7, 2, 5], [5, 1, 0, 9, 2], [8, 2, 4, 9, 3], [4, 3, 1, 1, 4]]
    ]
    data = np.asarray(data, dtype=np.float32)
    data = np.expand_dims(data, axis=0)
    pad = 1

    edge_detection_kernel = np.array([
        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]  # sobel
    ], dtype=np.float32)

    edge_detection_kernel = edge_detection_kernel.reshape((1, 1, 3, 3))

    res = convolve_2d(data, edge_detection_kernel, padding=pad, stride=2)
    res = np.squeeze(res, axis=0)
    print(res)
    print()


# numberOfFilters, out_channels, kernel_size, stride
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
                            print(i, j)
                            print(image_rectangle.shape[2])
                            convolution_result[image_idx, filter_position, output_h_idx, output_w_idx] = \
                                np.sum(inner_result)
                            output_w_idx += 1
                    output_h_idx += 1

    return convolution_result
