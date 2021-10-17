import random

from cifar10 import Cifar10
from utils import show_image


def show_test_image(images, labels, classes):
    idx = random.randint(0, 10000)
    selected_class_idx = int(labels[idx])

    print('Selected index: {} - Class: {}'
          .format(idx, classes[selected_class_idx]))

    img = images[idx].reshape(3, 32, 32)
    show_image(img)


def main():
    dataset = Cifar10()

    show_test_image(dataset.train_images, dataset.train_labels, dataset.classes)


if __name__ == '__main__':
    main()
