#!/usr/bin/env python

"""
A simple example pyside app that demonstrates dragging and dropping
of files onto a GUI.
- This app allows dragging and dropping of an image file
that this then displayed in the GUI
- Alternatively an image can be loaded using the button
- This app includes a workaround for using pyside for dragging and dropping
with OSx
- This app should work on Linux, Windows and OSx
"""


from __future__ import division, unicode_literals, print_function, absolute_import

from PySide import QtGui, QtCore
import sys
import platform

import lbp

from skimage import data, io, filters
from skimage import feature
import cv2
import matplotlib.pyplot as plt
from skimage.filters import roberts, sobel, scharr, prewitt
from multiprocessing import Process

# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping on OSx
op_sys = platform.system()
if op_sys == 'Darwin':
    from Foundation import NSURL


class MainWindowWidget(QtGui.QWidget):
    """
    Subclass the widget and add a button to load images.

    Alternatively set up dragging and dropping of image files onto the widget
    """

    def __init__(self):
        super(MainWindowWidget, self).__init__()

        # Button that allows loading of images
        self.load_button = QtGui.QPushButton("Load image")
        self.load_button.clicked.connect(self.load_image_but)

        # Button that computes canny edge
        self.edge_button = QtGui.QPushButton("Canny edge")
        self.edge_button.clicked.connect(self.canny_process)

        # Button that computes normal edge
        self.edge_button_normal = QtGui.QPushButton("Normal edge")
        self.edge_button_normal.clicked.connect(self.edge_process)

        # Button that computes local binary pattern
        self.lbp_button = QtGui.QPushButton("LBP")
        self.lbp_button.clicked.connect(self.localBinaryPatter_process)

        # Image viewing region
        self.lbl = QtGui.QLabel(self)

        # A horizontal layout to include the button on the left
        layout_button = QtGui.QHBoxLayout()
        layout_button.addWidget(self.load_button)
        layout_button.addWidget(self.edge_button)
        layout_button.addWidget(self.edge_button_normal)
        layout_button.addWidget(self.lbp_button)
        layout_button.addStretch()

        # A Vertical layout to include the button layout and then the image
        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout_button)
        layout.addWidget(self.lbl)

        self.setLayout(layout)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        self.show()

    def load_image_but(self):
        """
        Open a File dialog when the button is pressed
        :return:
        """

        #Get the file location
        self.fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        # Load the image from the location
        self.load_image()

    def canny_process(self):
        p = Process(None, self.find_image_edge_canny)
        p.start()

    def edge_process(self):
        p = Process(None, self.find_image_edge)
        p.start()

    def localBinaryPatter_process(self):
        p = Process(None, self.localBinaryPatter)
        p.start()

    def localBinaryPatter(self):
        lbp.draw_lbp_plot(self.img)

    def find_image_edge_canny(self):

        im = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        edges1 = feature.canny(im)
        edges2 = feature.canny(im, sigma=2)

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(8, 3), sharex=True, sharey=True)

        # img = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        ax1.imshow(im, cmap=plt.cm.gray)
        ax1.axis('off')
        ax1.set_title('ori image', fontsize=20)

        ax2.imshow(edges1, cmap=plt.cm.gray)
        ax2.axis('off')
        ax2.set_title('Canny filter, $\sigma=1$', fontsize=20)

        ax3.imshow(edges2, cmap=plt.cm.gray)
        ax3.axis('off')
        ax3.set_title('Canny filter, $\sigma=2$', fontsize=20)

        fig.tight_layout()

        plt.show()

    def find_image_edge(self):

        image = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)

        edge_roberts = roberts(image)
        edge_sobel = sobel(image)

        fig, ax = plt.subplots(ncols=2, sharex=True, sharey=True,
                               figsize=(8, 4))

        ax[0].imshow(edge_roberts, cmap=plt.cm.gray)
        ax[0].set_title('Roberts Edge Detection')

        ax[1].imshow(edge_sobel, cmap=plt.cm.gray)
        ax[1].set_title('Sobel Edge Detection')

        for a in ax:
            a.axis('off')

        plt.tight_layout()

        plt.show()


    def load_image(self):
        """
        Set the image to the pixmap
        :return:
        """
        img = cv2.imread(self.fname, -1)
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QtGui.QImage(self.img.data, self.img.shape[1], self.img.shape[0], self.img.shape[1]*self.img.shape[2], QtGui.QImage.Format_RGB888)

        pixmap = QtGui.QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.lbl.setPixmap(pixmap)

    def update_pixelMap(self, cvImg):
        qimg = QtGui.QImage(cvImg.data, cvImg.shape[1], cvImg.shape[0], cvImg.shape[1]*cvImg.shape[2], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.lbl.setPixmap(pixmap)

    # The following three methods set up dragging and dropping for the app
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget
        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                if op_sys == 'Darwin':
                    fname = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())
                else:
                    fname = str(url.toLocalFile())

            self.fname = fname
            self.load_image()
        else:
            e.ignore()

# Run if called directly
if __name__ == '__main__':
    # Initialise the application
    app = QtGui.QApplication(sys.argv)
    # Call the widget
    ex = MainWindowWidget()
sys.exit(app.exec_())
